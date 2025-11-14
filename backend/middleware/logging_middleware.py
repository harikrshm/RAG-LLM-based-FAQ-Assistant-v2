"""
Logging and Request Tracking Middleware

Enhanced logging with request IDs and detailed tracking.
"""

import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request logging and tracking.
    
    Adds request IDs, tracks timing, logs request/response details.
    """
    
    def __init__(self, app):
        """Initialize logging middleware."""
        super().__init__(app)
        logger.info("Request logging middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with detailed logging.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response with tracking headers
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request ID in request state for access in handlers
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Extract request details
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log incoming request
        logger.info(
            f"[{request_id}] Incoming request: "
            f"{request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        # Log request headers (excluding sensitive ones) in debug mode
        if logger.isEnabledFor(logging.DEBUG):
            safe_headers = self._get_safe_headers(request.headers)
            logger.debug(f"[{request_id}] Request headers: {safe_headers}")
        
        # Track request body size if present
        content_length = request.headers.get("content-length", "0")
        logger.debug(f"[{request_id}] Request body size: {content_length} bytes")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add tracking headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # Log response
            logger.info(
                f"[{request_id}] Response: "
                f"{response.status_code} "
                f"in {process_time:.4f}s"
            )
            
            # Log slow requests
            if process_time > 5.0:
                logger.warning(
                    f"[{request_id}] SLOW REQUEST: "
                    f"{request.method} {request.url.path} "
                    f"took {process_time:.2f}s"
                )
            
            # Track response size
            if hasattr(response, "body"):
                response_size = len(response.body) if response.body else 0
                logger.debug(f"[{request_id}] Response size: {response_size} bytes")
            
            return response
            
        except Exception as e:
            # Log exception with request ID
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Request failed: "
                f"{request.method} {request.url.path} "
                f"after {process_time:.4f}s - {str(e)}",
                exc_info=True
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check X-Forwarded-For header (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_safe_headers(self, headers: Headers) -> dict:
        """
        Get headers with sensitive values redacted.
        
        Args:
            headers: Request headers
            
        Returns:
            Dictionary of safe headers
        """
        sensitive_keys = {
            "authorization",
            "x-api-key",
            "cookie",
            "x-auth-token",
        }
        
        safe_headers = {}
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                safe_headers[key] = "[REDACTED]"
            else:
                safe_headers[key] = value
        
        return safe_headers


class RequestMetrics:
    """
    Simple in-memory metrics collector for monitoring.
    
    Tracks request counts, response times, and error rates.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.total_requests = 0
        self.total_errors = 0
        self.endpoint_counts = {}
        self.status_code_counts = {}
        self.total_response_time = 0.0
        self.slow_requests = 0
        
        logger.info("Request metrics collector initialized")
    
    def record_request(
        self,
        endpoint: str,
        status_code: int,
        response_time: float,
    ):
        """
        Record request metrics.
        
        Args:
            endpoint: Request endpoint path
            status_code: HTTP status code
            response_time: Response time in seconds
        """
        self.total_requests += 1
        
        # Track by endpoint
        if endpoint not in self.endpoint_counts:
            self.endpoint_counts[endpoint] = 0
        self.endpoint_counts[endpoint] += 1
        
        # Track by status code
        if status_code not in self.status_code_counts:
            self.status_code_counts[status_code] = 0
        self.status_code_counts[status_code] += 1
        
        # Track errors (4xx and 5xx)
        if status_code >= 400:
            self.total_errors += 1
        
        # Track response times
        self.total_response_time += response_time
        
        # Track slow requests (>5s)
        if response_time > 5.0:
            self.slow_requests += 1
    
    def get_metrics(self) -> dict:
        """
        Get current metrics summary.
        
        Returns:
            Dictionary with metrics
        """
        avg_response_time = (
            self.total_response_time / self.total_requests
            if self.total_requests > 0
            else 0.0
        )
        
        error_rate = (
            (self.total_errors / self.total_requests * 100)
            if self.total_requests > 0
            else 0.0
        )
        
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate_percent": round(error_rate, 2),
            "average_response_time_seconds": round(avg_response_time, 4),
            "slow_requests": self.slow_requests,
            "endpoint_counts": self.endpoint_counts,
            "status_code_counts": self.status_code_counts,
        }
    
    def reset(self):
        """Reset all metrics."""
        self.total_requests = 0
        self.total_errors = 0
        self.endpoint_counts = {}
        self.status_code_counts = {}
        self.total_response_time = 0.0
        self.slow_requests = 0
        logger.info("Request metrics reset")


# Global metrics instance
_metrics_instance = RequestMetrics()


def get_metrics() -> RequestMetrics:
    """Get the global metrics instance."""
    return _metrics_instance

