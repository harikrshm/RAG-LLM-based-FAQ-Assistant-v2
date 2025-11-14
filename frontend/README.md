# Chat Widget Frontend

This is the frontend application for the Mutual Fund FAQ Assistant chat widget.

## Architecture

The chat widget is built with:
- **React 18** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Tailwind CSS** + Custom CSS Variables for styling (Groww design tokens)
- **Axios** for API communication

## Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ChatWidget/     # Main widget container
│   │   ├── FloatingButton/ # FAB to open/close widget
│   │   ├── ChatHeader/     # Widget header with controls
│   │   └── ...            # More components
│   ├── types/             # TypeScript type definitions
│   │   ├── chat.ts        # Chat domain types
│   │   ├── components.ts  # Component props types
│   │   └── index.ts       # Barrel export
│   ├── utils/             # Utility functions
│   │   └── helpers.ts     # Common helpers
│   ├── styles/            # Global styles
│   │   └── design-tokens.css  # Groww design system tokens
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global CSS
├── index.html             # HTML entry point
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind config
└── package.json           # Dependencies and scripts
```

## Components

### ChatWidget
Main container component that orchestrates the entire chat experience.

**Features:**
- Floating button to open/close
- Expandable/collapsible interface
- Minimize/maximize functionality
- Session management
- Welcome message support
- Configurable positioning and theming

### FloatingButton
Floating action button (FAB) that triggers the chat widget.

**Features:**
- Smooth animations
- Unread message badge
- Icon transitions
- Responsive positioning

### ChatHeader
Header section with title, subtitle, and action buttons.

**Features:**
- Minimize/maximize controls
- Close button
- Configurable title and subtitle
- Smooth hover effects

## Design System

The widget uses Groww's design tokens defined in `src/styles/design-tokens.css`:

- **Colors**: Primary green (#00D09C), text, backgrounds, borders
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Consistent spacing scale (1-20)
- **Border Radius**: From small (4px) to full (9999px)
- **Shadows**: Multiple shadow levels for depth
- **Transitions**: Smooth animations
- **Z-Index**: Layering system

## Configuration

The widget accepts a `ChatWidgetConfig` object:

```typescript
interface ChatWidgetConfig {
  apiBaseUrl: string;                    // Backend API URL
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  theme?: 'light' | 'dark' | 'auto';
  enableSoundNotifications?: boolean;
  maxMessages?: number;
  welcomeMessage?: string;
  placeholderText?: string;
  headerTitle?: string;
  headerSubtitle?: string;
}
```

## Development

### Prerequisites
- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Setup

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

The development server will start at `http://localhost:5173`.

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run format       # Format with Prettier
npm run format:check # Check formatting
```

### Type Checking

TypeScript type checking is automatically performed during build. To check types manually:

```bash
npx tsc --noEmit
```

## API Integration

The widget communicates with the backend API at `/api/chat`:

**Request:**
```typescript
{
  query: string;
  sessionId?: string;
  context?: Record<string, any>;
}
```

**Response:**
```typescript
{
  query: string;
  answer: string;
  sources: Source[];
  confidenceScore?: number;
  hasSufficientInfo?: boolean;
  fallbackMessage?: string;
  retrievedChunksCount?: number;
  responseTimeMs?: number;
  timestamp: string;
}
```

## Styling

The widget uses a combination of:

1. **CSS Variables** - Groww design tokens in `design-tokens.css`
2. **Component CSS** - Component-specific styles
3. **Tailwind CSS** - Utility classes for rapid development

### Custom CSS Variables

All design tokens are available as CSS variables:

```css
var(--color-primary)          /* Primary green */
var(--color-text-primary)     /* Text color */
var(--spacing-4)              /* 16px spacing */
var(--radius-base)            /* 8px border radius */
var(--shadow-md)              /* Medium shadow */
var(--transition-all)         /* Smooth transition */
```

## Accessibility

The widget follows accessibility best practices:

- **ARIA labels** on all interactive elements
- **Keyboard navigation** support
- **Focus indicators** for keyboard users
- **Screen reader** compatible
- **Color contrast** meets WCAG AA standards

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Responsive Design

The widget adapts to different screen sizes:

- **Desktop**: Fixed size widget in configured position
- **Tablet**: Same as desktop
- **Mobile**: Full-screen overlay

## Performance

Optimizations implemented:

- **Code splitting** - React vendor chunk separation
- **Lazy loading** - Components loaded on demand
- **Memoization** - React.memo for expensive components
- **Debouncing** - Input debouncing for API calls
- **Build optimization** - Vite's optimized production builds

## Testing

(To be implemented in future tasks)

## Deployment

```bash
# Build production bundle
npm run build

# Output will be in dist/
# Deploy dist/ to your hosting service
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Contributing

1. Follow the existing code structure
2. Use TypeScript for type safety
3. Follow the design system tokens
4. Write meaningful component names
5. Add comments for complex logic
6. Run linting before committing

## License

Proprietary - Groww
