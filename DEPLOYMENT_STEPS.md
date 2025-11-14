# Deployment Steps: FAQ Assistant Demo

This guide walks you through deploying the FAQ Assistant to Railway (backend) and Vercel (frontend) for a demo.

## Prerequisites

- GitHub account with repository access
- Google Gemini API key (get from https://makersuite.google.com/app/apikey or https://aistudio.google.com/app/apikey)
- Railway account (we'll create this)
- Vercel account (we'll create this)

## Phase 1: Local API Key Setup

### Step 1.1: Create Backend .env File

1. Navigate to the `backend` directory
2. Create a file named `.env` (if it doesn't exist)
3. Add the following content:

```bash
GEMINI_API_KEY=your_actual_api_key_here
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

**Important:** Replace `your_actual_api_key_here` with your actual Google Gemini API key.

### Step 1.2: Verify Local Setup (Optional)

Test that the backend runs locally:

```bash
cd backend
uvicorn main:app --reload
```

Open http://localhost:8000/health in your browser. You should see a JSON response with `{"status": "healthy", ...}`.

Press `Ctrl+C` to stop the server.

## Phase 2: Backend Deployment (Railway)

### Step 2.1: Create Railway Account

1. Go to https://railway.app
2. Click "Start a New Project" or "Login"
3. Sign up with GitHub (recommended) or email
4. Verify your email if prompted

### Step 2.2: Create New Project

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub repositories if prompted
4. Find and select your repository: `RAG-LLM-based-FAQ-Assistant-v2`
5. Railway will auto-detect Python and start building

### Step 2.3: Configure Backend Service

Railway should auto-detect the configuration from `railway.json` and `nixpacks.toml`. Verify these settings:

1. Go to your service → Settings
2. Check:
   - **Root Directory**: Leave empty (or set to `backend` if auto-detection fails)
   - **Build Command**: Should be auto-detected from `nixpacks.toml`
   - **Start Command**: Should be `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 2.4: Set Environment Variables

1. In Railway dashboard, go to your service → Variables tab
2. Click "New Variable" and add each of the following:

**Required Variables:**

```
GEMINI_API_KEY=your_gemini_api_key_here
```

```
ENVIRONMENT=production
```

```
DEBUG=false
```

```
LOG_LEVEL=INFO
```

**CORS Configuration (update after frontend deployment):**

```
CORS_ORIGINS_ENV=https://your-frontend.vercel.app
```

(We'll update this with the actual Vercel URL after frontend deployment)

**Vector Database Paths:**

```
VECTORDB_PATH=/app/data/vectordb
```

```
METADATA_PATH=/app/data/metadata_index.json
```

```
SOURCE_URLS_PATH=/app/data/source_urls.json
```

**Optional Variables (defaults work, but you can set explicitly):**

```
LLM_PROVIDER=gemini
```

```
LLM_MODEL=gemini-pro
```

```
LLM_TEMPERATURE=0.1
```

```
RAG_TOP_K=5
```

### Step 2.5: Add Persistent Storage (for Vector Database)

1. In Railway dashboard → Your service → Volumes tab
2. Click "Add Volume"
3. Set:
   - **Mount Path**: `/app/data`
   - **Name**: `data-volume` (or any name)
4. Click "Add"

This volume will store your vector database and metadata files persistently.

### Step 2.6: Deploy Backend

1. Railway will automatically deploy when you push to the main branch
2. Or click "Deploy" manually in the dashboard
3. Wait for deployment to complete (2-5 minutes)
4. Watch the build logs for any errors

### Step 2.7: Get Backend URL and Verify

1. Once deployed, Railway will provide a URL like: `https://your-project-name.railway.app`
2. Click on the URL or copy it from the dashboard
3. Test the health endpoint:
   - Open: `https://your-backend-url.railway.app/health`
   - Should return: `{"status": "healthy", ...}`
4. Test readiness endpoint:
   - Open: `https://your-backend-url.railway.app/ready`
   - Should return: `{"status": "ready", ...}`

**Important:** Save this backend URL - you'll need it for frontend configuration!

## Phase 3: Frontend Deployment (Vercel)

### Step 3.1: Create Vercel Account

1. Go to https://vercel.com
2. Click "Sign Up" or "Login"
3. Sign up with GitHub (recommended)
4. Verify your email if prompted

### Step 3.2: Import Project

1. In Vercel dashboard, click "Add New Project"
2. Import your GitHub repository: `RAG-LLM-based-FAQ-Assistant-v2`
3. Vercel will auto-detect Vite framework

### Step 3.3: Configure Frontend Settings

Vercel should auto-detect settings from `vercel.json`. Verify:

1. **Framework Preset**: Vite (auto-detected)
2. **Root Directory**: Leave empty (or set to `frontend` if needed)
3. **Build Command**: `cd frontend && npm install && npm run build`
4. **Output Directory**: `frontend/dist`
5. **Install Command**: `cd frontend && npm install`

### Step 3.4: Set Environment Variables

1. In Vercel dashboard → Project Settings → Environment Variables
2. Click "Add New"
3. Add:

**Required:**

```
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

**Important:** Replace `your-backend-url.railway.app` with the actual Railway backend URL from Step 2.7!

4. Select environment: **Production** (and optionally Preview and Development)
5. Click "Save"

### Step 3.5: Deploy Frontend

1. Click "Deploy" button
2. Vercel will:
   - Install dependencies
   - Build the frontend
   - Deploy to CDN
3. Wait for deployment (2-3 minutes)
4. You'll get a URL like: `https://your-project-name.vercel.app`

### Step 3.6: Update Backend CORS

1. Go back to Railway dashboard
2. Navigate to your backend service → Variables tab
3. Find `CORS_ORIGINS_ENV` variable
4. Click "Edit" and update the value to:

```
https://your-project-name.vercel.app
```

Replace `your-project-name.vercel.app` with your actual Vercel frontend URL.

5. Save the variable
6. Railway will automatically redeploy (or trigger a redeploy manually)

## Phase 4: Post-Deployment Verification

### Step 4.1: Test Frontend

1. Open your frontend URL: `https://your-project-name.vercel.app`
2. Verify the chat widget loads
3. Open browser Developer Tools (F12) → Console tab
4. Check for any errors (should be none)

### Step 4.2: Test Backend API

**Option 1: Test from Frontend**
- Click the chat widget
- Send a test message: "What is expense ratio?"
- Verify you get a response

**Option 2: Test Directly**
- Open: `https://your-backend-url.railway.app/health`
- Should return: `{"status": "healthy", ...}`

### Step 4.3: Test End-to-End Flow

1. Open chat widget on frontend
2. Send test query: "What is expense ratio?"
3. Verify:
   - Response appears
   - Sources are displayed at the bottom
   - Source links open in new tab when clicked
   - No errors in browser console

### Step 4.4: Check Logs

**Railway Logs:**
1. Go to Railway dashboard → Your service → Deployments
2. Click on latest deployment → View Logs
3. Look for any errors or warnings

**Vercel Logs:**
1. Go to Vercel dashboard → Your project → Deployments
2. Click on latest deployment → View Logs
3. Look for any errors or warnings

## Phase 5: Data Ingestion (If Needed)

If your vector database is not populated, you need to ingest data:

### Step 5.1: Run Data Ingestion Locally

1. Ensure you have data sources configured in `data/source_urls.json`
2. Run ingestion:
   ```bash
   python run_ingestion.py
   ```
3. This creates:
   - `data/vectordb/` - Vector database
   - `data/metadata_index.json` - Metadata index
   - `data/source_urls.json` - Source URLs

### Step 5.2: Upload Data to Railway

**Option 1: Using Railway CLI**

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Link project: `railway link`
4. Upload files:
   ```bash
   railway run --service your-service-name -- sh -c "mkdir -p /app/data && cp -r data/vectordb /app/data/ && cp data/metadata_index.json /app/data/ && cp data/source_urls.json /app/data/"
   ```

**Option 2: Using Railway Dashboard**

1. Go to Railway dashboard → Your service → Volumes
2. Click on your volume
3. Use Railway's file browser to upload files (if available)

**Option 3: SSH into Container**

1. Railway dashboard → Your service → Settings → Generate SSH Command
2. Copy the SSH command and run it
3. Upload files using `scp` or `rsync`

## Troubleshooting

### Backend Fails to Start

- **Check Railway logs** for error messages
- **Verify `GEMINI_API_KEY`** is set correctly in Railway variables
- **Check build logs** for dependency installation errors
- **Verify Python version** (should be 3.11+)

### Frontend Can't Connect to Backend

- **Verify `VITE_API_BASE_URL`** matches your Railway backend URL exactly
- **Check CORS settings** - ensure `CORS_ORIGINS_ENV` includes your Vercel URL
- **Test backend directly** - open `https://your-backend-url.railway.app/health` in browser
- **Check browser console** for CORS errors

### No Responses from Chat

- **Check vector database** is populated (see Phase 5)
- **Verify LLM API key** is valid - test with a simple curl request
- **Check Railway logs** for LLM API errors
- **Verify environment variables** are set correctly

### CORS Errors

- **Ensure `CORS_ORIGINS_ENV`** includes your exact Vercel URL (with `https://`)
- **No trailing slashes** in CORS origins
- **Redeploy backend** after updating CORS variables

### Build Failures

**Backend (Railway):**
- Check `backend/requirements.txt` for dependency issues
- Verify Python version compatibility
- Check build logs for specific error messages

**Frontend (Vercel):**
- Check `frontend/package.json` for dependency issues
- Verify Node.js version (should be 20+)
- Check build logs for TypeScript or build errors

## Quick Reference

### Backend URLs
- Health: `https://your-backend-url.railway.app/health`
- Readiness: `https://your-backend-url.railway.app/ready`
- API Docs: `https://your-backend-url.railway.app/docs`

### Frontend URL
- Main: `https://your-project-name.vercel.app`

### Environment Variables Summary

**Railway (Backend):**
- `GEMINI_API_KEY` - Required
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `CORS_ORIGINS_ENV` - Your Vercel URL
- `VECTORDB_PATH=/app/data/vectordb`
- `METADATA_PATH=/app/data/metadata_index.json`
- `SOURCE_URLS_PATH=/app/data/source_urls.json`

**Vercel (Frontend):**
- `VITE_API_BASE_URL` - Your Railway backend URL

## Next Steps

After successful deployment:

1. **Monitor logs** regularly for errors
2. **Test all features** thoroughly
3. **Set up custom domains** (optional) if needed
4. **Configure monitoring** (if not already done)
5. **Share demo URL** with stakeholders

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Railway and Vercel logs
3. Verify all environment variables are set correctly
4. Test endpoints individually to isolate issues

