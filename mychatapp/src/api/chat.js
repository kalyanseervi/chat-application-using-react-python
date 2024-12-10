import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/chat';

export const fetchChatRooms = async (token) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/rooms`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching chat rooms:', error);
    throw error;
  }
};
