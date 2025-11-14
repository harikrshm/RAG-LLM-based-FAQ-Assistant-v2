/**
 * MessageList Component
 * 
 * Displays the list of messages in the conversation history.
 */

import React, { useEffect, useRef } from 'react';
import { MessageListProps } from '../../types';
import { MessageBubble } from '../MessageBubble';
import './MessageList.css';

const MessageList: React.FC<MessageListProps> = ({ 
  messages, 
  isLoading = false,
  onRetry,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle scroll to bottom on initial load
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, []);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="message-list-empty">
        <div className="message-list-empty__icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            <line x1="9" y1="10" x2="15" y2="10" />
            <line x1="9" y1="14" x2="13" y2="14" />
          </svg>
        </div>
        <h3 className="message-list-empty__title">Start a Conversation</h3>
        <p className="message-list-empty__text">
          Ask me anything about mutual fund schemes. I can help with expense ratios, 
          exit loads, minimum SIP amounts, and more.
        </p>
      </div>
    );
  }

  return (
    <div className="message-list" ref={containerRef}>
      {messages.map((message) => (
        <div key={message.id} className="message-list__item">
          <MessageBubble
            message={message}
            onRetry={onRetry ? () => onRetry(message.id) : undefined}
          />
        </div>
      ))}
      
      {/* Loading indicator for new message */}
      {isLoading && (
        <div className="message-list__item message-list__item--loading">
          <MessageBubble
            message={{
              id: 'loading',
              content: '',
              role: 'assistant',
              timestamp: new Date(),
              isLoading: true,
            }}
          />
        </div>
      )}
      
      {/* Invisible element for auto-scroll */}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;

