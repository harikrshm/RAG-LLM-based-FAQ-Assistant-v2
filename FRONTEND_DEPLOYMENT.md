# Frontend Deployment Guide

Since you want to deploy only the frontend (website), here are the best options:

## Option 1: Deploy to Vercel (Recommended for Frontend)

Vercel is specifically designed for frontend deployments and offers:
- Automatic HTTPS
- Global CDN
- Fast deployments
- Free tier with generous limits

### Steps:

1. **Go to https://vercel.com** and sign up with GitHub
2. **Click "Add New Project"** → Import your repository
3. **Configure settings:**
   - Framework Preset: Vite (auto-detected)
   - Root Directory: Leave empty (or `frontend` if needed)
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
4. **Add environment variable:**
   - `VITE_API_BASE_URL` = Your backend API URL (when you deploy backend later)
   - For now, you can use: `http://localhost:8000` or leave it for later
5. **Click "Deploy"**

Vercel will automatically:
- Build your frontend
- Deploy to CDN
- Provide a URL like: `https://your-project.vercel.app`

## Option 2: Deploy to Railway (Frontend)

Railway can host frontend, but Vercel is better suited for static sites.

### Steps:

1. **In Railway dashboard**, create a new service
2. **Set Root Directory**: `frontend`
3. **Set Build Command**: `npm install && npm run build`
4. **Set Start Command**: `npx serve -s dist -l $PORT`
5. **Add environment variable**: `VITE_API_BASE_URL` (your backend URL)
6. **Deploy**

## Option 3: Deploy to Netlify (Alternative)

Netlify is also excellent for frontend deployments.

### Steps:

1. **Go to https://netlify.com** and sign up
2. **Connect GitHub repository**
3. **Configure:**
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
4. **Add environment variable**: `VITE_API_BASE_URL`
5. **Deploy**

## Current Configuration

- ✅ Removed `nixpacks.toml` (was causing build issues)
- ✅ Updated `railway.json` for frontend deployment (if using Railway)
- ✅ `vercel.json` is already configured for Vercel deployment

## Recommended: Use Vercel for Frontend

For frontend-only deployment, **Vercel is the best choice**:
- Optimized for static sites and SPAs
- Automatic deployments on git push
- Built-in CDN and edge functions
- Free tier is very generous
- Better performance for frontend

## Next Steps

1. **Deploy frontend to Vercel** (recommended)
2. **When ready to deploy backend**, use Railway for backend
3. **Update `VITE_API_BASE_URL`** in Vercel with your Railway backend URL

## Quick Vercel Deployment

```bash
# 1. Go to vercel.com and sign up
# 2. Import your GitHub repository
# 3. Configure:
#    - Build: cd frontend && npm install && npm run build
#    - Output: frontend/dist
# 4. Add env var: VITE_API_BASE_URL (set later when backend is deployed)
# 5. Deploy!
```

Your frontend will be live in minutes!

