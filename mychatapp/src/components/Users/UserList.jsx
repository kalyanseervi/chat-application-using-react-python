import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/auth";
import LogoutButton from "../LogoutButton";
import {  toast } from "react-toastify";

function UserList() {
  const [users, setUsers] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [friends, setFriends] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true); // To show a skeleton loader

  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
    fetchFriendRequests();
    fetchFriends();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.get("/users");
      setUsers(res.data);
    } catch (err) {
      setError("Failed to fetch users");
    } finally {
      setLoading(false); // Hide the loader
    }
  };

  const fetchFriendRequests = async () => {
    try {
      const res = await api.get("/users/friend-requests");
      setFriendRequests(res.data);
    } catch (err) {
      setError("Failed to fetch friend requests");
    }
  };

  const fetchFriends = async () => {
    try {
      const res = await api.get("/users/friends");
      setFriends(res.data);
    } catch (err) {
      setError("Failed to fetch friends");
    }
  };

  const sendFriendRequest = async (receiverId) => {
    try {
      await api.post(`/users/friend-request/${receiverId}`);
      toast.success('Friend request sent!')
      
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send friend request");
    }
  };

  const acceptFriendRequest = async (requestId) => {
    try {
      await api.post(`/users/accept-friend-request/${requestId}`);
      toast.success('Friend request accepted!')
      
      fetchFriendRequests();
      fetchFriends();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to accept friend request");
    }
  };

  const openChat = async (friendId) => {
    try {
      const res = await api.post(`/chat/chat-room/private/${friendId}`);
      const roomId = res.data.room_id;
      navigate(`/chat/${roomId}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create or fetch chat room");
    }
  };

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Your Dashboard</h1>
        <LogoutButton />
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      {/* Skeleton Loader */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className="animate-pulse p-4 border rounded-lg shadow-md bg-gray-100"
            >
              <div className="w-12 h-12 bg-gray-300 rounded-full mb-4"></div>
              <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-300 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Friends Section */}
          <h2 className="text-2xl font-semibold mt-8 mb-4">Your Friends</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {friends.length === 0 ? (
              <p className="text-gray-500">No friends yet. Start sending requests!</p>
            ) : (
              friends.map((friend) => (
                <div
                  key={friend.userId}
                  className="p-4 border rounded-lg shadow-md bg-white hover:shadow-lg transition"
                >
                  <div className="flex items-center space-x-4">
                    <img
                      src={friend.profile_picture || "https://via.placeholder.com/150"}
                      alt={friend.username}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    <div className="flex-grow">
                      <h3 className="text-lg font-semibold">{friend.username}</h3>
                      <p className={`text-sm ${friend.is_online ? "text-green-500" : "text-gray-400"}`}>
                        {friend.is_online ? "Online" : "Offline"}
                      </p>
                    </div>
                    <button
                      className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                      onClick={() => openChat(friend.userId)}
                    >
                      Chat
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Friend Requests Section */}
          <h2 className="text-2xl font-semibold mt-8 mb-4">Friend Requests</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {friendRequests.length === 0 ? (
              <p className="text-gray-500">No pending friend requests!</p>
            ) : (
              friendRequests.map((request) => (
                <div
                  key={request.id}
                  className="p-4 border rounded-lg shadow-md bg-white hover:shadow-lg transition"
                >
                  <div className="flex items-center space-x-4">
                    <img
                      src={request.user.profile_picture || "https://via.placeholder.com/150"}
                      alt={request.user.username}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    <div>
                      <h3 className="text-lg font-semibold">{request.user.username}</h3>
                    </div>
                    <button
                      className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
                      onClick={() => acceptFriendRequest(request.id)}
                    >
                      Accept
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* All Users Section */}
          <h2 className="text-2xl font-semibold mt-8 mb-4">Discover Users</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {users.map((user) => (
              <div
                key={user.id}
                className="p-4 border rounded-lg shadow-md bg-white hover:shadow-lg transition"
              >
                <div className="flex items-center space-x-4">
                  <img
                    src={user.profile_picture || "https://via.placeholder.com/150"}
                    alt={user.username}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <h3 className="text-lg font-semibold">{user.username}</h3>
                  </div>
                  <button
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                    onClick={() => sendFriendRequest(user.id)}
                  >
                    Add Friend
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default UserList;
