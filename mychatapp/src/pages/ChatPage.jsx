import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import ChatRoom from '../components/ChatRoom';

const ChatPage = () => {
  const { user } = useContext(AuthContext);

  if (!user) {
    return <p>Please log in first.</p>;
  }

  return <ChatRoom token={user.token} />;
};

export default ChatPage;
