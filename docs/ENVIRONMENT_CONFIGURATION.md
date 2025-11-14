# Environment-Specific Configuration Guide

This guide explains how to configure different environments (development, staging, production) for the FAQ Assistant.

## Overview

The application supports three environments:
- **Development**: Local development with hot reload and debug features
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

## Environment Files

### Backend Environment Files

- `backend/.env.development.example` - Development configuration template
- `backend/.env.staging.example` - Staging configuration template
- `backend/.env.production.example` - Production configuration template

### Frontend Environment Files

- `frontend/.env.development.example` - Development configuration template
- `frontend/.env.staging.example` - Staging configuration template
- `frontend/.env.production.example` - Production configuration template

## Development Environment

### Purpose

Local development with:
- Hot reload enabled
- Debug mode enabled
- Verbose logging
- Local database
- Lenient rate limiting

### Backend Configuration

**File**: `backend/.env.development`

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
VECTORDB_PATH=data/vectordb
RATE_LIMIT_PER_MINUTE=120
```

**Key Settings:**
- `DEBUG=true`: Enable debug mode
- `LOG_LEVEL=DEBUG`: Verbose logging
- `CORS_ORIGINS`: Localhost origins
- `VECTORDB_PATH`: Local path (not `/app/data`)
- `RATE_LIMIT_PER_MINUTE=120`: More lenient for testing

### Frontend Configuration

**File**: `frontend/.env.development`

```bash
VITE_API_BASE_URL=http://localhost:8000
```

**Key Settings:**
- `VITE_API_BASE_URL`: Points to local backend
- Hot reload enabled automatically

### Running Development

**Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Staging Environment

### Purpose

Pre-production testing with:
- Production-like configuration
- Staging database
- Moderate rate limiting
- Error tracking enabled

### Backend Configuration

**File**: `backend/.env.staging` (set in Railway/Vercel)

```bash
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yourdomain.com,https://staging-frontend.vercel.app
VECTORDB_PATH=/app/data/vectordb
RATE_LIMIT_PER_MINUTE=60
```

**Key Settings:**
- `ENVIRONMENT=staging`: Identifies staging
- `DEBUG=false`: Production-like behavior
- `LOG_LEVEL=INFO`: Standard logging
- `CORS_ORIGINS`: Staging domains only
- `VECTORDB_PATH=/app/data/vectordb`: Persistent storage

### Frontend Configuration

**File**: `frontend/.env.staging` (set in Vercel)

```bash
VITE_API_BASE_URL=https://staging-api.yourdomain.com
```

**Key Settings:**
- `VITE_API_BASE_URL`: Points to staging backend

### Deploying to Staging

**Railway (Backend):**
1. Create staging service
2. Set environment variables
3. Deploy from `develop` branch

**Vercel (Frontend):**
1. Create preview deployment
2. Set environment variables for Preview
3. Deploy from `develop` branch

## Production Environment

### Purpose

Live production environment with:
- Optimized performance
- Security hardened
- Monitoring enabled
- Strict rate limiting

### Backend Configuration

**File**: `backend/.env.production` (set in Railway)

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS_ENV=https://yourdomain.com,https://www.yourdomain.com
VECTORDB_PATH=/app/data/vectordb
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

**Key Settings:**
- `ENVIRONMENT=production`: Identifies production
- `DEBUG=false`: No debug mode
- `LOG_LEVEL=INFO`: Standard logging (not DEBUG)
- `CORS_ORIGINS_ENV`: Production domains only
- `RATE_LIMIT_PER_MINUTE=60`: Standard rate limiting
- `VECTORDB_PATH=/app/data/vectordb`: Persistent storage

### Frontend Configuration

**File**: `frontend/.env.production` (set in Vercel)

```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

**Key Settings:**
- `VITE_API_BASE_URL`: Points to production backend

### Deploying to Production

**Railway (Backend):**
1. Use production service
2. Set environment variables
3. Deploy from `main` branch

**Vercel (Frontend):**
1. Use production deployment
2. Set environment variables for Production
3. Deploy from `main` branch

## Environment Variable Comparison

### Backend Variables

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `ENVIRONMENT` | `development` | `staging` | `production` |
| `DEBUG` | `true` | `false` | `false` |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `INFO` |
| `CORS_ORIGINS` | `localhost:*` | `staging.*` | `yourdomain.com` |
| `VECTORDB_PATH` | `data/vectordb` | `/app/data/vectordb` | `/app/data/vectordb` |
| `RATE_LIMIT_PER_MINUTE` | `120` | `60` | `60` |
| `RATE_LIMIT_PER_HOUR` | `2000` | `1000` | `1000` |

### Frontend Variables

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://staging-api.*` | `https://api.yourdomain.com` |

## Platform-Specific Configuration

### Railway (Backend)

**Development:**
- Use local `.env.development` file
- Run locally with `uvicorn --reload`

**Staging:**
- Create separate Railway service
- Set environment variables in Railway dashboard
- Deploy from `develop` branch

**Production:**
- Use main Railway service
- Set environment variables in Railway dashboard
- Deploy from `main` branch

### Vercel (Frontend)

**Development:**
- Use local `.env.development` file
- Run locally with `npm run dev`

**Staging:**
- Set environment variables for "Preview" environment
- Deploy from `develop` branch
- Preview URLs automatically generated

**Production:**
- Set environment variables for "Production" environment
- Deploy from `main` branch
- Uses production domain

## Setting Environment Variables

### Local Development

**Backend:**
```bash
cd backend
cp .env.development.example .env.development
# Edit .env.development with your values
```

**Frontend:**
```bash
cd frontend
cp .env.development.example .env.development
# Edit .env.development with your values
```

### Railway (Backend)

1. Go to Railway dashboard
2. Select service
3. Go to Variables tab
4. Add variables:
   - Click "New Variable"
   - Enter name and value
   - Select environment (if applicable)

### Vercel (Frontend)

1. Go to Vercel dashboard
2. Select project
3. Go to Settings → Environment Variables
4. Add variables:
   - Enter name and value
   - Select environments (Production, Preview, Development)
   - Click "Save"

## Environment Detection

### Backend

The backend detects environment from:
1. `ENVIRONMENT` environment variable
2. Falls back to `development` if not set

The `Settings` class automatically loads environment-specific `.env` files:
- `.env.development` when `ENVIRONMENT=development`
- `.env.staging` when `ENVIRONMENT=staging`
- `.env.production` when `ENVIRONMENT=production`
- Falls back to `.env` if environment-specific file doesn't exist

```python
ENVIRONMENT: str = "development"  # Default
```

**Note**: Set the `ENVIRONMENT` variable before starting the application to load the correct configuration file.

### Frontend

Vite automatically loads environment files:
- `.env.development` - Development
- `.env.staging` - Staging (if using Vite mode)
- `.env.production` - Production
- `.env.local` - Local overrides (gitignored)

## Best Practices

### ✅ Do

1. **Use Different API Keys**: Separate keys per environment
2. **Restrict CORS**: Only allow necessary origins
3. **Disable Debug**: Never enable debug in production
4. **Use Secrets**: Store sensitive data in platform secrets
5. **Document Changes**: Update this guide when adding variables
6. **Test Locally**: Test with development config first

### ❌ Don't

1. **Don't Commit Secrets**: Never commit `.env` files
2. **Don't Share Keys**: Use different keys per environment
3. **Don't Enable Debug in Production**: Security risk
4. **Don't Use Production Data**: Use test data in dev/staging
5. **Don't Skip Validation**: Verify environment variables

## Migration Between Environments

### Development → Staging

1. Copy development config
2. Update URLs to staging
3. Update CORS origins
4. Change `ENVIRONMENT=staging`
5. Set `DEBUG=false`
6. Deploy to staging

### Staging → Production

1. Copy staging config
2. Update URLs to production
3. Update CORS origins
4. Change `ENVIRONMENT=production`
5. Verify all settings
6. Deploy to production

## Troubleshooting

### Wrong Environment Detected

**Problem**: Application using wrong environment

**Solutions**:
1. Check `ENVIRONMENT` variable is set correctly
2. Verify environment file is loaded
3. Check platform environment settings
4. Restart application

### Environment Variables Not Loading

**Problem**: Variables not available

**Solutions**:
1. Check file name matches environment
2. Verify file location
3. Check platform environment settings
4. Restart application

### CORS Errors in Staging/Production

**Problem**: CORS errors after deployment

**Solutions**:
1. Verify `CORS_ORIGINS_ENV` includes correct domains
2. Check protocol matches (https)
3. Ensure no trailing slashes
4. Restart backend after changes

## Quick Reference

### Development

```bash
# Backend
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:*

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### Staging

```bash
# Backend
ENVIRONMENT=staging
DEBUG=false
CORS_ORIGINS_ENV=https://staging.*

# Frontend
VITE_API_BASE_URL=https://staging-api.yourdomain.com
```

### Production

```bash
# Backend
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS_ENV=https://yourdomain.com

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Related Documentation

- [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md) - Complete variable reference
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Deployment instructions
- [Railway Deployment](./RAILWAY_DEPLOYMENT.md) - Railway-specific setup
- [Vercel Deployment](./VERCEL_DEPLOYMENT.md) - Vercel-specific setup

