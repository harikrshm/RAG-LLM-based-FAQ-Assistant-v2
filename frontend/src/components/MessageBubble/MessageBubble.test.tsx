/**
 * Unit tests for MessageBubble component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble } from './MessageBubble';
import { Message } from '../../types/chat';

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    const userMessage: Message = {
      id: '1',
      content: 'Hello',
      role: 'user',
      timestamp: new Date('2024-01-01T10:00:00Z'),
    };

    render(<MessageBubble message={userMessage} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText(/10:00/i)).toBeInTheDocument();
  });

  it('renders assistant message correctly', () => {
    const assistantMessage: Message = {
      id: '2',
      content: 'Hi there!',
      role: 'assistant',
      timestamp: new Date('2024-01-01T10:00:01Z'),
    };

    render(<MessageBubble message={assistantMessage} />);
    
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
    expect(screen.getByText('FAQ Assistant')).toBeInTheDocument();
  });

  it('renders error message when error is present', () => {
    const errorMessage: Message = {
      id: '3',
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      error: 'Something went wrong',
    };

    render(<MessageBubble message={errorMessage} />);
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('displays retry button for error messages', () => {
    const onRetry = vi.fn();
    const errorMessage: Message = {
      id: '3',
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      error: 'Error message',
    };

    render(<MessageBubble message={errorMessage} onRetry={onRetry} />);
    
    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();
    
    retryButton.click();
    expect(onRetry).toHaveBeenCalled();
  });

  it('does not display retry button when no error', () => {
    const message: Message = {
      id: '1',
      content: 'Normal message',
      role: 'user',
      timestamp: new Date(),
    };

    render(<MessageBubble message={message} />);
    
    expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
  });

  it('renders sources when present', () => {
    const messageWithSources: Message = {
      id: '1',
      content: 'Answer with sources',
      role: 'assistant',
      timestamp: new Date(),
      sources: [
        {
          url: 'https://example.com',
          title: 'Example Source',
          sourceType: 'groww_page',
        },
        {
          url: 'https://example2.com',
          title: 'Another Source',
          sourceType: 'amc_website',
        },
      ],
    };

    render(<MessageBubble message={messageWithSources} />);
    
    expect(screen.getByTestId('sources-section')).toBeInTheDocument();
    expect(screen.getByText('Example Source')).toBeInTheDocument();
    expect(screen.getByText('Another Source')).toBeInTheDocument();
  });

  it('does not render sources section when no sources', () => {
    const message: Message = {
      id: '1',
      content: 'Answer without sources',
      role: 'assistant',
      timestamp: new Date(),
    };

    render(<MessageBubble message={message} />);
    
    expect(screen.queryByTestId('sources-section')).not.toBeInTheDocument();
  });

  it('renders links in message content', () => {
    const messageWithLink: Message = {
      id: '1',
      content: 'Check out https://example.com for more info',
      role: 'assistant',
      timestamp: new Date(),
    };

    render(<MessageBubble message={messageWithLink} />);
    
    const link = screen.getByRole('link', { name: /example.com/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://example.com');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('applies correct CSS class based on role', () => {
    const userMessage: Message = {
      id: '1',
      content: 'User message',
      role: 'user',
      timestamp: new Date(),
    };

    const { container } = render(<MessageBubble message={userMessage} />);
    const bubble = container.querySelector('.message-bubble--user');
    expect(bubble).toBeInTheDocument();
  });
});

