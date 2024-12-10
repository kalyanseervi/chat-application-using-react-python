// src/components/LogoutButton.jsx

import React from "react";
import { useAuth } from "../context/AuthContext";  // Assuming the correct path
import api from "../api/auth";

const LogoutButton = () => {
    const { logoutUser } = useAuth();
  

    const handleLogout = async () => {
        try {
            await api.post("/auth/logout");  // Send logout request to the backend
            logoutUser();  // Clear frontend authentication
            window.location.href = "/"
        } catch (error) {
            console.error("Error logging out", error);
        }
    };

    return (
        <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg mb-4"
        >
            Logout
        </button>
    );
};

export default LogoutButton;
