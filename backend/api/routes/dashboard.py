"""
Monitoring Dashboard API Routes

Endpoints for dashboard metrics and monitoring data.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from backend.services.monitoring import get_monitoring_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/metrics", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    time_window_minutes: int = Query(default=60, ge=1, le=1440, description="Time window in minutes")
):
    """
    Get comprehensive dashboard metrics.
    
    Args:
        time_window_minutes: Time window for metrics (default: 60 minutes)
        
    Returns:
        Dashboard metrics including response time, error rate, usage, and health
    """
    try:
        monitoring = get_monitoring_service()
        
        # Get all metrics
        error_stats = monitoring.get_error_stats(time_window_minutes=time_window_minutes)
        performance_stats = monitoring.get_performance_stats(
            "response_time",
            time_window_minutes=time_window_minutes,
        )
        request_stats = monitoring.get_request_stats(time_window_minutes=time_window_minutes)
        health_status = monitoring.get_health_status()
        dashboard_metrics = monitoring.get_dashboard_metrics(time_window_minutes=time_window_minutes)
        
        # Calculate error rate
        total_requests = request_stats.get("total_requests", 0)
        total_errors = error_stats.get("total_errors", 0)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
        
        # Calculate average response time
        response_time_data = performance_stats.get("response_time_ms", {})
        avg_response_time = response_time_data.get("mean", 0.0) if isinstance(response_time_data, dict) else 0.0
        
        # Get response time percentiles
        p50 = response_time_data.get("p50", 0.0) if isinstance(response_time_data, dict) else 0.0
        p95 = response_time_data.get("p95", 0.0) if isinstance(response_time_data, dict) else 0.0
        p99 = response_time_data.get("p99", 0.0) if isinstance(response_time_data, dict) else 0.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "overview": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "status": health_status.get("status", "unknown"),
            },
            "response_time": {
                "mean_ms": round(avg_response_time, 2),
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "min_ms": response_time_data.get("min", 0.0) if isinstance(response_time_data, dict) else 0.0,
                "max_ms": response_time_data.get("max", 0.0) if isinstance(response_time_data, dict) else 0.0,
            },
            "errors": {
                "total": total_errors,
                "rate_percent": round(error_rate, 2),
                "by_type": error_stats.get("errors_by_type", {}),
                "by_endpoint": error_stats.get("errors_by_endpoint", {}),
            },
            "requests": {
                "total": total_requests,
                "by_endpoint": request_stats.get("requests_by_endpoint", {}),
                "by_status_code": request_stats.get("requests_by_status_code", {}),
            },
            "health": health_status,
            "metrics": dashboard_metrics,
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard metrics",
        )


@router.get("/dashboard/response-time", response_model=Dict[str, Any])
async def get_response_time_metrics(
    time_window_minutes: int = Query(default=60, ge=1, le=1440),
    endpoint: Optional[str] = Query(default=None, description="Filter by endpoint"),
):
    """
    Get response time metrics.
    
    Args:
        time_window_minutes: Time window for metrics
        endpoint: Optional endpoint filter
        
    Returns:
        Response time metrics
    """
    try:
        monitoring = get_monitoring_service()
        
        if endpoint:
            # Get endpoint-specific metrics
            performance_stats = monitoring.get_performance_stats(
                f"response_time_{endpoint}",
                time_window_minutes=time_window_minutes,
            )
        else:
            performance_stats = monitoring.get_performance_stats(
                "response_time",
                time_window_minutes=time_window_minutes,
            )
        
        response_time_data = performance_stats.get("response_time_ms", {})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "endpoint": endpoint,
            "metrics": {
                "mean_ms": round(response_time_data.get("mean", 0.0), 2) if isinstance(response_time_data, dict) else 0.0,
                "p50_ms": round(response_time_data.get("p50", 0.0), 2) if isinstance(response_time_data, dict) else 0.0,
                "p95_ms": round(response_time_data.get("p95", 0.0), 2) if isinstance(response_time_data, dict) else 0.0,
                "p99_ms": round(response_time_data.get("p99", 0.0), 2) if isinstance(response_time_data, dict) else 0.0,
                "min_ms": response_time_data.get("min", 0.0) if isinstance(response_time_data, dict) else 0.0,
                "max_ms": response_time_data.get("max", 0.0) if isinstance(response_time_data, dict) else 0.0,
            },
        }
    except Exception as e:
        logger.error(f"Error getting response time metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve response time metrics",
        )


@router.get("/dashboard/error-rate", response_model=Dict[str, Any])
async def get_error_rate_metrics(
    time_window_minutes: int = Query(default=60, ge=1, le=1440),
):
    """
    Get error rate metrics.
    
    Args:
        time_window_minutes: Time window for metrics
        
    Returns:
        Error rate metrics
    """
    try:
        monitoring = get_monitoring_service()
        
        error_stats = monitoring.get_error_stats(time_window_minutes=time_window_minutes)
        request_stats = monitoring.get_request_stats(time_window_minutes=time_window_minutes)
        
        total_requests = request_stats.get("total_requests", 0)
        total_errors = error_stats.get("total_errors", 0)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "metrics": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_percent": round(error_rate, 2),
                "errors_per_second": round(total_errors / (time_window_minutes * 60), 2) if time_window_minutes > 0 else 0.0,
            },
            "errors_by_type": error_stats.get("errors_by_type", {}),
            "errors_by_endpoint": error_stats.get("errors_by_endpoint", {}),
        }
    except Exception as e:
        logger.error(f"Error getting error rate metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve error rate metrics",
        )


@router.get("/dashboard/usage", response_model=Dict[str, Any])
async def get_usage_metrics(
    time_window_minutes: int = Query(default=60, ge=1, le=1440),
):
    """
    Get usage metrics (requests per endpoint, status codes, etc.).
    
    Args:
        time_window_minutes: Time window for metrics
        
    Returns:
        Usage metrics
    """
    try:
        monitoring = get_monitoring_service()
        
        request_stats = monitoring.get_request_stats(time_window_minutes=time_window_minutes)
        
        total_requests = request_stats.get("total_requests", 0)
        requests_per_minute = total_requests / time_window_minutes if time_window_minutes > 0 else 0.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "metrics": {
                "total_requests": total_requests,
                "requests_per_minute": round(requests_per_minute, 2),
                "requests_per_second": round(requests_per_minute / 60, 2),
            },
            "requests_by_endpoint": request_stats.get("requests_by_endpoint", {}),
            "requests_by_status_code": request_stats.get("requests_by_status_code", {}),
        }
    except Exception as e:
        logger.error(f"Error getting usage metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage metrics",
        )


@router.get("/dashboard/health", response_model=Dict[str, Any])
async def get_health_metrics():
    """
    Get health status metrics.
    
    Returns:
        Health status metrics
    """
    try:
        monitoring = get_monitoring_service()
        
        health_status = monitoring.get_health_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health": health_status,
        }
    except Exception as e:
        logger.error(f"Error getting health metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health metrics",
        )


@router.get("/dashboard/time-series", response_model=Dict[str, Any])
async def get_time_series_metrics(
    metric: str = Query(description="Metric name (response_time, error_rate, requests)"),
    time_window_minutes: int = Query(default=60, ge=1, le=1440),
    interval_minutes: int = Query(default=5, ge=1, le=60, description="Interval for data points"),
):
    """
    Get time series data for a metric.
    
    Args:
        metric: Metric name
        time_window_minutes: Time window for metrics
        interval_minutes: Interval between data points
        
    Returns:
        Time series data
    """
    try:
        monitoring = get_monitoring_service()
        
        # Calculate number of intervals
        num_intervals = time_window_minutes // interval_minutes
        
        # Get metrics for each interval
        time_series_data = []
        
        for i in range(num_intervals):
            interval_start = time_window_minutes - (i + 1) * interval_minutes
            interval_end = time_window_minutes - i * interval_minutes
            
            if metric == "response_time":
                stats = monitoring.get_performance_stats(
                    "response_time",
                    time_window_minutes=interval_end,
                )
                value = stats.get("response_time_ms", {}).get("mean", 0.0) if isinstance(stats.get("response_time_ms"), dict) else 0.0
            elif metric == "error_rate":
                error_stats = monitoring.get_error_stats(time_window_minutes=interval_end)
                request_stats = monitoring.get_request_stats(time_window_minutes=interval_end)
                total_requests = request_stats.get("total_requests", 0)
                total_errors = error_stats.get("total_errors", 0)
                value = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
            elif metric == "requests":
                request_stats = monitoring.get_request_stats(time_window_minutes=interval_end)
                value = request_stats.get("total_requests", 0)
            else:
                value = 0.0
            
            time_series_data.append({
                "timestamp": (datetime.now() - timedelta(minutes=interval_end)).isoformat(),
                "value": round(value, 2),
            })
        
        # Reverse to get chronological order
        time_series_data.reverse()
        
        return {
            "metric": metric,
            "time_window_minutes": time_window_minutes,
            "interval_minutes": interval_minutes,
            "data_points": time_series_data,
        }
    except Exception as e:
        logger.error(f"Error getting time series metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve time series metrics",
        )


@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_dashboard_summary():
    """
    Get a quick summary of key metrics for dashboard display.
    
    Returns:
        Summary metrics
    """
    try:
        monitoring = get_monitoring_service()
        
        # Get metrics for last hour
        error_stats = monitoring.get_error_stats(time_window_minutes=60)
        performance_stats = monitoring.get_performance_stats("response_time", time_window_minutes=60)
        request_stats = monitoring.get_request_stats(time_window_minutes=60)
        health_status = monitoring.get_health_status()
        
        total_requests = request_stats.get("total_requests", 0)
        total_errors = error_stats.get("total_errors", 0)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
        
        response_time_data = performance_stats.get("response_time_ms", {})
        avg_response_time = response_time_data.get("mean", 0.0) if isinstance(response_time_data, dict) else 0.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "status": health_status.get("status", "unknown"),
                "total_requests": total_requests,
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "uptime_percent": health_status.get("uptime_percent", 0.0),
            },
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary",
        )

