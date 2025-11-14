/**
 * TypeScript types for chat functionality
 */

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  sources?: Source[];
  isLoading?: boolean;
  error?: string;
}

export interface Source {
  url: string;
  title?: string;
  sourceType?: 'groww_page' | 'amc_website' | 'sebi_website' | 'amfi_website' | 'unknown';
  amcName?: string;
  relevanceScore?: number;
  excerpt?: string;
}

export interface ChatRequest {
  query: string;
  sessionId?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  query: string;
  answer: string;
  sources: Source[];
  confidenceScore?: number;
  hasSufficientInfo?: boolean;
  fallbackMessage?: string;
  retrievedChunksCount?: number;
  responseTimeMs?: number;
  timestamp: string;
}

export interface ChatWidgetConfig {
  apiBaseUrl: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  theme?: 'light' | 'dark' | 'auto';
  enableSoundNotifications?: boolean;
  maxMessages?: number;
  welcomeMessage?: string;
  placeholderText?: string;
  headerTitle?: string;
  headerSubtitle?: string;
}

export interface ChatState {
  messages: Message[];
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  hasUnreadMessages: boolean;
}

export type MessageRole = 'user' | 'assistant';

export type SourceType = 'groww_page' | 'amc_website' | 'sebi_website' | 'amfi_website' | 'unknown';

