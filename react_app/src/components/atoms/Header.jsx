import React, { useState } from 'react';
import { HiChatBubbleLeftEllipsis } from "react-icons/hi2";
import ChatHistoryModal from './ChatHistoryModal';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRobot } from '@fortawesome/free-solid-svg-icons';
import './Header.scss';

const Header = ({ onSelectSession }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <header className="header">
      <div className="header-left">
        <FontAwesomeIcon icon={faRobot} className="robot-icon" />
        <h1>Python Assistant</h1>
      </div>
      <div className="header-right">
        <button className="history-button" onClick={handleOpenModal} title="Previous Chat">
          <HiChatBubbleLeftEllipsis size={20} />
        </button>
      </div>
      {isModalOpen && <ChatHistoryModal onClose={handleCloseModal} onSelectSession={onSelectSession} />}
    </header>
  );
};

export default Header;
