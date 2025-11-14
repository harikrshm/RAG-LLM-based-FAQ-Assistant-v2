"""
Alerting Service

Sends alerts for critical errors and performance degradation.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts."""
    ERROR_RATE = "error_rate"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_DOWN = "service_down"
    HIGH_ERROR_COUNT = "high_error_count"
    SLOW_RESPONSE = "slow_response"
    CRITICAL_ERROR = "critical_error"


@dataclass
class Alert:
    """Represents an alert."""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertingService:
    """
    Service for sending alerts on critical errors and performance issues.
    """
    
    def __init__(
        self,
        error_rate_threshold: float = 0.1,  # 10% error rate
        slow_response_threshold_ms: float = 5000.0,  # 5 seconds
        critical_error_threshold: int = 10,  # 10 critical errors
        time_window_minutes: int = 5,
    ):
        """
        Initialize alerting service.
        
        Args:
            error_rate_threshold: Error rate threshold (errors per second)
            slow_response_threshold_ms: Slow response threshold in milliseconds
            critical_error_threshold: Number of critical errors to trigger alert
            time_window_minutes: Time window for checking thresholds
        """
        self.error_rate_threshold = error_rate_threshold
        self.slow_response_threshold_ms = slow_response_threshold_ms
        self.critical_error_threshold = critical_error_threshold
        self.time_window_minutes = time_window_minutes
        
        # Alert handlers (callbacks)
        self.alert_handlers: List[Callable[[Alert], None]] = []
        
        # Recent alerts (to prevent spam)
        self.recent_alerts: deque = deque(maxlen=100)
        self.alert_cooldown_minutes = 5  # Don't send same alert within 5 minutes
        
        # Alert state tracking
        self.active_alerts: Dict[str, Alert] = {}
        
        logger.info("AlertingService initialized")
    
    def register_handler(self, handler: Callable[[Alert], None]):
        """
        Register an alert handler.
        
        Args:
            handler: Function that takes an Alert and sends it
        """
        self.alert_handlers.append(handler)
        logger.info(f"Alert handler registered: {handler.__name__}")
    
    def check_error_rate(
        self,
        error_count: int,
        request_count: int,
        time_window_minutes: int,
    ) -> Optional[Alert]:
        """
        Check if error rate exceeds threshold.
        
        Args:
            error_count: Number of errors in time window
            request_count: Number of requests in time window
            time_window_minutes: Time window in minutes
            
        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if request_count == 0:
            return None
        
        error_rate = error_count / (request_count * time_window_minutes * 60)
        
        if error_rate > self.error_rate_threshold:
            severity = AlertSeverity.CRITICAL if error_rate > self.error_rate_threshold * 2 else AlertSeverity.HIGH
            
            alert = Alert(
                alert_type=AlertType.ERROR_RATE,
                severity=severity,
                message=f"High error rate detected: {error_rate:.2%} (threshold: {self.error_rate_threshold:.2%})",
                timestamp=datetime.now(),
                details={
                    "error_count": error_count,
                    "request_count": request_count,
                    "error_rate": error_rate,
                    "threshold": self.error_rate_threshold,
                    "time_window_minutes": time_window_minutes,
                },
            )
            
            return alert
        
        return None
    
    def check_performance_degradation(
        self,
        avg_response_time_ms: float,
        p95_response_time_ms: float,
    ) -> Optional[Alert]:
        """
        Check if performance has degraded.
        
        Args:
            avg_response_time_ms: Average response time in milliseconds
            p95_response_time_ms: 95th percentile response time in milliseconds
            
        Returns:
            Alert if performance degraded, None otherwise
        """
        if p95_response_time_ms > self.slow_response_threshold_ms:
            severity = AlertSeverity.HIGH if p95_response_time_ms > self.slow_response_threshold_ms * 2 else AlertSeverity.MEDIUM
            
            alert = Alert(
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                severity=severity,
                message=f"Performance degradation detected: p95={p95_response_time_ms:.0f}ms (threshold: {self.slow_response_threshold_ms:.0f}ms)",
                timestamp=datetime.now(),
                details={
                    "avg_response_time_ms": avg_response_time_ms,
                    "p95_response_time_ms": p95_response_time_ms,
                    "threshold_ms": self.slow_response_threshold_ms,
                },
            )
            
            return alert
        
        return None
    
    def check_critical_errors(
        self,
        critical_error_count: int,
    ) -> Optional[Alert]:
        """
        Check if critical error count exceeds threshold.
        
        Args:
            critical_error_count: Number of critical errors
            
        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if critical_error_count >= self.critical_error_threshold:
            alert = Alert(
                alert_type=AlertType.CRITICAL_ERROR,
                severity=AlertSeverity.CRITICAL,
                message=f"Critical error threshold exceeded: {critical_error_count} errors",
                timestamp=datetime.now(),
                details={
                    "critical_error_count": critical_error_count,
                    "threshold": self.critical_error_threshold,
                },
            )
            
            return alert
        
        return None
    
    def check_service_health(
        self,
        health_status: str,
    ) -> Optional[Alert]:
        """
        Check if service is unhealthy.
        
        Args:
            health_status: Service health status
            
        Returns:
            Alert if service unhealthy, None otherwise
        """
        if health_status == "unhealthy":
            alert = Alert(
                alert_type=AlertType.SERVICE_DOWN,
                severity=AlertSeverity.CRITICAL,
                message="Service health check failed: service is unhealthy",
                timestamp=datetime.now(),
                details={
                    "health_status": health_status,
                },
            )
            
            return alert
        
        return None
    
    def send_alert(self, alert: Alert):
        """
        Send an alert through all registered handlers.
        
        Args:
            alert: Alert to send
        """
        # Check if we've sent this alert recently (cooldown)
        alert_key = f"{alert.alert_type.value}_{alert.severity.value}"
        
        if alert_key in self.active_alerts:
            existing_alert = self.active_alerts[alert_key]
            time_since_last = datetime.now() - existing_alert.timestamp
            
            if time_since_last.total_seconds() < self.alert_cooldown_minutes * 60:
                logger.debug(f"Alert {alert_key} still in cooldown, skipping")
                return
        
        # Store as active alert
        self.active_alerts[alert_key] = alert
        self.recent_alerts.append(alert)
        
        # Send through all handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via handler {handler.__name__}: {e}")
        
        logger.warning(f"Alert sent: {alert.alert_type.value} - {alert.message}")
    
    def resolve_alert(self, alert_type: AlertType, severity: AlertSeverity):
        """
        Mark an alert as resolved.
        
        Args:
            alert_type: Type of alert
            severity: Severity of alert
        """
        alert_key = f"{alert_type.value}_{severity.value}"
        
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            logger.info(f"Alert resolved: {alert_key}")
            
            # Remove from active alerts after a delay
            del self.active_alerts[alert_key]
    
    def check_and_alert(
        self,
        error_stats: Dict[str, Any],
        performance_stats: Dict[str, Any],
        health_status: Dict[str, Any],
    ):
        """
        Check metrics and send alerts if thresholds exceeded.
        
        Args:
            error_stats: Error statistics from monitoring service
            performance_stats: Performance statistics from monitoring service
            health_status: Health status from monitoring service
        """
        # Check error rate
        if "total_errors" in error_stats and "total_requests" in error_stats:
            error_alert = self.check_error_rate(
                error_count=error_stats["total_errors"],
                request_count=error_stats.get("total_requests", 1),
                time_window_minutes=error_stats.get("time_window_minutes", 5),
            )
            if error_alert:
                self.send_alert(error_alert)
        
        # Check performance degradation
        if "response_time_ms" in performance_stats:
            response_time = performance_stats["response_time_ms"]
            if isinstance(response_time, dict):
                avg = response_time.get("mean", 0)
                p95 = response_time.get("p95", 0)
                
                perf_alert = self.check_performance_degradation(avg, p95)
                if perf_alert:
                    self.send_alert(perf_alert)
        
        # Check critical errors
        if "errors_by_type" in error_stats:
            critical_count = sum(
                count for error_type, count in error_stats["errors_by_type"].items()
                if "critical" in error_type.lower() or "exception" in error_type.lower()
            )
            
            critical_alert = self.check_critical_errors(critical_count)
            if critical_alert:
                self.send_alert(critical_alert)
        
        # Check service health
        if "status" in health_status:
            health_alert = self.check_service_health(health_status["status"])
            if health_alert:
                self.send_alert(health_alert)
    
    def get_active_alerts(self) -> List[Alert]:
        """
        Get all active alerts.
        
        Returns:
            List of active alerts
        """
        return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    def get_recent_alerts(self, limit: int = 50) -> List[Alert]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return list(self.recent_alerts)[-limit:]


# Alert handlers
def console_alert_handler(alert: Alert):
    """
    Console alert handler (for development/testing).
    
    Args:
        alert: Alert to handle
    """
    print(f"\n{'='*60}")
    print(f"ALERT [{alert.severity.value.upper()}]")
    print(f"Type: {alert.alert_type.value}")
    print(f"Message: {alert.message}")
    print(f"Time: {alert.timestamp}")
    print(f"Details: {alert.details}")
    print(f"{'='*60}\n")


def logging_alert_handler(alert: Alert):
    """
    Logging alert handler.
    
    Args:
        alert: Alert to handle
    """
    log_level = {
        AlertSeverity.LOW: logging.INFO,
        AlertSeverity.MEDIUM: logging.WARNING,
        AlertSeverity.HIGH: logging.ERROR,
        AlertSeverity.CRITICAL: logging.CRITICAL,
    }.get(alert.severity, logging.WARNING)
    
    logger.log(
        log_level,
        f"ALERT [{alert.alert_type.value}] {alert.message}",
        extra=alert.details,
    )


def webhook_alert_handler(webhook_url: str):
    """
    Create a webhook alert handler.
    
    Args:
        webhook_url: Webhook URL to send alerts to
        
    Returns:
        Alert handler function
    """
    import requests
    
    def handler(alert: Alert):
        """Send alert to webhook."""
        try:
            payload = {
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "details": alert.details,
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send alert to webhook: {e}")
    
    return handler


# Singleton instance
_alerting_instance: Optional[AlertingService] = None


def get_alerting_service() -> AlertingService:
    """
    Get or create the singleton AlertingService instance.
    
    Returns:
        AlertingService instance
    """
    global _alerting_instance
    
    if _alerting_instance is None:
        _alerting_instance = AlertingService()
        
        # Register default handlers
        _alerting_instance.register_handler(logging_alert_handler)
        _alerting_instance.register_handler(console_alert_handler)
    
    return _alerting_instance

