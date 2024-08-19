import React, { useState, useEffect } from 'react';
import { FiX } from 'react-icons/fi';
import './ChatHistoryModal.scss';

const ChatHistoryModal = ({ onClose, onSelectSession }) => {
  const [previousChats, setPreviousChats] = useState([]);

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/chat_history');
        const data = await response.json();
        setPreviousChats(data.chat_history || []); // Ensure data.chat_history is defined
      } catch (error) {
        console.error('Error fetching chat history:', error);
        setPreviousChats([]); // Set to empty array on error
      }
    };
    fetchChatHistory();
  }, []);

  const handleChatClick = (sessionId) => {
    onSelectSession(sessionId);
    onClose();  // Close the modal after selection
  };

  return (
    <div className="chat-history-modal">
      <div className="modal-content">
        <button className="close-button" onClick={onClose}>
          <FiX size={24} />
        </button>
        <h2>Previous Chats</h2>
        <ul>
          {previousChats.map((chat) => (
            <li key={chat.session_id} onClick={() => handleChatClick(chat.session_id)}>
              {chat.last_user_message || 'Chat with Assistant'}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ChatHistoryModal;
