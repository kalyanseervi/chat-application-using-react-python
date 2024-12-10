import axios from "axios";

const API_URL = "http://localhost:8000"; // Replace with your backend URL

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const authValue = localStorage.getItem("auth"); // Get the stored value of "auth"

  if (authValue) {
    try {
      const parsedAuth = JSON.parse(authValue); // Parse the string into an object
      const token = parsedAuth.token; // Access the token from the parsed object

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error("Error parsing auth data:", error); // Handle any parsing errors
    }
  }

  return config;
});

// Handle expired or invalid tokens globally
api.interceptors.response.use(
  (response) => response, // Pass through successful responses
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle expired or invalid token
      console.warn("Session expired or unauthorized access detected.");
      localStorage.removeItem("auth"); // Clear stored token
      window.location.href = "/login"; // Redirect to login
      alert("Session expired. Please log in again.");
    }
    return Promise.reject(error);
  }
);

export default api;
