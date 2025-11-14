"""
Alerting Scheduler

Periodically checks metrics and sends alerts.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime

from backend.services.monitoring import get_monitoring_service
from backend.services.alerting import get_alerting_service

logger = logging.getLogger(__name__)


class AlertingScheduler:
    """
    Scheduler for periodic alert checks.
    """
    
    def __init__(self, check_interval_seconds: int = 60):
        """
        Initialize alerting scheduler.
        
        Args:
            check_interval_seconds: Interval between checks in seconds
        """
        self.check_interval_seconds = check_interval_seconds
        self.monitoring = get_monitoring_service()
        self.alerting = get_alerting_service()
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
        logger.info(f"AlertingScheduler initialized with {check_interval_seconds}s interval")
    
    async def check_and_alert_loop(self):
        """Main loop for checking metrics and sending alerts."""
        logger.info("Alerting scheduler started")
        
        while self.running:
            try:
                # Get metrics from monitoring service
                error_stats = self.monitoring.get_error_stats(time_window_minutes=5)
                performance_stats = self.monitoring.get_performance_stats(
                    "response_time",
                    time_window_minutes=5,
                )
                health_status = self.monitoring.get_health_status()
                
                # Check and send alerts
                self.alerting.check_and_alert(
                    error_stats=error_stats,
                    performance_stats=performance_stats,
                    health_status=health_status,
                )
                
            except Exception as e:
                logger.error(f"Error in alerting check loop: {e}", exc_info=True)
            
            # Wait for next check
            await asyncio.sleep(self.check_interval_seconds)
    
    def start(self):
        """Start the alerting scheduler."""
        if self.running:
            logger.warning("Alerting scheduler already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self.check_and_alert_loop())
        logger.info("Alerting scheduler started")
    
    def stop(self):
        """Stop the alerting scheduler."""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
        logger.info("Alerting scheduler stopped")
    
    async def check_once(self):
        """Perform a single check (for manual triggering)."""
        try:
            error_stats = self.monitoring.get_error_stats(time_window_minutes=5)
            performance_stats = self.monitoring.get_performance_stats(
                "response_time",
                time_window_minutes=5,
            )
            health_status = self.monitoring.get_health_status()
            
            self.alerting.check_and_alert(
                error_stats=error_stats,
                performance_stats=performance_stats,
                health_status=health_status,
            )
        except Exception as e:
            logger.error(f"Error in manual alert check: {e}", exc_info=True)


# Singleton instance
_scheduler_instance: Optional[AlertingScheduler] = None


def get_alerting_scheduler(check_interval_seconds: int = 60) -> AlertingScheduler:
    """
    Get or create the singleton AlertingScheduler instance.
    
    Args:
        check_interval_seconds: Interval between checks
        
    Returns:
        AlertingScheduler instance
    """
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = AlertingScheduler(check_interval_seconds=check_interval_seconds)
    
    return _scheduler_instance

