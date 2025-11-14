# Load Testing Guide

This document describes how to perform load testing on the FAQ Assistant API.

## Overview

Load testing verifies that the system can handle concurrent requests and maintains acceptable performance under various load conditions.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install aiohttp
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Ensure vector database is initialized** with test data

## Running Load Tests

### Basic Usage

Run a default medium load test:
```bash
python -m backend.tests.load.run_load_tests
```

### Run Specific Scenario

Run a specific test scenario:
```bash
python -m backend.tests.load.run_load_tests --scenario high_load
```

### Run All Scenarios

Run all test scenarios:
```bash
python -m backend.tests.load.run_load_tests --all
```

### Custom Base URL

Test against a different server:
```bash
python -m backend.tests.load.run_load_tests --base-url http://staging.example.com:8000
```

## Test Scenarios

### Low Load

Light load test with minimal concurrency:
- **Requests**: 10
- **Concurrency**: 2
- **Expected Success Rate**: 100%
- **Expected Max Response Time**: 5 seconds

```bash
python -m backend.tests.load.run_load_tests --scenario low_load
```

### Medium Load

Moderate load test:
- **Requests**: 50
- **Concurrency**: 10
- **Expected Success Rate**: 95%
- **Expected Max Response Time**: 10 seconds

```bash
python -m backend.tests.load.run_load_tests --scenario medium_load
```

### High Load

Heavy load test:
- **Requests**: 100
- **Concurrency**: 25
- **Expected Success Rate**: 90%
- **Expected Max Response Time**: 15 seconds

```bash
python -m backend.tests.load.run_load_tests --scenario high_load
```

### Stress Test

Stress test to find breaking point:
- **Requests**: 200
- **Concurrency**: 50
- **Expected Success Rate**: 80%
- **Expected Max Response Time**: 30 seconds

```bash
python -m backend.tests.load.run_load_tests --scenario stress_test
```

### Ramp-Up Test

Gradually increase load:
- **Initial Users**: 1
- **Max Users**: 20
- **Ramp-Up Time**: 30 seconds
- **Requests Per User**: 5
- **Expected Success Rate**: 95%

```bash
python -m backend.tests.load.run_load_tests --scenario ramp_up
```

### Sustained Load

Sustained load over time:
- **Requests**: 500
- **Concurrency**: 20
- **Expected Success Rate**: 95%
- **Expected Max Response Time**: 10 seconds

```bash
python -m backend.tests.load.run_load_tests --scenario sustained_load
```

## Performance Thresholds

The load tests validate results against these thresholds:

- **P95 Response Time**: < 5000ms (5 seconds)
- **P99 Response Time**: < 10000ms (10 seconds)
- **Error Rate**: < 5%
- **Success Rate**: ≥ 95%

## Understanding Results

### Success Rate

Percentage of requests that completed successfully (HTTP 200).

**Good**: ≥ 95%
**Warning**: 90-95%
**Failure**: < 90%

### Response Time Metrics

- **Mean**: Average response time
- **Median (P50)**: 50th percentile response time
- **P95**: 95th percentile response time (95% of requests faster)
- **P99**: 99th percentile response time (99% of requests faster)
- **Min/Max**: Minimum and maximum response times

**Good**: P95 < 5 seconds
**Warning**: P95 5-10 seconds
**Failure**: P95 > 10 seconds

### Requests Per Second

Throughput metric indicating system capacity.

**Good**: Consistent throughput under load
**Warning**: Throughput degrades under high load
**Failure**: Throughput drops significantly

## Interpreting Results

### Healthy System

```
Success Rate: 98.5%
P95 Response Time: 2.5s
P99 Response Time: 4.0s
Requests/Second: 15.2
```

### System Under Stress

```
Success Rate: 85.0%
P95 Response Time: 8.5s
P99 Response Time: 15.0s
Requests/Second: 8.5
```

### System Failure

```
Success Rate: 45.0%
P95 Response Time: 25.0s
P99 Response Time: 45.0s
Requests/Second: 2.1
```

## Troubleshooting

### High Error Rate

**Symptoms**: Success rate < 90%

**Possible Causes**:
- Server not running
- Database connection issues
- Resource exhaustion (memory, CPU)
- Rate limiting

**Solutions**:
- Check server logs
- Verify database connectivity
- Monitor system resources
- Adjust rate limits

### Slow Response Times

**Symptoms**: P95 > 10 seconds

**Possible Causes**:
- Slow database queries
- LLM API latency
- Network issues
- Insufficient resources

**Solutions**:
- Optimize database queries
- Use faster LLM provider
- Check network connectivity
- Scale up resources

### Timeout Errors

**Symptoms**: Many timeout errors

**Possible Causes**:
- Slow LLM responses
- Database timeouts
- Network latency

**Solutions**:
- Increase timeout values
- Optimize slow operations
- Use connection pooling
- Add caching

## Best Practices

1. **Start Small**: Begin with low load tests and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and network during tests
3. **Test Regularly**: Run load tests after major changes
4. **Document Baselines**: Record baseline performance metrics
5. **Test Realistic Scenarios**: Use realistic query patterns
6. **Test Different Times**: Run tests at different times to account for variability

## Continuous Integration

Add load tests to CI/CD pipeline:

```yaml
# .github/workflows/load-test.yml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install aiohttp
      - name: Start server
        run: |
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 10
      - name: Run load tests
        run: |
          python -m backend.tests.load.run_load_tests --scenario medium_load
```

## Advanced Usage

### Custom Test Script

Create custom load test:

```python
import asyncio
from backend.tests.load.test_load import run_concurrent_requests, print_results

async def custom_test():
    result = await run_concurrent_requests(
        num_requests=1000,
        concurrency=50,
        queries=["Your custom query"],
    )
    print_results(result, "Custom Test")

asyncio.run(custom_test())
```

### Integration with Monitoring

Monitor system metrics during load tests:

```bash
# Terminal 1: Run load test
python -m backend.tests.load.run_load_tests --scenario high_load

# Terminal 2: Monitor metrics
watch -n 1 'curl -s http://localhost:8000/api/dashboard/summary | jq'
```

## Performance Optimization

Based on load test results:

1. **Add Caching**: Cache frequent queries
2. **Optimize Database**: Index frequently queried fields
3. **Connection Pooling**: Reuse database connections
4. **Async Operations**: Use async/await for I/O operations
5. **Rate Limiting**: Implement rate limiting to prevent overload
6. **Horizontal Scaling**: Scale out to multiple instances
7. **CDN**: Use CDN for static assets

