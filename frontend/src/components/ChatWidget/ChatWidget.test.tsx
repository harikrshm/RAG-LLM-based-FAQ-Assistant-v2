/**
 * Unit tests for ChatWidget component
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatWidget } from './ChatWidget';
import * as chatService from '../../services/chatService';

// Mock dependencies
vi.mock('../../services/chatService');
vi.mock('../FloatingButton', () => ({
  FloatingButton: ({ onClick }: { onClick: () => void }) => (
    <button onClick={onClick} data-testid="floating-button">
      Open Chat
    </button>
  ),
}));

describe('ChatWidget', () => {
  const defaultConfig = {
    apiBaseUrl: 'http://localhost:8000',
    welcomeMessage: 'Welcome! How can I help?',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders floating button when closed', () => {
    render(<ChatWidget config={defaultConfig} />);
    expect(screen.getByTestId('floating-button')).toBeInTheDocument();
  });

  it('opens widget when floating button is clicked', async () => {
    const user = userEvent.setup();
    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Welcome! How can I help?')).toBeInTheDocument();
    });
  });

  it('displays welcome message when configured', async () => {
    const user = userEvent.setup();
    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Welcome! How can I help?')).toBeInTheDocument();
    });
  });

  it('does not display welcome message when not configured', async () => {
    const user = userEvent.setup();
    render(<ChatWidget config={{ apiBaseUrl: 'http://localhost:8000' }} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.queryByText('Welcome! How can I help?')).not.toBeInTheDocument();
    });
  });

  it('sends message when user types and submits', async () => {
    const user = userEvent.setup();
    const mockSendMessage = vi.spyOn(chatService, 'sendMessage').mockResolvedValue({
      success: true,
      response: {
        query: 'test query',
        answer: 'test answer',
        sources: [],
        confidence_score: 0.9,
        has_sufficient_info: true,
        retrieved_chunks_count: 3,
        response_time_ms: 100,
      },
    });

    render(<ChatWidget config={defaultConfig} />);
    
    // Open widget
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    // Wait for widget to open
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    // Type and send message
    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'What is a mutual fund?');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Verify message was sent
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          query: 'What is a mutual fund?',
        })
      );
    });
  });

  it('displays user message immediately after sending', async () => {
    const user = userEvent.setup();
    vi.spyOn(chatService, 'sendMessage').mockResolvedValue({
      success: true,
      response: {
        query: 'test query',
        answer: 'test answer',
        sources: [],
        confidence_score: 0.9,
        has_sufficient_info: true,
        retrieved_chunks_count: 3,
        response_time_ms: 100,
      },
    });

    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'Test message');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });
  });

  it('displays loading indicator while sending message', async () => {
    const user = userEvent.setup();
    vi.spyOn(chatService, 'sendMessage').mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        success: true,
        response: {
          query: 'test',
          answer: 'answer',
          sources: [],
          confidence_score: 0.9,
          has_sufficient_info: true,
          retrieved_chunks_count: 3,
          response_time_ms: 100,
        },
      }), 100))
    );

    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'Test');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Check for loading indicator
    await waitFor(() => {
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  it('displays error message when API call fails', async () => {
    const user = userEvent.setup();
    const mockError = new Error('API Error');
    vi.spyOn(chatService, 'sendMessage').mockRejectedValue(mockError);

    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'Test');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('calls onError callback when error occurs', async () => {
    const user = userEvent.setup();
    const onError = vi.fn();
    const mockError = new Error('API Error');
    vi.spyOn(chatService, 'sendMessage').mockRejectedValue(mockError);

    render(<ChatWidget config={defaultConfig} onError={onError} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'Test');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(onError).toHaveBeenCalled();
    });
  });

  it('prevents sending empty messages', async () => {
    const user = userEvent.setup();
    const mockSendMessage = vi.spyOn(chatService, 'sendMessage');

    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it('prevents sending message while loading', async () => {
    const user = userEvent.setup();
    vi.spyOn(chatService, 'sendMessage').mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        success: true,
        response: {
          query: 'test',
          answer: 'answer',
          sources: [],
          confidence_score: 0.9,
          has_sufficient_info: true,
          retrieved_chunks_count: 3,
          response_time_ms: 100,
        },
      }), 100))
    );

    render(<ChatWidget config={defaultConfig} />);
    
    const button = screen.getByTestId('floating-button');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'First message');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Try to send another message while loading
    await user.type(input, 'Second message');
    await user.click(sendButton);

    // Should only have one API call
    await waitFor(() => {
      expect(chatService.sendMessage).toHaveBeenCalledTimes(1);
    });
  });
});

