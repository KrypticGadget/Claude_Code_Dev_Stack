# Semantic Analysis API - Production Docker Image
FROM node:18-alpine AS base

# Install system dependencies for Tree-sitter and native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    bash

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM base AS development
RUN npm ci
COPY . .
EXPOSE 3001
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS build
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S semantic -u 1001

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application
COPY --from=build --chown=semantic:nodejs /app/dist ./dist
COPY --chown=semantic:nodejs . .

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3001
ENV HOST=0.0.0.0

# Switch to non-root user
USER semantic

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3001/api/v1/health', (res) => { \
        process.exit(res.statusCode === 200 ? 0 : 1) \
    }).on('error', () => process.exit(1))"

# Expose port
EXPOSE 3001

# Start the application
CMD ["npm", "start"]

# Labels for metadata
LABEL maintainer="Claude Code Dev Stack" \
      version="1.0.0" \
      description="Semantic Analysis API Server" \
      org.opencontainers.image.source="https://github.com/claude-code/semantic-api" \
      org.opencontainers.image.documentation="https://github.com/claude-code/semantic-api/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"