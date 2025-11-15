# Render Deployment Plan - Phase 2 Option C: Docker + Cloud Platform

## Overview

Deploy both frontend and backend to Render.com using Docker containers. Render supports Docker deployments natively and can host both services with automatic HTTPS, health checks, and environment variable management.

## Architecture

```
┌─────────────────────────────────────┐
│         Render Platform             │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   Frontend   │  │   Backend   │ │
│  │  (Docker)    │  │  (Docker)   │ │
│  │              │  │             │ │
│  │  Nginx       │  │  FastAPI    │ │
│  │  Port 80     │  │  Port 8000  │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │                 │        │
│         └────────┬────────┘        │
│                  │                 │
│         HTTPS (Auto-provisioned)   │
└─────────────────────────────────────┘
```

## Prerequisites

- Render.com account (sign up at https://render.com)
- GitHub repository access
- Google Gemini API key
- Docker files already exist (Dockerfile.backend, Dockerfile.frontend)

## Deployment Strategy

### Option 1: Using render.yaml (Recommended)
- Single configuration file for both services
- Automatic service discovery
- Easier to manage

### Option 2: Manual Service Creation
- Create services individually in Render dashboard
- More control over each service
- Better for learning Render UI

**We'll use Option 1 (render.yaml) for consistency and automation.**

## Tasks Breakdown

### Task 1: Create Render Configuration File
**Objective**: Create `render.yaml` to define both frontend and backend services

**Subtasks**:
1.1. Create `render.yaml` with backend service configuration
1.2. Add frontend service configuration to `render.yaml`
1.3. Configure service dependencies and networking
1.4. Add health check configurations
1.5. Set up environment variable placeholders

**Files to create**:
- `render.yaml` - Render service configuration

**Configuration Details**:
- Backend: Docker service, port 8000, health check endpoint
- Frontend: Docker service, port 80, depends on backend
- Environment variables: GEMINI_API_KEY, CORS_ORIGINS, etc.

### Task 2: Update Dockerfiles for Render Compatibility
**Objective**: Ensure Dockerfiles work optimally with Render's environment

**Subtasks**:
2.1. Review Dockerfile.backend for Render compatibility
2.2. Update backend Dockerfile to use PORT environment variable (Render provides this)
2.3. Review Dockerfile.frontend for Render compatibility
2.4. Ensure frontend Dockerfile builds correctly for production
2.5. Test Docker builds locally (optional but recommended)

**Files to modify**:
- `Dockerfile.backend` - Update CMD to use $PORT variable
- `Dockerfile.frontend` - Verify no changes needed

**Key Changes**:
- Backend: Change from hardcoded port 8000 to `$PORT` (Render provides this)
- Frontend: Should work as-is (uses port 80)

### Task 3: Update Frontend Configuration for Render
**Objective**: Configure frontend to connect to Render backend URL

**Subtasks**:
3.1. Review current API base URL configuration in frontend
3.2. Update frontend to use environment variable for backend URL
3.3. Create documentation for setting VITE_API_BASE_URL in Render
3.4. Ensure build-time environment variable injection works

**Files to review/modify**:
- `frontend/src/App.tsx` - Already uses VITE_API_BASE_URL (good!)
- `frontend/vite.config.ts` - Verify environment variable handling
- `Dockerfile.frontend` - May need to pass build args

**Configuration**:
- Frontend will use `VITE_API_BASE_URL` environment variable
- Set in Render dashboard: `VITE_API_BASE_URL=https://your-backend-service.onrender.com`

### Task 4: Create Deployment Documentation
**Objective**: Create comprehensive guide for deploying to Render

**Subtasks**:
4.1. Create step-by-step deployment guide
4.2. Document environment variables needed
4.3. Create troubleshooting guide
4.4. Document Render-specific considerations (persistent storage, etc.)

**Files to create**:
- `docs/RENDER_DEPLOYMENT.md` - Complete deployment guide
- `RENDER_ENVIRONMENT_VARIABLES.md` - Environment variables reference

**Documentation Sections**:
- Prerequisites
- Step-by-step deployment instructions
- Environment variables setup
- Testing and verification
- Troubleshooting common issues
- Render-specific considerations (ephemeral storage, etc.)

### Task 5: Prepare for Deployment
**Objective**: Final preparations before deploying to Render

**Subtasks**:
5.1. Create .dockerignore files if needed
5.2. Verify all required files are present
5.3. Create deployment checklist
5.4. Commit all changes to repository

**Files to create/verify**:
- `.dockerignore` - Exclude unnecessary files from Docker builds
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist

**Pre-deployment Checklist**:
- [ ] render.yaml created and validated
- [ ] Dockerfiles updated for Render
- [ ] Environment variables documented
- [ ] Frontend configured for Render backend URL
- [ ] All changes committed to repository
- [ ] GitHub repository connected to Render

### Task 6: Deploy to Render
**Objective**: Deploy both services to Render platform

**Subtasks**:
6.1. Connect GitHub repository to Render
6.2. Create new Blueprint (if using render.yaml) or create services manually
6.3. Configure backend service:
   - Set Dockerfile path: `Dockerfile.backend`
   - Set root directory: `.` (project root)
   - Configure environment variables
   - Set health check path: `/health`
6.4. Configure frontend service:
   - Set Dockerfile path: `Dockerfile.frontend`
   - Set root directory: `.` (project root)
   - Set VITE_API_BASE_URL to backend URL
   - Configure build settings
6.5. Deploy backend service first
6.6. Wait for backend to be healthy
6.7. Deploy frontend service
6.8. Verify both services are running

**Render Dashboard Steps**:
1. New → Blueprint (if using render.yaml) OR New → Web Service
2. Connect GitHub repository
3. Select branch (main)
4. Configure service settings
5. Add environment variables
6. Deploy

### Task 7: Post-Deployment Verification
**Objective**: Verify deployment is working correctly

**Subtasks**:
7.1. Test backend health endpoint
7.2. Test backend API endpoints
7.3. Test frontend accessibility
7.4. Test frontend-backend communication
7.5. Verify CORS configuration
7.6. Test chat widget functionality
7.7. Check logs for errors

**Test URLs**:
- Backend Health: `https://your-backend.onrender.com/health`
- Backend API Docs: `https://your-backend.onrender.com/docs`
- Frontend: `https://your-frontend.onrender.com`

## Environment Variables

### Backend Service (Required)
```
GEMINI_API_KEY=your_gemini_api_key
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend.onrender.com
```

### Backend Service (Optional)
```
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

### Frontend Service (Required)
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

## Render-Specific Considerations

### Ephemeral Storage
- Render's filesystem is ephemeral (resets on restart)
- ChromaDB data will be lost on restart
- **Solution**: Use external storage or rebuild vector DB on startup
- For production: Consider external ChromaDB or Pinecone

### Port Configuration
- Render provides `$PORT` environment variable
- Backend must listen on `$PORT` (not hardcoded 8000)
- Frontend uses port 80 (standard for web)

### Health Checks
- Render automatically checks health endpoints
- Backend: `/health` endpoint
- Frontend: HTTP 200 on root path

### Auto-Deploy
- Render can auto-deploy on git push
- Configure in service settings
- Useful for continuous deployment

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down has cold start delay
- Upgrade to paid plan for always-on services

## Success Criteria

- [ ] Backend service deployed and accessible
- [ ] Frontend service deployed and accessible
- [ ] Backend health check returns 200 OK
- [ ] Frontend can communicate with backend
- [ ] No CORS errors in browser console
- [ ] Chat widget loads and functions correctly
- [ ] API endpoints respond correctly
- [ ] Environment variables configured correctly

## Rollback Plan

If deployment fails:
1. Check Render build logs
2. Check Render runtime logs
3. Verify environment variables
4. Test Docker builds locally
5. Review Dockerfile configurations
6. Check service health endpoints

## Next Steps After Deployment

1. Set up custom domains (optional)
2. Configure monitoring and alerts
3. Set up external vector database (if needed)
4. Configure backup strategy for data
5. Set up CI/CD for automatic deployments
6. Monitor performance and optimize

## Estimated Time

- Task 1: 15 minutes
- Task 2: 20 minutes
- Task 3: 10 minutes
- Task 4: 30 minutes
- Task 5: 10 minutes
- Task 6: 30 minutes (deployment time)
- Task 7: 15 minutes

**Total**: ~2 hours

## Files Reference

**Existing Files**:
- `Dockerfile.backend` - Backend Docker configuration
- `Dockerfile.frontend` - Frontend Docker configuration
- `docker-compose.yml` - Local Docker Compose (reference)
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies

**Files to Create**:
- `render.yaml` - Render service configuration
- `docs/RENDER_DEPLOYMENT.md` - Deployment guide
- `RENDER_ENVIRONMENT_VARIABLES.md` - Environment variables reference
- `.dockerignore` - Docker ignore file
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist

**Files to Modify**:
- `Dockerfile.backend` - Update to use $PORT variable
- `frontend/src/App.tsx` - Verify environment variable usage (should be OK)

