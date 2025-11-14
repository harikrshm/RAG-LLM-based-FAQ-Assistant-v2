# Testing Guide

This document describes the testing procedures for the FAQ Assistant application.

## Overview

The testing suite includes:
- Unit tests for backend services and API endpoints
- Integration tests for end-to-end flows
- Accuracy tests for response validation
- Compliance tests for investment advice blocking
- Load tests for performance validation

## Test Structure

```
backend/tests/
├── __init__.py
├── accuracy/          # Response accuracy tests
├── compliance/        # Compliance tests
├── integration/       # Integration tests
├── load/             # Load tests
└── data/             # Test datasets
```

## Running Tests

### All Tests

Run all test suites:
```bash
cd backend
pytest tests/ -v
```

### Specific Test Suites

**Unit Tests:**
```bash
# Backend services
pytest backend/services/*.test.py -v

# API endpoints
pytest backend/api/routes/*.test.py -v

# Data ingestion
pytest data_ingestion/*.test.py -v
```

**Integration Tests:**
```bash
pytest backend/tests/integration/ -v
```

**Accuracy Tests:**
```bash
pytest backend/tests/accuracy/ -v
```

**Compliance Tests:**
```bash
pytest backend/tests/compliance/ -v
```

**Load Tests:**
```bash
python -m backend.tests.load.run_load_tests --scenario medium_load
```

### With Coverage

Run tests with coverage report:
```bash
pytest tests/ --cov=backend --cov-report=html --cov-report=term
```

### Specific Test

Run a specific test file:
```bash
pytest backend/tests/integration/test_chat_flow.py -v
```

Run a specific test function:
```bash
pytest backend/tests/integration/test_chat_flow.py::test_successful_chat_response -v
```

## Test Categories

### Unit Tests

Test individual components in isolation.

**Backend Services:**
- `backend/services/rag_retrieval.test.py` - RAG retrieval pipeline
- `backend/services/llm_service.test.py` - LLM service
- `backend/services/vector_store.test.py` - Vector store operations
- `backend/services/response_generator.test.py` - Response generation

**API Endpoints:**
- `backend/api/routes/chat.test.py` - Chat API endpoint
- `backend/api/routes/health.test.py` - Health check endpoints
- `backend/main.test.py` - Main application tests

**Data Ingestion:**
- `data_ingestion/chunker.test.py` - Text chunking
- `data_ingestion/embedder.test.py` - Embedding generation
- `data_ingestion/scraper.test.py` - Web scraping
- `data_ingestion/processor.test.py` - Document processing
- `data_ingestion/pipeline.test.py` - Ingestion pipeline

### Integration Tests

Test end-to-end workflows.

**Files:**
- `backend/tests/integration/test_chat_flow.py` - Complete chat flow
- `backend/tests/integration/test_rag_pipeline.py` - RAG pipeline integration
- `backend/tests/integration/test_api_integration.py` - API integration

**Coverage:**
- Successful responses
- Error handling
- Source citations
- Fallback mechanisms
- Performance validation

### Accuracy Tests

Validate response accuracy against known queries.

**Files:**
- `backend/tests/accuracy/test_response_accuracy.py` - Response accuracy validation
- `backend/tests/accuracy/test_accuracy_metrics.py` - Accuracy metrics calculation
- `backend/tests/accuracy/test_dataset.py` - Test dataset

**Validation:**
- Keyword presence
- Confidence scores
- Source relevance
- Response completeness

### Compliance Tests

Ensure no investment advice is generated.

**Files:**
- `backend/tests/compliance/test_investment_advice_blocking.py` - Investment advice blocking
- `backend/tests/compliance/test_compliance_dataset.py` - Compliance test dataset

**Validation:**
- Query blocking
- Response blocking
- Pattern detection
- Context-dependent blocking

### Load Tests

Validate system performance under load.

**Files:**
- `backend/tests/load/test_load.py` - Load testing functionality
- `backend/tests/load/run_load_tests.py` - Load test runner

**Scenarios:**
- Low load (10 requests, 2 concurrent)
- Medium load (50 requests, 10 concurrent)
- High load (100 requests, 25 concurrent)
- Stress test (200 requests, 50 concurrent)
- Ramp-up test (gradual increase)
- Sustained load (500 requests, 20 concurrent)

## Test Configuration

### Environment Variables

Set up test environment:
```bash
export ENVIRONMENT=test
export LOG_LEVEL=WARNING
export VECTORDB_PATH=test_data/vectordb
export GEMINI_API_KEY=test_key  # Use test key or mock
```

### Test Database

Use separate test database:
```bash
export VECTORDB_PATH=test_data/vectordb
export METADATA_PATH=test_data/metadata_index.json
```

### Mocking External Services

For unit tests, mock external services:
- LLM API calls
- Vector database operations
- HTTP requests

## Pre-Deployment Checklist

Before deploying to production, ensure:

### 1. All Tests Pass

```bash
# Run all tests
pytest tests/ -v

# Check coverage (aim for >80%)
pytest tests/ --cov=backend --cov-report=term
```

### 2. Load Tests Pass

```bash
# Run medium load test
python -m backend.tests.load.run_load_tests --scenario medium_load

# Verify:
# - Success rate >= 95%
# - P95 response time < 5 seconds
# - Error rate < 5%
```

### 3. Compliance Tests Pass

```bash
# Run compliance tests
pytest backend/tests/compliance/ -v

# Verify:
# - No investment advice generated
# - All blocked queries are blocked
# - All allowed queries are allowed
```

### 4. Accuracy Tests Pass

```bash
# Run accuracy tests
pytest backend/tests/accuracy/ -v

# Verify:
# - Accuracy >= 80%
# - Keywords present in responses
# - Sources are relevant
```

### 5. Integration Tests Pass

```bash
# Run integration tests
pytest backend/tests/integration/ -v

# Verify:
# - End-to-end flows work
# - Error handling works
# - Fallback mechanisms work
```

### 6. Code Quality

```bash
# Run linters
flake8 backend/
black --check backend/
mypy backend/

# Fix any issues
```

### 7. Documentation Updated

- API documentation updated
- README updated
- Deployment guide updated
- Testing guide updated (this document)

### 8. Environment Configuration

- Environment variables set
- Secrets configured
- Database initialized
- Vector database populated

### 9. Monitoring Setup

- Monitoring service configured
- Alerts configured
- Logging configured
- Dashboard accessible

### 10. Security Checks

- API keys secured
- CORS configured correctly
- Rate limiting enabled
- Input validation working

## Continuous Integration

### GitHub Actions

Example CI workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest backend/tests/ -v --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Data Management

### Test Datasets

Test datasets are stored in:
- `backend/tests/data/test_queries.json` - Test queries
- `backend/tests/accuracy/test_dataset.py` - Accuracy test dataset
- `backend/tests/compliance/test_compliance_dataset.py` - Compliance dataset

### Adding New Tests

1. **Unit Test:**
   - Create `*.test.py` file next to source file
   - Use pytest fixtures for setup
   - Mock external dependencies

2. **Integration Test:**
   - Add to `backend/tests/integration/`
   - Use real services (with test database)
   - Test end-to-end flows

3. **Test Data:**
   - Add to appropriate dataset file
   - Include expected results
   - Document test case

## Troubleshooting

### Tests Failing

1. **Check environment:**
   ```bash
   echo $ENVIRONMENT
   echo $VECTORDB_PATH
   ```

2. **Check dependencies:**
   ```bash
   pip list | grep pytest
   ```

3. **Run with verbose output:**
   ```bash
   pytest tests/ -v -s
   ```

4. **Check logs:**
   ```bash
   tail -f logs/app.log
   ```

### Mock Issues

If mocks aren't working:
- Check import paths
- Verify mock decorators
- Check mock return values

### Database Issues

If database tests fail:
- Ensure test database path is set
- Check database permissions
- Verify test data is loaded

## Best Practices

1. **Write Tests First:** Use TDD when possible
2. **Test Edge Cases:** Include boundary conditions
3. **Mock External Services:** Don't depend on external APIs
4. **Keep Tests Fast:** Unit tests should be fast
5. **Use Fixtures:** Share test setup code
6. **Document Tests:** Add docstrings to test functions
7. **Maintain Coverage:** Aim for >80% coverage
8. **Run Tests Regularly:** Run before commits
9. **Fix Flaky Tests:** Investigate and fix unstable tests
10. **Update Tests:** Keep tests in sync with code changes

## Performance Benchmarks

Target performance metrics:

- **Response Time:**
  - Mean: < 2 seconds
  - P95: < 5 seconds
  - P99: < 10 seconds

- **Throughput:**
  - Requests/second: > 10
  - Concurrent users: > 20

- **Success Rate:**
  - Overall: > 95%
  - Under load: > 90%

- **Accuracy:**
  - Keyword accuracy: > 80%
  - Source relevance: > 75%

## Test Reports

Generate test reports:

```bash
# HTML report
pytest tests/ --html=report.html --self-contained-html

# Coverage report
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html

# JUnit XML (for CI)
pytest tests/ --junitxml=report.xml
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

