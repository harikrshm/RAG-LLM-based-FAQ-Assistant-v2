/**
 * ChatInput Component
 * 
 * Input field with send button for chat messages.
 */

import React, { useState, useRef, useEffect } from 'react';
import { ChatInputProps } from '../../types';
import './ChatInput.css';

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSubmit,
  disabled = false,
  placeholder = 'Type your question...',
  maxLength = 1000,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  // Focus input when component mounts or becomes enabled
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      onChange(newValue);
    }
  };

  const handleSubmit = () => {
    const trimmedValue = value.trim();
    if (trimmedValue && !disabled) {
      onSubmit();
      // Clear input after submit
      onChange('');
      // Reset textarea height
      if (inputRef.current) {
        inputRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (but allow Shift+Enter for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    
    // Escape to blur
    if (e.key === 'Escape') {
      inputRef.current?.blur();
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  const characterCount = value.length;
  const remainingChars = maxLength - characterCount;
  const isNearLimit = remainingChars < 50;
  const isAtLimit = remainingChars === 0;

  return (
    <div className={`chat-input ${isFocused ? 'chat-input--focused' : ''} ${disabled ? 'chat-input--disabled' : ''}`}>
      <div className="chat-input__wrapper">
        <textarea
          ref={inputRef}
          className="chat-input__field"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={maxLength}
          rows={1}
          aria-label="Type your message"
          aria-describedby="chat-input-hint"
        />
        
        <button
          className="chat-input__send"
          onClick={handleSubmit}
          disabled={disabled || !value.trim()}
          aria-label="Send message"
          type="button"
        >
          {disabled ? (
            <svg
              className="chat-input__send-icon chat-input__send-icon--loading"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          ) : (
            <svg
              className="chat-input__send-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>
      
      {/* Character count and hint */}
      <div className="chat-input__footer">
        <span
          id="chat-input-hint"
          className="chat-input__hint"
          aria-live="polite"
        >
          Press Enter to send, Shift+Enter for new line
        </span>
        {maxLength > 0 && (
          <span
            className={`chat-input__count ${isNearLimit ? 'chat-input__count--warning' : ''} ${isAtLimit ? 'chat-input__count--error' : ''}`}
            aria-live="polite"
          >
            {characterCount}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
};

export default ChatInput;

