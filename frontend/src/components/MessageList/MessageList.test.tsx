/**
 * Unit tests for MessageList component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageList } from './MessageList';
import { Message } from '../../types/chat';

describe('MessageList', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      content: 'Hello',
      role: 'user',
      timestamp: new Date('2024-01-01T10:00:00Z'),
    },
    {
      id: '2',
      content: 'Hi there!',
      role: 'assistant',
      timestamp: new Date('2024-01-01T10:00:01Z'),
    },
  ];

  it('renders empty state when no messages', () => {
    render(<MessageList messages={[]} />);
    
    expect(screen.getByText('Start a Conversation')).toBeInTheDocument();
    expect(screen.getByText(/Ask me anything about mutual fund schemes/i)).toBeInTheDocument();
  });

  it('renders list of messages', () => {
    render(<MessageList messages={mockMessages} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('displays loading indicator when loading', () => {
    render(<MessageList messages={mockMessages} isLoading={true} />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('does not display loading indicator when not loading', () => {
    render(<MessageList messages={mockMessages} isLoading={false} />);
    
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', async () => {
    const onRetry = vi.fn();
    const messagesWithError: Message[] = [
      {
        id: '1',
        content: '',
        role: 'assistant',
        timestamp: new Date(),
        error: 'Error message',
      },
    ];

    render(<MessageList messages={messagesWithError} onRetry={onRetry} />);
    
    const retryButton = screen.getByRole('button', { name: /retry/i });
    retryButton.click();

    expect(onRetry).toHaveBeenCalledWith('1');
  });

  it('renders messages in correct order', () => {
    const orderedMessages: Message[] = [
      {
        id: '1',
        content: 'First',
        role: 'user',
        timestamp: new Date('2024-01-01T10:00:00Z'),
      },
      {
        id: '2',
        content: 'Second',
        role: 'assistant',
        timestamp: new Date('2024-01-01T10:00:01Z'),
      },
      {
        id: '3',
        content: 'Third',
        role: 'user',
        timestamp: new Date('2024-01-01T10:00:02Z'),
      },
    ];

    render(<MessageList messages={orderedMessages} />);
    
    const messageElements = screen.getAllByText(/First|Second|Third/);
    expect(messageElements[0]).toHaveTextContent('First');
    expect(messageElements[1]).toHaveTextContent('Second');
    expect(messageElements[2]).toHaveTextContent('Third');
  });

  it('handles messages with sources', () => {
    const messageWithSources: Message[] = [
      {
        id: '1',
        content: 'Answer with sources',
        role: 'assistant',
        timestamp: new Date(),
        sources: [
          {
            url: 'https://example.com',
            title: 'Example Source',
            source_type: 'groww_page',
          },
        ],
      },
    ];

    render(<MessageList messages={messageWithSources} />);
    
    expect(screen.getByText('Answer with sources')).toBeInTheDocument();
    expect(screen.getByText('Example Source')).toBeInTheDocument();
  });
});

