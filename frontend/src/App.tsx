/**
 * App Component
 * 
 * Root application component that initializes the ChatWidget.
 */

import React, { useEffect } from 'react';
import { ChatWidget } from './components/ChatWidget';
import type { ChatWidgetConfig } from './types';
import { initApiClient } from './services/apiClient';
import './index.css';

const App: React.FC = () => {
  // Initialize API client
  useEffect(() => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    
    initApiClient({
      baseURL: apiBaseUrl,
      timeout: 30000, // 30 seconds
    });

    // Optional: Check backend health on startup
    // checkHealth().then(isHealthy => {
    //   if (!isHealthy) {
    //     console.warn('Backend health check failed');
    //   }
    // });
  }, []);

  // Widget configuration
  const config: ChatWidgetConfig = {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    position: 'bottom-right',
    theme: 'light',
    enableSoundNotifications: false,
    maxMessages: 100,
    welcomeMessage: 'Hello! I can help you with factual questions about mutual fund schemes. How can I assist you today?',
    placeholderText: 'Ask about mutual funds...',
    headerTitle: 'Mutual Fund FAQ Assistant',
    headerSubtitle: 'Powered by Groww',
  };

  // Error handler
  const handleError = (error: Error) => {
    console.error('ChatWidget Error:', error);
    // TODO: Add error tracking/reporting
  };

  return (
    <div className="app">
      <ChatWidget config={config} onError={handleError} />
    </div>
  );
};

export default App;
