# NGROK Integration Guide for Claude Code Dev Stack v3.6.9

Complete external access and webhook testing setup with advanced features.

## Overview

This comprehensive NGROK integration provides:

- **Automatic Tunnel Creation** for all services
- **Custom Domain Support** (Premium feature)
- **Tunnel Persistence** through service restarts
- **Health Monitoring** with automated recovery
- **Multiple Service Support** (web, API, WebSocket, terminal)
- **Security Configuration** with authentication and IP restrictions
- **Webhook Testing** with signature verification
- **Performance Monitoring** and alerting

## Quick Start

### 1. Install NGROK

```bash
# Download from https://ngrok.com/download
# Or use package manager:

# macOS
brew install ngrok/ngrok/ngrok

# Windows (Chocolatey)
choco install ngrok

# Linux
snap install ngrok
```

### 2. Get Auth Token

1. Sign up at [ngrok.com](https://ngrok.com)
2. Get your auth token from the dashboard
3. Set environment variable:

```bash
export NGROK_AUTHTOKEN=your_token_here
```

### 3. Start All Services

```bash
# Start everything with NGROK integration
npm run services:start

# Or use the startup scripts
./scripts/start-ngrok-complete.sh        # Linux/macOS
scripts\start-ngrok-complete.bat         # Windows
```

## Configuration

### Environment Variables

Copy `config/ngrok/.env.example` to `config/ngrok/.env` and configure:

```env
# Required
NGROK_AUTHTOKEN=your_ngrok_auth_token_here
NGROK_REGION=us

# Optional - Custom Domains (Premium)
NGROK_CUSTOM_DOMAIN_WEBAPP=your-app.ngrok.app
NGROK_CUSTOM_DOMAIN_API=your-api.ngrok.app

# Optional - Subdomains (Free)
NGROK_SUBDOMAIN_WEBAPP=claude-webapp
NGROK_SUBDOMAIN_API=claude-api

# Security
NGROK_OAUTH_PROVIDER=google
NGROK_ALLOWED_EMAILS=your-email@example.com
NGROK_TERMINAL_PASSWORD=secure_password
```

### Advanced Configuration

The main configuration file is `config/ngrok/ngrok-advanced.yml`:

```yaml
version: "2"
authtoken: ${NGROK_AUTHTOKEN}
region: ${NGROK_REGION:-us}

tunnels:
  webapp:
    proto: http
    addr: 3000
    domain: ${NGROK_CUSTOM_DOMAIN_WEBAPP}
    oauth:
      provider: ${NGROK_OAUTH_PROVIDER}
      allow_emails: ${NGROK_ALLOWED_EMAILS}
    # ... advanced options
```

## Service Architecture

### Port Mapping

| Service | Port | Description | NGROK Tunnel |
|---------|------|-------------|--------------|
| Web App | 3000 | React PWA Frontend | `webapp` |
| API Server | 8000 | Unified Backend API | `backend` |
| API Alt | 3001 | Alternative API | `api` |
| WebSocket | 3002 | Real-time Communication | `websocket` |
| Terminal | 3003 | Web Terminal Access | `terminal` |
| Webhooks | 4000 | Webhook Testing | `webhooks` |
| Monitoring | 4040 | NGROK Dashboard | `monitoring` |
| Preview | 5173 | Vite Dev Server | `preview` |

### Security Features

- **OAuth Integration** (Google, GitHub, etc.)
- **IP Whitelisting** for sensitive services
- **Basic Authentication** for terminal access
- **Webhook Signature Verification**
- **Rate Limiting** and circuit breakers
- **HTTPS Enforcement** with security headers

## Usage

### Command Line Interface

```bash
# Start/stop tunnels
claude-code-ngrok start --all
claude-code-ngrok stop
claude-code-ngrok restart

# Check status
claude-code-ngrok status --watch
claude-code-ngrok urls --copy

# View logs
claude-code-ngrok logs --follow --type all
```

### Individual Components

```bash
# NGROK Manager
node scripts/ngrok-manager.js start
node scripts/ngrok-manager.js status
node scripts/ngrok-manager.js urls

# Webhook Server
node scripts/webhook-server.js
curl -X POST https://your-webhooks.ngrok.app/webhook/test

# Health Monitor
node scripts/ngrok-health-monitor.js start
node scripts/ngrok-health-monitor.js status
```

### Service Orchestrator

```bash
# Start all services
node scripts/start-all-services.js start

# Stop all services
node scripts/start-all-services.js stop

# Check status
node scripts/start-all-services.js status
```

## Webhook Testing

### Supported Webhook Types

1. **Generic Webhooks**
   ```bash
   POST https://your-webhooks.ngrok.app/webhook/service-name
   ```

2. **GitHub Webhooks**
   ```bash
   POST https://your-webhooks.ngrok.app/webhook/github
   # Includes signature verification
   ```

3. **Discord Webhooks**
   ```bash
   POST https://your-webhooks.ngrok.app/webhook/discord
   ```

4. **Slack Webhooks**
   ```bash
   POST https://your-webhooks.ngrok.app/webhook/slack
   # Handles URL verification
   ```

5. **Custom Webhooks**
   ```bash
   POST https://your-webhooks.ngrok.app/webhook/custom/your-id
   ```

### Webhook Features

- **Signature Verification** for GitHub, GitLab, etc.
- **Request Logging** with full payload capture
- **Replay Functionality** for testing
- **Rate Limiting** and security
- **Real-time Log Viewing**
- **Statistics and Analytics**

### Testing Webhooks

```bash
# View logs
curl https://your-webhooks.ngrok.app/logs

# Test webhook
curl -X POST https://your-webhooks.ngrok.app/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": true, "message": "Hello from NGROK!"}'

# Generate test payload
curl https://your-webhooks.ngrok.app/test/generate?service=github

# View statistics
curl https://your-webhooks.ngrok.app/stats
```

## Health Monitoring

### Features

- **Tunnel Health Checks** every 30 seconds
- **Performance Monitoring** with response time tracking
- **Automated Alerts** via Slack, email, etc.
- **Recovery Automation** with restart capabilities
- **Historical Data** collection and analysis

### Configuration

```env
# Slack alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Email alerts (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### Monitoring Dashboard

Access health monitoring data:

```bash
# Current status
curl http://localhost:4040/api/tunnels

# Health monitor status
node scripts/ngrok-health-monitor.js status

# Performance metrics
cat logs/ngrok-performance.jsonl
```

## Security Best Practices

### 1. Authentication

```yaml
# OAuth for web services
oauth:
  provider: google
  allow_emails: ["team@company.com"]

# Basic auth for admin services
basic_auth: "admin:secure_password"
```

### 2. IP Restrictions

```yaml
# Limit access by IP
ip_restriction:
  allow_cidrs: ["192.168.1.0/24", "10.0.0.0/8"]
```

### 3. Webhook Security

```javascript
// Verify GitHub webhooks
const signature = req.get('X-Hub-Signature-256');
const payload = req.body;
const secret = process.env.GITHUB_WEBHOOK_SECRET;

const expectedSignature = 'sha256=' + 
  crypto.createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

const isValid = crypto.timingSafeEqual(
  Buffer.from(signature),
  Buffer.from(expectedSignature)
);
```

### 4. Rate Limiting

```yaml
# Circuit breaker configuration
circuit_breaker: 0.5  # 50% failure rate

# Rate limiting in webhook server
rateLimitMax: 100
rateLimitWindow: 60000  # 1 minute
```

## Troubleshooting

### Common Issues

1. **NGROK not found**
   ```bash
   # Install NGROK
   brew install ngrok/ngrok/ngrok
   
   # Verify installation
   ngrok version
   ```

2. **Auth token not set**
   ```bash
   # Set auth token
   export NGROK_AUTHTOKEN=your_token_here
   
   # Or configure via CLI
   ngrok config add-authtoken your_token_here
   ```

3. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :3000
   
   # Kill process
   kill -9 <PID>
   ```

4. **Tunnel connection failed**
   ```bash
   # Check NGROK status
   curl http://localhost:4040/api/tunnels
   
   # Restart NGROK
   node scripts/ngrok-manager.js restart
   ```

### Debug Mode

Enable debug logging:

```env
NGROK_LOG_LEVEL=debug
NODE_ENV=development
DEBUG=ngrok:*
```

### Health Check Endpoints

Each service provides health check endpoints:

```bash
# Service health checks
curl http://localhost:3000/health  # Web app
curl http://localhost:8000/health  # API server
curl http://localhost:4000/health  # Webhook server
curl http://localhost:4040/api/tunnels  # NGROK status
```

## Performance Optimization

### 1. Connection Pooling

```yaml
# Optimize connections
max_conns: 0  # Unlimited
heartbeat_interval: 30s
session_heartbeat_interval: 30s
```

### 2. Compression

```yaml
# Enable compression
compression: true
websocket_tcp_converter: true
```

### 3. Circuit Breakers

```yaml
# Prevent cascade failures
circuit_breaker: 0.5  # 50% failure threshold
```

### 4. Health Check Tuning

```javascript
// Adjust health check intervals
const monitor = new NgrokHealthMonitor({
  checkInterval: 30000,        // 30 seconds
  alertThreshold: 3,           // 3 consecutive failures
  responseTimeThreshold: 5000  // 5 second timeout
});
```

## Integration Examples

### GitHub Actions

```yaml
name: Deploy with NGROK
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup NGROK
        run: |
          npm install
          npm run services:start
      - name: Test webhooks
        run: |
          curl ${{ env.NGROK_WEBHOOK_URL }}/webhook/github
```

### Docker Integration

```dockerfile
# Add to Dockerfile
RUN npm install -g @ngrok/ngrok
COPY config/ngrok/ /app/config/ngrok/
CMD ["npm", "run", "services:start"]
```

### CI/CD Pipeline

```bash
# In your CI/CD pipeline
export NGROK_AUTHTOKEN=${{ secrets.NGROK_TOKEN }}
npm run services:start
npm run test:integration
npm run services:stop
```

## API Reference

### NGROK Manager API

```javascript
const NgrokManager = require('./scripts/ngrok-manager');

const manager = new NgrokManager({
  configPath: './config/ngrok/ngrok-advanced.yml',
  tunnels: ['webapp', 'api', 'websocket']
});

await manager.initialize();
const urls = manager.getTunnelUrls();
const status = await manager.getStatus();
```

### Webhook Server API

```javascript
const WebhookServer = require('./scripts/webhook-server');

const server = new WebhookServer({
  port: 4000,
  enableSecurity: true,
  rateLimitMax: 100
});

await server.start();
```

### Health Monitor API

```javascript
const NgrokHealthMonitor = require('./scripts/ngrok-health-monitor');

const monitor = new NgrokHealthMonitor({
  checkInterval: 30000,
  enableSlackAlerts: true
});

await monitor.start();
```

## Support

For issues and questions:

- **Documentation**: This guide
- **Logs**: Check `logs/ngrok*.log` files
- **Status**: Use `claude-code-ngrok status`
- **Health**: Use `node scripts/ngrok-health-monitor.js status`

## License

This NGROK integration is part of Claude Code Dev Stack v3.6.9 and follows the same MIT license terms.