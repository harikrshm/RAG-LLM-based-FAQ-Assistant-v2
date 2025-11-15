/**
 * API Client
 * 
 * Low-level HTTP client for communicating with the backend API.
 * Handles request/response transformation and error handling.
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { ChatRequest, ChatResponse } from '../types';

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
}

export interface ReadinessCheckResponse {
  status: 'ready' | 'not_ready';
  checks?: Record<string, boolean>;
  timestamp: string;
}

export class ApiError extends Error {
  public code: string;
  public status?: number;
  public response?: any;

  constructor(message: string, code: string, status?: number, response?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.response = response;
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

class ApiClient {
  private client: AxiosInstance | null = null;

  /**
   * Initialize the API client with configuration
   */
  init(config: ApiClientConfig): void {

    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (requestConfig) => {
        // Optional: Add auth tokens, request IDs, etc.
        return requestConfig;
      },
      (error) => {
        return Promise.reject(this.handleError(error));
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * Get the initialized API client instance
   */
  getInstance(): AxiosInstance {
    if (!this.client) {
      throw new ApiError(
        'API client not initialized. Call init() first.',
        'CLIENT_NOT_INITIALIZED'
      );
    }
    return this.client;
  }

  /**
   * Handle errors and convert them to ApiError
   */
  private handleError(error: any): ApiError {
    // Network errors (no response)
    if (!error.response) {
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        return new ApiError(
          'Request timed out. Please try again.',
          'TIMEOUT_ERROR',
          undefined,
          error
        );
      }

      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        return new ApiError(
          'Network error. Please check your internet connection.',
          'NETWORK_ERROR',
          0,
          error
        );
      }

      return new ApiError(
        'Unable to connect to the server. Please try again later.',
        'CONNECTION_ERROR',
        0,
        error
      );
    }

    // HTTP errors (with response)
    const status = error.response.status;
    const data = error.response.data;

    // Extract error message from response
    let message = 'An error occurred';
    if (data?.detail) {
      message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    } else if (data?.message) {
      message = data.message;
    } else if (data?.error) {
      message = data.error;
    } else if (error.message) {
      message = error.message;
    }

    // Create specific error codes based on status
    let code = 'API_ERROR';
    if (status === 400) {
      code = 'BAD_REQUEST';
    } else if (status === 401) {
      code = 'UNAUTHORIZED';
    } else if (status === 403) {
      code = 'FORBIDDEN';
    } else if (status === 404) {
      code = 'NOT_FOUND';
    } else if (status === 429) {
      code = 'RATE_LIMIT';
    } else if (status >= 500) {
      code = 'SERVER_ERROR';
    }

    return new ApiError(message, code, status, data);
  }

  /**
   * Send a chat message
   */
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.getInstance().post<ChatResponse>(
        '/api/chat',
        request
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await this.getInstance().get<HealthCheckResponse>('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Readiness check endpoint
   */
  async readinessCheck(): Promise<ReadinessCheckResponse> {
    try {
      const response = await this.getInstance().get<ReadinessCheckResponse>('/ready');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }
}

// Singleton instance
const apiClient = new ApiClient();

/**
 * Initialize the API client
 */
export const initApiClient = (config: ApiClientConfig): void => {
  apiClient.init(config);
};

/**
 * Get the API client instance
 */
export const getApiClient = (): ApiClient => {
  return apiClient;
};

