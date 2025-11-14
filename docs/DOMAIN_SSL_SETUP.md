# Domain Name and SSL Certificate Configuration Guide

This guide covers setting up custom domain names and SSL certificates for the FAQ Assistant deployment.

## Overview

Both Railway (backend) and Vercel (frontend) provide automatic SSL certificates via Let's Encrypt. This guide covers:
- Setting up custom domains
- SSL certificate configuration
- DNS configuration
- Troubleshooting

## Railway (Backend) Domain Setup

### Step 1: Add Custom Domain in Railway

1. Go to Railway dashboard
2. Select your backend service
3. Navigate to **Settings** → **Networking**
4. Click **"Add Custom Domain"** or **"Generate Domain"**

### Step 2: Railway-Generated Domain (Quick Start)

Railway provides a free subdomain:
- Format: `your-service-name.up.railway.app`
- SSL: Automatically provisioned
- No DNS configuration needed

### Step 3: Custom Domain Configuration

If you have your own domain:

1. **Add Domain in Railway**
   - Enter your domain: `api.yourdomain.com`
   - Railway will show DNS configuration needed

2. **Configure DNS Records**

   **Option A: CNAME Record (Recommended for subdomains)**
   ```
   Type: CNAME
   Name: api (or @ for root)
   Value: your-service.up.railway.app
   TTL: 3600 (or default)
   ```

   **Option B: A Record (For apex/root domain)**
   ```
   Type: A
   Name: @
   Value: [Railway IP addresses - provided in dashboard]
   TTL: 3600
   ```

3. **Wait for DNS Propagation**
   - Usually takes 5-60 minutes
   - Check with: `dig api.yourdomain.com` or `nslookup api.yourdomain.com`

4. **SSL Certificate Provision**
   - Railway automatically provisions SSL via Let's Encrypt
   - Usually completes within 5-10 minutes after DNS propagates
   - Check status in Railway dashboard

### Step 4: Verify SSL Certificate

```bash
# Check SSL certificate
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com

# Or use online tool
# https://www.ssllabs.com/ssltest/
```

## Vercel (Frontend) Domain Setup

### Step 1: Add Domain in Vercel

1. Go to Vercel dashboard
2. Select your project
3. Navigate to **Settings** → **Domains**
4. Click **"Add Domain"**

### Step 2: Add Domain

Enter your domain:
- Root domain: `yourdomain.com`
- Subdomain: `www.yourdomain.com` or `app.yourdomain.com`

### Step 3: Configure DNS Records

Vercel will show required DNS records:

**For Root Domain (apex):**
```
Type: A
Name: @
Value: 76.76.21.21 (Vercel IP - check dashboard for current IPs)
TTL: 3600
```

**For Subdomain:**
```
Type: CNAME
Name: www (or your subdomain)
Value: cname.vercel-dns.com
TTL: 3600
```

**Alternative: Use CNAME Flattening (if supported by DNS provider)**
```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
TTL: 3600
```

### Step 4: SSL Certificate Provision

- Vercel automatically provisions SSL via Let's Encrypt
- Usually completes within 5-10 minutes after DNS propagates
- Check status in Vercel dashboard → Domains

### Step 5: Verify SSL Certificate

```bash
# Check SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Or visit: https://yourdomain.com
```

## DNS Provider Configuration

### Common DNS Providers

#### Cloudflare

1. **Add Domain to Cloudflare**
   - Add site → Enter domain
   - Cloudflare will scan existing DNS records

2. **Add DNS Records**
   - Go to DNS → Records
   - Add CNAME or A record as shown in Railway/Vercel

3. **SSL/TLS Settings**
   - SSL/TLS → Encryption mode: **Full** or **Full (strict)**
   - This ensures end-to-end encryption

4. **Proxy Status**
   - Orange cloud (proxied): Recommended for DDoS protection
   - Gray cloud (DNS only): Use if having SSL issues

#### Namecheap

1. **Go to Domain List**
2. **Click Manage** next to your domain
3. **Go to Advanced DNS**
4. **Add Records**
   - Host Record: `api` (or `www`)
   - Type: CNAME or A
   - Value: As provided by Railway/Vercel
   - TTL: Automatic

#### GoDaddy

1. **Go to My Products** → **DNS**
2. **Add Record**
   - Type: CNAME or A
   - Name: `api` (or `www`)
   - Value: As provided by Railway/Vercel
   - TTL: 1 Hour

#### Google Domains

1. **Go to DNS** section
2. **Add Custom Records**
   - Type: CNAME or A
   - Name: `api` (or `www`)
   - Value: As provided by Railway/Vercel
   - TTL: 3600

## SSL Certificate Details

### Automatic SSL (Let's Encrypt)

Both Railway and Vercel use Let's Encrypt for automatic SSL:
- **Free**: No cost
- **Automatic Renewal**: Certificates auto-renew every 90 days
- **Wildcard Support**: Available on some platforms
- **Validation**: Automatic via DNS or HTTP

### Certificate Types

1. **Single Domain**
   - Covers: `api.yourdomain.com`
   - Most common for subdomains

2. **Wildcard**
   - Covers: `*.yourdomain.com`
   - Useful for multiple subdomains
   - Requires DNS validation

3. **Multi-Domain**
   - Covers multiple specific domains
   - Useful for multiple domains

## Environment Configuration

### Update Environment Variables

After setting up domains, update environment variables:

**Backend (Railway):**
```bash
# No changes needed - Railway uses PORT environment variable
# Domain is configured in Railway dashboard
```

**Frontend (Vercel):**
```bash
# Update VITE_API_BASE_URL to use custom domain
VITE_API_BASE_URL=https://api.yourdomain.com
```

**Backend CORS:**
```bash
# Update CORS_ORIGINS_ENV to include frontend domain
CORS_ORIGINS_ENV=https://yourdomain.com,https://www.yourdomain.com
```

## Domain Verification

### Check DNS Propagation

```bash
# Using dig
dig api.yourdomain.com
dig www.yourdomain.com

# Using nslookup
nslookup api.yourdomain.com
nslookup www.yourdomain.com

# Online tools
# https://dnschecker.org/
# https://www.whatsmydns.net/
```

### Check SSL Certificate

```bash
# Command line
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com

# Online tools
# https://www.ssllabs.com/ssltest/
# https://www.sslshopper.com/ssl-checker.html
```

### Verify HTTPS Access

```bash
# Test backend
curl https://api.yourdomain.com/health

# Test frontend
curl -I https://yourdomain.com
```

## Troubleshooting

### DNS Not Propagating

**Problem**: DNS changes not visible

**Solutions**:
1. Wait longer (can take up to 48 hours, usually 5-60 minutes)
2. Clear DNS cache: `sudo dscacheutil -flushcache` (Mac) or `ipconfig /flushdns` (Windows)
3. Check DNS records are correct
4. Verify DNS provider settings

### SSL Certificate Not Issuing

**Problem**: SSL certificate not provisioning

**Solutions**:
1. Verify DNS is fully propagated
2. Check domain is correctly configured in Railway/Vercel
3. Ensure port 80/443 is accessible
4. Wait 10-15 minutes after DNS propagation
5. Check Railway/Vercel logs for errors

### Mixed Content Warnings

**Problem**: HTTP resources on HTTPS page

**Solutions**:
1. Ensure all API calls use HTTPS
2. Update `VITE_API_BASE_URL` to use HTTPS
3. Check for hardcoded HTTP URLs
4. Use relative URLs where possible

### CORS Errors After Domain Setup

**Problem**: CORS errors with custom domain

**Solutions**:
1. Update `CORS_ORIGINS_ENV` to include new domain
2. Ensure protocol matches (HTTPS)
3. Check for trailing slashes
4. Verify backend CORS configuration

### Certificate Expiration

**Problem**: SSL certificate expired

**Solutions**:
1. Railway/Vercel auto-renew certificates
2. If manual renewal needed, check platform documentation
3. Verify DNS records are still correct
4. Check platform status page for issues

## Best Practices

### Domain Naming

1. **Use Subdomains**
   - `api.yourdomain.com` for backend
   - `app.yourdomain.com` or `www.yourdomain.com` for frontend
   - Easier DNS management

2. **Consistent Naming**
   - Use clear, descriptive subdomains
   - Follow company naming conventions

3. **Avoid Root Domain for API**
   - Use subdomain for API (e.g., `api.yourdomain.com`)
   - Keep root domain for main website

### SSL Configuration

1. **Force HTTPS**
   - Configure redirects from HTTP to HTTPS
   - Railway/Vercel do this automatically

2. **HSTS Headers**
   - Enable HTTP Strict Transport Security
   - Vercel enables this automatically
   - Railway: Configure in application

3. **Certificate Monitoring**
   - Monitor certificate expiration
   - Set up alerts if possible

### DNS Management

1. **Use Short TTL During Setup**
   - TTL: 300 (5 minutes) during initial setup
   - Change to 3600 (1 hour) after verification

2. **Keep DNS Records Updated**
   - Document all DNS records
   - Update when changing providers

3. **Use DNS Provider Features**
   - Cloudflare: Use proxy for DDoS protection
   - Enable DNSSEC if available

## Example Configuration

### Complete Setup Example

**Backend (Railway):**
- Domain: `api.faq-assistant.com`
- DNS: CNAME → `your-service.up.railway.app`
- SSL: Automatic via Let's Encrypt
- Status: ✅ Active

**Frontend (Vercel):**
- Domain: `faq-assistant.com` (root)
- DNS: A record → Vercel IPs
- SSL: Automatic via Let's Encrypt
- Status: ✅ Active

**Environment Variables:**

Backend:
```bash
CORS_ORIGINS_ENV=https://faq-assistant.com,https://www.faq-assistant.com
```

Frontend:
```bash
VITE_API_BASE_URL=https://api.faq-assistant.com
```

## Security Considerations

1. **Always Use HTTPS**
   - Never use HTTP in production
   - Redirect HTTP to HTTPS

2. **Validate Certificates**
   - Use valid SSL certificates
   - Check certificate chain

3. **Monitor Certificate Status**
   - Set up monitoring
   - Check expiration dates

4. **Use Strong Cipher Suites**
   - Railway/Vercel configure this automatically
   - Verify with SSL Labs test

## Support

- **Railway**: https://docs.railway.app/networking/custom-domains
- **Vercel**: https://vercel.com/docs/concepts/projects/domains
- **Let's Encrypt**: https://letsencrypt.org/docs/
- **SSL Labs**: https://www.ssllabs.com/ssltest/

## Next Steps

1. Set up custom domains
2. Verify SSL certificates
3. Update environment variables
4. Test HTTPS access
5. Configure monitoring

