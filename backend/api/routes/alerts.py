"""
Alerts API Routes

Endpoints for managing and viewing alerts.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from backend.services.alerting import get_alerting_service, AlertType, AlertSeverity

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_active_alerts():
    """
    Get all active alerts.
    
    Returns:
        List of active alerts
    """
    try:
        alerting = get_alerting_service()
        alerts = alerting.get_active_alerts()
        
        return [
            {
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "details": alert.details,
                "resolved": alert.resolved,
            }
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Error getting alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts",
        )


@router.get("/alerts/recent", response_model=List[Dict[str, Any]])
async def get_recent_alerts(limit: int = 50):
    """
    Get recent alerts.
    
    Args:
        limit: Maximum number of alerts to return
        
    Returns:
        List of recent alerts
    """
    try:
        alerting = get_alerting_service()
        alerts = alerting.get_recent_alerts(limit=limit)
        
        return [
            {
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "details": alert.details,
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            }
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Error getting recent alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent alerts",
        )


@router.post("/alerts/resolve")
async def resolve_alert(alert_type: str, severity: str):
    """
    Mark an alert as resolved.
    
    Args:
        alert_type: Type of alert
        severity: Severity of alert
        
    Returns:
        Success message
    """
    try:
        alerting = get_alerting_service()
        
        # Convert string to enum
        try:
            alert_type_enum = AlertType(alert_type)
            severity_enum = AlertSeverity(severity)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid alert type or severity: {e}",
            )
        
        alerting.resolve_alert(alert_type_enum, severity_enum)
        
        return {"message": "Alert resolved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert",
        )


@router.post("/alerts/test")
async def test_alert():
    """
    Send a test alert (for testing alert handlers).
    
    Returns:
        Success message
    """
    try:
        from backend.services.alerting import Alert, AlertType, AlertSeverity
        from datetime import datetime
        
        alerting = get_alerting_service()
        
        test_alert = Alert(
            alert_type=AlertType.CRITICAL_ERROR,
            severity=AlertSeverity.MEDIUM,
            message="Test alert - this is a test",
            timestamp=datetime.now(),
            details={"test": True},
        )
        
        alerting.send_alert(test_alert)
        
        return {"message": "Test alert sent successfully"}
    except Exception as e:
        logger.error(f"Error sending test alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test alert",
        )

