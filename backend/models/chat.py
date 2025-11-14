"""
Chat Models

Pydantic models for chat request/response with source citations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Enum for source types."""
    GROWW_PAGE = "groww_page"
    AMC_WEBSITE = "amc_website"
    SEBI_WEBSITE = "sebi_website"
    AMFI_WEBSITE = "amfi_website"
    UNKNOWN = "unknown"


class SourceCitation(BaseModel):
    """
    Model for source citation.
    
    Represents a single source that contributed to the answer.
    """
    url: str = Field(..., description="Source URL")
    title: Optional[str] = Field(None, description="Page/document title")
    source_type: SourceType = Field(
        default=SourceType.UNKNOWN,
        description="Type of source"
    )
    amc_name: Optional[str] = Field(None, description="AMC name if applicable")
    relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Relevance score (0-1)"
    )
    excerpt: Optional[str] = Field(
        None,
        max_length=200,
        description="Short excerpt from source"
    )
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
                "title": "HDFC Equity Fund - Direct Growth",
                "source_type": "groww_page",
                "amc_name": "HDFC Mutual Fund",
                "relevance_score": 0.92,
                "excerpt": "The expense ratio for HDFC Equity Fund is 1.5%..."
            }
        }


class ChatRequest(BaseModel):
    """
    Model for chat request.
    
    Represents a user query to the FAQ assistant.
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query about mutual funds"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for tracking conversation"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context (e.g., user preferences, filters)"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """Validate and clean query."""
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Check for empty query after cleaning
        if not v.strip():
            raise ValueError('Query cannot be empty')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the expense ratio of HDFC Equity Fund?",
                "session_id": "user-session-123",
                "context": {
                    "amc_filter": "HDFC Mutual Fund"
                }
            }
        }


class ChatResponse(BaseModel):
    """
    Model for chat response.
    
    Represents the assistant's answer with source citations.
    """
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceCitation] = Field(
        default_factory=list,
        description="List of source citations"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for the answer (0-1)"
    )
    has_sufficient_info: bool = Field(
        default=True,
        description="Whether sufficient information was found to answer"
    )
    fallback_message: Optional[str] = Field(
        None,
        description="Fallback message if information is insufficient"
    )
    retrieved_chunks_count: int = Field(
        default=0,
        ge=0,
        description="Number of chunks retrieved from knowledge base"
    )
    response_time_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Response generation time in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )
    
    @validator('answer')
    def validate_answer(cls, v):
        """Validate answer content."""
        if not v.strip():
            raise ValueError('Answer cannot be empty')
        return v
    
    @validator('sources')
    def validate_sources(cls, v):
        """Ensure at least one source is provided."""
        # Note: We allow empty sources for fallback responses
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the expense ratio of HDFC Equity Fund?",
                "answer": "The expense ratio of HDFC Equity Fund (Direct Growth) is 1.05% per annum. This is the annual fee charged by the fund for managing your investment.",
                "sources": [
                    {
                        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
                        "title": "HDFC Equity Fund - Direct Growth",
                        "source_type": "groww_page",
                        "amc_name": "HDFC Mutual Fund",
                        "relevance_score": 0.95
                    }
                ],
                "confidence_score": 0.92,
                "has_sufficient_info": True,
                "retrieved_chunks_count": 5,
                "response_time_ms": 342.5,
                "timestamp": "2024-11-14T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """
    Model for error response.
    
    Represents an error that occurred during processing.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "query_processing_error",
                "message": "Unable to process the query. Please try rephrasing.",
                "detail": "LLM service timeout after 30 seconds",
                "timestamp": "2024-11-14T10:30:00Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """Model for health check response."""
    status: str = Field(..., description="Health status")
    timestamp: float = Field(..., description="Response timestamp")
    environment: str = Field(..., description="Environment name")
    version: str = Field(..., description="API version")


class ReadinessCheckResponse(BaseModel):
    """Model for readiness check response."""
    status: str = Field(..., description="Readiness status")
    timestamp: float = Field(..., description="Response timestamp")
    checks: Dict[str, str] = Field(..., description="Individual component checks")

