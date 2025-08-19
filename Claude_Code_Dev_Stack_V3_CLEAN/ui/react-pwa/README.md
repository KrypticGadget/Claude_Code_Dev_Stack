# Claude Code Dev Stack - React PWA

A production-ready Progressive Web Application built with React, TypeScript, and Material-UI that unifies all UI components and patterns from the Claude Code development environment.

## Features

### 🚀 Progressive Web App (PWA)
- **Offline Support**: Works without internet connection
- **Installable**: Can be installed on desktop and mobile devices
- **Push Notifications**: Real-time notifications for development events
- **Background Sync**: Sync data when connection is restored

### 🎨 Modern UI/UX
- **Material Design 3**: Latest Material-UI components and theming
- **Dark/Light Themes**: Supports system, dark, and light themes
- **Responsive Design**: Mobile-first approach with desktop optimization
- **Smooth Animations**: Framer Motion animations throughout the app
- **Accessible**: WCAG 2.1 AA compliant

### 🔧 Development Features
- **AI Chat Interface**: Real-time chat with Claude AI assistant
- **Interactive Documentation**: Browse and search comprehensive docs
- **Component Library**: Explore reusable UI components with live examples
- **Code Generation**: AI-powered code generation and suggestions
- **Real-time Collaboration**: WebSocket-based real-time features

### 🛠 Technical Stack
- **React 18**: Latest React with concurrent features
- **TypeScript**: Full type safety and IntelliSense
- **Material-UI v5**: Modern Material Design components
- **Zustand**: Lightweight state management
- **React Query**: Server state management and caching
- **Vite**: Fast build tool and dev server
- **Vitest**: Unit testing framework
- **Playwright**: End-to-end testing
- **Storybook**: Component documentation and testing

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/claude-code-dev-stack.git
   cd claude-code-dev-stack/ui/react-pwa
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   Navigate to `http://localhost:3000`

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run unit tests
npm run test:e2e     # Run end-to-end tests

# Code Quality
npm run lint         # Run ESLint
npm run format       # Format code with Prettier
npm run type-check   # TypeScript type checking

# Documentation
npm run storybook    # Start Storybook
npm run build-storybook  # Build Storybook
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI components
│   ├── layout/         # Layout components
│   ├── features/       # Feature-specific components
│   ├── charts/         # Data visualization components
│   └── editors/        # Code/text editors
├── pages/              # Page components
│   ├── dashboard/      # Dashboard page
│   ├── chat/          # AI chat interface
│   ├── docs/          # Documentation browser
│   ├── components/    # Component library
│   └── settings/      # Settings page
├── hooks/             # Custom React hooks
├── store/             # State management
├── utils/             # Utility functions
├── types/             # TypeScript type definitions
├── styles/            # Global styles and themes
└── assets/            # Static assets
```

## Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080

# Feature Flags
VITE_ENABLE_PWA=true
VITE_ENABLE_ANALYTICS=false

# Development
VITE_DEBUG_MODE=true
```

### PWA Configuration

The PWA configuration is in `vite.config.ts`. Key features:

- **Service Worker**: Automatic updates and offline support
- **Web App Manifest**: Installability and native app feel
- **Background Sync**: Sync data when online
- **Push Notifications**: Real-time notifications

### Theme Customization

Customize the theme in `src/styles/theme.ts`:

```typescript
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#60A5FA', // Customize primary color
    },
    // ... other customizations
  },
});
```

## Features Documentation

### 🤖 AI Chat Interface
- Real-time chat with Claude AI
- Code syntax highlighting
- Message history and persistence
- Voice input support (when available)
- Typing indicators

### 📚 Interactive Documentation
- Search and filter documentation
- Live code examples
- Interactive diagrams
- Progressive disclosure
- Mobile-optimized reading

### 🧩 Component Library
- Browse all UI components
- Live previews and examples
- Props documentation
- Copy-to-clipboard code snippets
- Storybook integration

### ⚙️ Settings Management
- Theme and appearance customization
- Language and region settings
- Notification preferences
- Storage management
- Profile management

## API Integration

### WebSocket Connection
```typescript
import { useAppStore } from '@store/appStore';

function useWebSocket() {
  const { connect, disconnect, isConnected } = useAppStore();
  
  useEffect(() => {
    connect({
      host: 'localhost',
      port: 8080,
      protocol: 'ws'
    });
    
    return () => disconnect();
  }, []);
}
```

### REST API
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

// Usage in components
const { data, error, isLoading } = useQuery({
  queryKey: ['docs'],
  queryFn: () => api.get('/api/docs').then(res => res.data),
});
```

## Testing

### Unit Testing with Vitest
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

Example test:
```typescript
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '@components/ui/LoadingSpinner';

test('renders loading spinner with message', () => {
  render(<LoadingSpinner message="Loading..." />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});
```

### E2E Testing with Playwright
```bash
# Run E2E tests
npm run test:e2e

# Run in headed mode
npm run test:e2e -- --headed
```

### Component Testing with Storybook
```bash
# Start Storybook
npm run storybook

# Build Storybook
npm run build-storybook
```

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

### Docker Deployment
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Performance Optimization

### Code Splitting
Components are automatically code-split using React.lazy():

```typescript
const Dashboard = React.lazy(() => import('@pages/dashboard/Dashboard'));
```

### Bundle Analysis
```bash
npm run build
npx vite-bundle-analyzer dist
```

### PWA Optimization
- Service worker caching strategies
- Resource prioritization
- Background sync for offline functionality
- Push notification optimization

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### PWA Support
- Chrome/Edge: Full PWA support
- Firefox: Installable web apps
- Safari: Add to Home Screen
- Mobile browsers: Native app-like experience

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow the existing code style
- Use TypeScript for all new code
- Write tests for new features
- Update documentation as needed

### Commit Messages
Follow conventional commits:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation updates
- `style:` code style changes
- `refactor:` code refactoring
- `test:` test additions/updates

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Support

- 📧 Email: support@claudecode.dev
- 💬 Discord: [Claude Code Community](https://discord.gg/claudecode)
- 📖 Docs: [docs.claudecode.dev](https://docs.claudecode.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/claude-code-dev-stack/issues)

## Acknowledgments

- **Anthropic**: For Claude AI integration
- **Material-UI Team**: For the excellent component library
- **React Team**: For the amazing framework
- **Vite Team**: For the fast build tool
- **Open Source Community**: For all the amazing libraries and tools

---

Built with ❤️ by the Claude Code team