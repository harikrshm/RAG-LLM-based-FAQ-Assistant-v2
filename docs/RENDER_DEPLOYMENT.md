# Render Deployment Guide

Complete step-by-step guide for deploying the FAQ Assistant chatbot to Render.com using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Methods](#deployment-methods)
5. [Step-by-Step Deployment](#step-by-step-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Testing and Verification](#testing-and-verification)
8. [Troubleshooting](#troubleshooting)
9. [Render-Specific Considerations](#render-specific-considerations)
10. [Maintenance and Updates](#maintenance-and-updates)

## Prerequisites

Before deploying, ensure you have:

- ✅ **Render.com account** - Sign up at [render.com](https://render.com)
- ✅ **GitHub account** - Repository must be on GitHub
- ✅ **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- ✅ **Repository access** - Code pushed to GitHub repository
- ✅ **Required files** - `render.yaml`, `Dockerfile.backend`, `Dockerfile.frontend` present

## Architecture Overview

```
┌─────────────────────────────────────┐
│         Render Platform             │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   Frontend   │  │   Backend   │ │
│  │  (Docker)    │  │  (Docker)   │ │
│  │              │  │             │ │
│  │  Nginx       │  │  FastAPI    │ │
│  │  Port 80     │  │  Port $PORT │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │                 │        │
│         └────────┬────────┘        │
│                  │                 │
│         HTTPS (Auto-provisioned)   │
└─────────────────────────────────────┘
```

**Services**:
- **Backend**: FastAPI application running in Docker container
- **Frontend**: React/Vite application served by Nginx in Docker container
- **Communication**: Frontend → Backend via HTTPS API calls

## Pre-Deployment Checklist

Before deploying, verify:

- [ ] `render.yaml` exists and is configured correctly
- [ ] `Dockerfile.backend` uses `$PORT` environment variable
- [ ] `Dockerfile.frontend` accepts `VITE_API_BASE_URL` build argument
- [ ] All code is committed and pushed to GitHub
- [ ] Google Gemini API key is ready
- [ ] Repository is connected to GitHub

## Deployment Methods

### Method 1: Blueprint Deployment (Recommended)

Uses `render.yaml` to deploy both services automatically.

**Advantages**:
- Single configuration file
- Automatic service creation
- Environment variables pre-configured
- Easier to manage

### Method 2: Manual Service Creation

Create services individually in Render dashboard.

**Advantages**:
- More control over each service
- Better for learning Render UI
- Useful for troubleshooting

**We'll use Method 1 (Blueprint) for this guide.**

## Step-by-Step Deployment

### Step 1: Prepare Repository

1. **Verify files are present**:
   ```bash
   # Check required files exist
   ls render.yaml
   ls Dockerfile.backend
   ls Dockerfile.frontend
   ```

2. **Commit and push to GitHub**:
   ```bash
   git add render.yaml Dockerfile.backend Dockerfile.frontend
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

### Step 2: Connect Repository to Render

1. **Sign in to Render**:
   - Go to [render.com](https://render.com)
   - Sign in or create account

2. **Create New Blueprint**:
   - Click **"New +"** → **"Blueprint"**
   - Or go to [dashboard.render.com/new/blueprint](https://dashboard.render.com/new/blueprint)

3. **Connect GitHub Repository**:
   - Click **"Connect GitHub"** or **"Connect Repository"**
   - Authorize Render to access your repositories
   - Select your repository: `RAG-LLM-based-FAQ-Assistant-v2`
   - Select branch: `main` (or your deployment branch)

4. **Render will detect `render.yaml`**:
   - Render automatically detects the Blueprint file
   - Shows preview of services to be created

### Step 3: Configure Environment Variables

Before deploying, set the required secret:

1. **Set GEMINI_API_KEY**:
   - In the Blueprint preview, find the backend service
   - Click on **Environment Variables**
   - Find `GEMINI_API_KEY` (marked as `sync: false`)
   - Click **"Set Value"** or **"Add"**
   - Enter your Google Gemini API key
   - Mark as **"Secret"** (recommended)
   - Click **"Save"**

2. **Review other variables**:
   - Other variables are pre-configured in `render.yaml`
   - You can override them here if needed

### Step 4: Deploy Services

1. **Review Blueprint**:
   - Check service names: `faq-assistant-backend` and `faq-assistant-frontend`
   - Verify Dockerfile paths are correct
   - Review plan (Free tier)

2. **Apply Blueprint**:
   - Click **"Apply"** or **"Deploy"**
   - Render will create both services
   - Deployment starts automatically

3. **Monitor Deployment**:
   - Watch build logs in real-time
   - Backend builds first (Docker image)
   - Frontend builds after backend
   - Each service shows build progress

### Step 5: Wait for Backend Deployment

1. **Backend Build Process**:
   - Docker image builds from `Dockerfile.backend`
   - Python dependencies install
   - Container starts
   - Health check runs at `/health`

2. **Verify Backend is Running**:
   - Wait for status: **"Live"** (green)
   - Note the backend URL (e.g., `https://faq-assistant-backend-xyz.onrender.com`)
   - Test health endpoint: `https://your-backend-url.onrender.com/health`

3. **Check Logs**:
   - Click on backend service
   - Go to **"Logs"** tab
   - Verify no errors
   - Check for "Application startup complete" message

### Step 6: Update Frontend Configuration

After backend is deployed:

1. **Get Backend URL**:
   - Copy backend service URL from Render dashboard
   - Format: `https://faq-assistant-backend-xyz.onrender.com`

2. **Update Frontend Environment Variable**:
   - Go to frontend service in Render dashboard
   - Navigate to **"Environment"** tab
   - Find `VITE_API_BASE_URL`
   - Update value with actual backend URL
   - Click **"Save Changes"**

3. **Frontend Rebuilds Automatically**:
   - Render detects environment variable change
   - Triggers automatic rebuild
   - New build includes updated API URL

### Step 7: Update Backend CORS Configuration

After frontend is deployed:

1. **Get Frontend URL**:
   - Copy frontend service URL from Render dashboard
   - Format: `https://faq-assistant-frontend-xyz.onrender.com`

2. **Update Backend CORS**:
   - Go to backend service in Render dashboard
   - Navigate to **"Environment"** tab
   - Find `CORS_ORIGINS`
   - Update value with frontend URL
   - Click **"Save Changes"**

3. **Backend Restarts Automatically**:
   - Service restarts with new CORS configuration
   - Takes ~30 seconds

## Post-Deployment Configuration

### Verify Service URLs

Both services should now be live:

- **Backend**: `https://faq-assistant-backend-xyz.onrender.com`
- **Frontend**: `https://faq-assistant-frontend-xyz.onrender.com`

### Update render.yaml (Optional)

For future deployments, update `render.yaml` with actual URLs:

```yaml
envVars:
  - key: CORS_ORIGINS
    value: https://faq-assistant-frontend-xyz.onrender.com  # Actual URL
  - key: VITE_API_BASE_URL
    value: https://faq-assistant-backend-xyz.onrender.com  # Actual URL
```

## Testing and Verification

### Test Backend

1. **Health Check**:
   ```bash
   curl https://your-backend.onrender.com/health
   ```
   Expected: `{"status": "healthy", ...}`

2. **API Documentation**:
   - Visit: `https://your-backend.onrender.com/docs`
   - Should show Swagger UI

3. **Test Chat Endpoint**:
   ```bash
   curl -X POST https://your-backend.onrender.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is expense ratio?", "sessionId": "test-123"}'
   ```

### Test Frontend

1. **Visit Frontend URL**:
   - Open: `https://your-frontend.onrender.com`
   - Should load without errors

2. **Check Browser Console**:
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Verify no CORS errors

3. **Test Chat Widget**:
   - Click chat widget (bottom-right)
   - Send a test message
   - Verify response appears
   - Check sources are displayed

### End-to-End Test

1. **Open Frontend**:
   - Visit frontend URL in browser

2. **Test Chat Flow**:
   - Open chat widget
   - Send query: "What is expense ratio?"
   - Verify:
     - ✅ Response appears
     - ✅ Sources are displayed
     - ✅ Links work correctly
     - ✅ No console errors

## Troubleshooting

### Backend Won't Start

**Symptoms**: Service shows "Failed" or keeps restarting

**Solutions**:
1. Check build logs for errors
2. Verify `GEMINI_API_KEY` is set correctly
3. Check Dockerfile.backend uses `$PORT` variable
4. Review runtime logs for Python errors
5. Verify health check endpoint exists (`/health`)

### Frontend Can't Connect to Backend

**Symptoms**: Network errors, CORS errors, 404 errors

**Solutions**:
1. Verify `VITE_API_BASE_URL` is set correctly
2. Check backend URL is accessible (test `/health`)
3. Verify `CORS_ORIGINS` includes frontend URL
4. Check browser console for specific errors
5. Ensure frontend was rebuilt after setting `VITE_API_BASE_URL`

### Build Failures

**Symptoms**: Docker build fails, service won't deploy

**Solutions**:
1. Check Dockerfile syntax
2. Verify all required files exist
3. Check build logs for specific errors
4. Test Docker builds locally:
   ```bash
   docker build -f Dockerfile.backend -t test-backend .
   docker build -f Dockerfile.frontend -t test-frontend .
   ```

### Environment Variables Not Working

**Symptoms**: Variables not being used, defaults being used

**Solutions**:
1. Verify variable names are correct (case-sensitive)
2. For frontend: Ensure `VITE_` prefix is present
3. Check service logs for environment variable values
4. Rebuild service after adding variables
5. For frontend: Variables must be set before build

### Services Keep Restarting

**Symptoms**: Service status shows restarting loop

**Solutions**:
1. Check health check endpoint is correct
2. Verify health check returns 200 OK
3. Check logs for application errors
4. Verify port configuration (`$PORT` variable)
5. Check resource limits (Free tier has limits)

## Render-Specific Considerations

### Ephemeral Storage

**Important**: Render's filesystem is ephemeral (resets on restart).

**Impact**:
- ChromaDB data will be lost on restart
- File uploads are not persistent
- Logs are not persisted

**Solutions**:
- Use external storage for vector database (Pinecone, external ChromaDB)
- Use Render Disk for persistent storage (paid plans)
- Rebuild vector database on startup (for small datasets)

### Port Configuration

- Render provides `$PORT` environment variable automatically
- Backend must listen on `$PORT` (not hardcoded)
- Frontend uses port 80 (standard for web services)
- Port is automatically configured by Render

### Health Checks

- Render automatically checks health endpoints
- Backend: `/health` endpoint (configured in `render.yaml`)
- Frontend: HTTP 200 on root path (`/`)
- Failed health checks cause service restart

### Auto-Deploy

- Render can auto-deploy on git push
- Configure in service settings → **"Auto-Deploy"**
- Useful for continuous deployment
- Deploys from selected branch (usually `main`)

### Free Tier Limitations

**Important Limitations**:
- Services spin down after 15 minutes of inactivity
- First request after spin-down has cold start delay (~30 seconds)
- Limited build minutes per month
- Limited bandwidth

**Upgrade Options**:
- **Starter Plan** ($7/month): Always-on services
- **Professional Plan** ($25/month): More resources

### Resource Limits

**Free Tier**:
- 512 MB RAM per service
- 0.5 CPU per service
- Limited build minutes

**Monitor Usage**:
- Check service metrics in Render dashboard
- Watch for memory/CPU spikes
- Upgrade if hitting limits

## Maintenance and Updates

### Updating Code

1. **Make Changes Locally**:
   ```bash
   # Make code changes
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Render Auto-Deploys**:
   - If auto-deploy is enabled, Render rebuilds automatically
   - Monitor deployment in dashboard

3. **Manual Deploy**:
   - Go to service in Render dashboard
   - Click **"Manual Deploy"**
   - Select branch/commit
   - Click **"Deploy"**

### Updating Environment Variables

1. **Via Dashboard**:
   - Go to service → **Environment** tab
   - Add/update variables
   - Click **"Save Changes"**
   - Service restarts automatically

2. **Via render.yaml**:
   - Update `render.yaml`
   - Commit and push
   - Render detects changes
   - Updates services automatically

### Monitoring

1. **View Logs**:
   - Service → **Logs** tab
   - Real-time log streaming
   - Search and filter logs

2. **View Metrics**:
   - Service → **Metrics** tab
   - CPU, memory, request metrics
   - Response times

3. **Set Up Alerts**:
   - Service → **Alerts** tab
   - Configure email/Slack notifications
   - Set thresholds for errors

### Backup and Recovery

**Data Backup**:
- Vector database: Use external storage (Pinecone)
- Configuration: Stored in `render.yaml` (version controlled)
- Environment variables: Export from dashboard

**Recovery**:
- Recreate services from `render.yaml`
- Restore environment variables
- Rebuild vector database if needed

## Quick Reference

### Service URLs

- **Backend**: `https://faq-assistant-backend-xyz.onrender.com`
- **Frontend**: `https://faq-assistant-frontend-xyz.onrender.com`
- **Backend Health**: `https://your-backend.onrender.com/health`
- **Backend Docs**: `https://your-backend.onrender.com/docs`

### Key Files

- `render.yaml` - Render Blueprint configuration
- `Dockerfile.backend` - Backend Docker configuration
- `Dockerfile.frontend` - Frontend Docker configuration
- `RENDER_ENVIRONMENT_VARIABLES.md` - Environment variables guide

### Common Commands

```bash
# Test backend locally
docker build -f Dockerfile.backend -t test-backend .
docker run -p 8000:8000 -e PORT=8000 test-backend

# Test frontend locally
docker build -f Dockerfile.frontend -t test-frontend .
docker run -p 80:80 test-frontend

# Check service health
curl https://your-backend.onrender.com/health
```

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Docker Guide](https://render.com/docs/docker)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Project Environment Variables Guide](../RENDER_ENVIRONMENT_VARIABLES.md)

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review Render service logs
3. Check [Render Status Page](https://status.render.com)
4. Consult [Render Community](https://community.render.com)
5. Review project documentation

---

**Last Updated**: Based on Render platform as of deployment date
**Deployment Method**: Docker + Render Blueprint
**Estimated Deployment Time**: 10-15 minutes

