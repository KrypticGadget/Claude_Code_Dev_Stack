# Context Preservation System Dockerfile
# Multi-stage build for production optimization

# Base stage with common dependencies
FROM node:18-alpine AS base
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    postgresql-client \
    redis \
    curl \
    bash \
    jq \
    && rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM base AS development
ENV NODE_ENV=development

# Install development dependencies
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Create directories
RUN mkdir -p logs data cache

# Set permissions
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${CONTEXT_API_PORT:-3100}/api/context/health || exit 1

# Expose port
EXPOSE 3100

# Start development server
CMD ["npm", "run", "dev"]

# Production stage
FROM base AS production
ENV NODE_ENV=production

# Copy source code (only production files)
COPY --chown=node:node context-manager.js ./
COPY --chown=node:node context-api.js ./
COPY --chown=node:node context-client.js ./
COPY --chown=node:node package*.json ./
COPY --chown=node:node scripts/ ./scripts/

# Create directories
RUN mkdir -p logs data cache && \
    chown -R node:node logs data cache

# Switch to non-root user
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${CONTEXT_API_PORT:-3100}/api/context/health || exit 1

# Expose port
EXPOSE 3100

# Start production server
CMD ["node", "context-api.js"]

# Testing stage
FROM development AS testing
ENV NODE_ENV=test

# Copy test files
COPY --chown=node:node tests/ ./tests/
COPY --chown=node:node jest.config.js ./
COPY --chown=node:node .eslintrc.js ./

# Run tests
RUN npm test

# Monitoring stage
FROM node:18-alpine AS monitoring
WORKDIR /app

# Install monitoring dependencies
RUN apk add --no-cache curl jq postgresql-client redis

# Copy monitoring scripts
COPY --chown=node:node scripts/monitoring/ ./
COPY package*.json ./

# Install only monitoring dependencies
RUN npm ci --only=production && npm cache clean --force

USER node

EXPOSE 3102

CMD ["node", "monitor.js"]