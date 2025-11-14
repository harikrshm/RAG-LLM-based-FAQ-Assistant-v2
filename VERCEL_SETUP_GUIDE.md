# Vercel Project Setup Guide - Step by Step

Complete guide for creating and configuring a new Vercel project for the FAQ Assistant chatbot.

## Prerequisites

Before starting, ensure you have:
- ✅ GitHub account
- ✅ Repository pushed to GitHub: `RAG-LLM-based-FAQ-Assistant-v2`
- ✅ Google Gemini API key (get from https://makersuite.google.com/app/apikey)

## Step 1: Create New Project in Vercel

### 1.1 Go to Vercel

1. Open https://vercel.com
2. Click **"Sign Up"** or **"Log In"**
3. Sign in with your GitHub account (recommended)

### 1.2 Import Repository

1. Click **"Add New Project"** button
2. You'll see a list of your GitHub repositories
3. Find and select: **`RAG-LLM-based-FAQ-Assistant-v2`**
4. Click **"Import"**

## Step 2: Configure Project Settings

### 2.1 Framework Preset

Vercel should **auto-detect** Vite framework. Verify:
- **Framework Preset**: `Vite` (should be auto-detected)
- If not detected, select **"Other"** or **"Vite"** manually

### 2.2 Root Directory

- **Root Directory**: Leave **empty** (default)
- This means Vercel will use the project root

### 2.3 Build and Output Settings

Configure these settings:

**Build Command:**
```
cd frontend && npm install && npm run build
```

**Output Directory:**
```
frontend/dist
```

**Install Command:**
```
cd frontend && npm install
```

**Development Command:**
```
cd frontend && npm run dev
```
(This is optional, for local development)

### 2.4 Production Branch

**IMPORTANT:** Set this correctly!

- **Production Branch**: Select **`main`**
- This ensures production deploys from the main branch
- Preview deployments will still work for other branches/PRs

## Step 3: Configure Environment Variables

**CRITICAL STEP** - Don't skip this!

### 3.1 Add Environment Variables

Before deploying, click **"Environment Variables"** section and add:

#### Required Variables:

**1. GEMINI_API_KEY** (Required)
```
Name: GEMINI_API_KEY
Value: your_actual_gemini_api_key_here
Environments: ☑ Production ☑ Preview ☑ Development
```

**2. ENVIRONMENT** (Required)
```
Name: ENVIRONMENT
Value: production
Environments: ☑ Production
```

**3. DEBUG** (Required)
```
Name: DEBUG
Value: false
Environments: ☑ Production
```

**4. LOG_LEVEL** (Required)
```
Name: LOG_LEVEL
Value: INFO
Environments: ☑ Production ☑ Preview ☑ Development
```

#### Optional Variables (Recommended):

**5. VITE_API_BASE_URL** (Optional - for same-domain deployment)
```
Name: VITE_API_BASE_URL
Value: /api
Environments: ☑ Production ☑ Preview ☑ Development
```

**6. CORS_ORIGINS_ENV** (Optional - if using custom domain)
```
Name: CORS_ORIGINS_ENV
Value: https://your-custom-domain.com
Environments: ☑ Production
```

**7. LLM_PROVIDER** (Optional)
```
Name: LLM_PROVIDER
Value: gemini
Environments: ☑ Production ☑ Preview ☑ Development
```

**8. LLM_MODEL** (Optional)
```
Name: LLM_MODEL
Value: gemini-pro
Environments: ☑ Production ☑ Preview ☑ Development
```

### 3.2 Environment Selection

For each variable, select which environments it applies to:
- **Production**: Used for production deployments
- **Preview**: Used for PR preview deployments
- **Development**: Used for local development with Vercel CLI

**Important:** 
- Variables starting with `VITE_` are exposed to frontend
- Other variables are only available to backend/serverless functions

## Step 4: Review Configuration

Before deploying, verify:

- ✅ Framework: Vite (auto-detected)
- ✅ Root Directory: Empty (project root)
- ✅ Build Command: `cd frontend && npm install && npm run build`
- ✅ Output Directory: `frontend/dist`
- ✅ Production Branch: `main`
- ✅ Environment Variables: At least `GEMINI_API_KEY` is set

## Step 5: Deploy

### 5.1 Initial Deployment

1. Click **"Deploy"** button
2. Vercel will:
   - Clone your repository
   - Install frontend dependencies (`npm install`)
   - Build frontend (`npm run build`)
   - Detect Python from `requirements.txt`
   - Install Python dependencies
   - Deploy frontend as static site
   - Deploy backend as serverless functions
3. Wait for deployment (2-5 minutes)
4. Watch the build logs for any errors

### 5.2 Monitor Build Logs

During deployment, watch for:
- ✅ Frontend build succeeds
- ✅ Python detected from `requirements.txt`
- ✅ Python dependencies installed
- ✅ Serverless function `api/index.py` detected
- ❌ Any errors (check and fix if needed)

## Step 6: Verify Deployment

### 6.1 Get Your URLs

After deployment completes, you'll get:

- **Production URL**: `https://your-project-name.vercel.app`
- **Deployment URL**: Shown in Vercel dashboard

### 6.2 Test Backend API

1. Open: `https://your-project-name.vercel.app/api/health`
2. Should return: `{"status": "healthy", ...}`
3. If you get an error, check function logs in Vercel dashboard

### 6.3 Test Frontend

1. Open: `https://your-project-name.vercel.app`
2. Check browser console (F12) for errors
3. Click chat widget
4. Send test message: "What is expense ratio?"
5. Verify response appears

### 6.4 Test End-to-End

1. Open chat widget
2. Send query: "What is expense ratio?"
3. Verify:
   - ✅ Response appears
   - ✅ Sources are displayed
   - ✅ Links work
   - ✅ No console errors

## Step 7: Post-Deployment Configuration

### 7.1 Verify Branch Settings

1. Go to **Settings** → **Git**
2. Verify **Production Branch** is `main`
3. Verify **Auto-Deploy** is enabled

### 7.2 Check Function Logs

1. Go to **Deployments** → Latest deployment
2. Click **"View Function Logs"**
3. Check for any errors or warnings

### 7.3 Monitor Performance

1. Go to **Analytics** tab (if available)
2. Monitor:
   - Function invocations
   - Function duration
   - Error rate

## Troubleshooting

### Build Fails

**Issue**: Frontend build fails
- Check build logs
- Verify Node.js version (should be 20.x from engines field)
- Test build locally: `cd frontend && npm run build`

**Issue**: Python dependencies fail
- Check `requirements.txt` exists at root
- Verify Python runtime is detected
- Check function logs for specific errors

### API Not Working

**Issue**: `/api/health` returns 404
- Check `api/index.py` exists
- Verify `vercel.json` has correct rewrites
- Check function logs in Vercel dashboard

**Issue**: `/api/health` returns 500 error
- Check `GEMINI_API_KEY` is set correctly
- Verify environment variables are set for Production
- Check function logs for specific error messages

### Frontend Can't Connect to Backend

**Issue**: CORS errors in browser console
- Verify `VITE_API_BASE_URL` is set to `/api`
- Check backend CORS configuration
- Verify frontend and backend are on same domain

**Issue**: Network errors
- Check `VITE_API_BASE_URL` environment variable
- Verify API routes are accessible
- Check browser network tab for failed requests

## Configuration Checklist

Before deploying, ensure:

- [ ] Repository is connected to Vercel
- [ ] Framework preset is Vite (or auto-detected)
- [ ] Build command: `cd frontend && npm install && npm run build`
- [ ] Output directory: `frontend/dist`
- [ ] Production branch: `main`
- [ ] `GEMINI_API_KEY` environment variable is set
- [ ] `ENVIRONMENT=production` is set
- [ ] `DEBUG=false` is set
- [ ] `LOG_LEVEL=INFO` is set
- [ ] `VITE_API_BASE_URL=/api` is set (optional but recommended)
- [ ] `requirements.txt` exists at project root
- [ ] `api/index.py` exists
- [ ] `vercel.json` is configured correctly

## Quick Reference

### URLs After Deployment

- **Frontend**: `https://your-project-name.vercel.app`
- **Backend API**: `https://your-project-name.vercel.app/api`
- **Health Check**: `https://your-project-name.vercel.app/api/health`
- **API Docs**: `https://your-project-name.vercel.app/api/docs`

### Key Files

- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies (at root)
- `api/index.py` - Serverless function entry point
- `frontend/package.json` - Frontend dependencies
- `.vercelignore` - Files to exclude from deployment

### Environment Variables Summary

**Required:**
- `GEMINI_API_KEY` - Your Gemini API key
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`

**Optional:**
- `VITE_API_BASE_URL=/api`
- `CORS_ORIGINS_ENV` - Custom domain
- `LLM_PROVIDER=gemini`
- `LLM_MODEL=gemini-pro`

## Next Steps After Successful Deployment

1. ✅ Test all endpoints
2. ✅ Test chat widget functionality
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring and alerts
5. ✅ Review function logs regularly
6. ✅ Monitor performance metrics

## Support

If you encounter issues:
1. Check build logs in Vercel dashboard
2. Check function logs for backend errors
3. Review `VERCEL_BRANCH_CONFIG.md` for branch issues
4. Review `docs/VERCEL_FULL_STACK_DEPLOYMENT.md` for detailed troubleshooting

