/**
 * ChatWidget Component
 * 
 * Main chat widget component with floating button and expandable interface.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ChatWidgetProps, ChatState, Message } from '../../types';
import { generateId } from '../../utils/helpers';
import { sendMessage, convertResponseToMessage, getErrorMessage } from '../../services/chatService';
import { FloatingButton } from '../FloatingButton';
import { ChatHeader } from '../ChatHeader';
import { MessageList } from '../MessageList';
import { ChatInput } from '../ChatInput';
import LoadingOverlay from './LoadingOverlay';
import './ChatWidget.css';

const ChatWidget: React.FC<ChatWidgetProps> = ({ config, className, onError }) => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isOpen: false,
    isLoading: false,
    error: null,
    sessionId: null,
    hasUnreadMessages: false,
  });

  const [isMinimized, setIsMinimized] = useState(false);

  // Initialize session ID
  useEffect(() => {
    const sessionId = generateId();
    setState(prev => ({ ...prev, sessionId }));
    
    // Add welcome message if configured
    if (config.welcomeMessage) {
      const welcomeMsg: Message = {
        id: generateId(),
        content: config.welcomeMessage,
        role: 'assistant',
        timestamp: new Date(),
      };
      setState(prev => ({
        ...prev,
        messages: [welcomeMsg],
      }));
    }
  }, [config.welcomeMessage]);

  // Handle opening/closing widget
  const toggleWidget = useCallback(() => {
    setState(prev => ({
      ...prev,
      isOpen: !prev.isOpen,
      hasUnreadMessages: prev.isOpen ? prev.hasUnreadMessages : false,
    }));
    
    // Reset minimized state when closing
    if (state.isOpen) {
      setIsMinimized(false);
    }
  }, [state.isOpen]);

  // Handle minimize/maximize
  const toggleMinimize = useCallback(() => {
    setIsMinimized(prev => !prev);
  }, []);

  const [inputValue, setInputValue] = useState('');

  // Handle sending messages
  const handleSendMessage = useCallback(async () => {
    const trimmedValue = inputValue.trim();
    if (!trimmedValue || state.isLoading || !state.sessionId) {
      return;
    }

    // Add user message to chat
    const userMessage: Message = {
      id: generateId(),
      content: trimmedValue,
      role: 'user',
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    // Clear input
    setInputValue('');

    // Send message to API
    try {
      const result = await sendMessage({
        query: trimmedValue,
        sessionId: state.sessionId,
      });

      if (result.success && result.response) {
        // Convert API response to Message format
        const assistantMessage = convertResponseToMessage(
          result.response,
          trimmedValue
        );

        setState(prev => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
          isLoading: false,
        }));
      } else {
        // Handle error
        const errorMessage = result.error
          ? getErrorMessage(result.error)
          : 'Failed to get response. Please try again.';

        const errorMsg: Message = {
          id: generateId(),
          content: '',
          role: 'assistant',
          timestamp: new Date(),
          error: errorMessage,
        };

        setState(prev => ({
          ...prev,
          messages: [...prev.messages, errorMsg],
          isLoading: false,
          error: errorMessage,
        }));

        // Call error handler if provided
        if (onError && result.error) {
          onError(result.error);
        }
      }
    } catch (error) {
      // Unexpected error
      const errorMessage = error instanceof Error
        ? getErrorMessage(error)
        : 'An unexpected error occurred. Please try again.';

      const errorMsg: Message = {
        id: generateId(),
        content: '',
        role: 'assistant',
        timestamp: new Date(),
        error: errorMessage,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMsg],
        isLoading: false,
        error: errorMessage,
      }));

      if (onError) {
        onError(error instanceof Error ? error : new Error(String(error)));
      }
    }
  }, [inputValue, state.isLoading, state.sessionId, onError]);

  // Position class based on config
  const positionClass = config.position || 'bottom-right';

  return (
    <div className={`chat-widget-container chat-widget-container--${positionClass} ${className || ''}`}>
      {/* Floating button */}
      {!state.isOpen && (
        <FloatingButton
          onClick={toggleWidget}
          hasUnreadMessages={state.hasUnreadMessages}
          isOpen={state.isOpen}
        />
      )}

      {/* Chat widget */}
      {state.isOpen && (
        <div
          className={`chat-widget ${isMinimized ? 'chat-widget--minimized' : ''}`}
          role="dialog"
          aria-label={config.headerTitle || 'Chat widget'}
          aria-modal="true"
        >
          {/* Loading overlay - shown during API calls */}
          {state.isLoading && !isMinimized && (
            <LoadingOverlay show={state.isLoading} message="Getting answer..." />
          )}
          {/* Header */}
          <ChatHeader
            title={config.headerTitle || 'FAQ Assistant'}
            subtitle={config.headerSubtitle || 'Ask questions about mutual funds'}
            onClose={toggleWidget}
            isMinimized={isMinimized}
            onToggleMinimize={toggleMinimize}
          />

          {/* Body - Only show if not minimized */}
          {!isMinimized && (
            <>
              <div className="chat-widget-body">
                <MessageList
                  messages={state.messages}
                  isLoading={state.isLoading}
                  onRetry={(messageId) => {
                    // TODO: Implement retry logic
                    console.log('Retry message:', messageId);
                  }}
                />
              </div>

              {/* Footer */}
              <div className="chat-widget-footer">
                <ChatInput
                  value={inputValue}
                  onChange={setInputValue}
                  onSubmit={handleSendMessage}
                  disabled={state.isLoading}
                  placeholder={config.placeholderText || 'Type your question...'}
                  maxLength={config.maxMessages ? undefined : 1000}
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatWidget;

