import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function PublicRoute({ children }) {
  const { token } = useAuth();
  return token ? <Navigate to="/users" replace /> : children;
}

export default PublicRoute;
