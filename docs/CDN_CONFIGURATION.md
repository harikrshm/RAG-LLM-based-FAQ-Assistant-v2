# CDN Configuration Guide

This guide covers configuring Content Delivery Network (CDN) for frontend assets to improve performance and reduce latency.

## Overview

CDN improves performance by:
- **Reducing Latency**: Serving assets from edge locations closer to users
- **Caching**: Storing static assets at edge locations
- **Bandwidth Optimization**: Reducing load on origin server
- **Global Distribution**: Serving content worldwide

## CDN Options

### Option 1: Vercel Built-in CDN (Recommended)

Vercel automatically provides a global CDN for all deployments.

**Features:**
- ✅ Automatic CDN (no configuration needed)
- ✅ Global edge network
- ✅ Automatic HTTPS
- ✅ Image optimization
- ✅ Cache invalidation on deploy

**Configuration:**

Already configured in `vercel.json`:

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

**Cache Strategy:**
- **Static Assets** (`/assets/*`): 1 year cache (immutable)
- **HTML** (`index.html`): No cache (always fresh)
- **Other Files**: Based on file extension

### Option 2: Cloudflare CDN

If you want additional CDN layer or using Cloudflare Pages:

**Setup Steps:**

1. **Add Cloudflare to Domain**
   - Add domain to Cloudflare
   - Update DNS nameservers
   - Enable Cloudflare proxy (orange cloud)

2. **Configure Caching Rules**

   In Cloudflare Dashboard → Rules → Page Rules:

   **Rule 1: Cache Static Assets**
   ```
   URL Pattern: *yourdomain.com/assets/*
   Settings:
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month
   ```

   **Rule 2: Don't Cache HTML**
   ```
   URL Pattern: *yourdomain.com/index.html
   Settings:
   - Cache Level: Bypass
   ```

3. **Configure Browser Cache TTL**

   Cloudflare → Caching → Browser Cache TTL:
   - Set to "Respect Existing Headers"

4. **Enable Auto Minify**

   Cloudflare → Speed → Optimization:
   - ✅ Auto Minify: JavaScript, CSS, HTML

5. **Enable Brotli Compression**

   Cloudflare → Speed → Optimization:
   - ✅ Brotli: Enabled

### Option 3: AWS CloudFront

For AWS deployments:

**Setup Steps:**

1. **Create CloudFront Distribution**
   - Origin: S3 bucket or custom origin
   - Viewer Protocol Policy: Redirect HTTP to HTTPS
   - Allowed HTTP Methods: GET, HEAD, OPTIONS

2. **Configure Cache Behaviors**

   **Default Behavior:**
   - Path Pattern: `*`
   - Cache Policy: CachingOptimized
   - Origin Request Policy: CORS-S3Origin

   **Static Assets:**
   - Path Pattern: `/assets/*`
   - Cache Policy: CachingOptimized
   - TTL: 31536000 (1 year)

3. **Set Cache Headers**

   Use CloudFront Functions or Lambda@Edge to set headers:

   ```javascript
   // Set cache headers for static assets
   if (request.uri.match(/\/assets\//)) {
     response.headers['cache-control'] = {
       value: 'public, max-age=31536000, immutable'
     };
   }
   ```

## Cache Headers Configuration

### Static Assets (JS, CSS, Images)

**Cache-Control Header:**
```
Cache-Control: public, max-age=31536000, immutable
```

**Rationale:**
- `public`: Can be cached by CDN and browsers
- `max-age=31536000`: 1 year cache
- `immutable`: File won't change (content-hashed filenames)

**Implementation:**

Already configured in `vercel.json`:
```json
{
  "source": "/assets/(.*)",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=31536000, immutable"
    }
  ]
}
```

### HTML Files

**Cache-Control Header:**
```
Cache-Control: public, max-age=0, must-revalidate
```

**Rationale:**
- Always fetch latest HTML
- Ensures users get latest version
- Vite injects content-hashed asset references

**Implementation:**

```json
{
  "source": "/index.html",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=0, must-revalidate"
    }
  ]
}
```

### Other Files

**Cache-Control Header:**
```
Cache-Control: public, max-age=86400
```

**Rationale:**
- 1 day cache for other files
- Balance between freshness and performance

## Vite Build Optimization for CDN

### Content Hashing

Vite automatically adds content hashes to filenames:

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        // Content hashing is automatic
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]',
      },
    },
  },
});
```

**Benefits:**
- Filenames change when content changes
- Enables long cache times (immutable)
- Automatic cache invalidation

### Code Splitting

Already configured in `vite.config.ts`:

```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
      },
    },
  },
}
```

**Benefits:**
- Smaller initial bundle
- Better caching (vendor code cached separately)
- Faster subsequent loads

## CDN Performance Optimization

### 1. Enable Compression

**Vercel**: Automatic (Gzip/Brotli)
**Cloudflare**: Enable Auto Minify and Brotli
**CloudFront**: Enable compression in distribution settings

### 2. Image Optimization

**Vercel**: Automatic image optimization
**Cloudflare**: Polish (automatic image optimization)
**CloudFront**: Use Lambda@Edge for image optimization

### 3. HTTP/2 and HTTP/3

All modern CDNs support HTTP/2 and HTTP/3:
- ✅ Vercel: Automatic
- ✅ Cloudflare: Automatic
- ✅ CloudFront: Automatic

### 4. Preconnect and DNS Prefetch

Add to `index.html`:

```html
<link rel="preconnect" href="https://api.yourdomain.com">
<link rel="dns-prefetch" href="https://api.yourdomain.com">
```

## Monitoring CDN Performance

### Key Metrics

1. **Cache Hit Ratio**
   - Target: > 90%
   - Measures: Percentage of requests served from cache

2. **Response Time**
   - Target: < 100ms (from CDN)
   - Measures: Time to first byte

3. **Bandwidth Savings**
   - Measures: Data served from CDN vs origin

### Tools

- **Vercel Analytics**: Built-in performance metrics
- **Cloudflare Analytics**: Detailed CDN metrics
- **CloudFront CloudWatch**: AWS metrics
- **Google Analytics**: Real user monitoring

## Cache Invalidation

### Automatic (Vercel)

Vercel automatically invalidates cache on deployment:
- New deployment → Cache cleared
- No manual action needed

### Manual (Cloudflare)

1. **Purge Everything**
   ```
   Cloudflare Dashboard → Caching → Purge Cache → Purge Everything
   ```

2. **Purge by URL**
   ```
   Cloudflare Dashboard → Caching → Purge Cache → Custom Purge
   ```

### Manual (CloudFront)

1. **Invalidate Paths**
   ```
   AWS Console → CloudFront → Invalidations → Create Invalidation
   Paths: /assets/*
   ```

## Testing CDN Configuration

### Check Cache Headers

```bash
# Check static asset headers
curl -I https://yourdomain.com/assets/index.abc123.js

# Should return:
# Cache-Control: public, max-age=31536000, immutable

# Check HTML headers
curl -I https://yourdomain.com/index.html

# Should return:
# Cache-Control: public, max-age=0, must-revalidate
```

### Test CDN Location

```bash
# Check CDN edge location
curl -I https://yourdomain.com/assets/index.js | grep -i "cf-ray\|x-vercel\|x-amz"

# Vercel: X-Vercel-* headers
# Cloudflare: CF-Ray header
# CloudFront: X-Amz-Cf-* headers
```

### Verify Compression

```bash
# Test Gzip compression
curl -H "Accept-Encoding: gzip" -I https://yourdomain.com/assets/index.js

# Should return:
# Content-Encoding: gzip
```

## Best Practices

### ✅ Do

1. **Use Content Hashing**: Enable long cache times
2. **Cache Static Assets**: 1 year for immutable assets
3. **Don't Cache HTML**: Always fetch latest
4. **Enable Compression**: Gzip/Brotli
5. **Monitor Performance**: Track cache hit ratio
6. **Use CDN**: Leverage edge caching

### ❌ Don't

1. **Don't Cache HTML**: Users need latest version
2. **Don't Use Wildcards**: Be specific with cache rules
3. **Don't Skip Compression**: Significant bandwidth savings
4. **Don't Ignore Metrics**: Monitor CDN performance

## Troubleshooting

### Assets Not Caching

**Problem**: Cache headers not applied

**Solution**:
1. Check `vercel.json` configuration
2. Verify file paths match patterns
3. Check CDN configuration
4. Test with curl to see headers

### Stale Content

**Problem**: Users seeing old version

**Solution**:
1. Verify HTML is not cached
2. Check content hashing is working
3. Clear CDN cache if needed
4. Verify deployment completed

### Slow Asset Loading

**Problem**: Assets loading slowly

**Solution**:
1. Check CDN is enabled
2. Verify edge locations
3. Check compression is enabled
4. Review asset sizes
5. Consider image optimization

## Configuration Files

### vercel.json

Current configuration includes:
- Cache headers for static assets
- Cache headers for HTML
- Security headers

### vite.config.ts

Current configuration includes:
- Code splitting
- Content hashing (automatic)
- Source maps

## Cost Considerations

### Vercel

- **Free Tier**: 100GB bandwidth/month
- **Pro Plan**: Unlimited bandwidth
- CDN included in all plans

### Cloudflare

- **Free Tier**: Unlimited bandwidth
- **Pro Plan**: $20/month (additional features)
- CDN included in all plans

### CloudFront

- **Pay-as-you-go**: Based on data transfer
- **Free Tier**: 50GB/month for 12 months
- Pricing varies by region

## Next Steps

1. Deploy to Vercel (automatic CDN)
2. Verify cache headers
3. Monitor performance
4. Optimize images if needed
5. Set up monitoring

## Related Documentation

- [Vercel Deployment Guide](./VERCEL_DEPLOYMENT.md)
- [Static Hosting Guide](./STATIC_HOSTING.md)
- [Domain and SSL Setup](./DOMAIN_SSL_SETUP.md)

