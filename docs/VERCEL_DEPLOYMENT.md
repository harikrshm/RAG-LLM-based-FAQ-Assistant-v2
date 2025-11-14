# Vercel Deployment Guide - Frontend

This guide walks you through deploying the FAQ Assistant frontend to Vercel.

## Prerequisites

- Vercel account (sign up at https://vercel.com)
- GitHub account with repository access
- Backend API URL (deployed on Railway or other platform)

## Step 1: Prepare Repository

Ensure your repository has:
- ✅ `frontend/package.json` with build scripts
- ✅ `vercel.json` configuration file
- ✅ `.vercelignore` file (optional but recommended)
- ✅ Frontend builds successfully locally

## Step 2: Connect Repository to Vercel

1. Go to https://vercel.com and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the project settings

## Step 3: Configure Project Settings

### 3.1 Framework Preset

- **Framework Preset**: Vite (or Other)
- Vercel should auto-detect Vite

### 3.2 Build Settings

- **Root Directory**: Leave empty (or set to `frontend` if needed)
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/dist`
- **Install Command**: `cd frontend && npm install`

### 3.3 Environment Variables

Add environment variables in Vercel dashboard:

**Required:**
```bash
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

**Optional (for different environments):**
```bash
# Production
VITE_API_BASE_URL=https://api.yourdomain.com

# Preview (for PR previews)
VITE_API_BASE_URL=https://staging-api.yourdomain.com

# Development
VITE_API_BASE_URL=http://localhost:8000
```

### 3.4 Environment-Specific Variables

Vercel allows setting variables per environment:
- **Production**: Used for production deployments
- **Preview**: Used for PR preview deployments
- **Development**: Used for local development (via Vercel CLI)

## Step 4: Deploy

1. Click "Deploy" button
2. Vercel will:
   - Install dependencies
   - Build the frontend
   - Deploy to CDN
3. Wait for deployment to complete
4. You'll get a URL like: `https://your-project.vercel.app`

## Step 5: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed:
   - Add CNAME record pointing to Vercel
   - Or add A record if using apex domain
4. Vercel automatically provisions SSL certificate

## Step 6: Verify Deployment

1. Visit your deployment URL
2. Open browser console and check for errors
3. Test the chat widget functionality
4. Verify API calls are going to correct backend URL

## Configuration Files

### vercel.json

The `vercel.json` file configures:
- Build and output directories
- SPA routing (rewrites)
- Cache headers for static assets
- Environment variables

### .vercelignore

Excludes unnecessary files from deployment:
- Backend files
- Documentation
- Development files
- Build artifacts

## Environment Variables

### Setting in Vercel Dashboard

1. Go to Project Settings → Environment Variables
2. Add variable: `VITE_API_BASE_URL`
3. Set value: Your backend API URL
4. Select environments: Production, Preview, Development

### Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link

# Set environment variable
vercel env add VITE_API_BASE_URL production
```

## Deployment Workflow

### Automatic Deployments

- **Production**: Deploys on push to main/master branch
- **Preview**: Deploys on pull requests
- **Manual**: Deploy from Vercel dashboard

### Build Process

1. Vercel clones repository
2. Runs `npm install` in frontend directory
3. Runs `npm run build`
4. Serves `frontend/dist` directory
5. Applies rewrites for SPA routing

## Caching Strategy

Vercel automatically caches:
- Static assets (JS, CSS, images) - Long cache (1 year)
- HTML files - Short cache (revalidated)
- API routes - No cache

The `vercel.json` configures:
- Long cache for assets (`/assets/*`)
- Immutable cache for hashed files

## Troubleshooting

### Build Fails

1. **Check build logs** in Vercel dashboard
2. **Verify Node version** - Vercel uses Node 20 by default
3. **Check dependencies** - Ensure `package.json` is correct
4. **Verify build command** - Test locally first

### Environment Variables Not Working

1. **Check variable name** - Must start with `VITE_`
2. **Rebuild after adding** - Variables are injected at build time
3. **Check environment** - Ensure variable is set for correct environment
4. **Verify in build logs** - Check if variable is available

### Routing Issues (404 on Refresh)

1. **Check vercel.json** - Ensure rewrites are configured
2. **Verify output directory** - Should be `frontend/dist`
3. **Check index.html** - Should exist in output directory

### CORS Errors

1. **Verify backend CORS** - Backend must allow Vercel domain
2. **Check API URL** - Ensure `VITE_API_BASE_URL` is correct
3. **Check protocol** - HTTPS for production

## Performance Optimization

### Vercel Features

- **Automatic CDN** - Global edge network
- **Image Optimization** - Automatic image optimization
- **Edge Functions** - Serverless functions at edge
- **Analytics** - Built-in performance analytics

### Best Practices

1. **Use environment variables** - Don't hardcode URLs
2. **Optimize images** - Use Vercel's image optimization
3. **Enable compression** - Vercel does this automatically
4. **Monitor performance** - Use Vercel Analytics

## Cost

**Free Tier:**
- Unlimited deployments
- 100GB bandwidth/month
- Suitable for most projects

**Pro Plan ($20/month):**
- More bandwidth
- Team collaboration
- Advanced analytics

## Alternative: Netlify Deployment

If you prefer Netlify:

1. Create `netlify.toml`:
```toml
[build]
  command = "cd frontend && npm install && npm run build"
  publish = "frontend/dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. Follow Netlify's deployment guide

## Next Steps

1. Set up custom domain
2. Configure preview deployments
3. Set up monitoring
4. Configure CI/CD for automated deployments

## Support

- Vercel Documentation: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- Project Issues: Create issue in repository

