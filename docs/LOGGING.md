# Logging Configuration

This document describes the logging system configuration for the FAQ Assistant application.

## Overview

The application uses Python's `logging` module with a centralized configuration system that provides:

- Environment-specific log levels
- File and console logging
- Log rotation and archival
- Structured logging for better analysis
- Request context tracking

## Log Levels

The application uses standard Python log levels with environment-specific defaults:

- **DEBUG**: Detailed diagnostic information (development only)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause application failure

### Environment-Specific Levels

- **Development**: DEBUG
- **Staging**: INFO
- **Production**: WARNING
- **Test**: WARNING

## Log Files

Logs are stored in the `logs/` directory:

- `logs/app.log` - Main application log (all levels)
- `logs/error.log` - Error log (ERROR and above only)
- `logs/access.log` - Access log (request/response logging)

### Log Rotation

- **app.log**: Rotates when file reaches 10MB, keeps 5 backups
- **error.log**: Rotates when file reaches 10MB, keeps 10 backups
- **access.log**: Rotates daily at midnight, keeps 30 days

## Configuration

Logging is configured in `backend/utils/logging_config.py` and initialized in `backend/main.py`.

### Environment Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `ENVIRONMENT`: Environment name (development, staging, production)

### Example Configuration

```python
from backend.utils.logging_config import setup_logging

setup_logging(
    log_level="INFO",
    log_file="logs/app.log",
    enable_file_logging=True,
    enable_console_logging=True,
)
```

## Logging Best Practices

### 1. Use Appropriate Log Levels

```python
logger.debug("Detailed diagnostic information")
logger.info("General information")
logger.warning("Potential issue")
logger.error("Error occurred")
logger.critical("Critical failure")
```

### 2. Include Context

```python
logger.info(f"Processing request: {request_id}, endpoint: {endpoint}")
logger.error(f"Failed to process query: {query}", exc_info=True)
```

### 3. Use Structured Logging

```python
logger.info(
    "Query processed",
    extra={
        "query": query,
        "session_id": session_id,
        "response_time_ms": response_time,
    }
)
```

### 4. Avoid Logging Sensitive Information

Never log:
- API keys
- Passwords
- Personal user data
- Authentication tokens

## Request Context

The logging middleware automatically adds request context to log records:

- `request_id`: Unique request identifier
- `session_id`: User session identifier (if available)

## Third-Party Logger Configuration

Third-party library loggers are configured to reduce noise:

- `uvicorn`: WARNING
- `fastapi`: WARNING
- `httpx`: WARNING
- `chromadb`: WARNING
- `google.generativeai`: WARNING
- `sentence_transformers`: WARNING

## Access Logging

Access logs track HTTP requests and responses:

- Request method and path
- Response status code
- Response time
- Client IP address

Access logs are written to `logs/access.log` and rotated daily.

## Error Logging

Errors are logged to both `logs/app.log` and `logs/error.log`:

- Error type and message
- Stack trace (if available)
- Request context
- Endpoint information

## Production Considerations

In production:

1. Set `LOG_LEVEL` to `WARNING` or `ERROR`
2. Enable file logging for persistence
3. Monitor log file sizes
4. Set up log aggregation (e.g., ELK stack, CloudWatch)
5. Configure log retention policies
6. Set up alerts for ERROR and CRITICAL logs

## Log Analysis

### Common Patterns

- **High error rate**: Check `logs/error.log` for patterns
- **Slow requests**: Check access logs for response times > 5s
- **Service failures**: Check for CRITICAL level logs

### Tools

- **grep**: Search log files
- **tail**: Monitor logs in real-time
- **ELK Stack**: Centralized log aggregation
- **CloudWatch**: AWS log aggregation
- **Splunk**: Enterprise log analysis

## Troubleshooting

### Logs Not Appearing

1. Check log file permissions
2. Verify `LOG_LEVEL` setting
3. Check disk space
4. Verify logger configuration

### Too Much Logging

1. Increase `LOG_LEVEL` to WARNING or ERROR
2. Check third-party logger levels
3. Review debug statements

### Logs Too Large

1. Reduce log retention (backupCount)
2. Increase log rotation size
3. Use log compression
4. Implement log archival

