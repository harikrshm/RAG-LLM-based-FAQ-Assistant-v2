# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Access to hosting platform (AWS, GCP, Azure, Vercel, Railway, etc.)
- Domain name (optional)
- SSL certificate (for production)

## Deployment Options

### Option 1: Docker Compose (Recommended for VPS/Cloud)

1. **Prepare Environment Files**

```bash
# Copy and configure environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env and add your API keys
# Edit frontend/.env and set VITE_API_BASE_URL
```

2. **Build and Deploy**

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

3. **Update Frontend API URL**

Update `VITE_API_BASE_URL` in `frontend/.env` to point to your backend URL, then rebuild:

```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Option 2: Separate Backend and Frontend Deployment

#### Backend Deployment (FastAPI)

**Using Railway/Render/Fly.io:**

1. Connect your repository
2. Set environment variables
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

**Using AWS/GCP/Azure:**

1. Build Docker image:
```bash
docker build -f Dockerfile.backend -t faq-backend .
```

2. Push to container registry
3. Deploy to container service (ECS, Cloud Run, Container Instances)

#### Frontend Deployment (React)

**Using Vercel (Recommended):**

See [Vercel Deployment Guide](./VERCEL_DEPLOYMENT.md) for detailed instructions.

Quick steps:
1. Connect repository to Vercel
2. Configure build settings (auto-detected)
3. Set environment variable: `VITE_API_BASE_URL`
4. Deploy automatically on push

**Using Netlify:**

See [Static Hosting Guide](./STATIC_HOSTING.md) for detailed instructions.

Quick steps:
1. Connect repository to Netlify
2. Build command: `cd frontend && npm install && npm run build`
3. Output directory: `frontend/dist`
4. Set environment variable: `VITE_API_BASE_URL`

**Using Static Hosting (S3, GitHub Pages, etc.):**

See [Static Hosting Guide](./STATIC_HOSTING.md) for detailed instructions.

Quick steps:
1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Upload `frontend/dist/` folder to your hosting provider
3. Configure SPA routing (redirect all routes to index.html)

## Environment-Specific Configuration

### Development

- Use `.env` files with development values
- Enable hot reload
- Use local vector database

### Production

- Set `API_RELOAD=false` in backend
- Use production LLM API keys
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Enable monitoring and logging
- Use persistent volumes for vector database

## Monitoring

### Health Checks

The backend includes a health check endpoint at `/health`. Configure your hosting platform to use this for health monitoring.

### Logging

- Backend logs: Check `backend/logs/app.log` or container logs
- Frontend logs: Check browser console and hosting platform logs

### Metrics

Consider integrating:
- Sentry for error tracking
- Prometheus for metrics
- Grafana for visualization

## Scaling

### Horizontal Scaling

- Use load balancer for backend
- Deploy multiple backend instances
- Use shared vector database (ChromaDB with persistent storage)

### Vertical Scaling

- Increase container resources
- Optimize vector database performance
- Use GPU for embeddings (if available)

## Security Checklist

- [ ] Set strong `SECRET_KEY` in production
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up API authentication (if needed)
- [ ] Secure environment variables
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Regular security updates

## Troubleshooting

### Backend Issues

- Check logs: `docker-compose logs backend`
- Verify environment variables
- Check vector database connectivity
- Verify LLM API key

### Frontend Issues

- Check browser console
- Verify API URL configuration
- Check CORS settings
- Verify build output

## Rollback Procedure

1. Keep previous Docker images tagged
2. Update docker-compose.yml to use previous image
3. Run `docker-compose up -d`
4. Monitor health checks

