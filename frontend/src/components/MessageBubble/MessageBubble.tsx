/**
 * MessageBubble Component
 * 
 * Displays a single message with distinct styling for user vs assistant messages.
 */

import React from 'react';
import { MessageBubbleProps } from '../../types';
import { formatTimestamp } from '../../utils/helpers';
import { parseLinks, renderLinks } from '../../utils/linkParser';
import { SourcesSection } from '../SourcesSection';
import './MessageBubble.css';

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onRetry }) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`message-bubble message-bubble--${message.role}`}>
      {/* Avatar */}
      <div className="message-bubble__avatar" aria-hidden="true">
        {isUser ? (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
          </svg>
        )}
      </div>

      {/* Content */}
      <div className="message-bubble__content">
        {/* Header with role and timestamp */}
        <div className="message-bubble__header">
          <span className="message-bubble__role">
            {isUser ? 'You' : 'FAQ Assistant'}
          </span>
          <span className="message-bubble__timestamp">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Message text */}
        {message.content && (
          <div className="message-bubble__text">
            {renderLinks(parseLinks(message.content), 'message-bubble__link')}
          </div>
        )}

        {/* Loading state */}
        {message.isLoading && (
          <div className="message-bubble__loading" role="status" aria-live="polite">
            <span className="typing-dot" aria-hidden="true"></span>
            <span className="typing-dot" aria-hidden="true"></span>
            <span className="typing-dot" aria-hidden="true"></span>
            <span className="typing-text">Thinking...</span>
            <span className="sr-only">Assistant is thinking, please wait...</span>
          </div>
        )}

        {/* Error state */}
        {message.error && (
          <div className="message-bubble__error">
            <svg 
              className="message-bubble__error-icon" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span className="message-bubble__error-text">{message.error}</span>
            {onRetry && (
              <button
                onClick={onRetry}
                className="message-bubble__retry-button"
                aria-label="Retry sending message"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="23 4 23 10 17 10" />
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
                </svg>
                Retry
              </button>
            )}
          </div>
        )}

        {/* Sources section */}
        {isAssistant && message.sources && message.sources.length > 0 && (
          <SourcesSection
            sources={message.sources}
            onSourceClick={(source) => {
              // Optional: Track source clicks for analytics
              console.log('Source clicked:', source.url);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default MessageBubble;

