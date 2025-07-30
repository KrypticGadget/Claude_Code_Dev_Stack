# Database Operations Workflow Prompts

Use these prompts for specific database-related tasks with the Claude Code Agent System.

## Database Design

### New Database Schema
```
> Use the database-architecture agent to design complete database schema for [APPLICATION TYPE] supporting [USER SCALE] with optimal normalization
```

### Multi-Tenant Schema
```
> Use the database-architecture agent to design multi-tenant database architecture using [APPROACH] for [TENANT COUNT] tenants
```

### NoSQL Data Model
```
> Use the database-architecture agent to design NoSQL data model for [USE CASE] optimizing for [ACCESS PATTERN]
```

## Performance Optimization

### Query Optimization
```
> Use the database-architecture agent to optimize slow query [QUERY DESCRIPTION] currently taking [CURRENT TIME] to under [TARGET TIME]
```

### Index Strategy
```
> Use the database-architecture agent to analyze and create indexing strategy for [TABLE/COLLECTION] based on query patterns
```

### Database Tuning
```
> Use the database-architecture agent to tune [DATABASE TYPE] configuration for [WORKLOAD TYPE] with [HARDWARE SPECS]
```

## Migration Tasks

### Schema Migration
```
> Use the database-architecture agent to create migration plan from [CURRENT SCHEMA] to [NEW SCHEMA] with zero downtime
```

### Database Migration
```
> Use the database-architecture agent to migrate data from [SOURCE DB] to [TARGET DB] handling [DATA VOLUME] with validation
```

### Version Upgrade
```
> Use the database-architecture agent to plan upgrade from [CURRENT VERSION] to [TARGET VERSION] with rollback strategy
```

## Data Management

### Backup Strategy
```
> Use the database-architecture agent to implement backup strategy for [DATABASE] with [RPO] recovery point and [RTO] recovery time
```

### Archival Process
```
> Use the database-architecture agent to design data archival for [DATA TYPE] older than [PERIOD] to [STORAGE SOLUTION]
```

### Data Purge
```
> Use the database-architecture agent to implement data purge strategy for [TABLE] removing records based on [CRITERIA]
```

## Replication & HA

### Replication Setup
```
> Use the database-architecture agent to configure [REPLICATION TYPE] replication for [DATABASE] across [REGIONS/SERVERS]
```

### Failover Strategy
```
> Use the database-architecture agent to implement automatic failover for [DATABASE] with [FAILOVER TIME] maximum downtime
```

### Read Replica
```
> Use the database-architecture agent to setup read replicas for [USE CASE] with load balancing and lag monitoring
```

## Security Implementation

### Encryption Setup
```
> Use the security-architecture agent to implement database encryption for [DATA FIELDS] with key rotation policy
```

### Access Control
```
> Use the security-architecture agent to design database access control with roles for [USER TYPES] following principle of least privilege
```

### Audit Logging
```
> Use the security-architecture agent to implement database audit logging for [COMPLIANCE] tracking [OPERATIONS]
```

## Monitoring & Maintenance

### Performance Monitoring
```
> Use the database-architecture agent to setup monitoring for [DATABASE] tracking queries, locks, connections, and resource usage
```

### Health Checks
```
> Use the database-architecture agent to implement health check system monitoring replication lag, disk space, and query performance
```

### Maintenance Tasks
```
> Use the database-architecture agent to create maintenance plan including vacuum, analyze, and statistics updates for [DATABASE]
```

## Specific Database Tasks

### PostgreSQL Optimization
```
> Use the database-architecture agent to optimize PostgreSQL for [WORKLOAD] including vacuum settings, shared buffers, and work_mem
```

### MongoDB Sharding
```
> Use the database-architecture agent to implement MongoDB sharding for [COLLECTION] using [SHARD KEY] across [SHARD COUNT] shards
```

### Redis Configuration
```
> Use the database-architecture agent to configure Redis for [USE CASE] with persistence, memory limits, and eviction policy
```

### Elasticsearch Mapping
```
> Use the database-architecture agent to design Elasticsearch mapping for [DOCUMENT TYPE] optimizing for [SEARCH PATTERNS]
```

## Data Integrity

### Constraint Design
```
> Use the database-architecture agent to implement data integrity constraints for [SCHEMA] including foreign keys, checks, and triggers
```

### Data Validation
```
> Use the database-architecture agent to create data validation rules for [DATA FLOW] ensuring consistency and accuracy
```

### Reconciliation
```
> Use the database-architecture agent to design reconciliation process between [SYSTEM A] and [SYSTEM B] databases
```

## Advanced Patterns

### Event Sourcing
```
> Use the database-architecture agent to implement event sourcing for [DOMAIN] with event store and projection design
```

### CQRS Implementation
```
> Use the database-architecture agent to design CQRS pattern separating [WRITE MODEL] from [READ MODEL]
```

### Time-Series Data
```
> Use the database-architecture agent to design time-series database for [METRICS TYPE] with [RETENTION PERIOD] and aggregations
```

## Variables to Replace:
- `[APPLICATION TYPE]` - E-commerce, SaaS, etc.
- `[USER SCALE]` - 1K, 100K, 1M users
- `[APPROACH]` - Schema-per-tenant, shared schema
- `[DATABASE TYPE]` - PostgreSQL, MySQL, MongoDB
- `[WORKLOAD TYPE]` - OLTP, OLAP, mixed
- `[DATA VOLUME]` - GB, TB of data
- `[REPLICATION TYPE]` - Master-slave, multi-master
- `[COMPLIANCE]` - HIPAA, PCI, GDPR
- `[SHARD KEY]` - user_id, timestamp, etc.