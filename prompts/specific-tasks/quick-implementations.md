# Quick Implementation Tasks

Use these prompts for specific, focused development tasks.

## Authentication & Authorization

### Add JWT Authentication
```
> Use the security-architecture agent to implement JWT authentication for [APPLICATION] with refresh tokens and secure storage
```

### OAuth2 Integration
```
> Use the api-integration-specialist agent to add OAuth2 login with [PROVIDER] including profile sync and token management
```

### Role-Based Access Control
```
> Use the security-architecture agent to implement RBAC with roles [ROLE LIST] and permissions for [RESOURCES]
```

### Multi-Factor Authentication
```
> Use the security-architecture agent to add MFA using [METHOD] with backup codes and recovery options
```

## Search & Discovery

### Full-Text Search
```
> Use the backend-services agent to implement full-text search for [DATA TYPE] using [Elasticsearch/Algolia/PostgreSQL FTS]
```

### Autocomplete Feature
```
> Use the production-frontend agent to add autocomplete to [SEARCH BOX] with debouncing and keyboard navigation
```

### Faceted Search
```
> Use the backend-services agent to implement faceted search for [PRODUCTS/CONTENT] with filters for [ATTRIBUTES]
```

## File Handling

### File Upload System
```
> Use the backend-services agent to implement file upload for [FILE TYPES] with validation, virus scanning, and S3 storage
```

### Image Processing
```
> Use the backend-services agent to add image processing for uploads including resizing, optimization, and thumbnail generation
```

### Document Generation
```
> Use the backend-services agent to generate [DOCUMENT TYPE] from [DATA SOURCE] in [FORMAT] with templates
```

## Communication Features

### Email Notifications
```
> Use the api-integration-specialist agent to implement email notifications for [EVENTS] using [SERVICE] with templates
```

### Real-time Chat
```
> Use the backend-services agent to add real-time chat using WebSockets with typing indicators and read receipts
```

### Push Notifications
```
> Use the mobile-development agent to implement push notifications for [PLATFORMS] triggered by [EVENTS]
```

## Payment Processing

### Subscription Billing
```
> Use the api-integration-specialist agent to implement subscription billing with [PROVIDER] including trials and plan changes
```

### One-Time Payments
```
> Use the api-integration-specialist agent to add one-time payment processing for [USE CASE] with [PAYMENT METHODS]
```

### Invoice Generation
```
> Use the backend-services agent to generate invoices with [DETAILS] and automated sending via [METHOD]
```

## Data Import/Export

### CSV Import
```
> Use the backend-services agent to implement CSV import for [DATA TYPE] with validation and error reporting
```

### Excel Export
```
> Use the backend-services agent to add Excel export for [REPORT TYPE] with formatting and multiple sheets
```

### API Data Sync
```
> Use the api-integration-specialist agent to sync data between [SOURCE] and [DESTINATION] with conflict resolution
```

## Analytics & Reporting

### Dashboard Creation
```
> Use the frontend-mockup agent to design analytics dashboard showing [METRICS] with [VISUALIZATION TYPES]
```

### Report Generation
```
> Use the backend-services agent to generate [REPORT TYPE] reports with scheduling and email delivery
```

### Event Tracking
```
> Use the backend-services agent to implement event tracking for [USER ACTIONS] with [ANALYTICS PLATFORM]
```

## User Interface Components

### Data Table
```
> Use the production-frontend agent to create data table for [DATA TYPE] with sorting, filtering, and pagination
```

### Form Builder
```
> Use the production-frontend agent to implement dynamic form builder for [USE CASE] with validation and conditional fields
```

### Calendar Component
```
> Use the production-frontend agent to add calendar view for [DATA TYPE] with drag-drop and recurring events
```

## Performance Enhancements

### Add Caching Layer
```
> Use the performance-optimization agent to implement caching for [DATA/ENDPOINTS] using Redis with [STRATEGY]
```

### Implement CDN
```
> Use the devops-engineering agent to setup CDN for [ASSETS] with cache rules and purge functionality
```

### Database Indexing
```
> Use the database-architecture agent to analyze and add indexes for [QUERIES/TABLES] to improve performance
```

## DevOps Tasks

### Add Health Checks
```
> Use the devops-engineering agent to implement health check endpoints for [SERVICES] with dependency checks
```

### Setup Logging
```
> Use the devops-engineering agent to implement centralized logging for [APPLICATION] with structured logs
```

### Create Backup System
```
> Use the devops-engineering agent to setup automated backups for [DATA/SYSTEM] with [FREQUENCY] and retention
```

## Variables to Replace:
- `[APPLICATION]` - Your application name
- `[PROVIDER]` - Google, Facebook, GitHub, etc.
- `[ROLE LIST]` - Admin, user, moderator, etc.
- `[METHOD]` - SMS, TOTP, email
- `[DATA TYPE]` - Products, articles, users
- `[FILE TYPES]` - PDF, images, documents
- `[EVENTS]` - User signup, order placed, etc.
- `[METRICS]` - Revenue, users, conversion
- `[FREQUENCY]` - Hourly, daily, weekly