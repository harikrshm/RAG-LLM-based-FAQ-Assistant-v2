/**
 * FloatingButton Component
 * 
 * Floating action button to open/close the chat widget.
 */

import React from 'react';
import { FloatingButtonProps } from '../../types';
import './FloatingButton.css';

const FloatingButton: React.FC<FloatingButtonProps> = ({
  onClick,
  hasUnreadMessages = false,
  isOpen = false,
}) => {
  return (
    <button
      className={`floating-button ${isOpen ? 'floating-button--open' : ''}`}
      onClick={onClick}
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
      aria-expanded={isOpen}
    >
      {/* Icon changes based on open state */}
      {isOpen ? (
        <svg
          className="floating-button__icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      ) : (
        <>
          <svg
            className="floating-button__icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          {hasUnreadMessages && (
            <span className="floating-button__badge" aria-label="Unread messages">
              •
            </span>
          )}
        </>
      )}
    </button>
  );
};

export default FloatingButton;

