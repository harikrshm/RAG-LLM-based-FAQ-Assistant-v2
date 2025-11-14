"""
Monitoring Middleware

Middleware to track requests, errors, and performance metrics.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.services.monitoring import get_monitoring_service

logger = logging.getLogger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests, errors, and performance metrics.
    """
    
    def __init__(self, app):
        """Initialize monitoring middleware."""
        super().__init__(app)
        self.monitoring = get_monitoring_service()
        logger.info("MonitoringMiddleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track metrics.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            FastAPI response
        """
        start_time = time.time()
        
        # Extract user/session info if available
        user_id = request.headers.get("X-User-ID")
        session_id = request.headers.get("X-Session-ID")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Track request
            self.monitoring.track_request(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                user_id=user_id,
                session_id=session_id,
            )
            
            # Add monitoring headers
            response.headers["X-Response-Time-Ms"] = str(response_time_ms)
            
            return response
            
        except Exception as e:
            # Calculate response time even for errors
            response_time_ms = (time.time() - start_time) * 1000
            
            # Track error
            self.monitoring.track_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint=str(request.url.path),
                user_id=user_id,
                session_id=session_id,
            )
            
            # Re-raise exception
            raise

