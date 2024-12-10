import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/auth";  // Assuming you have an API utility to handle requests

const FriendList = () => {
  const [friends, setFriends] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const res = await api.get("/users/friends");
        setFriends(res.data);
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch friends");
        setLoading(false);
      }
    };
    fetchFriends();
  }, []);

  if (loading) {
    return (
      <div className="w-64 bg-gray-100 p-4 flex justify-center items-center">
        <span>Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-64 bg-gray-100 p-4 text-red-600">
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="w-64 bg-gray-100 p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4 text-center">Friends</h2>
      <ul className="space-y-3">
        {friends.map((friend) => (
          <li key={friend.userId} className="flex items-center space-x-3 hover:bg-gray-200 rounded-lg transition duration-200">
            <Link
              to={`/chat/chat-room/private/${friend.userId}`}
              className="flex items-center w-full p-2 text-blue-500 hover:text-blue-600"
            >
              <div className="relative">
                <img
                  src={friend.profile_picture || "/default-profile.png"}
                  alt={friend.username}
                  className="w-10 h-10 rounded-full object-cover"
                />
                {friend.is_online && (
                  <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white blink"></span>
                )}
              </div>
              <span className="ml-2 text-lg font-semibold">{friend.username}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FriendList;
