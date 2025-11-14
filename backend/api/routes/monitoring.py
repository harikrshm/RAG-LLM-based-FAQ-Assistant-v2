"""
Monitoring API Routes

Endpoints for accessing monitoring metrics and health status.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from backend.services.monitoring import get_monitoring_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["monitoring"])


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """
    Get monitoring metrics.
    
    Returns:
        Dictionary with monitoring metrics
    """
    try:
        monitoring = get_monitoring_service()
        metrics = monitoring.get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics",
        )


@router.get("/metrics/errors", response_model=Dict[str, Any])
async def get_error_metrics(time_window_minutes: int = 60):
    """
    Get error metrics.
    
    Args:
        time_window_minutes: Time window in minutes (default: 60)
        
    Returns:
        Dictionary with error metrics
    """
    try:
        monitoring = get_monitoring_service()
        error_stats = monitoring.get_error_stats(time_window_minutes=time_window_minutes)
        return error_stats
    except Exception as e:
        logger.error(f"Error getting error metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve error metrics",
        )


@router.get("/metrics/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    metric_name: str = "response_time",
    time_window_minutes: int = 60,
):
    """
    Get performance metrics.
    
    Args:
        metric_name: Name of the metric (default: "response_time")
        time_window_minutes: Time window in minutes (default: 60)
        
    Returns:
        Dictionary with performance metrics
    """
    try:
        monitoring = get_monitoring_service()
        perf_stats = monitoring.get_performance_stats(
            metric_name=metric_name,
            time_window_minutes=time_window_minutes,
        )
        return perf_stats
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics",
        )


@router.get("/metrics/requests", response_model=Dict[str, Any])
async def get_request_metrics(time_window_minutes: int = 60):
    """
    Get request metrics.
    
    Args:
        time_window_minutes: Time window in minutes (default: 60)
        
    Returns:
        Dictionary with request metrics
    """
    try:
        monitoring = get_monitoring_service()
        request_stats = monitoring.get_request_stats(time_window_minutes=time_window_minutes)
        return request_stats
    except Exception as e:
        logger.error(f"Error getting request metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve request metrics",
        )


@router.get("/health/monitoring", response_model=Dict[str, Any])
async def get_monitoring_health():
    """
    Get monitoring service health status.
    
    Returns:
        Dictionary with health status
    """
    try:
        monitoring = get_monitoring_service()
        health = monitoring.get_health_status()
        return health
    except Exception as e:
        logger.error(f"Error getting monitoring health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monitoring health",
        )

