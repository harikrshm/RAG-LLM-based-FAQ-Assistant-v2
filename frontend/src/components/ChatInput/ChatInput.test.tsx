/**
 * Unit tests for ChatInput component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatInput } from './ChatInput';

describe('ChatInput', () => {
  it('renders input field', () => {
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="" onChange={onChange} onSubmit={onSubmit} />);
    
    expect(screen.getByPlaceholderText(/type your question/i)).toBeInTheDocument();
  });

  it('calls onSubmit when send button is clicked', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="" onChange={onChange} onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/type your question/i);
    await user.type(input, 'Test message');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);
    
    expect(onSubmit).toHaveBeenCalled();
  });

  it('calls onSubmit when Enter key is pressed', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="" onChange={onChange} onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/type your question/i);
    await user.type(input, 'Test message');
    await user.keyboard('{Enter}');
    
    expect(onSubmit).toHaveBeenCalled();
  });

  it('does not call onSubmit for empty message', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="" onChange={onChange} onSubmit={onSubmit} />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);
    
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('does not call onSubmit when disabled', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="Test message" onChange={onChange} onSubmit={onSubmit} disabled={true} />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeDisabled();
    
    await user.click(sendButton);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('calls onChange when input value changes', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="" onChange={onChange} onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/type your question/i);
    await user.type(input, 'Test message');
    
    expect(onChange).toHaveBeenCalled();
  });

  it('handles multiline input with Shift+Enter', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatInput value="" onChange={onChange} onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/type your question/i);
    await user.type(input, 'Line 1');
    await user.keyboard('{Shift>}{Enter}{/Shift}');
    await user.type(input, 'Line 2');
    
    // Shift+Enter should create new line, not submit
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

