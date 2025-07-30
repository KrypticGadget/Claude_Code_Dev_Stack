# DevOps & Deployment Workflow Prompts

Use these prompts for DevOps, CI/CD, and deployment tasks with the Claude Code Agent System.

## CI/CD Pipeline Setup

### GitHub Actions Pipeline
```
> Use the devops-engineering agent to create GitHub Actions workflow for [PROJECT TYPE] with build, test, and deploy stages to [ENVIRONMENT]
```

### Jenkins Pipeline
```
> Use the devops-engineering agent to setup Jenkins pipeline for [APPLICATION] with parallel stages, quality gates, and [DEPLOYMENT TARGET]
```

### GitLab CI/CD
```
> Use the devops-engineering agent to configure GitLab CI/CD for [PROJECT] with environments, manual approvals, and rollback capability
```

## Container Management

### Docker Configuration
```
> Use the devops-engineering agent to create Dockerfile for [APPLICATION TYPE] with multi-stage build, security scanning, and size optimization
```

### Docker Compose
```
> Use the devops-engineering agent to setup Docker Compose for [STACK] with service dependencies, volumes, and networking
```

### Container Registry
```
> Use the devops-engineering agent to configure container registry pipeline with vulnerability scanning and image signing for [REGISTRY]
```

## Kubernetes Deployment

### K8s Manifests
```
> Use the devops-engineering agent to create Kubernetes manifests for [APPLICATION] including deployments, services, and ingress
```

### Helm Charts
```
> Use the devops-engineering agent to develop Helm chart for [APPLICATION] with configurable values and dependency management
```

### K8s Operators
```
> Use the devops-engineering agent to implement Kubernetes operator for [CUSTOM RESOURCE] with reconciliation logic
```

## Infrastructure as Code

### Terraform Modules
```
> Use the devops-engineering agent to create Terraform modules for [INFRASTRUCTURE] on [CLOUD PROVIDER] with state management
```

### CloudFormation
```
> Use the devops-engineering agent to write CloudFormation templates for [AWS SERVICES] with parameters and outputs
```

### Ansible Playbooks
```
> Use the devops-engineering agent to develop Ansible playbooks for [CONFIGURATION TASK] supporting [OS TYPES]
```

## Monitoring & Observability

### Monitoring Stack
```
> Use the devops-engineering agent to setup monitoring using [Prometheus/Datadog] for [APPLICATION] with dashboards and alerts
```

### Log Aggregation
```
> Use the devops-engineering agent to implement centralized logging with [ELK/Splunk] collecting from [SOURCES]
```

### Distributed Tracing
```
> Use the devops-engineering agent to add distributed tracing using [Jaeger/Zipkin] for [MICROSERVICES]
```

## Security & Compliance

### Security Scanning
```
> Use the security-architecture agent to implement security scanning in CI/CD including SAST, DAST, and dependency scanning
```

### Secrets Management
```
> Use the security-architecture agent to setup secrets management using [Vault/AWS Secrets] with rotation and audit logging
```

### Compliance Automation
```
> Use the security-architecture agent to automate [COMPLIANCE STANDARD] checks in deployment pipeline
```

## Deployment Strategies

### Blue-Green Deployment
```
> Use the devops-engineering agent to implement blue-green deployment for [APPLICATION] with automated testing and rollback
```

### Canary Deployment
```
> Use the devops-engineering agent to setup canary deployment releasing to [PERCENTAGE]% of traffic with monitoring
```

### Rolling Updates
```
> Use the devops-engineering agent to configure rolling updates for [SERVICE] with health checks and rollback triggers
```

## Cloud Platform Specific

### AWS Deployment
```
> Use the devops-engineering agent to deploy [APPLICATION] to AWS using [ECS/EKS/Lambda] with auto-scaling and load balancing
```

### Azure Deployment
```
> Use the devops-engineering agent to setup Azure deployment for [APPLICATION] using [AKS/App Service] with managed identity
```

### GCP Deployment
```
> Use the devops-engineering agent to configure GCP deployment using [GKE/Cloud Run] with traffic splitting
```

## Performance & Scaling

### Auto-Scaling Rules
```
> Use the devops-engineering agent to configure auto-scaling based on [METRICS] with min [MIN] and max [MAX] instances
```

### CDN Configuration
```
> Use the devops-engineering agent to setup CDN using [CloudFront/Cloudflare] for [ASSETS] with cache optimization
```

### Load Balancer
```
> Use the devops-engineering agent to configure load balancer with [ALGORITHM] routing and health checks for [SERVICES]
```

## Backup & Recovery

### Backup Automation
```
> Use the devops-engineering agent to automate backups for [RESOURCES] with [FREQUENCY] schedule and [RETENTION] policy
```

### Disaster Recovery
```
> Use the devops-engineering agent to implement DR plan for [APPLICATION] with [RTO] recovery time and [RPO] recovery point
```

### Restore Testing
```
> Use the devops-engineering agent to create automated restore testing for [BACKUP TYPE] validating data integrity
```

## Development Tools

### Local Development
```
> Use the script-automation agent to create local development environment setup script installing all dependencies for [PROJECT]
```

### Git Hooks
```
> Use the script-automation agent to setup git hooks for [CHECKS] running before commit/push
```

### Development Containers
```
> Use the devops-engineering agent to create development container configuration for [IDE] with all tools pre-installed
```

## Variables to Replace:
- `[PROJECT TYPE]` - Node.js, Python, Java, etc.
- `[ENVIRONMENT]` - dev, staging, production
- `[CLOUD PROVIDER]` - AWS, Azure, GCP
- `[METRICS]` - CPU, memory, requests/sec
- `[COMPLIANCE STANDARD]` - SOC2, HIPAA, PCI
- `[FREQUENCY]` - hourly, daily, weekly
- `[RTO]` - Recovery time objective
- `[RPO]` - Recovery point objective