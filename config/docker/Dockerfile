# Claude Code Dev Stack V3.0 - Multi-stage Docker Build
FROM node:18-alpine AS base

# Install system dependencies for native modules and Python hooks
RUN apk add --no-cache \
    python3 \
    py3-pip \
    make \
    g++ \
    git \
    bash \
    curl \
    jq \
    docker \
    docker-compose

# Install Python dependencies for hooks
RUN pip3 install --no-cache-dir \
    requests \
    pyyaml \
    psutil \
    colorama \
    click

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json* ./

# Install Node.js dependencies
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM base AS development

# Install all dependencies for development
RUN npm ci

# Install global development tools
RUN npm install -g \
    nodemon \
    concurrently \
    pm2 \
    typescript

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache /app/tmp

# Set permissions for hooks and scripts
RUN chmod +x bin/* && \
    chmod +x scripts/*.sh && \
    find core/hooks -name "*.py" -exec chmod +x {} \;

# Expose ports
EXPOSE 3000 3001 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Development command
CMD ["npm", "run", "dev"]

# Build stage
FROM development AS build

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    jq

# Install Python dependencies for hooks
RUN pip3 install --no-cache-dir \
    requests \
    pyyaml \
    psutil \
    colorama \
    click

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S claude && \
    adduser -S claude -u 1001 -G claude

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application and necessary files
COPY --from=build --chown=claude:claude /app/dist ./dist
COPY --from=build --chown=claude:claude /app/bin ./bin
COPY --from=build --chown=claude:claude /app/core ./core
COPY --from=build --chown=claude:claude /app/lib ./lib
COPY --from=build --chown=claude:claude /app/config ./config
COPY --from=build --chown=claude:claude /app/scripts ./scripts
COPY --chown=claude:claude index.js ./

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/cache /app/tmp && \
    chown -R claude:claude /app

# Set permissions
RUN chmod +x bin/* && \
    chmod +x scripts/*.sh && \
    find core/hooks -name "*.py" -exec chmod +x {} \;

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Switch to non-root user
USER claude

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose ports
EXPOSE 3000 3001 8080

# Start the application
CMD ["npm", "start"]

# Labels for metadata
LABEL maintainer="Claude Code Dev Stack Team" \
      version="3.0.0" \
      description="AI-powered development environment with 28 specialized agents" \
      org.opencontainers.image.source="https://github.com/KrypticGadget/Claude_Code_Dev_Stack" \
      org.opencontainers.image.documentation="https://github.com/KrypticGadget/Claude_Code_Dev_Stack/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"