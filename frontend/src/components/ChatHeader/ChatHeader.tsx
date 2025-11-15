/**
 * ChatHeader Component
 * 
 * Header section of the chat widget with title and controls.
 */

import React from 'react';
import type { ChatHeaderProps } from '../../types';
import './ChatHeader.css';

const ChatHeader: React.FC<ChatHeaderProps> = ({
  title,
  subtitle,
  onClose,
  isMinimized = false,
  onToggleMinimize,
}) => {
  return (
    <div className="chat-header">
      <div className="chat-header__content">
        <div className="chat-header__info">
          <h2 className="chat-header__title">{title}</h2>
          {subtitle && <p className="chat-header__subtitle">{subtitle}</p>}
        </div>
        
        <div className="chat-header__actions">
          {onToggleMinimize && (
            <button
              className="chat-header__button"
              onClick={onToggleMinimize}
              aria-label={isMinimized ? 'Maximize chat' : 'Minimize chat'}
              title={isMinimized ? 'Maximize' : 'Minimize'}
            >
              {isMinimized ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="15 3 21 3 21 9" />
                  <polyline points="9 21 3 21 3 15" />
                  <line x1="21" y1="3" x2="14" y2="10" />
                  <line x1="3" y1="21" x2="10" y2="14" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="4 14 10 14 10 20" />
                  <polyline points="20 10 14 10 14 4" />
                  <line x1="14" y1="10" x2="21" y2="3" />
                  <line x1="3" y1="21" x2="10" y2="14" />
                </svg>
              )}
            </button>
          )}
          
          <button
            className="chat-header__button chat-header__button--close"
            onClick={onClose}
            aria-label="Close chat"
            title="Close"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;

