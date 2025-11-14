# Railway Deployment Guide

This guide walks you through deploying the FAQ Assistant to Railway.

## Prerequisites

- Railway account (sign up at https://railway.app)
- GitHub account with repository access
- Google Gemini API key (or other LLM provider key)

## Step 1: Prepare Repository

Ensure your repository has:
- ✅ `backend/requirements.txt` with all dependencies
- ✅ `backend/main.py` as the FastAPI entry point
- ✅ `backend/.env.example` with required environment variables
- ✅ `railway.json` or `railway.toml` configuration file

## Step 2: Create Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect the project

## Step 3: Configure Backend Service

### 3.1 Service Settings

Railway should auto-detect Python. Configure:

- **Root Directory**: Leave empty (or set to `backend` if needed)
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3.2 Environment Variables

Add the following environment variables in Railway dashboard:

**Required:**
```bash
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS (add your frontend domain)
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Vector Database (Railway provides persistent storage)
VECTORDB_PATH=/app/data/vectordb
```

**Optional:**
```bash
# LLM Provider (default: gemini)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=500

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.5

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### 3.3 Persistent Storage

1. In Railway dashboard, go to your service
2. Click "Add Volume"
3. Mount path: `/app/data`
4. This will persist your vector database and knowledge base

## Step 4: Deploy Frontend (Optional - Separate Service)

### Option A: Deploy Frontend to Railway

1. Create a new service in the same project
2. Set root directory to `frontend`
3. Build command: `npm install && npm run build`
4. Start command: `npx serve -s dist -l $PORT`
5. Add environment variable: `VITE_API_BASE_URL=https://your-backend-url.railway.app`

### Option B: Deploy Frontend to Vercel (Recommended)

See [Vercel Deployment Guide](./VERCEL_DEPLOYMENT.md)

## Step 5: Configure Custom Domain (Optional)

1. In Railway dashboard, go to your service
2. Click "Settings" → "Networking"
3. Click "Generate Domain" or "Add Custom Domain"
4. For custom domain:
   - Add your domain
   - Update DNS records as instructed
   - Railway automatically provisions SSL certificate

## Step 6: Verify Deployment

1. Check service logs in Railway dashboard
2. Visit health endpoint: `https://your-service.railway.app/health`
3. Test chat endpoint: `https://your-service.railway.app/api/chat`

## Step 7: Update Frontend Configuration

Update your frontend environment variable:
```bash
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

Rebuild and redeploy frontend.

## Environment-Specific Configuration

### Development
```bash
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Staging
```bash
ENVIRONMENT=staging
DEBUG=false
CORS_ORIGINS=https://staging.yourdomain.com
```

### Production
```bash
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Monitoring and Logs

### View Logs
- Railway dashboard → Service → Logs tab
- Real-time log streaming available

### Metrics
- Railway provides basic metrics (CPU, Memory, Network)
- For advanced monitoring, integrate with external services

## Troubleshooting

### Build Fails
- Check `requirements.txt` for all dependencies
- Verify Python version compatibility
- Check build logs for specific errors

### Service Won't Start
- Verify `PORT` environment variable is used (Railway sets this)
- Check start command syntax
- Review application logs

### CORS Errors
- Ensure `CORS_ORIGINS` includes your frontend domain
- Check for trailing slashes in URLs
- Verify HTTPS/HTTP protocol matches

### Database/Storage Issues
- Ensure volume is mounted correctly
- Check write permissions on `/app/data`
- Verify persistent storage is provisioned

## Scaling

### Vertical Scaling
- Railway automatically scales based on usage
- Upgrade plan for more resources if needed

### Horizontal Scaling
- Railway supports multiple instances
- Configure in service settings

## Cost Estimation

**Free Tier:**
- $5 credit per month
- Suitable for development/testing

**Hobby Plan ($5/month):**
- $5 credit + $0.000463 per GB-hour
- Suitable for small production deployments

**Pro Plan ($20/month):**
- $20 credit + better pricing
- Suitable for medium-scale production

## Security Best Practices

1. **Never commit `.env` files** - Use Railway environment variables
2. **Use Railway secrets** - For sensitive API keys
3. **Enable HTTPS** - Railway provides automatic SSL
4. **Set CORS properly** - Only allow trusted domains
5. **Use rate limiting** - Already configured in backend
6. **Monitor logs** - Watch for suspicious activity

## Next Steps

1. Set up CI/CD (see [CI/CD Setup](./CICD_SETUP.md))
2. Configure monitoring and alerts
3. Set up staging environment
4. Implement backup strategy for vector database

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Create issue in repository

