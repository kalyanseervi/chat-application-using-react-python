import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import EmojiPicker from "emoji-picker-react";
import { BsImage, BsFileText } from "react-icons/bs";
import FriendList from "./FriendList"; // Optional for sidebar
import api from "../api/auth"; // Assuming you have an API service for fetching messages

const ChatRoom = () => {
  const { roomId } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [socket, setSocket] = useState(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [file, setFile] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const LIMIT = 20;
  const chatContainerRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch current user info from localStorage
    const authValue = localStorage.getItem("auth");
    if (!authValue) return;

    const parsedAuth = JSON.parse(authValue);
    setCurrentUser(parsedAuth.user);

    // Establish WebSocket connection
    const token = parsedAuth.token;
    const ws = new WebSocket(`ws://localhost:8000/chat/ws/chat/${roomId}?token=${token}`);

    ws.onopen = () => console.log("Connected to WebSocket");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "new_message") {
        setMessages((prevMessages) => [...prevMessages, data]);

        // Scroll to the bottom if user is at the bottom
        if (isAtBottom) {
          scrollToBottom();
        }
      }
    };
    ws.onerror = (e) => console.error("WebSocket error", e);
    ws.onclose = () => console.log("WebSocket connection closed");

    setSocket(ws);
    return () => {
      ws.close();
    };
  }, [roomId, isAtBottom]);

  useEffect(() => {
    fetchMessages();
  }, []);

  // Fetch messages from the server
  const fetchMessages = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const res = await api.get(`/chat/chat-room/${roomId}/messages`, {
        params: { limit: LIMIT, offset },
      });
      if (res.data.length > 0) {
        setMessages((prev) => [...res.data.reverse(), ...prev]); // Add older messages at the top
        setOffset((prev) => prev + LIMIT); // Update offset for next batch

        // Retain scroll position when older messages are loaded
        if (chatContainerRef.current) {
          const previousHeight = chatContainerRef.current.scrollHeight;
          setTimeout(() => {
            chatContainerRef.current.scrollTop =
              chatContainerRef.current.scrollHeight - previousHeight;
          }, 0);
        }
      }
    } catch (err) {
      console.error("Failed to fetch messages:", err);
    }
    setLoading(false);
  };

  // Handle scrolling to fetch older messages
  const handleScroll = () => {
    if (chatContainerRef.current.scrollTop === 0 && !loading) {
      fetchMessages();
    }

    // Update isAtBottom state based on current scroll position
    const { scrollHeight, scrollTop, clientHeight } = chatContainerRef.current;
    setIsAtBottom(scrollTop + clientHeight >= scrollHeight);
  };

  const sendMessage = () => {
    if (socket && input.trim()) {
      const messageData = {
        type: "message",
        content: input,
        file: file,
        timestamp: new Date().toISOString(),
      };

      // Add the sent message to the local state
      setMessages((prevMessages) => [
        ...prevMessages,
        { ...messageData, sender_id: currentUser.id },
      ]);

      // Send the message via WebSocket
      socket.send(JSON.stringify(messageData));

      setInput("");
      setFile(null); // Clear the file input after sending

      // Scroll to the bottom when a message is sent
      scrollToBottom();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleEmojiClick = (emoji) => {
    setInput((prevInput) => prevInput + emoji.emoji);
    setShowEmojiPicker(false);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="flex">
      {/* Optional Sidebar */}
      <FriendList />

      <div className="flex-grow p-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Chat Room {roomId}</h1>
          <button
            onClick={() => (window.location.href = "/")}
            className="bg-red-500 text-white px-4 py-2 rounded-lg"
          >
            Leave Room
          </button>
        </div>

        {/* Messages Section */}
        <div
          ref={chatContainerRef}
          className="border rounded-lg p-4 bg-white h-96 overflow-y-auto mb-4"
          onScroll={handleScroll}
        >
          {messages.map((msg, index) => {
            const isSender = msg.sender_id === currentUser?.id;
            return (
              <div
                key={index}
                className={`mb-4 flex items-start space-x-4 ${isSender ? "justify-end" : "justify-start"}`}
              >
                {!isSender && (
                  <img
                    src={`https://randomuser.me/api/portraits/men/${msg.sender_id}.jpg`}
                    alt="Sender Avatar"
                    className="w-10 h-10 rounded-full object-cover"
                  />
                )}
                <div
                  className={`max-w-md px-4 py-2 rounded-lg ${
                    isSender ? "bg-blue-100 text-right" : "bg-gray-100 text-left"
                  }`}
                >
                  <div className="font-semibold text-sm">
                    {isSender ? "You" : `User ${msg.sender_id}`}
                  </div>
                  <div>{msg.content}</div>
                  {msg.file && (
                    <div className="mt-2">
                      <a
                        href={msg.file}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 underline"
                      >
                        {msg.file.includes("image") ? (
                          <img src={msg.file} alt="Attachment" className="max-w-xs" />
                        ) : (
                          <BsFileText className="inline-block text-xl" />
                        )}
                      </a>
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-1">
                    {formatTime(msg.timestamp)}
                  </div>
                </div>
                {isSender && (
                  <img
                    src={`https://randomuser.me/api/portraits/men/${msg.sender_id}.jpg`}
                    alt="Your Avatar"
                    className="w-10 h-10 rounded-full object-cover"
                  />
                )}
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Section */}
        <div className="flex items-center">
          <div className="relative flex-grow">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              className="w-full border rounded-lg p-2 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className="absolute right-12 top-2 text-xl"
            >
              😊
            </button>
            {showEmojiPicker && (
              <div className="absolute bottom-16 left-0 z-10">
                <EmojiPicker onEmojiClick={handleEmojiClick} />
              </div>
            )}
          </div>

          <label htmlFor="file-upload" className="ml-2 cursor-pointer">
            <BsImage className="text-xl text-gray-600" />
            <input
              id="file-upload"
              type="file"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>

          <button
            onClick={sendMessage}
            className="ml-2 bg-blue-500 text-white px-4 py-2 rounded-lg"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatRoom;
