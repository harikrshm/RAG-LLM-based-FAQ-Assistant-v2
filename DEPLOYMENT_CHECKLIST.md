# Deployment Checklist

Use this checklist to track your deployment progress.

## Phase 1: Local Setup

- [ ] Get Google Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Run setup script: `.\scripts\setup-env-local.ps1` (Windows) or `bash scripts/setup-env-local.sh` (Linux/Mac)
- [ ] Or manually create `backend/.env` with `GEMINI_API_KEY=your_key`
- [ ] Test backend locally: `cd backend && uvicorn main:app --reload`
- [ ] Verify health endpoint: http://localhost:8000/health

## Phase 2: Railway Backend Deployment

- [ ] Create Railway account at https://railway.app
- [ ] Create new project from GitHub repository
- [ ] Select repository: `RAG-LLM-based-FAQ-Assistant-v2`
- [ ] Verify service settings (Root Directory, Build Command, Start Command)
- [ ] Add environment variables:
  - [ ] `GEMINI_API_KEY=your_key`
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=false`
  - [ ] `LOG_LEVEL=INFO`
  - [ ] `CORS_ORIGINS_ENV=https://your-frontend.vercel.app` (update after frontend deploy)
  - [ ] `VECTORDB_PATH=/app/data/vectordb`
  - [ ] `METADATA_PATH=/app/data/metadata_index.json`
  - [ ] `SOURCE_URLS_PATH=/app/data/source_urls.json`
- [ ] Add persistent volume: `/app/data`
- [ ] Deploy backend
- [ ] Get backend URL: `https://your-project.railway.app`
- [ ] Test health endpoint: `https://your-backend-url.railway.app/health`
- [ ] Test readiness: `https://your-backend-url.railway.app/ready`
- [ ] **Save backend URL for frontend configuration**

## Phase 3: Vercel Frontend Deployment

- [ ] Create Vercel account at https://vercel.com
- [ ] Import GitHub repository: `RAG-LLM-based-FAQ-Assistant-v2`
- [ ] Verify project settings (Framework, Root Directory, Build Command, Output Directory)
- [ ] Add environment variable: `VITE_API_BASE_URL=https://your-backend-url.railway.app`
- [ ] Deploy frontend
- [ ] Get frontend URL: `https://your-project.vercel.app`
- [ ] **Save frontend URL for CORS update**

## Phase 4: Update CORS

- [ ] Go back to Railway dashboard
- [ ] Update `CORS_ORIGINS_ENV` with Vercel frontend URL
- [ ] Wait for backend redeploy (or trigger manually)

## Phase 5: Verification

- [ ] Open frontend URL in browser
- [ ] Check browser console for errors (should be none)
- [ ] Test chat widget - send message: "What is expense ratio?"
- [ ] Verify response appears
- [ ] Verify sources are displayed
- [ ] Verify source links open in new tab
- [ ] Check Railway logs for errors
- [ ] Check Vercel logs for errors

## Phase 6: Data Ingestion (If Needed)

- [ ] Check if vector database exists locally
- [ ] Run data ingestion: `python run_ingestion.py`
- [ ] Upload data to Railway volume:
  - [ ] `data/vectordb/` → `/app/data/vectordb/`
  - [ ] `data/metadata_index.json` → `/app/data/metadata_index.json`
  - [ ] `data/source_urls.json` → `/app/data/source_urls.json`

## Quick Reference

### URLs
- Backend Health: `https://your-backend-url.railway.app/health`
- Backend API Docs: `https://your-backend-url.railway.app/docs`
- Frontend: `https://your-project.vercel.app`

### Key Environment Variables

**Railway:**
```
GEMINI_API_KEY=your_key
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS_ENV=https://your-frontend.vercel.app
VECTORDB_PATH=/app/data/vectordb
METADATA_PATH=/app/data/metadata_index.json
SOURCE_URLS_PATH=/app/data/source_urls.json
```

**Vercel:**
```
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

## Troubleshooting

- Backend fails: Check Railway logs, verify `GEMINI_API_KEY`
- Frontend can't connect: Verify `VITE_API_BASE_URL`, check CORS
- No responses: Check vector DB is populated, verify API key
- CORS errors: Ensure `CORS_ORIGINS_ENV` includes exact Vercel URL

