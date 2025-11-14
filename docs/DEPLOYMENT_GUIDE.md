# Complete Deployment Guide

This guide has been replaced with the Vercel Full-Stack Deployment Guide.

## Recommended: Vercel Full-Stack Deployment

For the simplest deployment experience, deploy both frontend and backend to Vercel:

👉 **[See Vercel Full-Stack Deployment Guide](./VERCEL_FULL_STACK_DEPLOYMENT.md)**

This guide covers:
- Deploying frontend and backend together on Vercel
- Serverless function configuration
- Environment variable setup
- Testing and verification
- Troubleshooting

## Quick Start

👉 **[See Quick Start Guide](../../VERCEL_QUICK_START.md)** - Deploy in 15 minutes

## Alternative Deployment Options

For other deployment scenarios, see:
- **[General Deployment Guide](./DEPLOYMENT.md)** - Docker, AWS, GCP, etc.
- **[Vercel Frontend Only](./VERCEL_DEPLOYMENT.md)** - Frontend-only deployment

---

## Legacy Railway Deployment (Deprecated)

This guide previously covered Railway deployment, which has been replaced with Vercel full-stack deployment.

For Railway deployment instructions, please refer to the Vercel guide or use Docker deployment.

### Step 1: Prepare Railway Account

1. Go to https://railway.app
2. Sign up or log in
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### Step 2: Configure Backend Service

1. **Service Detection**
   - Railway should auto-detect Python
   - If not, select "Python" as runtime

2. **Service Settings**
   - **Root Directory**: Leave empty (or set to `backend` if needed)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Verify Settings**
   - Railway sets `PORT` automatically
   - Don't hardcode port numbers

### Step 3: Set Environment Variables

Go to Service → Variables tab and add:

**Required:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

**CORS Configuration:**
```bash
CORS_ORIGINS_ENV=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

**Vector Database:**
```bash
VECTORDB_PATH=/app/data/vectordb
METADATA_PATH=/app/data/metadata_index.json
SOURCE_URLS_PATH=/app/data/source_urls.json
```

**Optional Configuration:**
```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.1
RAG_TOP_K=5
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### Step 4: Add Persistent Storage

1. Go to Service → Settings → Volumes
2. Click "Add Volume"
3. Mount path: `/app/data`
4. This persists your vector database

### Step 5: Deploy

1. Railway automatically deploys on push to main branch
2. Or click "Deploy" button
3. Wait for deployment to complete
4. Check logs for errors

### Step 6: Get Backend URL

1. Go to Service → Settings → Networking
2. Copy the generated URL (e.g., `your-service.up.railway.app`)
3. Or configure custom domain (see [Domain Configuration](#domain-configuration))

### Step 7: Verify Backend

```bash
# Health check
curl https://your-backend.railway.app/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Vercel Account

1. Go to https://vercel.com
2. Sign up or log in with GitHub
3. Click "Add New Project"
4. Import your GitHub repository

### Step 2: Configure Project

1. **Framework Detection**
   - Vercel should auto-detect Vite
   - If not, select "Other" or "Vite"

2. **Build Settings**
   - **Root Directory**: Leave empty (or set to `frontend`)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`

3. **Verify Settings**
   - Check that paths are correct
   - Verify build command matches your setup

### Step 3: Set Environment Variables

Go to Project → Settings → Environment Variables:

**Required:**
```bash
VITE_API_BASE_URL=https://your-backend.railway.app
```

**Environment-Specific:**
- **Production**: `https://api.yourdomain.com`
- **Preview**: `https://staging-api.yourdomain.com`
- **Development**: `http://localhost:8000`

### Step 4: Deploy

1. Click "Deploy" button
2. Vercel will:
   - Install dependencies
   - Build the frontend
   - Deploy to CDN
3. Wait for deployment to complete
4. You'll get a URL like: `https://your-project.vercel.app`

### Step 5: Verify Frontend

1. Visit deployment URL
2. Open browser console (F12)
3. Check for errors
4. Test chat widget functionality

---

## Domain Configuration

### Backend Domain (Railway)

#### Option 1: Railway-Generated Domain

- Format: `your-service.up.railway.app`
- SSL: Automatic
- No configuration needed

#### Option 2: Custom Domain

1. **Add Domain in Railway**
   - Service → Settings → Networking
   - Click "Add Custom Domain"
   - Enter: `api.yourdomain.com`

2. **Configure DNS**
   - Go to your DNS provider
   - Add CNAME record:
     ```
     Type: CNAME
     Name: api
     Value: your-service.up.railway.app
     TTL: 3600
     ```

3. **Wait for SSL**
   - Railway automatically provisions SSL
   - Usually takes 5-10 minutes
   - Check status in Railway dashboard

### Frontend Domain (Vercel)

#### Option 1: Vercel-Generated Domain

- Format: `your-project.vercel.app`
- SSL: Automatic
- No configuration needed

#### Option 2: Custom Domain

1. **Add Domain in Vercel**
   - Project → Settings → Domains
   - Click "Add Domain"
   - Enter: `yourdomain.com` or `www.yourdomain.com`

2. **Configure DNS**

   **For Subdomain (www):**
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   TTL: 3600
   ```

   **For Root Domain:**
   ```
   Type: A
   Name: @
   Value: 76.76.21.21 (check Vercel for current IPs)
   TTL: 3600
   ```

3. **Wait for SSL**
   - Vercel automatically provisions SSL
   - Usually takes 5-10 minutes
   - Check status in Vercel dashboard

### Update Environment Variables

After setting up domains, update:

**Backend:**
```bash
CORS_ORIGINS_ENV=https://yourdomain.com,https://www.yourdomain.com
```

**Frontend:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## Environment Variables

### Backend Environment Variables

**Required:**
```bash
GEMINI_API_KEY=your_key_here
ENVIRONMENT=production
CORS_ORIGINS_ENV=https://yourdomain.com
```

**Recommended:**
```bash
DEBUG=false
LOG_LEVEL=INFO
VECTORDB_PATH=/app/data/vectordb
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

**See**: [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md) for complete list

### Frontend Environment Variables

**Required:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

**Note**: Must start with `VITE_` prefix

---

## Post-Deployment Verification

### 1. Backend Health Check

```bash
# Health endpoint
curl https://api.yourdomain.com/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### 2. Backend Readiness Check

```bash
# Readiness endpoint
curl https://api.yourdomain.com/ready

# Expected response:
# {"ready":true}
```

### 3. Test Chat API

```bash
curl -X POST https://api.yourdomain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is mutual fund?",
    "sessionId": "test-session"
  }'

# Should return chat response with sources
```

### 4. Frontend Widget Test

1. Visit frontend URL
2. Open chat widget
3. Send a test message
4. Verify:
   - ✅ Message appears
   - ✅ Loading indicator shows
   - ✅ Response received
   - ✅ Sources displayed
   - ✅ Links work

### 5. CORS Verification

```bash
# Test CORS from browser console (on frontend domain)
fetch('https://api.yourdomain.com/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'test', sessionId: 'test'})
})
.then(r => r.json())
.then(console.log)
.catch(console.error);

# Should succeed without CORS errors
```

### 6. SSL Certificate Check

```bash
# Check SSL certificate
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com

# Or use online tool:
# https://www.ssllabs.com/ssltest/
```

---

## Troubleshooting

### Backend Issues

#### Deployment Fails

**Symptoms**: Build fails or service won't start

**Solutions**:
1. Check Railway logs for errors
2. Verify `requirements.txt` is correct
3. Check Python version compatibility
4. Verify start command is correct
5. Check environment variables are set

#### Service Won't Start

**Symptoms**: Service shows as "down" or "error"

**Solutions**:
1. Check logs in Railway dashboard
2. Verify `PORT` environment variable (Railway sets this)
3. Check start command syntax
4. Verify dependencies are installed
5. Check for import errors

#### CORS Errors

**Symptoms**: Frontend can't connect to backend

**Solutions**:
1. Verify `CORS_ORIGINS_ENV` includes frontend domain
2. Check protocol matches (https vs http)
3. Ensure no trailing slashes
4. Restart backend after changing CORS settings
5. Check browser console for specific error

#### Database/Storage Issues

**Symptoms**: Vector database not persisting

**Solutions**:
1. Verify volume is mounted at `/app/data`
2. Check volume has write permissions
3. Verify `VECTORDB_PATH` is correct
4. Check Railway volume status

### Frontend Issues

#### Build Fails

**Symptoms**: Vercel build fails

**Solutions**:
1. Check build logs in Vercel dashboard
2. Verify Node version (should be 20+)
3. Check `package.json` dependencies
4. Test build locally: `cd frontend && npm run build`
5. Check for TypeScript errors

#### Environment Variables Not Working

**Symptoms**: Variables undefined in production

**Solutions**:
1. Ensure variables start with `VITE_`
2. Rebuild after adding variables (they're build-time)
3. Check variable is set for correct environment
4. Verify variable name spelling
5. Check Vercel environment variable settings

#### Widget Not Loading

**Symptoms**: Widget doesn't appear or errors

**Solutions**:
1. Check browser console for errors
2. Verify `VITE_API_BASE_URL` is correct
3. Check CORS configuration
4. Verify backend is accessible
5. Check network tab for failed requests

#### Routing Issues (404 on Refresh)

**Symptoms**: 404 error when refreshing page

**Solutions**:
1. Verify `vercel.json` has rewrites configured
2. Check output directory is `frontend/dist`
3. Verify `index.html` exists in output
4. Check SPA routing is enabled

### Domain Issues

#### DNS Not Propagating

**Symptoms**: Domain not resolving

**Solutions**:
1. Wait longer (can take up to 48 hours, usually 5-60 minutes)
2. Clear DNS cache: `sudo dscacheutil -flushcache` (Mac) or `ipconfig /flushdns` (Windows)
3. Check DNS records are correct
4. Verify DNS provider settings
5. Use DNS checker: https://dnschecker.org/

#### SSL Certificate Not Issuing

**Symptoms**: SSL certificate not provisioning

**Solutions**:
1. Verify DNS is fully propagated
2. Check domain is correctly configured
3. Ensure port 80/443 is accessible
4. Wait 10-15 minutes after DNS propagation
5. Check platform logs for errors

---

## Maintenance

### Regular Tasks

#### Weekly
- ✅ Check deployment logs for errors
- ✅ Monitor error rates
- ✅ Review performance metrics

#### Monthly
- ✅ Update dependencies
- ✅ Review and rotate API keys
- ✅ Check SSL certificate expiration
- ✅ Review and update CORS origins if needed

#### Quarterly
- ✅ Review and update Groww page mappings
- ✅ Update design tokens if Groww changes
- ✅ Review and optimize performance
- ✅ Update documentation

### Updating Dependencies

**Backend:**
```bash
cd backend
pip install --upgrade -r requirements.txt
# Test locally
# Commit and push
# Railway auto-deploys
```

**Frontend:**
```bash
cd frontend
npm update
npm audit fix
# Test locally
# Commit and push
# Vercel auto-deploys
```

### Monitoring

**Backend (Railway):**
- Check Railway dashboard for metrics
- Review logs for errors
- Monitor resource usage

**Frontend (Vercel):**
- Check Vercel Analytics
- Review deployment logs
- Monitor performance metrics

### Backup Strategy

**Vector Database:**
- Railway volumes are automatically backed up
- Consider exporting data periodically
- Store backups in separate location

**Configuration:**
- Keep environment variables documented
- Version control configuration files
- Backup secrets securely

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] API keys obtained
- [ ] Domain names ready (if using custom domains)
- [ ] DNS access available

### Backend Deployment

- [ ] Railway account created
- [ ] Repository connected
- [ ] Service configured
- [ ] Environment variables set
- [ ] Volume mounted
- [ ] Deployed successfully
- [ ] Health check passing
- [ ] Domain configured (if custom)
- [ ] SSL certificate active

### Frontend Deployment

- [ ] Vercel account created
- [ ] Repository connected
- [ ] Project configured
- [ ] Environment variables set
- [ ] Build successful
- [ ] Deployed successfully
- [ ] Widget functional
- [ ] Domain configured (if custom)
- [ ] SSL certificate active

### Post-Deployment

- [ ] Backend health check passing
- [ ] Frontend loading correctly
- [ ] Widget functional
- [ ] CORS working
- [ ] SSL certificates valid
- [ ] API calls successful
- [ ] Sources displaying correctly
- [ ] Links opening correctly
- [ ] Error handling working
- [ ] Monitoring set up

---

## Quick Reference

### Backend URLs

- **Health**: `https://api.yourdomain.com/health`
- **Readiness**: `https://api.yourdomain.com/ready`
- **Chat API**: `https://api.yourdomain.com/api/chat`
- **Metrics**: `https://api.yourdomain.com/metrics`

### Frontend URLs

- **Main**: `https://yourdomain.com`
- **Widget**: Embedded on Groww pages

### Environment Variables

**Backend:**
```bash
GEMINI_API_KEY=...
CORS_ORIGINS_ENV=https://yourdomain.com
ENVIRONMENT=production
```

**Frontend:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Useful Commands

```bash
# Test backend health
curl https://api.yourdomain.com/health

# Test chat API
curl -X POST https://api.yourdomain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"test","sessionId":"test"}'

# Check SSL
openssl s_client -connect api.yourdomain.com:443
```

---

## Related Documentation

- [Railway Deployment Guide](./RAILWAY_DEPLOYMENT.md) - Detailed Railway setup
- [Vercel Deployment Guide](./VERCEL_DEPLOYMENT.md) - Detailed Vercel setup
- [Domain and SSL Setup](./DOMAIN_SSL_SETUP.md) - Domain configuration
- [Environment Variables](./ENVIRONMENT_VARIABLES.md) - Environment variables reference
- [CORS Configuration](./CORS_CONFIGURATION.md) - CORS setup guide
- [CI/CD Setup](./CICD_SETUP.md) - Automated deployment

---

## Support

If you encounter issues:

1. Check relevant documentation guides
2. Review troubleshooting section
3. Check platform logs (Railway/Vercel)
4. Verify environment variables
5. Test locally first
6. Check GitHub Issues

## Next Steps

After deployment:

1. Set up monitoring and alerts
2. Configure backup strategy
3. Set up staging environment
4. Document your specific configuration
5. Train team on deployment process

