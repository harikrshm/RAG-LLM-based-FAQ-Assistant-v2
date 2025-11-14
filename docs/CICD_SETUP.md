# CI/CD Pipeline Setup Guide

This guide explains how to set up Continuous Integration and Continuous Deployment (CI/CD) for the FAQ Assistant project.

## Overview

The CI/CD pipeline automates:
- **Testing**: Run tests on every push and pull request
- **Linting**: Check code quality and style
- **Building**: Build Docker images and frontend bundles
- **Deploying**: Automatically deploy to production on main branch

## Pipeline Structure

### GitHub Actions Workflows

Three workflow files are available:

1. **`.github/workflows/backend-ci.yml`**: Backend-specific CI/CD
2. **`.github/workflows/frontend-ci.yml`**: Frontend-specific CI/CD
3. **`.github/workflows/full-ci.yml`**: Combined pipeline for both

## Setup Steps

### Step 1: Configure GitHub Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions → New repository secret

**Required Secrets:**

#### Backend Secrets
```
RAILWAY_TOKEN=your_railway_token
RAILWAY_SERVICE_URL=your-backend.railway.app
GEMINI_API_KEY_TEST=test_api_key_for_ci
DOCKER_USERNAME=your_docker_username (optional)
DOCKER_PASSWORD=your_docker_password (optional)
```

#### Frontend Secrets
```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id
VITE_API_BASE_URL=https://your-backend.railway.app
VERCEL_URL=https://your-frontend.vercel.app
```

### Step 2: Get Railway Token

1. Go to Railway dashboard
2. Click on your profile → Settings → Tokens
3. Create new token
4. Copy token to GitHub secrets as `RAILWAY_TOKEN`

### Step 3: Get Vercel Credentials

1. Go to Vercel dashboard
2. Settings → Tokens → Create Token
3. Copy token to GitHub secrets as `VERCEL_TOKEN`

4. Get Project ID:
   - Go to project settings
   - Copy Project ID to `VERCEL_PROJECT_ID`

5. Get Org ID:
   - Go to team settings
   - Copy Org ID to `VERCEL_ORG_ID`

### Step 4: Enable GitHub Actions

1. Go to repository Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"
3. Save changes

## Workflow Details

### Backend CI/CD Workflow

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Only when `backend/` files change

**Jobs:**

1. **Test**
   - Set up Python 3.11
   - Install dependencies
   - Run linting (black, flake8, isort)
   - Run tests with coverage
   - Upload coverage to Codecov

2. **Build**
   - Build Docker image
   - Cache Docker layers
   - Only runs on push (not PRs)

3. **Deploy**
   - Deploy to Railway
   - Only runs on push to `main`
   - Uses production environment

### Frontend CI/CD Workflow

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Only when `frontend/` files change

**Jobs:**

1. **Test**
   - Set up Node.js 20
   - Install dependencies
   - Run linting (ESLint, Prettier)
   - Run type checking (TypeScript)
   - Run tests

2. **Build**
   - Build frontend application
   - Upload build artifacts
   - Only runs on push

3. **Deploy**
   - Deploy to Vercel
   - Only runs on push to `main`
   - Uses production environment

### Full CI/CD Workflow

Combines both backend and frontend workflows:
- Runs all tests in parallel
- Builds both services
- Deploys both on main branch push

## Workflow Triggers

### On Push to Main

1. ✅ Run all tests
2. ✅ Build both services
3. ✅ Deploy to production

### On Push to Develop

1. ✅ Run all tests
2. ✅ Build both services
3. ❌ No deployment (manual or staging only)

### On Pull Request

1. ✅ Run all tests
2. ❌ No builds
3. ❌ No deployments

## Environment-Specific Deployments

### Production (main branch)

- Backend: Deploys to Railway production
- Frontend: Deploys to Vercel production
- Automatic on push to `main`

### Staging (develop branch)

To enable staging deployments:

1. Create staging environments in Railway/Vercel
2. Add staging secrets:
   ```
   RAILWAY_STAGING_TOKEN
   VERCEL_STAGING_TOKEN
   ```
3. Update workflows to deploy on `develop` branch

### Preview (Pull Requests)

Vercel automatically creates preview deployments for PRs if:
- Vercel is connected to GitHub
- Preview deployments are enabled in Vercel settings

## Manual Deployment

### Deploy Backend Manually

```bash
# Using Railway CLI
railway up

# Or trigger workflow manually
# GitHub → Actions → Backend CI/CD → Run workflow
```

### Deploy Frontend Manually

```bash
# Using Vercel CLI
vercel --prod

# Or trigger workflow manually
# GitHub → Actions → Frontend CI/CD → Run workflow
```

## Testing in CI

### Backend Tests

```yaml
- name: Run tests
  run: pytest --cov=backend --cov-report=xml
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY_TEST }}
```

**Note**: Use a test API key, not production key.

### Frontend Tests

```yaml
- name: Run tests
  run: npm test -- --watchAll=false
  env:
    CI: true
```

**Note**: `CI=true` disables watch mode.

## Caching

### Python Dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'
```

Caches pip packages between runs.

### Node Dependencies

```yaml
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```

Caches npm packages between runs.

### Docker Layers

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

Caches Docker layers using GitHub Actions cache.

## Monitoring CI/CD

### GitHub Actions Dashboard

View workflow runs:
- GitHub → Actions tab
- See status, logs, and artifacts

### Notifications

Configure notifications:
- GitHub → Settings → Notifications
- Enable workflow run notifications

### Status Badges

Add to README.md:

```markdown
![Backend CI](https://github.com/your-org/your-repo/workflows/Backend%20CI%2FCD/badge.svg)
![Frontend CI](https://github.com/your-org/your-repo/workflows/Frontend%20CI%2FCD/badge.svg)
```

## Troubleshooting

### Workflow Not Running

**Problem**: Workflow doesn't trigger

**Solutions**:
1. Check file paths in `paths:` filter
2. Verify branch names match
3. Check workflow file syntax
4. Ensure Actions are enabled

### Tests Failing

**Problem**: Tests fail in CI but pass locally

**Solutions**:
1. Check environment variables are set
2. Verify test API keys
3. Check Python/Node versions match
4. Review test logs for errors

### Deployment Failing

**Problem**: Deployment step fails

**Solutions**:
1. Verify secrets are set correctly
2. Check Railway/Vercel tokens are valid
3. Verify service URLs are correct
4. Check deployment logs

### Build Failing

**Problem**: Build step fails

**Solutions**:
1. Check Dockerfile syntax
2. Verify dependencies are correct
3. Check build logs for errors
4. Test build locally first

## Best Practices

### ✅ Do

1. **Test Before Deploy**: Always run tests first
2. **Use Secrets**: Never commit tokens/keys
3. **Cache Dependencies**: Speed up workflows
4. **Separate Environments**: Different configs for dev/staging/prod
5. **Monitor Deployments**: Watch for failures
6. **Review Logs**: Check workflow logs regularly

### ❌ Don't

1. **Don't Skip Tests**: Always run tests
2. **Don't Commit Secrets**: Use GitHub secrets
3. **Don't Deploy on Every Push**: Only main branch
4. **Don't Ignore Failures**: Fix failing tests
5. **Don't Use Production Keys**: Use test keys in CI

## Advanced Configuration

### Conditional Deployments

Only deploy if tests pass:

```yaml
deploy:
  needs: [test]
  if: github.ref == 'refs/heads/main' && needs.test.result == 'success'
```

### Matrix Testing

Test on multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

### Scheduled Deployments

Deploy on schedule:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
```

## Security

### Secrets Management

- ✅ Use GitHub Secrets for sensitive data
- ✅ Rotate tokens regularly
- ✅ Use different tokens per environment
- ✅ Limit token permissions

### Code Scanning

Add security scanning:

```yaml
- name: Run security scan
  uses: github/super-linter@v4
```

## Related Documentation

- [Railway Deployment Guide](./RAILWAY_DEPLOYMENT.md)
- [Vercel Deployment Guide](./VERCEL_DEPLOYMENT.md)
- [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md)

## Quick Start

1. **Add Secrets**: Configure all required secrets
2. **Push to Main**: Workflow runs automatically
3. **Monitor**: Check Actions tab for status
4. **Verify**: Test deployed application

## Support

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Verify secrets are configured
3. Test locally first
4. Review this guide for common solutions

