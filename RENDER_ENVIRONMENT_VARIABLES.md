# Render Environment Variables Configuration Guide

This guide explains how to configure environment variables for deploying the FAQ Assistant to Render.com.

## Overview

Environment variables are configured in two ways:
1. **Via render.yaml** - For Blueprint deployments (recommended)
2. **Via Render Dashboard** - For manual service configuration

## Frontend Environment Variables

### VITE_API_BASE_URL (Required)

**Purpose**: Sets the backend API URL that the frontend will use to communicate with the backend service.

**Value Format**: `https://your-backend-service.onrender.com`

**How to Set**:

#### Option 1: Using render.yaml (Recommended)

The `render.yaml` file already includes this variable with a placeholder:

```yaml
envVars:
  - key: VITE_API_BASE_URL
    value: https://faq-assistant-backend.onrender.com
```

**Important**: After deploying the backend service, update this value with the actual backend URL from Render.

**Steps**:
1. Deploy backend service first
2. Copy the backend service URL from Render dashboard (e.g., `https://faq-assistant-backend-xyz.onrender.com`)
3. Update `render.yaml` with the actual URL
4. Commit and push changes
5. Redeploy frontend service

#### Option 2: Using Render Dashboard

1. Go to your Render dashboard
2. Select the **frontend service** (`faq-assistant-frontend`)
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Set:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend-service.onrender.com`
6. Click **Save Changes**
7. Render will automatically rebuild the service

**Note**: Since `VITE_` prefixed variables are injected at build time, the service will rebuild automatically when you save the environment variable.

### Example Values

```bash
# Development (local)
VITE_API_BASE_URL=http://localhost:8000

# Production (Render)
VITE_API_BASE_URL=https://faq-assistant-backend-xyz.onrender.com
```

## Backend Environment Variables

### Required Variables

#### GEMINI_API_KEY (Required)

**Purpose**: Google Gemini API key for LLM functionality.

**How to Set**:
1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. In Render dashboard → Backend service → Environment tab
3. Add environment variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: Your API key (keep it secret!)
   - **Mark as Secret**: ✅ (recommended)

**Note**: In `render.yaml`, this is marked as `sync: false`, meaning you must set it manually in the dashboard.

### Application Configuration

These are already set in `render.yaml` but can be overridden:

#### ENVIRONMENT
- **Default**: `production`
- **Purpose**: Sets the application environment

#### DEBUG
- **Default**: `false`
- **Purpose**: Enables/disables debug mode

#### LOG_LEVEL
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- **Purpose**: Sets logging verbosity

### CORS Configuration

#### CORS_ORIGINS

**Purpose**: Allowed CORS origins for API requests.

**Value Format**: Comma-separated URLs or single URL

**Example**:
```bash
CORS_ORIGINS=https://faq-assistant-frontend.onrender.com,https://your-custom-domain.com
```

**Important**: Update this after frontend deployment with the actual frontend URL.

**How to Update**:
1. Deploy frontend service
2. Copy frontend URL from Render dashboard
3. Update `CORS_ORIGINS` in backend service environment variables
4. Service will restart automatically

### LLM Configuration (Optional)

These have defaults in `render.yaml` but can be customized:

#### LLM_PROVIDER
- **Default**: `gemini`
- **Purpose**: LLM provider name

#### LLM_MODEL
- **Default**: `gemini-pro`
- **Purpose**: Model name to use

#### LLM_TEMPERATURE
- **Default**: `0.1`
- **Purpose**: Model temperature (0.0-1.0)

#### LLM_MAX_TOKENS
- **Default**: `500`
- **Purpose**: Maximum tokens in response

### RAG Configuration (Optional)

#### RAG_TOP_K
- **Default**: `5`
- **Purpose**: Number of top documents to retrieve

#### RAG_SIMILARITY_THRESHOLD
- **Default**: `0.5`
- **Purpose**: Minimum similarity score for retrieval

### Rate Limiting (Optional)

#### RATE_LIMIT_ENABLED
- **Default**: `true`
- **Purpose**: Enable/disable rate limiting

#### RATE_LIMIT_PER_MINUTE
- **Default**: `60`
- **Purpose**: Requests allowed per minute per IP

#### RATE_LIMIT_PER_HOUR
- **Default**: `1000`
- **Purpose**: Requests allowed per hour per IP

## Deployment Order

To ensure proper configuration:

1. **Deploy Backend First**:
   - Set `GEMINI_API_KEY` (required)
   - Other variables are set via `render.yaml`
   - Note the backend service URL

2. **Update Frontend Configuration**:
   - Update `VITE_API_BASE_URL` in `render.yaml` with backend URL
   - Or set it in Render dashboard
   - Deploy frontend service

3. **Update Backend CORS**:
   - Update `CORS_ORIGINS` in backend with frontend URL
   - Service will restart automatically

## Environment Variable Priority

Render uses the following priority (highest to lowest):
1. Environment variables set in Render dashboard
2. Environment variables in `render.yaml`
3. Default values in application code

## Security Best Practices

1. **Never commit secrets**:
   - `GEMINI_API_KEY` should never be in `render.yaml` or git
   - Use Render's secret environment variables

2. **Use Render Secrets**:
   - Mark sensitive variables as "Secret" in Render dashboard
   - They will be encrypted and hidden from logs

3. **Rotate Keys Regularly**:
   - Update API keys periodically
   - Update in Render dashboard, service restarts automatically

## Troubleshooting

### Frontend Can't Connect to Backend

**Symptoms**: Network errors, CORS errors, 404 errors

**Solutions**:
1. Verify `VITE_API_BASE_URL` is set correctly
2. Check backend URL is accessible (visit `/health` endpoint)
3. Verify CORS_ORIGINS includes frontend URL
4. Check browser console for specific errors

### Environment Variables Not Working

**Symptoms**: Variables not being used, defaults being used instead

**Solutions**:
1. Verify variable names are correct (case-sensitive)
2. For frontend: Ensure `VITE_` prefix is present
3. Check service logs for environment variable values
4. Rebuild service after adding variables

### Build-Time vs Runtime Variables

**Frontend (`VITE_` prefixed)**:
- Injected at **build time**
- Must be set before building Docker image
- Set in `render.yaml` or Render dashboard before deployment

**Backend**:
- Available at **runtime**
- Can be updated without rebuilding
- Changes require service restart

## Quick Reference

### Frontend Variables
```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### Backend Required Variables
```bash
GEMINI_API_KEY=your_api_key_here
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend.onrender.com
```

### Backend Optional Variables
```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=500
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.5
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## Additional Resources

- [Render Environment Variables Documentation](https://render.com/docs/environment-variables)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)

