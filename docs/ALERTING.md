# Alerting Configuration

This document describes the alerting system for monitoring critical errors and performance degradation.

## Overview

The alerting system monitors application metrics and sends alerts when thresholds are exceeded:

- **Error Rate**: High error rate detection
- **Performance Degradation**: Slow response times
- **Critical Errors**: Multiple critical errors
- **Service Health**: Service unavailability

## Alert Types

### Error Rate Alert

Triggered when error rate exceeds threshold (default: 10% or 0.1 errors per second).

**Severity Levels:**
- HIGH: Error rate > threshold
- CRITICAL: Error rate > 2x threshold

### Performance Degradation Alert

Triggered when response time exceeds threshold (default: 5000ms for p95).

**Severity Levels:**
- MEDIUM: p95 > threshold
- HIGH: p95 > 2x threshold

### Critical Error Alert

Triggered when number of critical errors exceeds threshold (default: 10 errors).

**Severity:** CRITICAL

### Service Down Alert

Triggered when service health check fails.

**Severity:** CRITICAL

## Configuration

### Environment Variables

- `ALERTING_ENABLED`: Enable/disable alerting (default: true)
- `ALERT_ERROR_RATE_THRESHOLD`: Error rate threshold (default: 0.1)
- `ALERT_SLOW_RESPONSE_THRESHOLD_MS`: Slow response threshold in ms (default: 5000)
- `ALERT_CRITICAL_ERROR_THRESHOLD`: Critical error count threshold (default: 10)
- `ALERT_WEBHOOK_URL`: Webhook URL for sending alerts
- `ALERT_CHECK_INTERVAL_SECONDS`: Check interval in seconds (default: 60)

### Example Configuration

```bash
ALERTING_ENABLED=true
ALERT_ERROR_RATE_THRESHOLD=0.1
ALERT_SLOW_RESPONSE_THRESHOLD_MS=5000
ALERT_CRITICAL_ERROR_THRESHOLD=10
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_CHECK_INTERVAL_SECONDS=60
```

## Alert Handlers

### Console Handler

Logs alerts to console (enabled by default for development).

### Logging Handler

Logs alerts using Python logging (enabled by default).

### Webhook Handler

Sends alerts to a webhook URL (configure via `ALERT_WEBHOOK_URL`).

**Webhook Payload:**
```json
{
  "alert_type": "error_rate",
  "severity": "high",
  "message": "High error rate detected: 15.00%",
  "timestamp": "2024-01-01T10:00:00",
  "details": {
    "error_count": 15,
    "request_count": 100,
    "error_rate": 0.15,
    "threshold": 0.1
  }
}
```

## API Endpoints

### Get Active Alerts

```http
GET /api/alerts
```

Returns all currently active alerts.

### Get Recent Alerts

```http
GET /api/alerts/recent?limit=50
```

Returns recent alerts (default: 50).

### Resolve Alert

```http
POST /api/alerts/resolve?alert_type=error_rate&severity=high
```

Marks an alert as resolved.

### Test Alert

```http
POST /api/alerts/test
```

Sends a test alert (for testing alert handlers).

## Integration Examples

### Slack Webhook

```python
from backend.services.alerting import get_alerting_service, webhook_alert_handler

alerting = get_alerting_service()
alerting.register_handler(
    webhook_alert_handler("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
)
```

### Email Alert Handler

```python
import smtplib
from email.mime.text import MIMEText
from backend.services.alerting import Alert, AlertSeverity

def email_alert_handler(alert: Alert):
    """Send alert via email."""
    if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
        # Send email
        msg = MIMEText(alert.message)
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.alert_type.value}"
        msg['From'] = "alerts@example.com"
        msg['To'] = "admin@example.com"
        
        # Send via SMTP
        # smtp.sendmail(...)
```

### Custom Handler

```python
from backend.services.alerting import Alert

def custom_handler(alert: Alert):
    """Custom alert handler."""
    # Your custom logic here
    print(f"Custom alert: {alert.message}")

# Register handler
alerting = get_alerting_service()
alerting.register_handler(custom_handler)
```

## Alert Cooldown

To prevent alert spam, alerts have a cooldown period (default: 5 minutes). The same alert type and severity won't be sent again within the cooldown period.

## Monitoring

The alerting scheduler runs continuously, checking metrics at configured intervals:

1. Retrieves error statistics
2. Retrieves performance statistics
3. Retrieves health status
4. Checks thresholds
5. Sends alerts if thresholds exceeded

## Best Practices

1. **Set Appropriate Thresholds**: Adjust thresholds based on your application's normal behavior
2. **Use Multiple Handlers**: Combine logging, webhook, and email handlers
3. **Monitor Alert Volume**: Too many alerts indicate threshold issues
4. **Resolve Alerts**: Mark alerts as resolved when issues are fixed
5. **Test Alerts**: Use `/api/alerts/test` to verify handlers work

## Troubleshooting

### Alerts Not Sending

1. Check `ALERTING_ENABLED` is true
2. Verify alert handlers are registered
3. Check logs for handler errors
4. Verify thresholds are appropriate

### Too Many Alerts

1. Increase thresholds
2. Increase cooldown period
3. Review alert conditions
4. Check for underlying issues

### Alerts Not Resolving

1. Verify underlying issue is fixed
2. Manually resolve via API
3. Check alert state

