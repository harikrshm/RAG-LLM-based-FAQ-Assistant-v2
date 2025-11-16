"""
Diagnostic API Routes

Endpoints for debugging and diagnostics.
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import traceback

from backend.services.llm_service import get_llm_service
from backend.services.vector_store import get_vector_store
from backend.services.response_generator import get_response_generator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["diagnostic"])


class TestLLMRequest(BaseModel):
    prompt: str = "What is a mutual fund?"


class TestResponseGeneratorRequest(BaseModel):
    query: str = "What is a mutual fund?"


@router.post("/test-llm")
async def test_llm_endpoint(request: TestLLMRequest) -> Dict[str, Any]:
    """
    Test LLM service directly with a prompt.
    
    Args:
        request: Test request with prompt
        
    Returns:
        Diagnostic information about LLM call
    """
    try:
        logger.info(f"Diagnostic: Testing LLM with prompt: {request.prompt[:100]}")
        
        llm_service = get_llm_service()
        
        result = llm_service.generate(
            prompt=request.prompt,
            temperature=0.1,
            max_tokens=100,
        )
        
        return {
            "status": "success",
            "prompt": request.prompt,
            "result": {
                "text": result.text[:500] if result.text else None,
                "text_length": len(result.text) if result.text else 0,
                "finish_reason": result.finish_reason,
                "finish_reason_type": type(result.finish_reason).__name__,
                "provider": result.provider,
                "model": result.model,
                "total_tokens": result.total_tokens,
            },
        }
    except Exception as e:
        logger.error(f"Diagnostic LLM test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


@router.post("/test-response-generator")
async def test_response_generator_endpoint(request: TestResponseGeneratorRequest) -> Dict[str, Any]:
    """
    Test response generator service directly.
    
    Args:
        request: Test request with query
        
    Returns:
        Diagnostic information about response generation
    """
    try:
        logger.info(f"Diagnostic: Testing response generator with query: {request.query[:100]}")
        
        response_gen = get_response_generator()
        
        result = response_gen.generate_response(
            query=request.query,
            session_id="diagnostic-test",
        )
        
        return {
            "status": "success",
            "query": request.query,
            "result": {
                "response": result.get("response", "")[:500],
                "response_length": len(result.get("response", "")),
                "sources_count": len(result.get("sources", [])),
                "chunks_retrieved": result.get("chunks_retrieved", 0),
                "is_fallback": result.get("is_fallback", False),
                "fallback_level": result.get("fallback_level", None),
                "guardrail_blocked": result.get("guardrail_blocked", False),
                "generation_time_ms": result.get("generation_time_ms", 0),
            },
        }
    except Exception as e:
        logger.error(f"Diagnostic response generator test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


@router.get("/test-vector-store")
async def test_vector_store_endpoint() -> Dict[str, Any]:
    """
    Test vector store service.
    
    Returns:
        Diagnostic information about vector store
    """
    try:
        logger.info("Diagnostic: Testing vector store")
        
        vector_store = get_vector_store()
        
        # Try a simple query
        results = vector_store.search(
            query="mutual fund",
            top_k=3,
        )
        
        return {
            "status": "success",
            "vector_store": {
                "collection_exists": True,
                "results_count": len(results) if results else 0,
                "sample_result": results[0] if results else None,
            },
        }
    except Exception as e:
        logger.error(f"Diagnostic vector store test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }
