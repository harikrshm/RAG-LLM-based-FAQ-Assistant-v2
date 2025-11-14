"""
Rate Limiting Middleware

Implements token bucket algorithm for rate limiting requests.
"""

import logging
import time
from typing import Dict, Tuple, Optional
from collections import defaultdict
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class TokenBucket:
    """
    Token bucket implementation for rate limiting.
    
    Uses token bucket algorithm to allow burst traffic while
    enforcing average rate limits.
    """
    
    def __init__(self, rate: int, period: int):
        """
        Initialize token bucket.
        
        Args:
            rate: Number of requests allowed per period
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if rate limit exceeded
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add based on elapsed time
        tokens_to_add = (elapsed / self.period) * self.rate
        
        if tokens_to_add > 0:
            self.tokens = min(self.rate, self.tokens + tokens_to_add)
            self.last_refill = now
    
    def get_reset_time(self) -> float:
        """Get time until bucket is fully refilled."""
        tokens_needed = self.rate - self.tokens
        if tokens_needed <= 0:
            return 0.0
        
        time_needed = (tokens_needed / self.rate) * self.period
        return time_needed


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.
    
    Tracks requests per IP address and enforces rate limits.
    """
    
    def __init__(self, app, rate_per_minute: int = 60, rate_per_hour: int = 1000):
        """
        Initialize rate limiter middleware.
        
        Args:
            app: FastAPI application
            rate_per_minute: Requests allowed per minute
            rate_per_hour: Requests allowed per hour
        """
        super().__init__(app)
        self.rate_per_minute = rate_per_minute
        self.rate_per_hour = rate_per_hour
        
        # Store token buckets per IP
        self.minute_buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(rate=self.rate_per_minute, period=60)
        )
        self.hour_buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(rate=self.rate_per_hour, period=3600)
        )
        
        # Track when we last cleaned up old buckets
        self.last_cleanup = time.time()
        
        logger.info(
            f"Rate limiter initialized: {rate_per_minute}/min, {rate_per_hour}/hour"
        )
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        # Skip rate limiting for health/readiness checks
        if request.url.path in ["/health", "/ready", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if rate limiting is enabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Check rate limits
        minute_allowed = self.minute_buckets[client_ip].consume()
        hour_allowed = self.hour_buckets[client_ip].consume()
        
        if not minute_allowed or not hour_allowed:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}"
            )
            
            # Get reset time
            if not minute_allowed:
                reset_time = self.minute_buckets[client_ip].get_reset_time()
                limit_type = "per-minute"
            else:
                reset_time = self.hour_buckets[client_ip].get_reset_time()
                limit_type = "per-hour"
            
            # Return 429 Too Many Requests
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Please try again in {int(reset_time)} seconds.",
                    "limit_type": limit_type,
                    "retry_after": int(reset_time),
                },
                headers={
                    "Retry-After": str(int(reset_time)),
                    "X-RateLimit-Limit-Minute": str(self.rate_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.rate_per_hour),
                    "X-RateLimit-Remaining-Minute": "0",
                    "X-RateLimit-Remaining-Hour": "0",
                },
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        minute_bucket = self.minute_buckets[client_ip]
        hour_bucket = self.hour_buckets[client_ip]
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.rate_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.rate_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(int(minute_bucket.tokens))
        response.headers["X-RateLimit-Remaining-Hour"] = str(int(hour_bucket.tokens))
        
        # Periodic cleanup of old buckets (every 5 minutes)
        if time.time() - self.last_cleanup > 300:
            self._cleanup_old_buckets()
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.
        
        Checks X-Forwarded-For header first (for proxies),
        then falls back to direct client IP.
        
        Args:
            request: FastAPI request
            
        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (for load balancers/proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP in the chain
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_buckets(self):
        """
        Clean up token buckets for IPs that haven't been seen recently.
        
        Prevents memory growth from storing buckets for one-time visitors.
        """
        logger.debug("Cleaning up old rate limit buckets")
        
        current_time = time.time()
        cutoff_time = current_time - 7200  # 2 hours
        
        # Clean minute buckets
        old_keys = [
            ip for ip, bucket in self.minute_buckets.items()
            if bucket.last_refill < cutoff_time
        ]
        for key in old_keys:
            del self.minute_buckets[key]
        
        # Clean hour buckets
        old_keys = [
            ip for ip, bucket in self.hour_buckets.items()
            if bucket.last_refill < cutoff_time
        ]
        for key in old_keys:
            del self.hour_buckets[key]
        
        self.last_cleanup = current_time
        
        if old_keys:
            logger.debug(f"Cleaned up {len(old_keys)} old rate limit buckets")

