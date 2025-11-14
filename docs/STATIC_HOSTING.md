# Static Hosting Deployment Guide

This guide covers deploying the frontend as static files to various hosting providers.

## Overview

The frontend is a static React application built with Vite. After building, it produces static files that can be hosted on any static hosting service.

## Build Process

### 1. Build the Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` directory with all static files.

### 2. Verify Build Output

```bash
ls frontend/dist
# Should contain:
# - index.html
# - assets/ (JS, CSS files)
# - Other static assets
```

## Deployment Options

### Option 1: AWS S3 + CloudFront

#### Setup Steps

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://your-bucket-name
   ```

2. **Configure Bucket for Static Website**
   - Enable static website hosting
   - Set index document: `index.html`
   - Set error document: `index.html` (for SPA routing)

3. **Upload Files**
   ```bash
   aws s3 sync frontend/dist s3://your-bucket-name --delete
   ```

4. **Set Bucket Policy**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::your-bucket-name/*"
       }
     ]
   }
   ```

5. **Create CloudFront Distribution**
   - Origin: S3 bucket
   - Default root object: `index.html`
   - Error pages: Redirect 404 to `/index.html` with 200 status

#### Environment Variables

Set `VITE_API_BASE_URL` before building:
```bash
export VITE_API_BASE_URL=https://your-api-url.com
npm run build
```

### Option 2: GitHub Pages

#### Setup Steps

1. **Install gh-pages**
   ```bash
   cd frontend
   npm install --save-dev gh-pages
   ```

2. **Add Script to package.json**
   ```json
   {
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d dist"
     }
   }
   ```

3. **Configure vite.config.ts**
   ```typescript
   export default defineConfig({
     base: '/your-repo-name/', // or '/' for custom domain
     // ... other config
   })
   ```

4. **Deploy**
   ```bash
   npm run deploy
   ```

### Option 3: Cloudflare Pages

#### Setup Steps

1. **Connect Repository**
   - Go to Cloudflare Dashboard → Pages
   - Connect GitHub repository

2. **Configure Build**
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `frontend/dist`
   - Root directory: `/` (or `frontend`)

3. **Set Environment Variables**
   - `VITE_API_BASE_URL`: Your backend API URL

4. **Deploy**
   - Cloudflare automatically deploys on push

### Option 4: Firebase Hosting

#### Setup Steps

1. **Install Firebase CLI**
   ```bash
   npm install -g firebase-tools
   ```

2. **Initialize Firebase**
   ```bash
   firebase init hosting
   ```

3. **Configure firebase.json**
   ```json
   {
     "hosting": {
       "public": "frontend/dist",
       "ignore": [
         "firebase.json",
         "**/.*",
         "**/node_modules/**"
       ],
       "rewrites": [
         {
           "source": "**",
           "destination": "/index.html"
         }
       ],
       "headers": [
         {
           "source": "/assets/**",
           "headers": [
             {
               "key": "Cache-Control",
               "value": "max-age=31536000"
             }
           ]
         }
       ]
     }
   }
   ```

4. **Deploy**
   ```bash
   firebase deploy --only hosting
   ```

### Option 5: Docker + Nginx (Containerized)

Already configured! See `Dockerfile.frontend`.

#### Deploy Container

```bash
# Build image
docker build -f Dockerfile.frontend -t faq-frontend .

# Run container
docker run -d -p 80:80 --name faq-frontend faq-frontend
```

#### With Docker Compose

```bash
docker-compose up frontend
```

## Environment Variables

### Build-Time Variables

Vite requires environment variables to be:
1. Prefixed with `VITE_`
2. Set before building
3. Available at build time (not runtime)

### Setting Variables

**Linux/Mac:**
```bash
export VITE_API_BASE_URL=https://api.example.com
npm run build
```

**Windows:**
```cmd
set VITE_API_BASE_URL=https://api.example.com
npm run build
```

**Using .env file:**
```bash
# frontend/.env.production
VITE_API_BASE_URL=https://api.example.com
```

Then build:
```bash
npm run build
```

## SPA Routing Configuration

All static hosts need to redirect all routes to `index.html` for client-side routing.

### Vercel
Already configured in `vercel.json`

### Netlify
Already configured in `netlify.toml`

### AWS S3 + CloudFront
- S3: Set error document to `index.html`
- CloudFront: Add error page rule (404 → `/index.html` with 200)

### GitHub Pages
Use `gh-pages` with `--add-history` flag or configure 404.html

### Cloudflare Pages
Automatic - Cloudflare handles SPA routing

### Firebase Hosting
Configured in `firebase.json` rewrites

## Caching Strategy

### Static Assets
- Cache for 1 year (immutable)
- Use content hashing in filenames
- Vite does this automatically

### HTML Files
- Short cache (revalidate)
- Always fetch latest HTML

### Configuration Examples

**Vercel** (`vercel.json`):
```json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

**Netlify** (`netlify.toml`):
```toml
[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

## Security Headers

### Recommended Headers

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

### Adding to Vercel

In `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### 404 on Refresh

**Problem**: Direct URL access returns 404

**Solution**: Configure SPA routing (redirect all routes to index.html)

### Environment Variables Not Working

**Problem**: Variables undefined in production

**Solution**: 
1. Ensure variables start with `VITE_`
2. Set variables before building
3. Rebuild after changing variables

### CORS Errors

**Problem**: API calls blocked by CORS

**Solution**:
1. Verify backend CORS configuration
2. Check `VITE_API_BASE_URL` is correct
3. Ensure backend allows frontend domain

### Build Fails

**Problem**: Build errors in CI/CD

**Solution**:
1. Test build locally first
2. Check Node version compatibility
3. Verify all dependencies are in package.json

## Comparison Table

| Provider | Free Tier | CDN | SSL | Custom Domain | CI/CD |
|----------|-----------|-----|-----|---------------|-------|
| Vercel | ✅ | ✅ | ✅ | ✅ | ✅ |
| Netlify | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cloudflare Pages | ✅ | ✅ | ✅ | ✅ | ✅ |
| GitHub Pages | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Firebase Hosting | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| AWS S3+CF | ❌ | ✅ | ✅ | ✅ | ⚠️ |

## Recommendation

**For Quick Deployment**: Vercel or Netlify
- Easiest setup
- Automatic SSL
- Built-in CI/CD
- Free tier

**For Enterprise**: AWS S3 + CloudFront
- More control
- Better for high scale
- Requires more setup

**For Containerized**: Docker + Nginx
- Full control
- Can deploy anywhere
- Requires container orchestration

## Next Steps

1. Choose hosting provider
2. Set up environment variables
3. Configure custom domain
4. Set up monitoring
5. Configure CI/CD

