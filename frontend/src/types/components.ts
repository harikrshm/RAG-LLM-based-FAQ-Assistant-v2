/**
 * TypeScript types for React components
 */

import type { Message, Source, ChatWidgetConfig } from './chat';

export interface ChatWidgetProps {
  config: ChatWidgetConfig;
  className?: string;
  onError?: (error: Error) => void;
}

export interface ChatHeaderProps {
  title: string;
  subtitle?: string;
  onClose: () => void;
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
}

export interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  onRetry?: (messageId: string) => void;
}

export interface MessageBubbleProps {
  message: Message;
  onRetry?: () => void;
}

export interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export interface SourcesSectionProps {
  sources: Source[];
  onSourceClick?: (source: Source) => void;
}

export interface FloatingButtonProps {
  onClick: () => void;
  hasUnreadMessages?: boolean;
  isOpen?: boolean;
}

export interface LoadingIndicatorProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
}

export interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export interface TypingIndicatorProps {
  show: boolean;
}

