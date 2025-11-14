"""
Health Check Routes

Additional health check endpoints for detailed monitoring.
"""

from fastapi import APIRouter
import time
import logging

from backend.services.vector_store import get_vector_store
from backend.services.llm_service import get_llm_service
from backend.services.response_generator import get_response_generator
from backend.services.rag_retrieval import get_rag_retrieval
from backend.middleware.logging_middleware import get_metrics
from backend.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health/vector-store")
async def check_vector_store_health():
    """
    Dedicated vector store health check.
    
    Returns:
        Vector store health details
    """
    try:
        vector_store = get_vector_store()
        health = vector_store.health_check()
        stats = vector_store.get_collection_stats()
        
        return {
            "status": health.get("status", "unknown"),
            "timestamp": time.time(),
            "details": health,
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e),
        }


@router.get("/health/llm")
async def check_llm_health():
    """
    Dedicated LLM service health check.
    
    Returns:
        LLM service health details
    """
    try:
        llm_service = get_llm_service()
        health = llm_service.health_check()
        
        return {
            "status": health.get("status", "unknown"),
            "timestamp": time.time(),
            "provider": health.get("provider"),
            "model": health.get("model"),
            "details": health,
        }
    except Exception as e:
        logger.error(f"LLM service health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e),
        }


@router.get("/health/rag-pipeline")
async def check_rag_pipeline_health():
    """
    Check RAG retrieval pipeline health.
    
    Returns:
        RAG pipeline health details
    """
    try:
        rag_retrieval = get_rag_retrieval()
        health = rag_retrieval.health_check()
        
        return {
            "status": health.get("status", "unknown"),
            "timestamp": time.time(),
            "details": health,
        }
    except Exception as e:
        logger.error(f"RAG pipeline health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e),
        }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Comprehensive health check with all components.
    
    Returns:
        Detailed health status for all services
    """
    components = {}
    
    # Vector Store
    try:
        vector_store = get_vector_store()
        components["vector_store"] = vector_store.health_check()
    except Exception as e:
        components["vector_store"] = {"status": "unhealthy", "error": str(e)}
    
    # LLM Service
    try:
        llm_service = get_llm_service()
        components["llm_service"] = llm_service.health_check()
    except Exception as e:
        components["llm_service"] = {"status": "unhealthy", "error": str(e)}
    
    # RAG Retrieval
    try:
        rag_retrieval = get_rag_retrieval()
        components["rag_retrieval"] = rag_retrieval.health_check()
    except Exception as e:
        components["rag_retrieval"] = {"status": "unhealthy", "error": str(e)}
    
    # Response Generator
    try:
        response_gen = get_response_generator()
        components["response_generator"] = response_gen.health_check()
    except Exception as e:
        components["response_generator"] = {"status": "unhealthy", "error": str(e)}
    
    # Request Metrics
    try:
        metrics = get_metrics()
        components["metrics"] = {
            "status": "healthy",
            "data": metrics.get_metrics(),
        }
    except Exception as e:
        components["metrics"] = {"status": "unhealthy", "error": str(e)}
    
    # Determine overall health
    all_healthy = all(
        comp.get("status") == "healthy"
        for comp in components.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "components": components,
        "all_systems_operational": all_healthy,
    }

