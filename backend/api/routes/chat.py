"""
Chat API Routes

Handles chat query endpoints for the FAQ assistant.
"""

from fastapi import APIRouter, HTTPException, status, Request
from typing import List, Optional
import logging
import time

from backend.models.chat import (
    ChatRequest,
    ChatResponse,
    SourceCitation,
    SourceType,
    ErrorResponse,
)
from backend.services.response_generator import get_response_generator
from backend.utils.citation import get_citation_formatter
from backend.exceptions import (
    QueryValidationError,
    MalformedQueryError,
    LLMServiceError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMAPIKeyError,
    VectorStoreError,
    VectorStoreNotInitializedError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["chat"])


def _classify_source_type(url: str) -> SourceType:
    """Classify source type based on URL."""
    url_lower = url.lower()
    
    if "groww.in" in url_lower:
        return SourceType.GROWW_PAGE
    elif "sebi.gov.in" in url_lower:
        return SourceType.SEBI_WEBSITE
    elif "amfiindia.com" in url_lower:
        return SourceType.AMFI_WEBSITE
    else:
        # Assume it's an AMC website if not one of the above
        return SourceType.AMC_WEBSITE


def _map_sources_to_citations(
    sources: List[dict],
    similarity_scores: Optional[List[float]] = None,
) -> List[SourceCitation]:
    """Map source dictionaries to SourceCitation objects."""
    citations = []
    
    for i, source in enumerate(sources):
        url = source.get("url", "")
        score = similarity_scores[i] if similarity_scores and i < len(similarity_scores) else None
        
        citation = SourceCitation(
            url=url,
            title=source.get("title"),
            source_type=_classify_source_type(url),
            amc_name=source.get("amc_name"),
            relevance_score=score,
        )
        citations.append(citation)
    
    return citations


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
) -> ChatResponse:
    """
    Chat endpoint for user queries.
    
    Processes user questions about mutual funds and returns factual responses
    with source citations.
    
    **Important:**
    - Only provides factual information, no investment advice
    - All responses are backed by verified sources
    - Sources are prioritized: Groww pages → External AMC/SEBI/AMFI → Generic fallback
    
    Args:
        request: ChatRequest with user query and optional session ID
        
    Returns:
        ChatResponse with answer and sources
        
    Raises:
        HTTPException: If query processing fails
    """
    start_time = time.time()
    
    # Get request ID from middleware if available
    request_id = getattr(http_request.state, "request_id", "unknown")
    
    try:
        logger.info(
            f"[{request_id}] Chat request: query='{request.query[:100]}...' "
            f"session_id={request.session_id}"
        )
        
        # Get response generator service
        response_gen = get_response_generator()
        
        # Extract filters from context if provided
        filters = None
        if request.context and "amc_filter" in request.context:
            filters = {"amc_name": request.context["amc_filter"]}
        
        # Generate response using RAG pipeline
        result = response_gen.generate_response(
            query=request.query,
            filters=filters,
            session_id=request.session_id,
        )
        
        # Check if query was blocked by guardrails
        if result.get("guardrail_blocked", False):
            logger.warning(f"Query blocked by guardrails: {request.query}")
            return ChatResponse(
                query=request.query,
                answer=result["response"],
                sources=[],
                confidence_score=0.0,
                has_sufficient_info=False,
                fallback_message="This query appears to be asking for investment advice, which I cannot provide.",
                retrieved_chunks_count=0,
                response_time_ms=result.get("generation_time_ms", 0.0),
            )
        
        # Check if this is a generic fallback (no sources found)
        is_fallback = result.get("is_fallback", False)
        
        # Map sources to citation objects
        citations = _map_sources_to_citations(
            sources=result.get("sources", []),
        )
        
        # Determine confidence based on fallback level and chunks retrieved
        fallback_level = result.get("fallback_level", "generic")
        chunks_count = result.get("chunks_retrieved", 0)
        
        if fallback_level == "groww":
            confidence = 0.95
        elif fallback_level == "external":
            confidence = 0.85
        elif fallback_level == "groww_sources_only":
            confidence = 0.90
        else:
            confidence = 0.3
        
        # Adjust confidence based on chunks retrieved
        if chunks_count == 0:
            confidence = 0.0
        elif chunks_count < 2:
            confidence *= 0.8
        
        # Calculate total response time
        total_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"[{request_id}] Chat response generated: chunks={chunks_count}, "
            f"sources={len(citations)}, time={total_time_ms:.2f}ms, "
            f"fallback_level={fallback_level}"
        )
        
        # Build response
        return ChatResponse(
            query=request.query,
            answer=result["response"],
            sources=citations,
            confidence_score=confidence,
            has_sufficient_info=not is_fallback,
            fallback_message=None if not is_fallback else "Limited information available",
            retrieved_chunks_count=chunks_count,
            response_time_ms=total_time_ms,
        )
        
    except (ValueError, QueryValidationError, MalformedQueryError) as e:
        # Validation errors
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query: {str(e)}",
        )
    
    except VectorStoreNotInitializedError as e:
        # Vector store not set up
        logger.error(f"Vector store not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge base is not initialized. Please contact support.",
        )
    
    except LLMAPIKeyError as e:
        # LLM API key issues
        logger.error(f"LLM API key error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not properly configured. Please contact support.",
        )
    
    except LLMTimeoutError as e:
        # LLM timeout
        logger.warning(f"LLM timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timed out while generating response. Please try again.",
        )
    
    except LLMRateLimitError as e:
        # Rate limit exceeded
        logger.warning(f"LLM rate limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Service is currently busy. Please try again in a few moments.",
        )
    
    except (LLMServiceError, VectorStoreError) as e:
        # General service errors
        logger.error(f"Service error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        )
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.get(
    "/chat/history",
    response_model=List[ChatResponse],
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_chat_history(
    session_id: Optional[str] = None,
):
    """
    Get chat history for a session (optional future feature).
    
    This endpoint is planned for future implementation to support
    conversation history and context across multiple queries.
    
    Args:
        session_id: Optional session ID to filter history
        
    Returns:
        List of previous chat interactions
    """
    # Future implementation: would retrieve from database/cache
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chat history feature is not yet implemented",
    )

