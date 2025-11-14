# CORS Configuration Guide

This guide explains how to configure CORS (Cross-Origin Resource Sharing) for the FAQ Assistant widget to allow embedding on Groww's website and other domains.

## Overview

CORS is required when the chat widget (frontend) is hosted on a different domain than the backend API. This is common when:
- Frontend is hosted on Vercel/Netlify
- Backend is hosted on Railway/AWS
- Widget is embedded on Groww's website (different domain)

## Current Configuration

The backend uses FastAPI's `CORSMiddleware` with the following settings:

```python
CORSMiddleware(
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", ...],
    expose_headers=["X-Request-ID", "X-Response-Time"],
    max_age=3600,
)
```

## Configuration Methods

### Method 1: Environment Variable (Recommended for Production)

Set `CORS_ORIGINS_ENV` environment variable with comma-separated origins:

```bash
# Production
CORS_ORIGINS_ENV=https://groww.in,https://www.groww.in,https://app.groww.in

# Staging
CORS_ORIGINS_ENV=https://staging.groww.in,https://staging-frontend.vercel.app

# Development
CORS_ORIGINS_ENV=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173
```

**Advantages:**
- Easy to update without code changes
- Supports multiple environments
- Can be set per deployment

### Method 2: Settings File (For Development)

Update `backend/config/settings.py`:

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://groww.in",
    "https://www.groww.in",
]
```

## CORS Headers Explained

### Request Headers (Allowed)

- `Content-Type`: Required for JSON requests
- `Authorization`: For future authentication
- `Accept`: Requested response format
- `Origin`: Automatically set by browser
- `X-Requested-With`: Common header for AJAX requests
- `X-Request-ID`: For request tracking

### Response Headers (Exposed)

- `X-Request-ID`: Request tracking ID
- `X-Response-Time`: Response processing time

### Methods Allowed

- `GET`: For health checks and readiness checks
- `POST`: For chat API requests
- `OPTIONS`: For CORS preflight requests

## Widget Embedding Scenarios

### Scenario 1: Widget on Groww Domain

**Setup:**
```bash
CORS_ORIGINS_ENV=https://groww.in,https://www.groww.in
```

**How it works:**
- Widget JavaScript loads from Groww's domain
- Makes API calls to backend (different domain)
- Browser checks CORS headers
- Request allowed if origin matches

### Scenario 2: Widget on Subdomain

**Setup:**
```bash
CORS_ORIGINS_ENV=https://app.groww.in,https://invest.groww.in
```

**Note:** Each subdomain needs to be explicitly listed.

### Scenario 3: Development/Testing

**Setup:**
```bash
CORS_ORIGINS_ENV=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173
```

## Preflight Requests

When making cross-origin requests, browsers send OPTIONS requests first:

```
OPTIONS /api/chat HTTP/1.1
Origin: https://groww.in
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

**Response:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://groww.in
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, Accept
Access-Control-Max-Age: 3600
```

The `max_age=3600` setting caches preflight responses for 1 hour, reducing overhead.

## Security Considerations

### ✅ Best Practices

1. **Specific Origins**: List exact domains, avoid wildcards in production
2. **HTTPS Only**: Use HTTPS origins in production
3. **No Wildcards**: Don't use `["*"]` in production
4. **Credentials**: Only enable if needed (currently enabled for session management)

### ⚠️ Security Warnings

**Don't do this:**
```python
allow_origins=["*"]  # ❌ Allows any domain - security risk!
```

**Do this instead:**
```python
allow_origins=["https://groww.in", "https://www.groww.in"]  # ✅ Specific domains
```

## Troubleshooting

### CORS Error: "No 'Access-Control-Allow-Origin' header"

**Problem**: Origin not in allowed list

**Solution**:
1. Check `CORS_ORIGINS_ENV` includes your domain
2. Verify domain matches exactly (including protocol and port)
3. Check for trailing slashes
4. Restart backend after changing environment variables

### CORS Error: "Credentials flag is true, but origin is not allowed"

**Problem**: `allow_credentials=True` but origin not allowed

**Solution**:
1. Ensure origin is explicitly listed (no wildcards)
2. Check protocol matches (http vs https)
3. Verify domain spelling

### Preflight Request Fails

**Problem**: OPTIONS request returns 404 or error

**Solution**:
1. Verify `allow_methods` includes "OPTIONS"
2. Check middleware order (CORS should be early)
3. Ensure OPTIONS requests aren't blocked by rate limiting

### CORS Works Locally but Not in Production

**Problem**: Different behavior in production

**Solution**:
1. Check environment variables are set correctly
2. Verify production domain matches exactly
3. Check for HTTPS/HTTP mismatch
4. Review production logs for CORS errors

## Testing CORS

### Test with curl

```bash
# Test preflight request
curl -X OPTIONS https://api.yourdomain.com/api/chat \
  -H "Origin: https://groww.in" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Check response headers
# Should include: Access-Control-Allow-Origin: https://groww.in
```

### Test in Browser Console

```javascript
// Test from Groww domain
fetch('https://api.yourdomain.com/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'test',
    sessionId: 'test-session'
  }),
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('CORS Error:', error));
```

### Browser DevTools

1. Open browser DevTools (F12)
2. Go to Network tab
3. Make a request from widget
4. Check request/response headers:
   - Request: `Origin` header
   - Response: `Access-Control-Allow-Origin` header
5. Look for CORS errors in Console tab

## Common Configurations

### Production (Groww Website)

```bash
CORS_ORIGINS_ENV=https://groww.in,https://www.groww.in,https://app.groww.in
```

### Staging

```bash
CORS_ORIGINS_ENV=https://staging.groww.in,https://staging-frontend.vercel.app
```

### Development

```bash
CORS_ORIGINS_ENV=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173
```

### Multi-Environment (Railway/Vercel)

Set different values per environment:
- **Production**: Groww domains
- **Preview**: Preview deployment URLs
- **Development**: Localhost URLs

## Advanced Configuration

### Wildcard Subdomains (Not Recommended)

If you need to support all subdomains:

```python
# Custom CORS origin function
def is_allowed_origin(origin: str) -> bool:
    allowed_domains = ["groww.in", "yourdomain.com"]
    for domain in allowed_domains:
        if origin.endswith(f".{domain}") or origin == f"https://{domain}":
            return True
    return False
```

**Note**: This requires custom middleware, not recommended for security.

### Dynamic Origin Validation

For more complex scenarios, you can create custom middleware:

```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

def validate_origin(origin: str) -> bool:
    # Custom validation logic
    allowed_patterns = [
        r"^https://.*\.groww\.in$",
        r"^https://groww\.in$",
    ]
    import re
    for pattern in allowed_patterns:
        if re.match(pattern, origin):
            return True
    return False
```

## Monitoring

### Log CORS Requests

CORS errors are logged by FastAPI. Check logs for:
- `CORS preflight request`
- `CORS origin not allowed`
- `CORS credentials not allowed`

### Metrics

Track CORS-related metrics:
- Preflight request count
- CORS error count
- Origin distribution

## Related Documentation

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md)
- [Deployment Guide](./DEPLOYMENT.md)

## Quick Reference

### Environment Variable

```bash
CORS_ORIGINS_ENV=https://domain1.com,https://domain2.com
```

### Settings File

```python
CORS_ORIGINS = [
    "https://domain1.com",
    "https://domain2.com",
]
```

### Verify Configuration

```bash
# Check current CORS origins
curl https://api.yourdomain.com/health -v

# Test from browser console
fetch('https://api.yourdomain.com/api/chat', {...})
```

## Support

If you encounter CORS issues:

1. Check browser console for specific error messages
2. Verify environment variables are set correctly
3. Check backend logs for CORS-related errors
4. Test with curl to isolate browser vs server issues
5. Review this guide for common solutions

