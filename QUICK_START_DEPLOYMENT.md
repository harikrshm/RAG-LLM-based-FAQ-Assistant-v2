# Quick Start: Deployment for Demo

This is a condensed guide for quickly deploying the FAQ Assistant for a demo.

## Prerequisites

- Google Gemini API key: https://makersuite.google.com/app/apikey
- GitHub account with repository access
- 30-40 minutes

## Step 1: Set Up API Key (2 minutes)

**Windows:**
```powershell
.\scripts\setup-env-local.ps1
```

**Linux/Mac:**
```bash
bash scripts/setup-env-local.sh
```

Or manually create `backend/.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

## Step 2: Deploy Backend to Railway (15 minutes)

1. Go to https://railway.app → Sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Go to **Variables** tab, add:
   ```
   GEMINI_API_KEY=your_api_key_here
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   VECTORDB_PATH=/app/data/vectordb
   METADATA_PATH=/app/data/metadata_index.json
   SOURCE_URLS_PATH=/app/data/source_urls.json
   ```
5. Go to **Volumes** tab → Add volume → Mount path: `/app/data`
6. Wait for deployment → Copy backend URL (e.g., `https://xxx.railway.app`)

## Step 3: Deploy Frontend to Vercel (10 minutes)

1. Go to https://vercel.com → Sign up with GitHub
2. Click "Add New Project" → Import repository
3. Go to **Settings** → **Environment Variables**
4. Add: `VITE_API_BASE_URL=https://your-backend-url.railway.app`
5. Click "Deploy" → Copy frontend URL (e.g., `https://xxx.vercel.app`)

## Step 4: Update CORS (2 minutes)

1. Go back to Railway → **Variables** tab
2. Add/Update: `CORS_ORIGINS_ENV=https://your-frontend-url.vercel.app`
3. Backend will auto-redeploy

## Step 5: Test (5 minutes)

1. Open frontend URL in browser
2. Click chat widget
3. Send test message: "What is expense ratio?"
4. Verify response appears

## Troubleshooting

- **Backend fails**: Check Railway logs, verify `GEMINI_API_KEY` is set
- **Frontend can't connect**: Verify `VITE_API_BASE_URL` matches Railway URL exactly
- **CORS errors**: Ensure `CORS_ORIGINS_ENV` includes exact Vercel URL (with https://)

## Full Documentation

For detailed instructions, see:
- [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) - Complete guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Checklist

