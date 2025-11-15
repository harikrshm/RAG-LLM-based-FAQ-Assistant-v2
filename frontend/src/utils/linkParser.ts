/**
 * Link Parser Utility
 * 
 * Parses text content and renders URLs as clickable links.
 */

import React from 'react';
import type { Source } from '../types';

/**
 * Regular expression to match URLs
 */
const URL_REGEX = /(https?:\/\/[^\s]+)/g;

/**
 * Regular expression to match markdown-style links [text](url)
 */
const MARKDOWN_LINK_REGEX = /\[([^\]]+)\]\(([^)]+)\)/g;

/**
 * Check if a URL is a Groww page
 */
export function isGrowwUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.includes('groww.in');
  } catch {
    return false;
  }
}

/**
 * Get source type from URL
 */
export function getSourceTypeFromUrl(url: string): Source['sourceType'] {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    
    if (hostname.includes('groww.in')) {
      return 'groww_page';
    } else if (hostname.includes('sebi.gov.in') || hostname.includes('sebi.com')) {
      return 'sebi_website';
    } else if (hostname.includes('amfiindia.com')) {
      return 'amfi_website';
    } else if (
      hostname.includes('sbi') ||
      hostname.includes('hdfc') ||
      hostname.includes('icici') ||
      hostname.includes('axis') ||
      hostname.includes('nippon') ||
      hostname.includes('amc')
    ) {
      return 'amc_website';
    }
    
    return 'unknown';
  } catch {
    return 'unknown';
  }
}

/**
 * Extract domain name from URL for display
 */
export function getDomainName(url: string): string {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname;
    
    // Remove www. prefix
    const domain = hostname.replace(/^www\./, '');
    
    // Extract main domain
    const parts = domain.split('.');
    if (parts.length >= 2) {
      return parts[parts.length - 2] + '.' + parts[parts.length - 1];
    }
    
    return domain;
  } catch {
    return url;
  }
}

/**
 * Parse text and replace URLs with link elements
 */
export interface ParsedLink {
  type: 'text' | 'link';
  content: string;
  url?: string;
  isGroww?: boolean;
  sourceType?: Source['sourceType'];
}

export function parseLinks(text: string): ParsedLink[] {
  const parts: ParsedLink[] = [];
  
  // First, handle markdown-style links [text](url)
  const markdownMatches = Array.from(text.matchAll(MARKDOWN_LINK_REGEX));
  
  if (markdownMatches.length > 0) {
    let currentIndex = 0;
    
    for (const match of markdownMatches) {
      const matchIndex = match.index!;
      const matchLength = match[0].length;
      const linkText = match[1];
      const linkUrl = match[2];
      
      // Add text before the match
      if (matchIndex > currentIndex) {
        const beforeText = text.substring(currentIndex, matchIndex);
        if (beforeText) {
          // Parse URLs in the before text
          const urlParts = parsePlainUrls(beforeText);
          parts.push(...urlParts);
        }
      }
      
      // Add the markdown link
      parts.push({
        type: 'link',
        content: linkText,
        url: linkUrl,
        isGroww: isGrowwUrl(linkUrl),
        sourceType: getSourceTypeFromUrl(linkUrl),
      });
      
      currentIndex = matchIndex + matchLength;
    }
    
    // Add remaining text after last match
    if (currentIndex < text.length) {
      const remainingText = text.substring(currentIndex);
      if (remainingText) {
        const urlParts = parsePlainUrls(remainingText);
        parts.push(...urlParts);
      }
    }
    
    return parts;
  }
  
  // If no markdown links, parse plain URLs
  return parsePlainUrls(text);
}

/**
 * Parse plain URLs in text
 */
function parsePlainUrls(text: string): ParsedLink[] {
  const parts: ParsedLink[] = [];
  let lastIndex = 0;
  
  const matches = Array.from(text.matchAll(URL_REGEX));
  
  for (const match of matches) {
    const matchIndex = match.index!;
    const url = match[0];
    
    // Add text before the URL
    if (matchIndex > lastIndex) {
      const beforeText = text.substring(lastIndex, matchIndex);
      if (beforeText) {
        parts.push({
          type: 'text',
          content: beforeText,
        });
      }
    }
    
    // Add the URL as a link
    parts.push({
      type: 'link',
      content: url,
      url: url,
      isGroww: isGrowwUrl(url),
      sourceType: getSourceTypeFromUrl(url),
    });
    
    lastIndex = matchIndex + url.length;
  }
  
  // Add remaining text after last URL
  if (lastIndex < text.length) {
    const remainingText = text.substring(lastIndex);
    if (remainingText) {
      parts.push({
        type: 'text',
        content: remainingText,
      });
    }
  }
  
  // If no URLs found, return the whole text as a single text part
  if (parts.length === 0) {
    parts.push({
      type: 'text',
      content: text,
    });
  }
  
  return parts;
}

/**
 * Render parsed links as React elements
 * Uses React.createElement instead of JSX to work in .ts file
 */
export function renderLinks(
  parsedLinks: ParsedLink[],
  className?: string
): React.ReactNode[] {
  return parsedLinks.map((part, index) => {
    if (part.type === 'link' && part.url) {
      return React.createElement(
        'a',
        {
          key: index,
          href: part.url,
          target: '_blank',
          rel: 'noopener noreferrer',
          className: className,
          'data-source-type': part.sourceType,
          'data-is-groww': part.isGroww,
        },
        part.content
      );
    }
    
    return React.createElement(
      'span',
      { key: index },
      part.content
    );
  });
}
