# Vercel Quick Start Deployment Guide

Quick guide to deploy the FAQ Assistant chatbot to Vercel in under 15 minutes.

## Prerequisites

- Vercel account (sign up at https://vercel.com)
- GitHub account
- Google Gemini API key (get from https://makersuite.google.com/app/apikey)

## Step 1: Connect Repository (2 minutes)

1. Go to https://vercel.com and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel auto-detects settings

## Step 2: Configure Environment Variables (3 minutes)

Go to Project Settings → Environment Variables, add:

**Required:**
```
GEMINI_API_KEY=your_api_key_here
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

**Optional (for now):**
```
VITE_API_BASE_URL=/api
```

Set for: **Production**, **Preview**, and **Development**

## Step 3: Deploy (5 minutes)

1. Click "Deploy" button
2. Wait for build to complete
3. Get your URL: `https://your-project.vercel.app`

## Step 4: Verify (5 minutes)

1. **Test Backend**: `https://your-project.vercel.app/api/health`
   - Should return: `{"status": "healthy"}`

2. **Test Frontend**: `https://your-project.vercel.app`
   - Open chat widget
   - Send test message: "What is expense ratio?"
   - Verify response appears

## That's It!

Your chatbot is now live on Vercel!

## Troubleshooting

**Build fails?**
- Check build logs in Vercel dashboard
- Verify `requirements.txt` exists at root
- Verify `api/index.py` exists

**API not working?**
- Check function logs in Vercel dashboard
- Verify `GEMINI_API_KEY` is set
- Test `/api/health` endpoint

**Frontend can't connect?**
- Verify `VITE_API_BASE_URL=/api` is set
- Check browser console for errors
- Verify CORS settings

## Next Steps

- See [Full Deployment Guide](docs/VERCEL_FULL_STACK_DEPLOYMENT.md) for detailed instructions
- Configure custom domain
- Set up monitoring
- Optimize performance

## Quick Reference

- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://your-project.vercel.app/api`
- **Health Check**: `https://your-project.vercel.app/api/health`
- **API Docs**: `https://your-project.vercel.app/api/docs`

