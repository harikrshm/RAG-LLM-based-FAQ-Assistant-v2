"""
Application Monitoring Service

Tracks errors, performance metrics, and application health.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class ErrorMetric:
    """Represents an error metric."""
    error_type: str
    error_message: str
    timestamp: datetime
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    stack_trace: Optional[str] = None


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    metric_name: str
    value: float
    timestamp: datetime
    endpoint: Optional[str] = None
    method: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetric:
    """Represents a request metric."""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class MonitoringService:
    """
    Service for tracking errors, performance metrics, and application health.
    """
    
    def __init__(self, max_errors: int = 1000, max_metrics: int = 10000):
        """
        Initialize monitoring service.
        
        Args:
            max_errors: Maximum number of errors to keep in memory
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_errors = max_errors
        self.max_metrics = max_metrics
        
        # Error tracking
        self.errors: deque = deque(maxlen=max_errors)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.error_lock = Lock()
        
        # Performance metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.metric_aggregates: Dict[str, List[float]] = defaultdict(list)
        self.metrics_lock = Lock()
        
        # Request tracking
        self.requests: deque = deque(maxlen=max_metrics)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.request_lock = Lock()
        
        # Health tracking
        self.health_status: Dict[str, Any] = {
            "status": "healthy",
            "last_check": datetime.now(),
            "uptime_start": datetime.now(),
        }
        
        logger.info("MonitoringService initialized")
    
    def track_error(
        self,
        error_type: str,
        error_message: str,
        endpoint: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ):
        """
        Track an error.
        
        Args:
            error_type: Type of error (e.g., "ValueError", "HTTPException")
            error_message: Error message
            endpoint: API endpoint where error occurred
            user_id: User ID (if available)
            session_id: Session ID (if available)
            stack_trace: Stack trace (if available)
        """
        error = ErrorMetric(
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now(),
            endpoint=endpoint,
            user_id=user_id,
            session_id=session_id,
            stack_trace=stack_trace,
        )
        
        with self.error_lock:
            self.errors.append(error)
            self.error_counts[error_type] += 1
        
        logger.error(
            f"Error tracked: {error_type} - {error_message}",
            extra={
                "endpoint": endpoint,
                "user_id": user_id,
                "session_id": session_id,
            }
        )
    
    def track_performance_metric(
        self,
        metric_name: str,
        value: float,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Track a performance metric.
        
        Args:
            metric_name: Name of the metric (e.g., "response_time", "query_time")
            value: Metric value
            endpoint: API endpoint (if applicable)
            method: HTTP method (if applicable)
            tags: Additional tags for filtering
        """
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            endpoint=endpoint,
            method=method,
            tags=tags or {},
        )
        
        with self.metrics_lock:
            self.metrics.append(metric)
            self.metric_aggregates[metric_name].append(value)
            
            # Keep only recent values (last 1000)
            if len(self.metric_aggregates[metric_name]) > 1000:
                self.metric_aggregates[metric_name] = \
                    self.metric_aggregates[metric_name][-1000:]
        
        logger.debug(
            f"Performance metric tracked: {metric_name}={value}",
            extra={
                "endpoint": endpoint,
                "method": method,
                "tags": tags,
            }
        )
    
    def track_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Track an API request.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            user_id: User ID (if available)
            session_id: Session ID (if available)
        """
        request = RequestMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
        )
        
        with self.request_lock:
            self.requests.append(request)
            self.request_counts[f"{method} {endpoint}"] += 1
        
        # Track as performance metric
        self.track_performance_metric(
            metric_name="response_time",
            value=response_time_ms,
            endpoint=endpoint,
            method=method,
            tags={"status_code": str(status_code)},
        )
    
    def get_error_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get error statistics for a time window.
        
        Args:
            time_window_minutes: Time window in minutes
            
        Returns:
            Dictionary with error statistics
        """
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        with self.error_lock:
            recent_errors = [
                e for e in self.errors
                if e.timestamp >= cutoff_time
            ]
            
            error_counts_by_type = defaultdict(int)
            for error in recent_errors:
                error_counts_by_type[error.error_type] += 1
            
            error_counts_by_endpoint = defaultdict(int)
            for error in recent_errors:
                if error.endpoint:
                    error_counts_by_endpoint[error.endpoint] += 1
        
        return {
            "total_errors": len(recent_errors),
            "errors_by_type": dict(error_counts_by_type),
            "errors_by_endpoint": dict(error_counts_by_endpoint),
            "time_window_minutes": time_window_minutes,
        }
    
    def get_performance_stats(
        self,
        metric_name: str,
        time_window_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        Get performance statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            time_window_minutes: Time window in minutes
            
        Returns:
            Dictionary with performance statistics
        """
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        with self.metrics_lock:
            recent_metrics = [
                m for m in self.metrics
                if m.metric_name == metric_name and m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {
                    "metric_name": metric_name,
                    "count": 0,
                    "time_window_minutes": time_window_minutes,
                }
            
            values = [m.value for m in recent_metrics]
            values.sort()
            
            return {
                "metric_name": metric_name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": values[len(values) // 2],
                "p95": values[int(len(values) * 0.95)] if len(values) > 0 else 0,
                "p99": values[int(len(values) * 0.99)] if len(values) > 0 else 0,
                "time_window_minutes": time_window_minutes,
            }
    
    def get_request_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get request statistics for a time window.
        
        Args:
            time_window_minutes: Time window in minutes
            
        Returns:
            Dictionary with request statistics
        """
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        with self.request_lock:
            recent_requests = [
                r for r in self.requests
                if r.timestamp >= cutoff_time
            ]
            
            if not recent_requests:
                return {
                    "total_requests": 0,
                    "time_window_minutes": time_window_minutes,
                }
            
            response_times = [r.response_time_ms for r in recent_requests]
            status_counts = defaultdict(int)
            endpoint_counts = defaultdict(int)
            
            for request in recent_requests:
                status_counts[request.status_code] += 1
                endpoint_counts[f"{request.method} {request.endpoint}"] += 1
            
            response_times.sort()
            
            return {
                "total_requests": len(recent_requests),
                "requests_per_second": len(recent_requests) / (time_window_minutes * 60),
                "response_time_ms": {
                    "min": min(response_times),
                    "max": max(response_times),
                    "mean": sum(response_times) / len(response_times),
                    "median": response_times[len(response_times) // 2],
                    "p95": response_times[int(len(response_times) * 0.95)],
                    "p99": response_times[int(len(response_times) * 0.99)],
                },
                "status_codes": dict(status_counts),
                "endpoint_counts": dict(endpoint_counts),
                "time_window_minutes": time_window_minutes,
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status.
        
        Returns:
            Dictionary with health status
        """
        uptime = datetime.now() - self.health_status["uptime_start"]
        
        # Get recent error rate
        error_stats = self.get_error_stats(time_window_minutes=5)
        error_rate = error_stats["total_errors"] / 300  # errors per second
        
        # Get recent request stats
        request_stats = self.get_request_stats(time_window_minutes=5)
        
        # Determine health status
        if error_rate > 0.1:  # More than 0.1 errors per second
            health_status = "unhealthy"
        elif request_stats.get("total_requests", 0) == 0:
            health_status = "degraded"
        else:
            health_status = "healthy"
        
        self.health_status["status"] = health_status
        self.health_status["last_check"] = datetime.now()
        
        return {
            **self.health_status,
            "uptime_seconds": uptime.total_seconds(),
            "error_rate_per_second": error_rate,
            "recent_errors": error_stats["total_errors"],
            "recent_requests": request_stats.get("total_requests", 0),
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for monitoring dashboard.
        
        Returns:
            Dictionary with dashboard metrics
        """
        return {
            "health": self.get_health_status(),
            "errors": self.get_error_stats(time_window_minutes=60),
            "performance": {
                "response_time": self.get_performance_stats(
                    "response_time",
                    time_window_minutes=60,
                ),
                "query_time": self.get_performance_stats(
                    "query_time",
                    time_window_minutes=60,
                ),
            },
            "requests": self.get_request_stats(time_window_minutes=60),
        }


# Singleton instance
_monitoring_instance: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """
    Get or create the singleton MonitoringService instance.
    
    Returns:
        MonitoringService instance
    """
    global _monitoring_instance
    
    if _monitoring_instance is None:
        _monitoring_instance = MonitoringService()
    
    return _monitoring_instance

