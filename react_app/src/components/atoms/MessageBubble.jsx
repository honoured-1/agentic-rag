import React from 'react';
import ReactMarkdown from 'react-markdown';
import './MessageBubble.scss';
import hljs from 'highlight.js';
import { useEffect } from 'react';
const MessageBubble = ({ message, isUser }) => {
 useEffect(() => {
   document.querySelectorAll('pre code').forEach((block) => {
     hljs.highlightBlock(block);
   });
 }, [message]);
 return (
<div className={`message-bubble ${isUser ? 'user' : 'ai'}`}>
<ReactMarkdown>{message}</ReactMarkdown>
</div>
 );
};
export default MessageBubble;