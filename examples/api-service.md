# Example: RESTful API Service with Authentication

This example demonstrates building a secure, scalable payment processing API service.

## Project Description
"RESTful API service for payment processing with multi-provider support, webhook notifications, fraud detection, and comprehensive admin dashboard"

## Quick Start Workflow

### Phase 1: API Architecture

```bash
> Use the backend-services agent to design payment processing API architecture
```

**Core Design Decisions**:
- RESTful API with OpenAPI 3.0 specification
- Microservices architecture
- Event-driven processing
- Multi-provider abstraction layer

### Phase 2: Security Implementation

```bash
> Use the security-architecture agent to implement payment API security
```

**Security Layers Implemented**:

1. **Authentication & Authorization**
   ```javascript
   // OAuth 2.0 + JWT implementation
   POST /auth/token
   {
     "grant_type": "client_credentials",
     "client_id": "{{client_id}}",
     "client_secret": "{{client_secret}}",
     "scope": "payments:write"
   }
   ```

2. **API Key Management**
   - Separate keys for test/live environments
   - Key rotation mechanism
   - Rate limiting per key
   - IP whitelisting

3. **Request Signing**
   ```javascript
   // HMAC-SHA256 signature verification
   const signature = crypto
     .createHmac('sha256', webhookSecret)
     .update(JSON.stringify(payload))
     .digest('hex');
   ```

### Phase 3: Core API Development

```bash
> Use the api-integration-specialist agent to implement payment provider integrations
```

**Providers Integrated**:
- Stripe
- PayPal
- Square
- Authorize.net
- Custom bank integrations

**Unified API Interface**:
```javascript
// POST /v1/payments
{
  "amount": 10000, // cents
  "currency": "USD",
  "payment_method": {
    "type": "card",
    "card": {
      "number": "4242424242424242",
      "exp_month": 12,
      "exp_year": 2025,
      "cvc": "123"
    }
  },
  "metadata": {
    "order_id": "ord_123456"
  }
}

// Response
{
  "id": "pay_a1b2c3d4e5",
  "status": "succeeded",
  "amount": 10000,
  "currency": "USD",
  "provider": "stripe",
  "provider_transaction_id": "ch_1234567890",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Phase 4: Database Architecture

```bash
> Use the database-architecture agent to design payment data model with PCI compliance
```

**Schema Design**:
```sql
-- Core tables with encryption
CREATE TABLE payments (
  id UUID PRIMARY KEY,
  amount BIGINT NOT NULL,
  currency VARCHAR(3) NOT NULL,
  status payment_status NOT NULL,
  provider VARCHAR(50) NOT NULL,
  provider_transaction_id VARCHAR(255),
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit logging
CREATE TABLE payment_events (
  id UUID PRIMARY KEY,
  payment_id UUID REFERENCES payments(id),
  event_type VARCHAR(50) NOT NULL,
  event_data JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PCI-compliant tokenization
CREATE TABLE payment_methods (
  id UUID PRIMARY KEY,
  customer_id UUID NOT NULL,
  token VARCHAR(255) UNIQUE NOT NULL,
  type payment_method_type NOT NULL,
  last_four VARCHAR(4),
  exp_month INTEGER,
  exp_year INTEGER,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Phase 5: Webhook System

```bash
> Use the middleware-specialist agent to implement webhook delivery system
```

**Webhook Implementation**:
- Exponential backoff retry logic
- Event deduplication
- Signature verification
- Dead letter queue
- Webhook debugging tools

```javascript
// Webhook delivery service
class WebhookService {
  async deliver(event) {
    const attempts = 0;
    const maxAttempts = 5;
    
    while (attempts < maxAttempts) {
      try {
        const signature = this.generateSignature(event);
        const response = await axios.post(webhook.url, event, {
          headers: {
            'X-Webhook-Signature': signature,
            'X-Webhook-Timestamp': Date.now(),
            'X-Webhook-Event': event.type
          },
          timeout: 30000
        });
        
        await this.logDelivery(webhook, event, response);
        break;
      } catch (error) {
        attempts++;
        await this.handleFailure(webhook, event, error, attempts);
        await this.exponentialBackoff(attempts);
      }
    }
  }
}
```

### Phase 6: Fraud Detection

```bash
> Use the performance-optimization agent to implement real-time fraud detection
```

**Fraud Detection Rules**:
```javascript
// Real-time fraud scoring
const fraudChecks = [
  velocityCheck,      // Transaction velocity
  geoCheck,          // Geographic anomalies  
  amountCheck,       // Unusual amounts
  deviceCheck,       // Device fingerprinting
  behaviorCheck      // User behavior analysis
];

const fraudScore = await Promise.all(
  fraudChecks.map(check => check(transaction))
).then(scores => scores.reduce((a, b) => a + b) / scores.length);

if (fraudScore > 0.7) {
  await flagForReview(transaction);
}
```

### Phase 7: Admin Dashboard

```bash
> Use the frontend-mockup agent to create admin dashboard for payment monitoring
```

**Dashboard Features**:
- Real-time transaction monitoring
- Fraud alert management
- Provider health status
- Revenue analytics
- Webhook logs
- API key management

## Production Infrastructure

```bash
> Use the devops-engineering agent to setup production infrastructure for payment API
```

### Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cloudflare│────▶│Load Balancer│────▶│ API Gateway │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
                   ┌────────────┐       ┌────────────┐       ┌────────────┐
                   │Payment API │       │Webhook Svc │       │ Fraud Svc  │
                   └────────────┘       └────────────┘       └────────────┘
                          │                     │                     │
                          └─────────────────────┼─────────────────────┘
                                                ▼
                                   ┌────────────────────┐
                                   │   PostgreSQL       │
                                   │   (Multi-Region)   │
                                   └────────────────────┘
```

### Deployment Configuration
- **Kubernetes**: EKS with auto-scaling
- **Monitoring**: Datadog APM + Custom metrics
- **Secrets**: AWS Secrets Manager
- **Compliance**: PCI DSS Level 1

## Performance Metrics

### API Performance
- Requests per second: 10,000+
- P99 latency: <100ms
- Availability: 99.99%
- Zero data breaches

### Business Metrics
- Transaction volume: $50M/month
- API consumers: 500+ businesses
- Webhook delivery rate: 99.8%
- Fraud detection accuracy: 96%

## Testing Strategy

```bash
> Use the testing-automation agent to implement comprehensive API testing
```

**Test Coverage**:
```javascript
// Integration tests
describe('Payment API', () => {
  test('successful payment flow', async () => {
    const payment = await createPayment({
      amount: 1000,
      currency: 'USD',
      payment_method: testCard
    });
    
    expect(payment.status).toBe('succeeded');
    expect(webhookReceived).toBe(true);
  });
  
  test('fraud detection triggers', async () => {
    const payment = await createPayment({
      amount: 999999,
      currency: 'USD',
      payment_method: suspiciousCard
    });
    
    expect(payment.status).toBe('requires_review');
  });
});
```

## Key Implementation Files

### API Route Handler
```javascript
// routes/payments.js
router.post('/v1/payments', 
  authenticate,
  validateRequest(paymentSchema),
  rateLimiter,
  async (req, res) => {
    const payment = await paymentService.create(req.body);
    await webhookService.queue('payment.created', payment);
    res.json(payment);
  }
);
```

### Provider Abstraction
```javascript
// providers/provider-factory.js
class ProviderFactory {
  static getProvider(providerName) {
    switch(providerName) {
      case 'stripe': return new StripeProvider();
      case 'paypal': return new PayPalProvider();
      case 'square': return new SquareProvider();
      default: throw new Error('Unknown provider');
    }
  }
}
```

## Commands Used

```bash
# Initial architecture
> Use the backend-services agent to design payment processing API architecture

# Security implementation
> Use the security-architecture agent to implement PCI-compliant security

# Database design
> Use the database-architecture agent to design payment schema with encryption

# Integration development
> Use the api-integration-specialist agent to implement Stripe integration

# Performance optimization
> Use the performance-optimization agent to optimize API response times

# Testing
> Use the testing-automation agent to create API test suite

# Deployment
> Use the devops-engineering agent to setup Kubernetes deployment
```

This example shows how the agent system can build a production-grade API service with enterprise security, scalability, and monitoring.