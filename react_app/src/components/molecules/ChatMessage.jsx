import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { TiThumbsUp, TiThumbsDown } from 'react-icons/ti';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { FiCopy, FiCheck } from 'react-icons/fi';
import './ChatMessage.scss';

const ChatMessage = ({ message, isUser, onThumbUp, onThumbDown }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 500);
  };

  console.log('Rendering message:', message); // Debugging log

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}>
      <div className="message-content">
        <ReactMarkdown
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <div style={{ position: 'relative' }}>
                  <SyntaxHighlighter
                    style={atomDark}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                  <CopyToClipboard text={String(children)} onCopy={handleCopy}>
                    <button className="copy-button">
                      {copied ? <FiCheck /> : <FiCopy />}
                    </button>
                  </CopyToClipboard>
                </div>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.text}
        </ReactMarkdown>
      </div>
      {!isUser && (
        <div className="feedback-container">
          <div className="feedback-buttons">
            <button className="thumbs-up" onClick={onThumbUp}>
              <TiThumbsUp />
            </button>
            <button className="thumbs-down" onClick={onThumbDown}>
              <TiThumbsDown />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
