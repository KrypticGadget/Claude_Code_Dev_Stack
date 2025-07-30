# New Enterprise System Project Template

Use these prompts to start various types of enterprise system projects with the Claude Code Agent System.

## ERP System

```
> Use the master-orchestrator agent to begin new project: "Enterprise Resource Planning system for [INDUSTRY] covering [MODULES] with multi-company support, workflow automation, and integration with [EXISTING SYSTEMS]."
```

## CRM Platform

```
> Use the master-orchestrator agent to begin new project: "Customer Relationship Management system for [BUSINESS TYPE] with contact management, sales pipeline, marketing automation, and [INTEGRATIONS]. Supporting [USER COUNT] users."
```

## Business Intelligence Platform

```
> Use the master-orchestrator agent to begin new project: "Business Intelligence platform with data warehousing, ETL pipelines, custom dashboards, and predictive analytics for [DATA SOURCES] serving [DEPARTMENTS]."
```

## HR Management System

```
> Use the master-orchestrator agent to begin new project: "Human Resources management system with employee records, payroll processing, benefits administration, performance tracking, and compliance for [COMPANY SIZE] employees."
```

## Supply Chain Management

```
> Use the master-orchestrator agent to begin new project: "Supply chain management system for [INDUSTRY] with inventory tracking, vendor management, procurement workflows, and logistics optimization across [LOCATIONS]."
```

## Document Management System

```
> Use the master-orchestrator agent to begin new project: "Enterprise document management system with version control, approval workflows, access controls, full-text search, and compliance for [REGULATIONS]."
```

## Financial Management System

```
> Use the master-orchestrator agent to begin new project: "Financial management system with general ledger, accounts payable/receivable, budgeting, financial reporting, and [COMPLIANCE STANDARDS] compliance."
```

## Project Management Platform

```
> Use the master-orchestrator agent to begin new project: "Enterprise project management platform for [METHODOLOGY] with resource planning, time tracking, collaboration tools, and portfolio management for [PROJECT TYPES]."
```

## Learning Management System

```
> Use the master-orchestrator agent to begin new project: "Corporate learning management system with course creation, certification tracking, compliance training, and analytics for [EMPLOYEE COUNT] learners."
```

## Asset Management System

```
> Use the master-orchestrator agent to begin new project: "Asset management system tracking [ASSET TYPES] with maintenance scheduling, depreciation calculation, location tracking, and lifecycle management."
```

## Variables to Replace:
- `[INDUSTRY]` - Manufacturing, retail, healthcare, etc.
- `[MODULES]` - Finance, inventory, HR, etc.
- `[EXISTING SYSTEMS]` - SAP, Oracle, legacy systems
- `[BUSINESS TYPE]` - B2B, B2C, specific industry
- `[USER COUNT]` - Expected system users
- `[DATA SOURCES]` - Databases, APIs, files
- `[DEPARTMENTS]` - Sales, marketing, operations
- `[COMPANY SIZE]` - 100, 1000, 10000+ employees
- `[LOCATIONS]` - Single site, multi-national
- `[REGULATIONS]` - HIPAA, SOX, GDPR
- `[COMPLIANCE STANDARDS]` - GAAP, IFRS, etc.
- `[METHODOLOGY]` - Agile, waterfall, hybrid

## Enterprise-Specific Requirements

### Scalability
```
"...designed for horizontal scaling supporting [TRANSACTION VOLUME] daily transactions across [USER BASE]"
```

### Security & Compliance
```
"...with role-based access control, audit logging, data encryption, and [COMPLIANCE] certification requirements"
```

### Integration Architecture
```
"...using enterprise service bus for integration with [SYSTEM LIST] via [REST/SOAP/MQ] protocols"
```

### High Availability
```
"...with 99.99% uptime SLA, disaster recovery, automated failover, and RTO of [MINUTES]"
```

### Multi-Tenancy
```
"...supporting multi-tenant architecture with data isolation, custom branding, and tenant-specific configurations"
```

## Deployment Considerations

### On-Premise
```
"...deployed on-premise in client data centers with [OS] servers and [DATABASE] database"
```

### Hybrid Cloud
```
"...hybrid deployment with sensitive data on-premise and compute in [CLOUD PROVIDER]"
```

### Private Cloud
```
"...deployed in private cloud with VPN access, dedicated resources, and compliance controls"
```

## Implementation Approach

### Phased Rollout
```
"...implemented in phases: Phase 1 [CORE MODULES], Phase 2 [ADDITIONAL MODULES], Phase 3 [INTEGRATIONS]"
```

### Department by Department
```
"...rolling out to [PILOT DEPARTMENT] first, then expanding to [OTHER DEPARTMENTS] based on lessons learned"
```

### Big Bang Migration
```
"...replacing [LEGACY SYSTEM] with full cutover on [TARGET DATE] including data migration and training"
```