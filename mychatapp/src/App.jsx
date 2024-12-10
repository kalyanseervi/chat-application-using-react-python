import React, { useState } from "react";
import { requestFCMToken, onMessageListener } from "./api/firebase";
import { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"; // Ensure Navigate is imported
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/LoginPage";
import Register from "./pages/RegisterPage";
import UserList from "./components/Users/UserList";
import ChatRoom from "./components/ChatRoom";
import api from "./api/auth";
import {ToastContainer, toast} from 'react-toastify';




function AppRoutes() {
  const { token } = useAuth();
  const isAuthenticated = !!token;

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/users" replace /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/users" replace /> : <Register />} />
      <Route path="/users" element={isAuthenticated ? <UserList /> : <Navigate to="/login" replace />} />
      <Route path="/chat/:roomId" element={isAuthenticated ? <ChatRoom /> : <Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to={isAuthenticated ? "/users" : "/login"} replace />} />
    </Routes>
  );
}

function App() {
  const [fcmToken, setFcmToken] = useState(null);
  useEffect(() => {
    const fetchFCMToken = async () => {
      try {
        const token = await requestFCMToken();
        setFcmToken(token);
        console.log("FCM Token:", token);
      } catch (err) {
        console.error("Error getting FCM token:", err);
      }
    };

    fetchFCMToken();

    onMessageListener()
      .then((payload) => {
        console.log("Foreground message received:", payload);
        toast(
          <div>
            <strong>{payload.notification.title}</strong>
            <strong>{payload.notification.body}</strong>
          </div>,
          {position:"top-right"}
        )
      })
      .catch((err) => {
        console.error("Error receiving message:", err);
      });
  }, []); // Dependency array ensures this runs only once

  return (
    <AuthProvider>
      <ToastContainer />
     
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
