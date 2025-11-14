# Vercel Deployment Fix - Runtime Error Solution

## Current Issue

Error: "Function Runtimes must have a valid version, for example `now-php@1.0.0`"

## Root Cause Analysis

The error occurs because:
1. Vercel detects `api/index.py` as a serverless function
2. But cannot determine the Python runtime version
3. The `functions` section in `vercel.json` was causing conflicts

## Solution Applied

**Removed `functions` section from `vercel.json`**

Vercel will now auto-detect Python from:
- `requirements.txt` at project root
- `api/*.py` files in the api directory

## Current Configuration

**vercel.json:**
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**No `functions` section** - Vercel auto-detects Python

## Verification Checklist

Before deploying, ensure:

- [ ] `requirements.txt` exists at project root
- [ ] `api/index.py` exists
- [ ] `backend/` directory is NOT in `.vercelignore`
- [ ] No `functions` section in `vercel.json`
- [ ] Rewrite destination is `/api/index` (not `/api/index.py`)

## If Error Persists

Try these alternatives:

### Alternative 1: Remove Rewrite Entirely

Remove the `/api/(.*)` rewrite and let Vercel handle routing automatically:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Then access API at: `/api/index` directly (Vercel auto-routes `api/index.py` to `/api/index`)

### Alternative 2: Use Individual Route Files

Instead of single `api/index.py`, create individual route files:
- `api/chat.py` → `/api/chat`
- `api/health.py` → `/api/health`

This avoids the catch-all rewrite issue.

### Alternative 3: Check Vercel Project Settings

In Vercel dashboard:
1. Go to Settings → General
2. Check "Node.js Version" - should be 20.x (from engines field)
3. Verify no conflicting runtime settings

## Testing After Fix

1. Deploy to Vercel
2. Check build logs - should see:
   - ✅ Python detected from requirements.txt
   - ✅ Installing Python dependencies
   - ✅ Function api/index.py detected
3. Test: `https://your-project.vercel.app/api/health`

