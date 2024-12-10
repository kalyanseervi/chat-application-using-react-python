import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {  toast } from "react-toastify";
import api from "../api/auth";

function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Reset error state
    setLoading(true); // Show loading state

    // Input validation
    if (!formData.username || !formData.email || !formData.password) {
      setError("All fields are required.");
      setLoading(false);
      return;
    }

    try {
      // Make register request to the API
      const response = await api.post("/auth/register", formData);

      toast.success("Successfully Registered!");

      // Delay redirection to allow the toast to display
      setTimeout(() => {
        navigate("/login");
      }, 3000); // Adjust the timeout as needed (3 seconds here)
    } catch (err) {
      // Handle errors
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false); // Hide loading state
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-sm bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-700 text-center">Create an Account</h2>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 p-3 rounded-md text-center mt-4">
            {error}
          </div>
        )}

        {/* Registration Form */}
        <form className="mt-6" onSubmit={handleSubmit}>
          {/* Username Field */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-600">
              Username
            </label>
            <input
              id="username"
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
              placeholder="Enter your username"
              required
            />
          </div>

          {/* Email Field */}
          <div className="mt-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-600">
              Email
            </label>
            <input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
              placeholder="Enter your email"
              required
            />
          </div>

          {/* Password Field */}
          <div className="mt-4">
            <label htmlFor="password" className="block text-sm font-medium text-gray-600">
              Password
            </label>
            <input
              id="password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
              placeholder="Enter your password"
              required
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className={`w-full bg-green-500 text-white py-2 mt-6 rounded-lg ${
              loading ? "opacity-50 cursor-not-allowed" : "hover:bg-green-600 transition-all"
            }`}
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">
            Already have an account?{" "}
            <a href="/login" className="text-green-600 hover:underline">
              Log in
            </a>
          </p>
        </div>
      </div>

     
      
    </div>
  );
}

export default Register;
