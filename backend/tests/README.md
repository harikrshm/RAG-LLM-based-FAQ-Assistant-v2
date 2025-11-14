# Backend Tests

This directory contains unit and integration tests for the FAQ Assistant backend.

## Test Structure

- `integration/` - Integration tests for end-to-end flows
  - `test_chat_flow.py` - End-to-end chat flow tests
  - `test_rag_pipeline.py` - RAG pipeline integration tests
  - `test_api_integration.py` - API endpoint integration tests

## Running Tests

### Run all tests
```bash
pytest backend/tests/
```

### Run integration tests only
```bash
pytest backend/tests/integration/
```

### Run specific test file
```bash
pytest backend/tests/integration/test_chat_flow.py
```

### Run with coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

### Run with verbose output
```bash
pytest backend/tests/ -v
```

## Test Requirements

Tests use `pytest` and `pytest-asyncio` for async test support. Make sure these are installed:

```bash
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

## Test Fixtures

Tests use mocks for external dependencies:
- Vector store (ChromaDB/Pinecone)
- LLM service (Gemini/local)
- Groww mapper service
- Response generator

## Integration Tests

Integration tests verify:
1. Complete chat flow from API request to response
2. RAG pipeline integration (retrieval + generation)
3. Error handling and edge cases
4. Performance characteristics
5. API endpoint behavior

## Skipped Tests

Some tests are marked with `@pytest.mark.skip` because they require:
- Real vector store with ingested data
- Real LLM service configuration
- Network connectivity

To run these tests, remove the skip decorator and ensure services are configured.

