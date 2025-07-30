# Security Hardening Prompts

Use these prompts to enhance the security of existing applications and infrastructure.

## Security Audits

### Comprehensive Security Audit
```
> Use the security-architecture agent to perform complete security audit of [APPLICATION] and create remediation plan
```

### Vulnerability Assessment
```
> Use the security-architecture agent to scan [APPLICATION/INFRASTRUCTURE] for vulnerabilities and prioritize fixes
```

### Penetration Testing
```
> Use the security-architecture agent to conduct penetration testing on [APPLICATION] simulating [THREAT TYPES]
```

### Code Security Review
```
> Use the security-architecture agent to review [CODEBASE/MODULE] for security vulnerabilities and best practices
```

## Authentication & Access Control

### MFA Implementation
```
> Use the security-architecture agent to add multi-factor authentication to [APPLICATION] using [TOTP/SMS/BIOMETRIC]
```

### OAuth2 Security
```
> Use the security-architecture agent to harden OAuth2 implementation in [APPLICATION] with PKCE and token rotation
```

### Session Management
```
> Use the security-architecture agent to improve session security for [APPLICATION] with secure cookies and timeout policies
```

### API Key Management
```
> Use the security-architecture agent to implement secure API key management with rotation and usage monitoring
```

## Data Protection

### Encryption at Rest
```
> Use the security-architecture agent to implement encryption at rest for [DATA TYPES] in [STORAGE SYSTEMS]
```

### Encryption in Transit
```
> Use the security-architecture agent to ensure all data transmission for [APPLICATION] uses TLS 1.3 with perfect forward secrecy
```

### Data Masking
```
> Use the security-architecture agent to implement data masking for [SENSITIVE FIELDS] in [ENVIRONMENTS]
```

### Key Management
```
> Use the security-architecture agent to implement key management system using [KMS/HSM] with rotation policies
```

## Application Security

### Input Validation
```
> Use the security-architecture agent to implement comprehensive input validation for [APPLICATION] preventing injection attacks
```

### XSS Prevention
```
> Use the security-architecture agent to audit and fix XSS vulnerabilities in [APPLICATION] with CSP implementation
```

### CSRF Protection
```
> Use the security-architecture agent to implement CSRF protection for [APPLICATION] using tokens and SameSite cookies
```

### SQL Injection Prevention
```
> Use the security-architecture agent to audit and fix SQL injection vulnerabilities using parameterized queries
```

## Infrastructure Security

### Network Segmentation
```
> Use the security-architecture agent to implement network segmentation for [INFRASTRUCTURE] with security zones
```

### Firewall Rules
```
> Use the devops-engineering agent to audit and optimize firewall rules for [APPLICATION] following least privilege
```

### Container Security
```
> Use the security-architecture agent to harden container security for [APPLICATION] with image scanning and runtime protection
```

### Kubernetes Security
```
> Use the security-architecture agent to implement Kubernetes security best practices including RBAC and network policies
```

## Compliance & Standards

### OWASP Top 10
```
> Use the security-architecture agent to audit [APPLICATION] against OWASP Top 10 and implement fixes
```

### PCI DSS Compliance
```
> Use the security-architecture agent to implement PCI DSS requirements for [PAYMENT SYSTEM] including scoping
```

### HIPAA Compliance
```
> Use the security-architecture agent to ensure HIPAA compliance for [HEALTHCARE APPLICATION] with audit controls
```

### GDPR Implementation
```
> Use the security-architecture agent to implement GDPR requirements including consent management and data portability
```

## Monitoring & Incident Response

### Security Monitoring
```
> Use the security-architecture agent to implement security monitoring for [APPLICATION] with SIEM integration
```

### Intrusion Detection
```
> Use the security-architecture agent to setup IDS/IPS for [INFRASTRUCTURE] with threat intelligence feeds
```

### Incident Response Plan
```
> Use the security-architecture agent to create incident response plan for [APPLICATION] with playbooks
```

### Security Alerting
```
> Use the security-architecture agent to implement security alerting for [THREAT TYPES] with escalation procedures
```

## API Security

### Rate Limiting
```
> Use the security-architecture agent to implement rate limiting for [API] with per-user and per-endpoint limits
```

### API Gateway Security
```
> Use the security-architecture agent to harden API gateway for [APPLICATION] with authentication and threat protection
```

### Webhook Security
```
> Use the security-architecture agent to secure webhook endpoints with signature verification and replay protection
```

### GraphQL Security
```
> Use the security-architecture agent to implement GraphQL security including query depth limiting and introspection control
```

## Cloud Security

### AWS Security
```
> Use the security-architecture agent to audit and harden AWS infrastructure using Security Hub and GuardDuty
```

### Azure Security
```
> Use the security-architecture agent to implement Azure security best practices with Security Center recommendations
```

### GCP Security
```
> Use the security-architecture agent to secure GCP infrastructure using Security Command Center and Cloud Armor
```

### Multi-Cloud Security
```
> Use the security-architecture agent to implement consistent security policies across [CLOUD PROVIDERS]
```

## Specific Hardening Tasks

### SSL/TLS Configuration
```
> Use the security-architecture agent to harden SSL/TLS configuration for [APPLICATION] with A+ rating
```

### Database Security
```
> Use the database-architecture agent to harden database security for [DATABASE TYPE] including access controls
```

### File Upload Security
```
> Use the security-architecture agent to secure file upload functionality with type validation and malware scanning
```

### Secret Management
```
> Use the security-architecture agent to implement secrets management using [VAULT/SECRETS MANAGER] removing hardcoded secrets
```

## Variables to Replace:
- `[APPLICATION]` - Your application name
- `[THREAT TYPES]` - Internal, external, APT
- `[DATA TYPES]` - PII, financial, health records
- `[STORAGE SYSTEMS]` - Database, S3, file system
- `[SENSITIVE FIELDS]` - SSN, credit cards, emails
- `[ENVIRONMENTS]` - Dev, staging, prod
- `[INFRASTRUCTURE]` - AWS, on-premise, hybrid
- `[CLOUD PROVIDERS]` - AWS, Azure, GCP