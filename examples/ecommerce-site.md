# Example: Full E-commerce Platform

This example demonstrates building a modern e-commerce platform with inventory management, multi-vendor support, and omnichannel capabilities.

## Project Description
"Full-featured e-commerce platform with multi-vendor marketplace, inventory management, AI-powered recommendations, mobile apps, and POS integration"

## Rapid Development Workflow

### Phase 1: Business Strategy

```bash
> Use the master-orchestrator agent to begin new project: "Full-featured e-commerce platform with multi-vendor marketplace, inventory management, AI-powered recommendations, and POS integration"
```

**Strategic Decisions**:
- Business model: Marketplace with 15% commission
- Target: SMB retailers + individual sellers
- Differentiator: AI recommendations + unified inventory
- Revenue projection: $5M GMV Year 1

### Phase 2: E-commerce Architecture

```bash
> Use the technical-specifications agent to define e-commerce platform requirements
```

**Core Modules Identified**:
1. **Storefront** - Customer-facing shopping experience
2. **Vendor Portal** - Seller management interface  
3. **Admin Dashboard** - Platform administration
4. **Inventory System** - Multi-location inventory
5. **Order Management** - Order processing & fulfillment
6. **Payment Gateway** - Multi-provider payments
7. **Mobile Apps** - iOS/Android shopping apps
8. **POS Integration** - Offline/online sync

### Phase 3: Frontend Development

```bash
> Use the frontend-architecture agent to design responsive e-commerce frontend
```

**Frontend Structure**:
```
storefront/
├── components/
│   ├── ProductGrid/
│   ├── ShoppingCart/
│   ├── Checkout/
│   └── AccountDashboard/
├── features/
│   ├── search/
│   ├── recommendations/
│   ├── wishlist/
│   └── reviews/
└── pages/
    ├── home/
    ├── category/
    ├── product/
    └── checkout/
```

**Key Features Implemented**:
- Server-side rendering for SEO
- Progressive Web App capabilities
- Real-time inventory updates
- Personalized recommendations
- One-click checkout

### Phase 4: Backend Services

```bash
> Use the backend-services agent to implement e-commerce microservices
```

**Microservices Architecture**:
```yaml
services:
  - name: product-service
    responsibilities:
      - Product catalog
      - Categories & attributes
      - Search & filtering
    
  - name: inventory-service
    responsibilities:
      - Stock management
      - Multi-location tracking
      - Real-time updates
      
  - name: order-service
    responsibilities:
      - Order processing
      - Payment orchestration
      - Fulfillment tracking
      
  - name: user-service
    responsibilities:
      - Customer accounts
      - Vendor accounts
      - Authentication
      
  - name: recommendation-service
    responsibilities:
      - AI/ML recommendations
      - Personalization
      - Analytics
```

### Phase 5: Database Design

```bash
> Use the database-architecture agent to design multi-vendor e-commerce schema
```

**Key Schema Elements**:
```sql
-- Multi-vendor products
CREATE TABLE products (
  id UUID PRIMARY KEY,
  vendor_id UUID REFERENCES vendors(id),
  sku VARCHAR(100) UNIQUE,
  name VARCHAR(255),
  description TEXT,
  base_price DECIMAL(10,2),
  attributes JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inventory tracking
CREATE TABLE inventory (
  id UUID PRIMARY KEY,
  product_id UUID REFERENCES products(id),
  location_id UUID REFERENCES locations(id),
  quantity INTEGER DEFAULT 0,
  reserved_quantity INTEGER DEFAULT 0,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(product_id, location_id)
);

-- Order management
CREATE TABLE orders (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES users(id),
  status order_status NOT NULL,
  subtotal DECIMAL(10,2),
  tax DECIMAL(10,2),
  shipping DECIMAL(10,2),
  total DECIMAL(10,2),
  shipping_address JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Phase 6: Payment Integration

```bash
> Use the api-integration-specialist agent to implement multi-provider payment system
```

**Payment Providers**:
- Stripe (Cards, ACH)
- PayPal (Express Checkout)
- Apple Pay / Google Pay
- Buy now, pay later (Affirm)
- Cryptocurrency (Optional)

**Implementation Example**:
```javascript
// Unified payment interface
class PaymentProcessor {
  async processPayment(order, paymentMethod) {
    const provider = this.getProvider(paymentMethod.type);
    
    try {
      // Process payment
      const result = await provider.charge({
        amount: order.total,
        currency: order.currency,
        source: paymentMethod.token,
        metadata: { orderId: order.id }
      });
      
      // Update order status
      await orderService.updatePaymentStatus(order.id, 'paid');
      
      // Trigger fulfillment
      await fulfillmentService.initiate(order.id);
      
      return result;
    } catch (error) {
      await this.handlePaymentFailure(order, error);
      throw error;
    }
  }
}
```

### Phase 7: AI Recommendations

```bash
> Use the performance-optimization agent to implement AI-powered product recommendations
```

**Recommendation Engine**:
```python
# ML model for personalized recommendations
class RecommendationEngine:
    def __init__(self):
        self.collaborative_filter = CollaborativeFiltering()
        self.content_filter = ContentBasedFiltering()
        self.trending_analyzer = TrendingProducts()
    
    def get_recommendations(self, user_id, context):
        # Combine multiple recommendation strategies
        collab_recs = self.collaborative_filter.recommend(user_id)
        content_recs = self.content_filter.recommend(user_id)
        trending = self.trending_analyzer.get_trending(context.category)
        
        # Weighted combination
        recommendations = self.combine_recommendations([
            (collab_recs, 0.4),
            (content_recs, 0.3),
            (trending, 0.3)
        ])
        
        return self.personalize_order(recommendations, user_id)
```

### Phase 8: Mobile Development

```bash
> Use the mobile-development agent to create native e-commerce mobile apps
```

**Mobile Features**:
- Barcode scanning
- Push notifications
- Offline browsing
- Mobile payments
- AR product preview

### Phase 9: POS Integration

```bash
> Use the integration-setup agent to implement POS system integration
```

**POS Sync Features**:
- Real-time inventory sync
- Unified customer database
- Cross-channel promotions
- Omnichannel returns

## Production Deployment

```bash
> Use the devops-engineering agent to deploy e-commerce platform
```

**Infrastructure**:
```yaml
production:
  frontend:
    - CloudFront CDN
    - S3 static hosting
    - Lambda@Edge for SSR
    
  backend:
    - EKS cluster (microservices)
    - RDS Aurora (PostgreSQL)
    - ElastiCache (Redis)
    - OpenSearch (product search)
    
  storage:
    - S3 (product images)
    - EFS (shared files)
    
  monitoring:
    - CloudWatch
    - Datadog APM
    - Sentry error tracking
```

## Results & Performance

### Technical Metrics
- Page load time: <1.5s
- Search response: <200ms  
- 99.95% uptime
- Handles 50K concurrent users

### Business Metrics (6 months)
- GMV: $2.8M
- Active sellers: 850
- Product catalog: 125K SKUs
- Conversion rate: 3.2%
- Mobile sales: 65%

### SEO Performance
- Organic traffic: +450%
- Page 1 rankings: 2,500 keywords
- Core Web Vitals: All green

## Key Features Showcase

### 1. Smart Search
```javascript
// Elasticsearch implementation
const searchProducts = async (query, filters) => {
  const results = await elastic.search({
    index: 'products',
    body: {
      query: {
        bool: {
          must: [
            { 
              multi_match: {
                query,
                fields: ['name^3', 'description', 'brand^2'],
                type: 'best_fields'
              }
            }
          ],
          filter: buildFilters(filters)
        }
      },
      aggs: buildAggregations(),
      highlight: {
        fields: {
          name: {},
          description: {}
        }
      }
    }
  });
  
  return formatSearchResults(results);
};
```

### 2. Real-time Inventory
```javascript
// WebSocket inventory updates
io.on('connection', (socket) => {
  socket.on('subscribe:product', (productId) => {
    socket.join(`product:${productId}`);
    
    // Send current inventory
    const inventory = await getInventory(productId);
    socket.emit('inventory:update', inventory);
  });
});

// Broadcast inventory changes
inventoryEvents.on('stock:changed', ({ productId, quantity }) => {
  io.to(`product:${productId}`).emit('inventory:update', { 
    productId, 
    quantity,
    availability: quantity > 0 ? 'in_stock' : 'out_of_stock'
  });
});
```

### 3. Vendor Dashboard
```javascript
// Vendor analytics API
router.get('/api/vendor/analytics', authenticate, async (req, res) => {
  const vendorId = req.user.vendorId;
  
  const analytics = await Promise.all([
    getVendorRevenue(vendorId, req.query),
    getTopProducts(vendorId, req.query),
    getCustomerMetrics(vendorId, req.query),
    getInventoryHealth(vendorId)
  ]);
  
  res.json({
    revenue: analytics[0],
    topProducts: analytics[1],
    customers: analytics[2],
    inventory: analytics[3]
  });
});
```

## Commands Used Throughout

```bash
# Initial setup
> Use the master-orchestrator agent to begin new project: "Full e-commerce platform..."

# Architecture
> Use the frontend-architecture agent to design multi-page e-commerce frontend
> Use the database-architecture agent to design multi-vendor marketplace schema

# Development
> Use the backend-services agent to implement product catalog microservice
> Use the api-integration-specialist agent to integrate Stripe and PayPal
> Use the frontend-mockup agent to create checkout flow prototype

# Optimization
> Use the performance-optimization agent to optimize product search
> Use the security-architecture agent to implement PCI compliance

# Deployment
> Use the devops-engineering agent to setup auto-scaling infrastructure
> Use the technical-documentation agent to create vendor API documentation
```

This comprehensive example demonstrates how the Claude Code Agent System can build a complete, production-ready e-commerce platform with modern features and scalable architecture.