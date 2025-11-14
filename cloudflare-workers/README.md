# Cloudflare Workers CDN Configuration

Optional Cloudflare Workers script for advanced CDN configuration.

## When to Use

Use this if you:
- Want custom CDN logic beyond Cloudflare Pages
- Need advanced cache control
- Want to add custom headers
- Need request/response transformation

## Setup

1. **Create Cloudflare Worker**
   - Go to Cloudflare Dashboard → Workers
   - Create new Worker
   - Copy code from `cdn-config.js`

2. **Add Route**
   - Workers → Routes
   - Add route: `yourdomain.com/*`
   - Select your worker

3. **Deploy**
   - Click "Save and Deploy"

## Features

- Custom cache headers based on file type
- Security headers
- Request/response transformation

## Note

If using Cloudflare Pages, this is optional. Cloudflare Pages handles CDN automatically.

