import React, { createContext, useState, useEffect, useContext, useMemo } from "react";

// Create AuthContext
export const AuthContext = createContext();

// Custom hook for using AuthContext
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    user: null,
    token: null,
  });

  // Load auth data from localStorage when the component mounts
  useEffect(() => {
    try {
      const storedAuth = localStorage.getItem("auth");
      if (storedAuth) {
        setAuth(JSON.parse(storedAuth));
      }
    } catch (error) {
      console.error("Failed to parse auth data from localStorage:", error);
    }
  }, []);

  // Login function
  const loginUser = (data) => {
    setAuth(data);
    try {
      localStorage.setItem("auth", JSON.stringify(data)); // Save to localStorage
    } catch (error) {
      console.error("Failed to save auth data to localStorage:", error);
    }
  };

  // Logout function
  const logoutUser = () => {
    setAuth({ user: null, token: null });
    try {
      localStorage.removeItem("auth");
    } catch (error) {
      console.error("Failed to remove auth data from localStorage:", error);
    }
  };

  // Memoize the context value to prevent unnecessary re-renders
  const value = useMemo(() => ({ ...auth, loginUser, logoutUser }), [auth]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
