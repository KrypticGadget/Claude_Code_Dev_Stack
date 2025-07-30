# Frontend Development Workflow Prompts

Use these prompts for specific frontend development tasks with the Claude Code Agent System.

## UI/UX Design Phase

### Create Wireframes
```
> Use the frontend-mockup agent to create wireframes for [PAGE/FEATURE NAME] showing [KEY ELEMENTS] with [DESIGN STYLE]
```

### Design System Creation
```
> Use the ui-ux-design agent to create a design system with color palette, typography, component library, and accessibility guidelines for [PROJECT NAME]
```

### User Flow Mapping
```
> Use the frontend-architecture agent to map user flows for [FEATURE] including all states, error handling, and edge cases
```

## Component Development

### React Component Structure
```
> Use the production-frontend agent to create React components for [FEATURE] with TypeScript, proper state management, and unit tests
```

### Vue.js Application
```
> Use the production-frontend agent to build Vue.js application structure for [PROJECT] with Vuex store, router configuration, and component hierarchy
```

### Angular Module
```
> Use the production-frontend agent to develop Angular module for [FUNCTIONALITY] with services, guards, and lazy loading
```

## State Management

### Redux Implementation
```
> Use the frontend-architecture agent to design Redux store structure for [APPLICATION] with actions, reducers, and middleware configuration
```

### Context API Setup
```
> Use the production-frontend agent to implement React Context API for [STATE TYPE] with providers, consumers, and optimization
```

### MobX Store
```
> Use the production-frontend agent to create MobX stores for [DOMAIN] with observables, actions, and computed values
```

## Performance Optimization

### Bundle Optimization
```
> Use the performance-optimization agent to analyze and optimize JavaScript bundle size for [APPLICATION] targeting [SIZE GOAL]
```

### Lazy Loading
```
> Use the production-frontend agent to implement lazy loading for [ROUTES/COMPONENTS] with loading states and error boundaries
```

### Image Optimization
```
> Use the performance-optimization agent to optimize images with responsive sizing, lazy loading, and modern formats for [PROJECT]
```

## Testing Strategies

### Component Testing
```
> Use the testing-automation agent to create comprehensive component tests for [COMPONENT NAME] covering props, events, and edge cases
```

### E2E Testing
```
> Use the testing-automation agent to write E2E tests for [USER FLOW] using [Cypress/Playwright] with visual regression testing
```

### Accessibility Testing
```
> Use the quality-assurance agent to audit [APPLICATION] for WCAG 2.1 compliance and create accessibility test suite
```

## Build & Deployment

### Build Configuration
```
> Use the script-automation agent to create optimized build configuration for [FRAMEWORK] with environment-specific settings
```

### CI/CD Pipeline
```
> Use the devops-engineering agent to setup frontend CI/CD pipeline with build, test, and deployment stages for [PLATFORM]
```

### Static Site Generation
```
> Use the production-frontend agent to convert [APPLICATION] to static site using [Next.js/Gatsby/Nuxt] for better SEO
```

## Common Enhancement Patterns

### Add Authentication
```
> Use the production-frontend agent to add authentication to [APPLICATION] with [AUTH PROVIDER] including protected routes and token management
```

### Implement Search
```
> Use the production-frontend agent to add search functionality to [PAGE] with autocomplete, filters, and result highlighting
```

### Add Animations
```
> Use the production-frontend agent to enhance [COMPONENT/PAGE] with smooth animations using [Framer Motion/GSAP/CSS]
```

### Dark Mode
```
> Use the production-frontend agent to implement dark mode toggle with CSS variables and local storage persistence
```

### Internationalization
```
> Use the production-frontend agent to add i18n support for [LANGUAGES] with dynamic loading and RTL support
```

## Variables to Replace:
- `[PAGE/FEATURE NAME]` - Specific page or feature
- `[KEY ELEMENTS]` - Main UI elements needed
- `[DESIGN STYLE]` - Material, minimal, etc.
- `[PROJECT NAME]` - Your project name
- `[FEATURE]` - Specific feature name
- `[FUNCTIONALITY]` - What it does
- `[APPLICATION]` - App name
- `[STATE TYPE]` - User, theme, cart, etc.
- `[SIZE GOAL]` - Target bundle size
- `[USER FLOW]` - Checkout, onboarding, etc.
- `[FRAMEWORK]` - React, Vue, Angular
- `[AUTH PROVIDER]` - Auth0, Firebase, custom