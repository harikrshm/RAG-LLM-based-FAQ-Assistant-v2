# Vercel Full-Stack Deployment Guide

Complete guide for deploying both frontend and backend to Vercel as a unified full-stack application.

## Overview

This guide walks you through deploying the FAQ Assistant chatbot with:
- **Frontend**: React/Vite application deployed as static site
- **Backend**: FastAPI application deployed as serverless functions

Both components are deployed together on Vercel, simplifying deployment and reducing configuration overhead.

## Prerequisites

- Vercel account (sign up at https://vercel.com)
- GitHub account with repository access
- Google Gemini API key (get from https://makersuite.google.com/app/apikey)
- Node.js 20+ installed locally (for testing)
- Python 3.11+ installed locally (for testing)

## Architecture

```
┌─────────────────────────────────────┐
│         Vercel Platform             │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   Frontend   │  │   Backend   │ │
│  │  (Static)    │  │ (Serverless)│ │
│  │              │  │             │ │
│  │  React/Vite  │  │  FastAPI    │ │
│  │  /frontend   │  │  /api/*     │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

## Step 1: Prepare Repository

Ensure your repository has the following structure:

```
project-root/
├── api/
│   └── index.py          # Vercel serverless function entry point
├── backend/              # Backend FastAPI code
├── frontend/             # Frontend React/Vite code
├── requirements.txt      # Python dependencies (at root)
├── vercel.json          # Vercel configuration
└── .vercelignore        # Files to exclude from deployment
```

## Step 2: Configure Vercel Project

### 2.1 Connect Repository to Vercel

1. Go to https://vercel.com and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the project settings

### 2.2 Configure Build Settings

In Vercel dashboard → Project Settings → General:

**Root Directory**: Leave empty (or set to project root)

**Build Command**: `cd frontend && npm install && npm run build`

**Output Directory**: `frontend/dist`

**Install Command**: `cd frontend && npm install`

**Framework Preset**: Vite (auto-detected)

### 2.3 Configure Python Runtime

Vercel will automatically detect Python from `requirements.txt` at the root.

The `vercel.json` configures:
- Python runtime version (3.9+)
- API routes mapping (`/api/*` → `/api/index.py`)

## Step 3: Set Environment Variables

Go to Project Settings → Environment Variables and add:

### Required Variables

```bash
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS (Vercel automatically adds its domains, but you can add custom domains)
CORS_ORIGINS_ENV=https://your-custom-domain.com
```

### Optional Variables

```bash
# LLM Provider Settings
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=500

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.5

# Vector Database Paths (for serverless, use /tmp or external storage)
VECTORDB_PATH=/tmp/vectordb
METADATA_PATH=/tmp/metadata_index.json
SOURCE_URLS_PATH=/tmp/source_urls.json

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

**Important Notes:**
- Set variables for **Production**, **Preview**, and **Development** environments
- Variables starting with `VITE_` are exposed to frontend
- Other variables are only available to backend/serverless functions

## Step 4: Deploy

### 4.1 Initial Deployment

1. Click "Deploy" button in Vercel dashboard
2. Vercel will:
   - Install frontend dependencies (`npm install`)
   - Build frontend (`npm run build`)
   - Install Python dependencies (`pip install -r requirements.txt`)
   - Deploy frontend as static site
   - Deploy backend as serverless functions
3. Wait for deployment to complete (2-5 minutes)
4. You'll get URLs:
   - Frontend: `https://your-project.vercel.app`
   - Backend API: `https://your-project.vercel.app/api`

### 4.2 Automatic Deployments

After initial deployment:
- **Production**: Auto-deploys on push to `main`/`master` branch
- **Preview**: Auto-deploys on pull requests
- **Manual**: Deploy from Vercel dashboard

## Step 5: Configure Frontend API URL

Since both frontend and backend are on the same domain, update frontend configuration:

### Option 1: Use Relative URLs (Recommended)

Update `frontend/src/services/apiClient.ts` or `frontend/src/App.tsx`:

```typescript
// Use relative URL for same-domain deployment
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
```

### Option 2: Set Environment Variable

In Vercel dashboard → Environment Variables:

```bash
VITE_API_BASE_URL=https://your-project.vercel.app/api
```

## Step 6: Verify Deployment

### 6.1 Test Backend API

1. **Health Check**:
   ```
   https://your-project.vercel.app/api/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **API Documentation**:
   ```
   https://your-project.vercel.app/api/docs
   ```
   Should show Swagger UI

3. **Test Chat Endpoint**:
   ```bash
   curl -X POST https://your-project.vercel.app/api/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is expense ratio?", "sessionId": "test-123"}'
   ```

### 6.2 Test Frontend

1. Visit: `https://your-project.vercel.app`
2. Open browser console (F12)
3. Check for errors
4. Test chat widget:
   - Click chat widget
   - Send a test message
   - Verify response appears

### 6.3 Test End-to-End Flow

1. Open chat widget
2. Send query: "What is expense ratio?"
3. Verify:
   - Response appears
   - Sources are displayed
   - Links work correctly
   - No console errors

## Step 7: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records:
   - Add CNAME record: `your-domain.com` → `cname.vercel-dns.com`
   - Or add A record for apex domain
4. Vercel automatically provisions SSL certificate
5. Update `CORS_ORIGINS_ENV` environment variable with your domain

## File Structure Explained

### `api/index.py`

Vercel serverless function entry point that:
- Imports FastAPI app from `backend/main.py`
- Uses Mangum adapter to convert ASGI app to Lambda handler
- Handles all `/api/*` routes

### `vercel.json`

Configuration file that:
- Sets build commands for frontend
- Configures Python runtime for serverless functions
- Maps `/api/*` routes to serverless function
- Sets up SPA routing rewrites
- Configures cache headers

### `requirements.txt`

Python dependencies at project root:
- Required by Vercel to detect Python project
- Includes all backend dependencies
- Includes `mangum` for ASGI adapter

## Serverless Function Considerations

### Cold Starts

- First request after inactivity may be slower (cold start)
- Subsequent requests are fast (warm function)
- Consider using Vercel Pro plan for better performance

### Stateless Functions

- Serverless functions are stateless
- Don't rely on in-memory state between requests
- Use external storage for:
  - Vector database (consider external ChromaDB or Pinecone)
  - Session data (if needed)
  - File uploads (use Vercel Blob or external storage)

### Function Timeout

- Vercel Free: 10 seconds
- Vercel Pro: 60 seconds
- Ensure your API responses complete within timeout

### Memory Limits

- Vercel Free: 1024 MB
- Vercel Pro: 3008 MB
- Monitor function memory usage

## Vector Database Options

Since serverless functions are stateless, consider:

### Option 1: External ChromaDB

Deploy ChromaDB separately (Railway, Render, etc.) and connect via API.

### Option 2: Pinecone (Recommended)

Use Pinecone as managed vector database:
1. Sign up at https://pinecone.io
2. Create index
3. Update `backend/services/vector_store.py` to use Pinecone
4. Set `PINECONE_API_KEY` environment variable

### Option 3: Vercel Blob Storage

For small datasets, use Vercel Blob Storage:
1. Install `@vercel/blob`
2. Store embeddings in Blob Storage
3. Load on function invocation

## Monitoring and Logs

### View Logs

1. Go to Vercel dashboard → Your project → Deployments
2. Click on deployment → View Function Logs
3. Check both:
   - Build logs
   - Runtime logs (serverless function logs)

### Function Metrics

Vercel dashboard shows:
- Function invocations
- Function duration
- Error rate
- Memory usage

### Error Tracking

Consider integrating:
- Sentry for error tracking
- Vercel Analytics for performance
- Custom logging to external service

## Troubleshooting

### Build Fails

**Issue**: Frontend build fails
- Check build logs in Vercel dashboard
- Verify Node.js version (Vercel uses Node 20)
- Test build locally: `cd frontend && npm run build`

**Issue**: Python dependencies fail to install
- Check `requirements.txt` syntax
- Verify Python version (Vercel uses Python 3.9+)
- Check for conflicting dependencies

### API Routes Not Working

**Issue**: `/api/*` routes return 404
- Verify `vercel.json` has correct rewrites
- Check `api/index.py` exists and is valid
- Verify Python runtime is configured

**Issue**: Function timeout
- Check function logs for slow operations
- Optimize database queries
- Consider increasing timeout (Vercel Pro)

### CORS Errors

**Issue**: Frontend can't call backend API
- Verify `CORS_ORIGINS_ENV` includes Vercel domain
- Check backend CORS configuration
- Ensure frontend uses correct API URL

### Environment Variables Not Working

**Issue**: Variables not available in functions
- Verify variables are set for correct environment
- Rebuild after adding variables
- Check variable names (case-sensitive)
- Frontend variables must start with `VITE_`

## Performance Optimization

### Frontend

- Enable Vercel's automatic image optimization
- Use code splitting
- Enable compression (automatic)
- Use CDN caching (automatic)

### Backend

- Optimize database queries
- Cache frequently accessed data
- Use connection pooling for external databases
- Minimize cold starts (keep functions warm)

## Cost Estimation

### Vercel Free Tier

- **Frontend**: Unlimited deployments, 100GB bandwidth/month
- **Serverless Functions**: 100GB-hours/month
- **Suitable for**: Development, small projects, demos

### Vercel Pro ($20/month)

- **Frontend**: Unlimited deployments, 1TB bandwidth/month
- **Serverless Functions**: 1000GB-hours/month
- **Function Timeout**: 60 seconds (vs 10 seconds)
- **Suitable for**: Production applications

## Security Best Practices

1. **Never commit `.env` files** - Use Vercel environment variables
2. **Use Vercel secrets** - For sensitive API keys
3. **Enable HTTPS** - Automatic with Vercel
4. **Set CORS properly** - Only allow trusted domains
5. **Use rate limiting** - Already configured in backend
6. **Monitor logs** - Watch for suspicious activity
7. **Keep dependencies updated** - Regular security updates

## Next Steps

1. **Set up monitoring** - Integrate error tracking
2. **Configure custom domain** - Use your own domain
3. **Set up CI/CD** - Automated testing and deployment
4. **Optimize performance** - Monitor and improve
5. **Scale as needed** - Upgrade plan if required

## Support

- Vercel Documentation: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- FastAPI Documentation: https://fastapi.tiangolo.com
- Project Issues: Create issue in repository

## Quick Reference

### URLs

- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://your-project.vercel.app/api`
- **Health Check**: `https://your-project.vercel.app/api/health`
- **API Docs**: `https://your-project.vercel.app/api/docs`

### Key Files

- `api/index.py` - Serverless function entry point
- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `backend/main.py` - FastAPI application
- `frontend/` - React/Vite frontend

### Environment Variables

- `GEMINI_API_KEY` - Required
- `VITE_API_BASE_URL` - Frontend API URL (optional, can use relative)
- `CORS_ORIGINS_ENV` - Allowed CORS origins
- Other backend variables as needed

