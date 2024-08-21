import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from '../molecules/ChatMessage';
import Header from '../atoms/Header';
import LoadingDots from '../atoms/LoadingDots';
import { BsChatRightFill } from "react-icons/bs";
import './ChatWindow.scss';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchSessionId = async () => {
      try {
        const response = await fetch('http://accurate-correy-honoured1-16c870eb.koyeb.app/api/new_session');
        const data = await response.json();
        setSessionId(data.session_id);
      } catch (error) {
        console.error('Error fetching session ID:', error);
      }
    };
    fetchSessionId();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchAIResponse = async (userMessage) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://accurate-correy-honoured1-16c870eb.koyeb.app/api/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { text: data.response, isUser: false }
      ]);
    } catch (error) {
      console.error('Error fetching AI response:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => {
    if (input.trim() === '') return; // Prevent sending empty messages
    const userMessage = input;
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);
    setInput('');
    fetchAIResponse(userMessage);
  };

  const handleNewChat = () => {
    window.location.reload();
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const sendFeedback = async (message, responseText, feedback) => {
    try {
      const feedbackData = {
        session_id: sessionId,
        message,
        response: responseText,
        feedback,
      };
      const feedbackResponse = await fetch('http://accurate-correy-honoured1-16c870eb.koyeb.app/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });
      const data = await feedbackResponse.json();
      console.log('Feedback response:', data); // Debugging log
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  };

  const handleThumbUp = (index) => {
    if (index > 0) {
      const userMessage = messages[index - 1].text;
      const aiResponse = messages[index].text;
      sendFeedback(userMessage, aiResponse, 'positive');
    }
  };

  const handleThumbDown = (index) => {
    if (index > 0) {
      const userMessage = messages[index - 1].text;
      const aiResponse = messages[index].text;
      sendFeedback(userMessage, aiResponse, 'negative');
    }
  };

  const handleSelectSession = (selectedSessionId) => {
    console.log('Selected session ID:', selectedSessionId); // Debugging log
    setSessionId(selectedSessionId);
    fetchChatHistory(selectedSessionId);
  };

  const fetchChatHistory = async (sessionId) => {
    try {
      const response = await fetch(`http://accurate-correy-honoured1-16c870eb.koyeb.app/api/chat_history/${sessionId}`);
      const data = await response.json();
      console.log('Fetched chat history:', data); // Debugging log

      // Map over the chat history and create separate entries for user and AI messages
      const formattedMessages = data.messages.flatMap((msg) => [
        { text: msg.message, isUser: true },
        { text: msg.response, isUser: false }
      ]);

      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error fetching chat history:', error);
      setMessages([]); // Set to empty array on error
    }
  };

  return (
    <div className="chat-window">
      <Header onSelectSession={handleSelectSession} /> {/* Pass the handleSelectSession function to Header */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            message={msg}
            isUser={msg.isUser}
            onThumbUp={() => handleThumbUp(index)}
            onThumbDown={() => handleThumbDown(index)}
          />
        ))}
        {isLoading && <LoadingDots />}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          rows="3"
        />
        <button className="new-chat-button" onClick={handleNewChat} title="New Chat">
          <BsChatRightFill size={17} />
        </button>
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;
