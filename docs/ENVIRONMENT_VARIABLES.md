# Environment Variables Guide

This document describes all environment variables used in the FAQ Assistant project.

## Backend Environment Variables

### Application Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | "Mutual Funds FAQ Assistant" | No |
| `VERSION` | Application version | "1.0.0" | No |
| `ENVIRONMENT` | Environment (development/staging/production) | "development" | No |
| `DEBUG` | Enable debug mode | `true` | No |
| `HOST` | Server host | "0.0.0.0" | No |
| `PORT` | Server port | 8000 | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | "INFO" | No |

### CORS Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGINS` | Comma-separated list of allowed origins | Localhost origins | No |
| `CORS_ORIGINS_ENV` | Alternative: Comma-separated string from env | None | No |

**Example:**
```bash
CORS_ORIGINS_ENV=https://example.com,https://www.example.com,https://staging.example.com
```

### Vector Database

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VECTORDB_PATH` | Path to vector database directory | "data/vectordb" | No |
| `VECTORDB_COLLECTION` | Collection name | "mutual_funds_faq" | No |

### Embeddings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMBEDDING_MODEL` | Sentence transformer model name | "all-MiniLM-L6-v2" | No |
| `EMBEDDING_DIMENSION` | Embedding vector dimension | 384 | No |

### LLM Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM provider (gemini/openai/anthropic/local) | "gemini" | No |
| `LLM_MODEL` | Model name | "gemini-pro" | No |
| `LLM_TEMPERATURE` | Temperature for generation | 0.1 | No |
| `LLM_MAX_TOKENS` | Maximum tokens in response | 500 | No |
| `LLM_REQUEST_TIMEOUT` | Request timeout in seconds | 30 | No |

### API Keys

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | "" | Yes (if using Gemini) |
| `OPENAI_API_KEY` | OpenAI API key | "" | Yes (if using OpenAI) |
| `ANTHROPIC_API_KEY` | Anthropic API key | "" | Yes (if using Anthropic) |
| `LOCAL_LLM_URL` | Local LLM API URL | None | Yes (if using local) |
| `LOCAL_LLM_API_KEY` | Local LLM API key | None | No |

### RAG Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RAG_TOP_K` | Number of chunks to retrieve | 5 | No |
| `RAG_SIMILARITY_THRESHOLD` | Minimum similarity score | 0.5 | No |

### Rate Limiting

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` | No |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute | 60 | No |
| `RATE_LIMIT_PER_HOUR` | Requests per hour | 1000 | No |

### Metadata Paths

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `METADATA_PATH` | Path to metadata index JSON | "data/metadata_index.json" | No |
| `SOURCE_URLS_PATH` | Path to source URLs JSON | "data/source_urls.json" | No |

## Frontend Environment Variables

### Build-Time Variables (Vite)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_BASE_URL` | Backend API base URL | "http://localhost:8000" | Yes |

**Note:** Vite requires the `VITE_` prefix for environment variables to be exposed to the client.

## Environment-Specific Configurations

### Development

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
VECTORDB_PATH=data/vectordb
```

### Staging

```bash
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.example.com
VECTORDB_PATH=/app/data/vectordb
```

### Production

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://example.com,https://www.example.com
VECTORDB_PATH=/app/data/vectordb
```

## Setting Environment Variables

### Local Development

Create `.env` files in respective directories:

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

**Frontend:**
```bash
cd frontend
cp .env.example .env
# Edit .env with your values
```

### Railway Deployment

1. Go to Railway dashboard
2. Select your service
3. Go to "Variables" tab
4. Add environment variables
5. Railway automatically applies them

### Docker Deployment

Use `docker-compose.yml` or pass via `-e` flag:

```bash
docker run -e GEMINI_API_KEY=your_key your-image
```

### Vercel Deployment

1. Go to Vercel dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Add variables for each environment (Production, Preview, Development)

## Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use secrets management** - Railway/Vercel provide secure storage
3. **Rotate API keys regularly** - Especially in production
4. **Use different keys per environment** - Don't share dev/prod keys
5. **Limit CORS origins** - Only allow trusted domains
6. **Use environment-specific configs** - Different settings per environment

## Validation

The application validates environment variables on startup. Check logs for:
- Missing required variables
- Invalid values
- Configuration warnings

## Troubleshooting

### Variables Not Loading

1. Check file name: `.env` (not `.env.txt`)
2. Verify file location: Same directory as application
3. Check for typos in variable names
4. Restart application after changes

### CORS Issues

1. Verify `CORS_ORIGINS` includes your frontend domain
2. Check for protocol mismatch (http vs https)
3. Ensure no trailing slashes
4. Check browser console for specific CORS errors

### API Key Issues

1. Verify key is set correctly (no extra spaces)
2. Check key has proper permissions
3. Verify key hasn't expired
4. Check API provider dashboard for usage/errors

## Examples

### Minimal Production Setup

```bash
# Backend
GEMINI_API_KEY=your_key_here
ENVIRONMENT=production
CORS_ORIGINS_ENV=https://yourdomain.com

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Full Production Setup

```bash
# Backend
APP_NAME=Mutual Funds FAQ Assistant
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
GEMINI_API_KEY=your_key_here
CORS_ORIGINS_ENV=https://yourdomain.com,https://www.yourdomain.com
VECTORDB_PATH=/app/data/vectordb
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

