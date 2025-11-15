# Render Deployment Checklist

Pre-deployment checklist for deploying FAQ Assistant to Render.com.

## Pre-Deployment Checklist

### Repository Setup

- [ ] Code is committed to GitHub repository
- [ ] All changes are pushed to `main` branch (or deployment branch)
- [ ] Repository is accessible from Render.com
- [ ] No sensitive data (API keys, passwords) in code or commits

### Required Files

- [ ] `render.yaml` exists and is configured correctly
- [ ] `Dockerfile.backend` exists and uses `$PORT` variable
- [ ] `Dockerfile.frontend` exists and accepts `VITE_API_BASE_URL`
- [ ] `.dockerignore` exists (optional but recommended)
- [ ] `requirements.txt` exists at project root (for backend)
- [ ] `backend/requirements.txt` exists (for backend dependencies)
- [ ] `frontend/package.json` exists (for frontend dependencies)

### Configuration Files Review

- [ ] `render.yaml`:
  - [ ] Backend service configured (`faq-assistant-backend`)
  - [ ] Frontend service configured (`faq-assistant-frontend`)
  - [ ] Health check paths set correctly (`/health` for backend, `/` for frontend)
  - [ ] Environment variables defined (except secrets)
  - [ ] Dockerfile paths are correct (`./Dockerfile.backend`, `./Dockerfile.frontend`)

- [ ] `Dockerfile.backend`:
  - [ ] Uses `$PORT` environment variable (not hardcoded 8000)
  - [ ] Health check uses `${PORT:-8000}` with fallback
  - [ ] Copies `backend/requirements.txt` correctly
  - [ ] Copies `backend/` directory correctly

- [ ] `Dockerfile.frontend`:
  - [ ] Accepts `VITE_API_BASE_URL` as build argument (`ARG`)
  - [ ] Sets `ENV VITE_API_BASE_URL` for build
  - [ ] Multi-stage build (Node builder → Nginx production)
  - [ ] Nginx configuration includes SPA routing

### Environment Variables

- [ ] **GEMINI_API_KEY** ready (get from Google AI Studio)
- [ ] **VITE_API_BASE_URL** placeholder set (will update after backend deployment)
- [ ] **CORS_ORIGINS** placeholder set (will update after frontend deployment)
- [ ] Other environment variables have default values in `render.yaml`

### Testing (Optional but Recommended)

- [ ] Backend Dockerfile builds locally:
  ```bash
  docker build -f Dockerfile.backend -t test-backend .
  ```
- [ ] Frontend Dockerfile builds locally:
  ```bash
  docker build -f Dockerfile.frontend -t test-frontend .
  ```
- [ ] Backend container runs locally:
  ```bash
  docker run -p 8000:8000 -e PORT=8000 -e GEMINI_API_KEY=test test-backend
  ```
- [ ] Frontend container runs locally:
  ```bash
  docker run -p 80:80 -e VITE_API_BASE_URL=http://localhost:8000 test-frontend
  ```

## Deployment Steps Checklist

### Step 1: Connect Repository to Render

- [ ] Sign in to Render.com
- [ ] Create new Blueprint
- [ ] Connect GitHub repository
- [ ] Select correct branch (`main`)
- [ ] Render detects `render.yaml`

### Step 2: Configure Secrets

- [ ] Set `GEMINI_API_KEY` in backend service:
  - [ ] Go to backend service → Environment tab
  - [ ] Add `GEMINI_API_KEY` environment variable
  - [ ] Enter API key value
  - [ ] Mark as "Secret" (recommended)
  - [ ] Save changes

### Step 3: Deploy Backend

- [ ] Apply Blueprint (creates both services)
- [ ] Monitor backend build logs
- [ ] Verify backend builds successfully
- [ ] Wait for backend to be "Live" (green status)
- [ ] Test backend health endpoint:
  ```bash
  curl https://your-backend.onrender.com/health
  ```
- [ ] Copy backend URL for next step

### Step 4: Configure Frontend

- [ ] Update `VITE_API_BASE_URL` in frontend service:
  - [ ] Go to frontend service → Environment tab
  - [ ] Find `VITE_API_BASE_URL`
  - [ ] Update with actual backend URL
  - [ ] Save changes (triggers rebuild)
- [ ] Monitor frontend build logs
- [ ] Verify frontend builds successfully
- [ ] Wait for frontend to be "Live"

### Step 5: Update Backend CORS

- [ ] Copy frontend URL
- [ ] Update `CORS_ORIGINS` in backend service:
  - [ ] Go to backend service → Environment tab
  - [ ] Find `CORS_ORIGINS`
  - [ ] Update with frontend URL
  - [ ] Save changes (triggers restart)

### Step 6: Verify Deployment

- [ ] Backend health check:
  - [ ] Visit: `https://your-backend.onrender.com/health`
  - [ ] Should return: `{"status": "healthy", ...}`
- [ ] Backend API docs:
  - [ ] Visit: `https://your-backend.onrender.com/docs`
  - [ ] Should show Swagger UI
- [ ] Frontend loads:
  - [ ] Visit: `https://your-frontend.onrender.com`
  - [ ] Should load without errors
- [ ] Browser console:
  - [ ] Open DevTools (F12)
  - [ ] Check Console tab
  - [ ] No CORS errors
  - [ ] No network errors
- [ ] Chat widget:
  - [ ] Click chat widget
  - [ ] Send test message
  - [ ] Verify response appears
  - [ ] Verify sources are displayed

## Post-Deployment Checklist

### Service URLs

- [ ] Backend URL noted: `https://________________.onrender.com`
- [ ] Frontend URL noted: `https://________________.onrender.com`
- [ ] URLs saved for future reference

### Documentation Update

- [ ] Update `render.yaml` with actual URLs (optional):
  - [ ] Update `CORS_ORIGINS` with frontend URL
  - [ ] Update `VITE_API_BASE_URL` with backend URL
- [ ] Commit updated `render.yaml` (optional)

### Monitoring Setup

- [ ] Check service logs for errors
- [ ] Verify service metrics (CPU, memory)
- [ ] Set up alerts (optional):
  - [ ] Service → Alerts tab
  - [ ] Configure email/Slack notifications

### Testing

- [ ] Test chat functionality:
  - [ ] Send multiple queries
  - [ ] Verify responses are correct
  - [ ] Check sources are accurate
- [ ] Test error handling:
  - [ ] Send invalid query
  - [ ] Verify error message appears
- [ ] Test on different browsers (optional):
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge

## Troubleshooting Checklist

If deployment fails:

- [ ] Check build logs for errors
- [ ] Verify environment variables are set correctly
- [ ] Check Dockerfile syntax
- [ ] Verify all required files exist
- [ ] Test Docker builds locally
- [ ] Check Render status page: https://status.render.com
- [ ] Review service logs for runtime errors
- [ ] Verify health check endpoints work
- [ ] Check CORS configuration
- [ ] Verify API keys are correct

## Quick Reference

### Service Names
- Backend: `faq-assistant-backend`
- Frontend: `faq-assistant-frontend`

### Key Files
- `render.yaml` - Render Blueprint configuration
- `Dockerfile.backend` - Backend Docker configuration
- `Dockerfile.frontend` - Frontend Docker configuration
- `RENDER_ENVIRONMENT_VARIABLES.md` - Environment variables guide
- `docs/RENDER_DEPLOYMENT.md` - Complete deployment guide

### Important URLs
- Render Dashboard: https://dashboard.render.com
- Render Documentation: https://render.com/docs
- Google AI Studio: https://makersuite.google.com/app/apikey

## Notes

- **Deployment Time**: ~10-15 minutes for both services
- **Free Tier**: Services spin down after 15 minutes of inactivity
- **Cold Start**: First request after spin-down may take ~30 seconds
- **Auto-Deploy**: Enable in service settings for automatic deployments on git push

---

**Last Updated**: Based on current Render deployment configuration
**Status**: Ready for deployment ✅
