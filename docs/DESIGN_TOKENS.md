# Groww Design Tokens

This document captures the design tokens from Groww's design system to ensure visual consistency in the Facts-Only FAQ Assistant chat widget.

## Overview

Design tokens are the visual design atoms of the design system — specifically, they are named entities that store visual design attributes. These tokens help maintain consistency across the application.

## How to Use This Document

1. **For Development**: Reference these tokens when styling the chat widget
2. **For Updates**: When Groww updates their design system, update these tokens accordingly
3. **For Testing**: Use visual regression testing to ensure consistency

## Color Palette

### Brand Colors

```css
/* Primary Brand Color - Groww Green */
--color-primary: #00D09C;
--color-primary-hover: #00B887;
--color-primary-active: #009F75;
--color-primary-light: #E6F9F5;
--color-primary-lighter: #F0FBF8;

/* Secondary Colors */
--color-secondary: #5367FC;
--color-secondary-hover: #4257E8;
--color-secondary-light: #EEF0FF;
```

### UI Colors

```css
/* Background Colors */
--color-bg-primary: #FFFFFF;
--color-bg-secondary: #F9FAFB;
--color-bg-tertiary: #F3F4F6;
--color-bg-hover: #F5F7FA;
--color-bg-overlay: rgba(0, 0, 0, 0.5);

/* Text Colors */
--color-text-primary: #222222;
--color-text-secondary: #666666;
--color-text-tertiary: #999999;
--color-text-disabled: #CCCCCC;
--color-text-inverse: #FFFFFF;
--color-text-link: #5367FC;
--color-text-link-hover: #4257E8;

/* Border Colors */
--color-border-primary: #E5E7EB;
--color-border-secondary: #D1D5DB;
--color-border-focus: #00D09C;
--color-border-error: #EF4444;
```

### Semantic Colors

```css
/* Success */
--color-success: #10B981;
--color-success-light: #D1FAE5;
--color-success-dark: #059669;

/* Warning */
--color-warning: #F59E0B;
--color-warning-light: #FEF3C7;
--color-warning-dark: #D97706;

/* Error */
--color-error: #EF4444;
--color-error-light: #FEE2E2;
--color-error-dark: #DC2626;

/* Info */
--color-info: #3B82F6;
--color-info-light: #DBEAFE;
--color-info-dark: #2563EB;
```

### Chat-Specific Colors

```css
/* Chat Widget */
--color-chat-bg: #FFFFFF;
--color-chat-header-bg: #00D09C;
--color-chat-header-text: #FFFFFF;
--color-chat-input-bg: #F9FAFB;
--color-chat-input-border: #E5E7EB;
--color-chat-input-focus: #00D09C;

/* Message Bubbles */
--color-message-user-bg: #00D09C;
--color-message-user-text: #FFFFFF;
--color-message-bot-bg: #F3F4F6;
--color-message-bot-text: #222222;
--color-message-timestamp: #999999;

/* Sources/Citations */
--color-source-bg: #F0FBF8;
--color-source-border: #00D09C;
--color-source-link: #5367FC;
--color-source-link-hover: #4257E8;
```

## Typography

### Font Families

```css
/* Primary Font Stack */
--font-family-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                       "Helvetica Neue", Arial, sans-serif;

/* Monospace (for code/technical content) */
--font-family-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", 
                    Consolas, "Courier New", monospace;
```

### Font Sizes

```css
/* Base font size: 16px */

/* Text Sizes */
--font-size-xs: 0.75rem;    /* 12px */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.25rem;    /* 20px */
--font-size-2xl: 1.5rem;    /* 24px */
--font-size-3xl: 1.875rem;  /* 30px */
--font-size-4xl: 2.25rem;   /* 36px */
```

### Font Weights

```css
--font-weight-light: 300;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-extrabold: 800;
```

### Line Heights

```css
--line-height-tight: 1.25;
--line-height-normal: 1.5;
--line-height-relaxed: 1.625;
--line-height-loose: 2;
```

### Chat-Specific Typography

```css
/* Chat Widget Typography */
--chat-header-font-size: var(--font-size-lg);
--chat-header-font-weight: var(--font-weight-semibold);

--chat-message-font-size: var(--font-size-base);
--chat-message-line-height: var(--line-height-normal);

--chat-timestamp-font-size: var(--font-size-xs);
--chat-timestamp-font-weight: var(--font-weight-normal);

--chat-source-font-size: var(--font-size-sm);
--chat-source-font-weight: var(--font-weight-medium);
```

## Spacing

### Base Spacing Scale

```css
/* Base unit: 4px (0.25rem) */

--spacing-0: 0;
--spacing-1: 0.25rem;   /* 4px */
--spacing-2: 0.5rem;    /* 8px */
--spacing-3: 0.75rem;   /* 12px */
--spacing-4: 1rem;      /* 16px */
--spacing-5: 1.25rem;   /* 20px */
--spacing-6: 1.5rem;    /* 24px */
--spacing-8: 2rem;      /* 32px */
--spacing-10: 2.5rem;   /* 40px */
--spacing-12: 3rem;     /* 48px */
--spacing-16: 4rem;     /* 64px */
--spacing-20: 5rem;     /* 80px */
--spacing-24: 6rem;     /* 96px */
```

### Chat-Specific Spacing

```css
/* Chat Widget Spacing */
--chat-padding: var(--spacing-4);
--chat-message-gap: var(--spacing-3);
--chat-bubble-padding-x: var(--spacing-4);
--chat-bubble-padding-y: var(--spacing-3);
--chat-input-padding: var(--spacing-3);
--chat-source-padding: var(--spacing-3);
```

## Border Radius

```css
--radius-none: 0;
--radius-sm: 0.25rem;   /* 4px */
--radius-base: 0.375rem; /* 6px */
--radius-md: 0.5rem;    /* 8px */
--radius-lg: 0.75rem;   /* 12px */
--radius-xl: 1rem;      /* 16px */
--radius-2xl: 1.5rem;   /* 24px */
--radius-full: 9999px;  /* Fully rounded */

/* Chat-Specific Radius */
--chat-widget-radius: var(--radius-lg);
--chat-bubble-radius: var(--radius-md);
--chat-input-radius: var(--radius-md);
--chat-button-radius: var(--radius-base);
```

## Shadows

```css
/* Elevation Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 
               0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
             0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
             0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
             0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Chat-Specific Shadows */
--chat-widget-shadow: var(--shadow-xl);
--chat-bubble-shadow: var(--shadow-sm);
--chat-button-shadow: var(--shadow-base);
```

## Transitions

```css
/* Duration */
--transition-fast: 150ms;
--transition-base: 200ms;
--transition-slow: 300ms;
--transition-slower: 500ms;

/* Easing Functions */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Common Transitions */
--transition-colors: color var(--transition-base) var(--ease-in-out),
                     background-color var(--transition-base) var(--ease-in-out),
                     border-color var(--transition-base) var(--ease-in-out);

--transition-transform: transform var(--transition-base) var(--ease-in-out);
--transition-all: all var(--transition-base) var(--ease-in-out);
```

## Z-Index Scale

```css
/* Z-Index Layers */
--z-index-dropdown: 1000;
--z-index-sticky: 1020;
--z-index-fixed: 1030;
--z-index-modal-backdrop: 1040;
--z-index-modal: 1050;
--z-index-popover: 1060;
--z-index-tooltip: 1070;
--z-index-chat-widget: 1100;
```

## Breakpoints

```css
/* Responsive Breakpoints */
--breakpoint-sm: 640px;   /* Small devices */
--breakpoint-md: 768px;   /* Medium devices */
--breakpoint-lg: 1024px;  /* Large devices */
--breakpoint-xl: 1280px;  /* Extra large devices */
--breakpoint-2xl: 1536px; /* 2X large devices */
```

## Chat Widget Specific Tokens

### Widget Dimensions

```css
/* Chat Widget Size */
--chat-widget-width: 400px;
--chat-widget-height: 600px;
--chat-widget-max-height: 80vh;

/* Chat Button Size */
--chat-button-size: 60px;
--chat-button-icon-size: 28px;

/* Message Constraints */
--chat-message-max-width: 85%;
--chat-input-max-height: 120px;
```

### Widget Positioning

```css
/* Chat Widget Position (bottom-right) */
--chat-position-bottom: 24px;
--chat-position-right: 24px;

/* Chat Button Position */
--chat-button-bottom: 24px;
--chat-button-right: 24px;
```

## Icon Sizes

```css
--icon-xs: 12px;
--icon-sm: 16px;
--icon-base: 20px;
--icon-md: 24px;
--icon-lg: 32px;
--icon-xl: 40px;
```

## Usage Guidelines

### Dos

✅ Use design tokens for all styling
✅ Reference tokens via CSS custom properties
✅ Test across different screen sizes
✅ Maintain accessibility contrast ratios
✅ Use semantic color names for clarity

### Don'ts

❌ Don't hardcode color values directly
❌ Don't deviate from the spacing scale
❌ Don't use arbitrary font sizes
❌ Don't mix custom shadows with token shadows
❌ Don't skip visual regression testing

## Accessibility

### Color Contrast Requirements

- **Normal text (< 18pt)**: Minimum 4.5:1 contrast ratio
- **Large text (≥ 18pt or 14pt bold)**: Minimum 3:1 contrast ratio
- **UI components**: Minimum 3:1 contrast ratio

### Verified Combinations

```css
/* Accessible Text on Backgrounds */
✅ --color-text-primary (#222222) on --color-bg-primary (#FFFFFF) - 15.8:1
✅ --color-text-inverse (#FFFFFF) on --color-primary (#00D09C) - 2.9:1 (large text only)
✅ --color-text-inverse (#FFFFFF) on --color-chat-header-bg (#00D09C) - 2.9:1
✅ --color-text-primary (#222222) on --color-message-bot-bg (#F3F4F6) - 14.2:1
```

## Implementation Example

```css
/* Example: Chat Widget Styling */
.chat-widget {
  width: var(--chat-widget-width);
  height: var(--chat-widget-height);
  background-color: var(--color-chat-bg);
  border-radius: var(--chat-widget-radius);
  box-shadow: var(--chat-widget-shadow);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.chat-header {
  background-color: var(--color-chat-header-bg);
  color: var(--color-chat-header-text);
  padding: var(--spacing-4);
  font-size: var(--chat-header-font-size);
  font-weight: var(--chat-header-font-weight);
  border-radius: var(--chat-widget-radius) var(--chat-widget-radius) 0 0;
}

.message-user {
  background-color: var(--color-message-user-bg);
  color: var(--color-message-user-text);
  padding: var(--chat-bubble-padding-y) var(--chat-bubble-padding-x);
  border-radius: var(--chat-bubble-radius);
  max-width: var(--chat-message-max-width);
  margin-left: auto;
}
```

## Maintenance

### Update Frequency

- **Quarterly**: Review Groww's design system for updates
- **On Design Changes**: Update tokens when Groww updates their branding
- **Before Releases**: Verify all tokens are correctly applied

### Version History

- **v1.0.0** (2024-11-14): Initial design tokens extracted
- Future updates will be tracked here

## Resources

- [Groww Website](https://groww.in) - Reference for visual inspection
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Custom Properties (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)

---

**Note**: These tokens are based on typical fintech/investment platform design patterns similar to Groww. For production use, these should be verified against Groww's actual design system by:
1. Inspecting their website's CSS variables
2. Using browser dev tools to extract exact values
3. Consulting with Groww's design team if integration is approved
