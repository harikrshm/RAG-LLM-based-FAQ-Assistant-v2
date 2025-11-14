# Monitoring Dashboard

This document describes the monitoring dashboard API endpoints for viewing key metrics.

## Overview

The monitoring dashboard provides comprehensive metrics about application performance, errors, usage, and health status. All endpoints are available under `/api/dashboard`.

## Endpoints

### Dashboard Summary

Get a quick summary of key metrics.

```http
GET /api/dashboard/summary
```

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "summary": {
    "status": "healthy",
    "total_requests": 1000,
    "error_rate_percent": 2.5,
    "avg_response_time_ms": 250.5,
    "uptime_percent": 99.9
  }
}
```

### Comprehensive Metrics

Get all dashboard metrics in one call.

```http
GET /api/dashboard/metrics?time_window_minutes=60
```

**Query Parameters:**
- `time_window_minutes` (optional): Time window for metrics (default: 60, max: 1440)

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "time_window_minutes": 60,
  "overview": {
    "total_requests": 1000,
    "total_errors": 25,
    "error_rate_percent": 2.5,
    "avg_response_time_ms": 250.5,
    "status": "healthy"
  },
  "response_time": {
    "mean_ms": 250.5,
    "p50_ms": 200.0,
    "p95_ms": 500.0,
    "p99_ms": 800.0,
    "min_ms": 50.0,
    "max_ms": 1000.0
  },
  "errors": {
    "total": 25,
    "rate_percent": 2.5,
    "by_type": {
      "ValidationError": 10,
      "ServiceError": 15
    },
    "by_endpoint": {
      "/api/chat": 20,
      "/api/health": 5
    }
  },
  "requests": {
    "total": 1000,
    "by_endpoint": {
      "/api/chat": 800,
      "/api/health": 200
    },
    "by_status_code": {
      "200": 975,
      "400": 10,
      "500": 15
    }
  },
  "health": {
    "status": "healthy",
    "uptime_percent": 99.9
  },
  "metrics": {
    "requests_per_minute": 16.67,
    "errors_per_minute": 0.42
  }
}
```

### Response Time Metrics

Get detailed response time metrics.

```http
GET /api/dashboard/response-time?time_window_minutes=60&endpoint=/api/chat
```

**Query Parameters:**
- `time_window_minutes` (optional): Time window (default: 60)
- `endpoint` (optional): Filter by specific endpoint

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "time_window_minutes": 60,
  "endpoint": "/api/chat",
  "metrics": {
    "mean_ms": 250.5,
    "p50_ms": 200.0,
    "p95_ms": 500.0,
    "p99_ms": 800.0,
    "min_ms": 50.0,
    "max_ms": 1000.0
  }
}
```

### Error Rate Metrics

Get error rate and error breakdown.

```http
GET /api/dashboard/error-rate?time_window_minutes=60
```

**Query Parameters:**
- `time_window_minutes` (optional): Time window (default: 60)

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "time_window_minutes": 60,
  "metrics": {
    "total_requests": 1000,
    "total_errors": 25,
    "error_rate_percent": 2.5,
    "errors_per_second": 0.007
  },
  "errors_by_type": {
    "ValidationError": 10,
    "ServiceError": 15
  },
  "errors_by_endpoint": {
    "/api/chat": 20,
    "/api/health": 5
  }
}
```

### Usage Metrics

Get request usage statistics.

```http
GET /api/dashboard/usage?time_window_minutes=60
```

**Query Parameters:**
- `time_window_minutes` (optional): Time window (default: 60)

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "time_window_minutes": 60,
  "metrics": {
    "total_requests": 1000,
    "requests_per_minute": 16.67,
    "requests_per_second": 0.28
  },
  "requests_by_endpoint": {
    "/api/chat": 800,
    "/api/health": 200
  },
  "requests_by_status_code": {
    "200": 975,
    "400": 10,
    "500": 15
  }
}
```

### Health Metrics

Get health status.

```http
GET /api/dashboard/health
```

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "health": {
    "status": "healthy",
    "uptime_percent": 99.9,
    "components": {
      "vector_store": "healthy",
      "llm_service": "healthy",
      "rag_pipeline": "healthy"
    }
  }
}
```

### Time Series Data

Get time series data for a metric.

```http
GET /api/dashboard/time-series?metric=response_time&time_window_minutes=60&interval_minutes=5
```

**Query Parameters:**
- `metric`: Metric name (`response_time`, `error_rate`, `requests`)
- `time_window_minutes` (optional): Time window (default: 60)
- `interval_minutes` (optional): Interval between data points (default: 5)

**Response:**
```json
{
  "metric": "response_time",
  "time_window_minutes": 60,
  "interval_minutes": 5,
  "data_points": [
    {
      "timestamp": "2024-01-01T09:00:00",
      "value": 200.5
    },
    {
      "timestamp": "2024-01-01T09:05:00",
      "value": 250.0
    },
    ...
  ]
}
```

## Dashboard Integration Examples

### React Dashboard Component

```typescript
import { useEffect, useState } from 'react';
import axios from 'axios';

interface DashboardMetrics {
  overview: {
    total_requests: number;
    error_rate_percent: number;
    avg_response_time_ms: number;
    status: string;
  };
  response_time: {
    mean_ms: number;
    p95_ms: number;
  };
  errors: {
    total: number;
    by_type: Record<string, number>;
  };
}

function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get('/api/dashboard/metrics');
        setMetrics(response.data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <div>Loading...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <div>
        <h2>Overview</h2>
        <p>Status: {metrics.overview.status}</p>
        <p>Total Requests: {metrics.overview.total_requests}</p>
        <p>Error Rate: {metrics.overview.error_rate_percent}%</p>
        <p>Avg Response Time: {metrics.overview.avg_response_time_ms}ms</p>
      </div>
      <div>
        <h2>Response Time</h2>
        <p>Mean: {metrics.response_time.mean_ms}ms</p>
        <p>P95: {metrics.response_time.p95_ms}ms</p>
      </div>
      <div>
        <h2>Errors</h2>
        <p>Total: {metrics.errors.total}</p>
        <ul>
          {Object.entries(metrics.errors.by_type).map(([type, count]) => (
            <li key={type}>{type}: {count}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

### Grafana Dashboard

Use Grafana with a JSON API data source:

1. Add JSON API data source pointing to `/api/dashboard/metrics`
2. Create panels for:
   - Response time (line chart)
   - Error rate (line chart)
   - Request count (bar chart)
   - Health status (stat panel)

### Prometheus Integration

Export metrics in Prometheus format:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
error_count = Counter('http_errors_total', 'Total HTTP errors')
response_time = Histogram('http_response_time_seconds', 'HTTP response time')
```

## Best Practices

1. **Polling Interval**: Poll dashboard endpoints every 30-60 seconds
2. **Time Windows**: Use appropriate time windows (1 hour for real-time, 24 hours for trends)
3. **Caching**: Cache dashboard data on the client side to reduce API calls
4. **Error Handling**: Handle API errors gracefully and show fallback data
5. **Visualization**: Use appropriate chart types:
   - Line charts for time series
   - Bar charts for categorical data
   - Gauges for single metrics
   - Tables for detailed breakdowns

## Performance Considerations

- Dashboard endpoints aggregate data, which may be computationally expensive
- Consider caching dashboard responses for 10-30 seconds
- Use time windows appropriately to balance detail vs. performance
- Monitor dashboard endpoint performance itself

