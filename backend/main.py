"""
FastAPI Application Entry Point

Main application file for the Mutual Funds FAQ Assistant backend.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from backend.config.settings import settings
from backend.api.routes import chat
from backend.middleware.rate_limiter import RateLimiterMiddleware
from backend.middleware.logging_middleware import (
    RequestLoggingMiddleware,
    get_metrics,
)
from backend.services.vector_store import get_vector_store
from backend.services.llm_service import get_llm_service
from backend.services.response_generator import get_response_generator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting up Mutual Funds FAQ Assistant API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize resources
    # TODO: Initialize vector database connection
    # TODO: Load LLM model
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mutual Funds FAQ Assistant API...")
    # TODO: Close database connections
    # TODO: Cleanup resources


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-based FAQ Assistant for Mutual Fund Schemes",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# Add middleware for request logging and tracking
app.add_middleware(RequestLoggingMiddleware)


# Middleware for metrics collection
@app.middleware("http")
async def collect_metrics(request: Request, call_next):
    """
    Collect request metrics for monitoring.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler
        
    Returns:
        Response object
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    metrics = get_metrics()
    metrics.record_request(
        endpoint=request.url.path,
        status_code=response.status_code,
        response_time=process_time,
    )
    
    return response


# CORS middleware - Configured for widget embedding
# Allows cross-origin requests from frontend domains
cors_origins = settings.get_cors_origins()
logger.info(f"CORS configured for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicit methods for widget API
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-Request-ID",
    ],
    expose_headers=[
        "X-Request-ID",
        "X-Response-Time",
    ],
    max_age=settings.CORS_MAX_AGE,  # Cache preflight requests
)

# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimiterMiddleware,
        rate_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        rate_per_hour=settings.RATE_LIMIT_PER_HOUR,
    )
    logger.info(
        f"Rate limiting enabled: {settings.RATE_LIMIT_PER_MINUTE}/min, "
        f"{settings.RATE_LIMIT_PER_HOUR}/hour"
    )
else:
    logger.warning("Rate limiting is DISABLED")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception that was raised
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Import and include health router
from backend.api.routes import health
app.include_router(health.router, prefix="/api", tags=["health"])


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        Dictionary with API info
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Simple health check endpoint.
    
    Returns 200 OK if service is running, regardless of dependency status.
    Use /ready for detailed dependency checks.
    
    Returns:
        Dictionary with basic health status
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "service": "mutual-funds-faq-assistant",
    }


# Readiness check endpoint with detailed component checks
@app.get("/ready", tags=["health"])
async def readiness_check():
    """
    Comprehensive readiness check for load balancers and orchestrators.
    
    Checks all critical dependencies:
    - Vector database connection and collection
    - Embedding model initialization
    - LLM service configuration
    - Response generator availability
    
    Returns:
        Dictionary with detailed readiness status
    """
    checks = {}
    all_healthy = True
    
    # Check Vector Store
    try:
        vector_store = get_vector_store()
        vector_health = vector_store.health_check()
        
        if vector_health.get("status") == "healthy":
            checks["vector_store"] = {
                "status": "healthy",
                "document_count": vector_health.get("document_count", 0),
                "collection": vector_health.get("collection_accessible", False),
            }
        else:
            checks["vector_store"] = {
                "status": "unhealthy",
                "error": vector_health.get("error", "Unknown error"),
            }
            all_healthy = False
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        checks["vector_store"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        all_healthy = False
    
    # Check LLM Service
    try:
        llm_service = get_llm_service()
        llm_health = llm_service.health_check()
        
        if llm_health.get("status") == "healthy":
            checks["llm_service"] = {
                "status": "healthy",
                "provider": llm_health.get("provider"),
                "model": llm_health.get("model"),
            }
        else:
            checks["llm_service"] = {
                "status": "unhealthy",
                "error": llm_health.get("error", "Unknown error"),
            }
            all_healthy = False
    except Exception as e:
        logger.error(f"LLM service health check failed: {e}")
        checks["llm_service"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        all_healthy = False
    
    # Check Response Generator (integrates all services)
    try:
        response_gen = get_response_generator()
        gen_health = response_gen.health_check()
        
        if gen_health.get("status") == "healthy":
            checks["response_generator"] = {
                "status": "healthy",
            }
        else:
            checks["response_generator"] = {
                "status": "unhealthy",
                "error": "One or more dependencies unhealthy",
            }
            all_healthy = False
    except Exception as e:
        logger.error(f"Response generator health check failed: {e}")
        checks["response_generator"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        all_healthy = False
    
    # Overall status
    status_code = 200 if all_healthy else 503
    
    response_data = {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "checks": checks,
        "all_systems_operational": all_healthy,
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_data,
    )


# Metrics endpoint
@app.get("/metrics", tags=["monitoring"])
async def get_request_metrics():
    """
    Get request metrics for monitoring.
    
    Returns:
        Dictionary with request metrics
    """
    metrics = get_metrics()
    return metrics.get_metrics()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

