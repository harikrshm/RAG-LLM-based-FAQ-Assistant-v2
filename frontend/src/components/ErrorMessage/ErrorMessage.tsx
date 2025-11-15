/**
 * ErrorMessage Component
 * 
 * Displays error messages with retry and dismiss options.
 */

import React from 'react';
import type { ErrorMessageProps } from '../../types';
import './ErrorMessage.css';

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  onRetry,
  onDismiss,
}) => {
  return (
    <div className="error-message" role="alert" aria-live="assertive">
      <div className="error-message__content">
        <div className="error-message__icon">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <div className="error-message__text">
          <p className="error-message__title">Something went wrong</p>
          <p className="error-message__description">{message}</p>
        </div>
      </div>
      
      <div className="error-message__actions">
        {onRetry && (
          <button
            className="error-message__retry"
            onClick={onRetry}
            aria-label="Retry request"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            className="error-message__dismiss"
            onClick={onDismiss}
            aria-label="Dismiss error"
          >
            <svg
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
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;


