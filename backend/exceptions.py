"""
Custom Exceptions

Application-specific exceptions for better error handling.
"""

from typing import Optional, Any


class BaseAppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details
        super().__init__(self.message)


# Query-related exceptions

class QueryValidationError(BaseAppException):
    """Raised when query validation fails."""
    pass


class MalformedQueryError(QueryValidationError):
    """Raised when query is malformed or cannot be processed."""
    pass


class QueryTooLongError(QueryValidationError):
    """Raised when query exceeds maximum length."""
    pass


class EmptyQueryError(QueryValidationError):
    """Raised when query is empty or only whitespace."""
    pass


# LLM-related exceptions

class LLMServiceError(BaseAppException):
    """Base exception for LLM service errors."""
    pass


class LLMConnectionError(LLMServiceError):
    """Raised when unable to connect to LLM service."""
    pass


class LLMTimeoutError(LLMServiceError):
    """Raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMServiceError):
    """Raised when LLM rate limit is exceeded."""
    pass


class LLMAPIKeyError(LLMServiceError):
    """Raised when LLM API key is invalid or missing."""
    pass


class LLMResponseError(LLMServiceError):
    """Raised when LLM returns invalid or empty response."""
    pass


# Vector store exceptions

class VectorStoreError(BaseAppException):
    """Base exception for vector store errors."""
    pass


class VectorStoreConnectionError(VectorStoreError):
    """Raised when unable to connect to vector database."""
    pass


class VectorStoreQueryError(VectorStoreError):
    """Raised when vector database query fails."""
    pass


class VectorStoreNotInitializedError(VectorStoreError):
    """Raised when vector store is not properly initialized."""
    pass


class EmbeddingGenerationError(VectorStoreError):
    """Raised when embedding generation fails."""
    pass


# Retrieval exceptions

class RetrievalError(BaseAppException):
    """Base exception for retrieval errors."""
    pass


class NoRelevantChunksError(RetrievalError):
    """Raised when no relevant chunks are found for query."""
    pass


class ChunkProcessingError(RetrievalError):
    """Raised when chunk processing fails."""
    pass


# Service configuration exceptions

class ConfigurationError(BaseAppException):
    """Raised when service configuration is invalid."""
    pass


class ServiceUnavailableError(BaseAppException):
    """Raised when a required service is unavailable."""
    pass


# Response generation exceptions

class ResponseGenerationError(BaseAppException):
    """Base exception for response generation errors."""
    pass


class GuardrailViolationError(ResponseGenerationError):
    """Raised when response violates guardrails (advice detected)."""
    pass


class PromptTooLongError(ResponseGenerationError):
    """Raised when prompt exceeds maximum token limit."""
    pass

