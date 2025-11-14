/**
 * Chat Service
 * 
 * High-level service for chat-related operations.
 */

import { getApiClient, ApiError } from './apiClient';
import { ChatRequest, ChatResponse, Message, Source } from '../types';
import { generateId } from '../utils/helpers';

export interface SendMessageOptions {
  query: string;
  sessionId: string;
  context?: Record<string, any>;
}

export interface SendMessageResult {
  success: boolean;
  response?: ChatResponse;
  error?: Error;
}

/**
 * Send a chat message and get response
 */
export const sendMessage = async (
  options: SendMessageOptions
): Promise<SendMessageResult> => {
  try {
    const apiClient = getApiClient();

    const request: ChatRequest = {
      query: options.query,
      sessionId: options.sessionId,
      context: options.context,
    };

    const response = await apiClient.sendChatMessage(request);

    return {
      success: true,
      response,
    };
  } catch (error) {
    // Ensure we return a proper Error object
    const apiError = error instanceof ApiError 
      ? error 
      : error instanceof Error 
        ? error 
        : new Error(String(error));
    
    return {
      success: false,
      error: apiError,
    };
  }
};

/**
 * Convert API response to Message format
 */
export const convertResponseToMessage = (
  response: ChatResponse,
  query: string
): Message => {
  // Convert sources from API format to Message format
  const sources: Source[] = response.sources.map((source) => ({
    url: source.url,
    title: source.title,
    sourceType: source.sourceType,
    amcName: source.amcName,
    relevanceScore: source.relevanceScore,
    excerpt: source.excerpt,
  }));

  return {
    id: generateId(),
    content: response.answer,
    role: 'assistant',
    timestamp: new Date(response.timestamp),
    sources: sources.length > 0 ? sources : undefined,
  };
};

/**
 * Check if backend is healthy
 */
export const checkHealth = async (): Promise<boolean> => {
  try {
    const apiClient = getApiClient();
    await apiClient.healthCheck();
    return true;
  } catch {
    return false;
  }
};

/**
 * Check if backend is ready
 */
export const checkReadiness = async (): Promise<{
  ready: boolean;
  checks?: Record<string, boolean>;
}> => {
  try {
    const apiClient = getApiClient();
    const result = await apiClient.readinessCheck();
    return {
      ready: result.status === 'ready',
      checks: result.checks,
    };
  } catch {
    return {
      ready: false,
    };
  }
};

/**
 * Get error message for display
 */
export const getErrorMessage = (error: Error): string => {
  const code = (error as any).code;
  const status = (error as any).status;

  // Network errors
  if (code === 'NETWORK_ERROR' || status === 0) {
    return 'Unable to connect to the server. Please check your internet connection and try again.';
  }

  // Rate limiting
  if (status === 429) {
    return 'Too many requests. Please wait a moment and try again.';
  }

  // Server errors
  if (status >= 500) {
    return 'Server error. Please try again later.';
  }

  // Client errors
  if (status >= 400 && status < 500) {
    return error.message || 'Invalid request. Please check your input and try again.';
  }

  // Default
  return error.message || 'An unexpected error occurred. Please try again.';
};


