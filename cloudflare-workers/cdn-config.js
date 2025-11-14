/**
 * Cloudflare Workers CDN Configuration
 * 
 * Optional: Use Cloudflare Workers for advanced CDN configuration
 * This is only needed if you want custom CDN logic beyond Cloudflare Pages
 */

/**
 * Cloudflare Worker to enhance CDN caching and headers
 * 
 * To use:
 * 1. Create a Cloudflare Worker
 * 2. Copy this code
 * 3. Add route: yourdomain.com/*
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  // Get response from origin
  const response = await fetch(request);
  
  // Clone response to modify headers
  const newResponse = new Response(response.body, response);
  
  // Set cache headers based on file type
  if (url.pathname.startsWith('/assets/')) {
    // Static assets: Long cache (1 year)
    newResponse.headers.set(
      'Cache-Control',
      'public, max-age=31536000, immutable'
    );
  } else if (url.pathname === '/index.html' || url.pathname === '/') {
    // HTML: No cache
    newResponse.headers.set(
      'Cache-Control',
      'public, max-age=0, must-revalidate'
    );
  } else if (/\.(js|css|woff2?|png|jpg|jpeg|gif|svg|ico|webp)$/.test(url.pathname)) {
    // Other static files: Long cache
    newResponse.headers.set(
      'Cache-Control',
      'public, max-age=31536000, immutable'
    );
  }
  
  // Security headers
  newResponse.headers.set('X-Content-Type-Options', 'nosniff');
  newResponse.headers.set('X-Frame-Options', 'SAMEORIGIN');
  newResponse.headers.set(
    'Referrer-Policy',
    'strict-origin-when-cross-origin'
  );
  
  return newResponse;
}

