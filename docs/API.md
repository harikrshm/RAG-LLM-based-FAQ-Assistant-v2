# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T01:00:00Z"
}
```

### Chat Query

**POST** `/api/chat`

Send a question to the FAQ assistant and get a factual answer with citations.

**Request Body:**
```json
{
  "question": "What is the expense ratio of XYZ mutual fund scheme?",
  "conversation_id": "optional-conversation-id"
}
```

**Response:**
```json
{
  "answer": "The expense ratio of XYZ mutual fund scheme is 1.5% per annum...",
  "sources": [
    {
      "url": "https://example.com/scheme-details",
      "title": "Scheme Details - XYZ AMC",
      "type": "groww" // or "amc", "sebi", "amfi"
    }
  ],
  "inline_sources": [
    {
      "text": "expense ratio",
      "url": "https://example.com/scheme-details"
    }
  ],
  "conversation_id": "generated-conversation-id",
  "timestamp": "2025-11-14T01:00:00Z"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-11-14T01:00:00Z"
}
```

## Rate Limiting

- Default: 60 requests per minute
- Configurable via `RATE_LIMIT_REQUESTS_PER_MINUTE` environment variable

## Authentication

Currently, the API does not require authentication. In production, implement API key or JWT authentication.

## CORS

CORS is configured to allow requests from configured origins. Update `CORS_ORIGINS` in environment variables.

## Error Codes

- `INVALID_REQUEST` - Invalid request format
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `LLM_ERROR` - LLM service error
- `VECTOR_STORE_ERROR` - Vector database error
- `NOT_FOUND` - Information not found

