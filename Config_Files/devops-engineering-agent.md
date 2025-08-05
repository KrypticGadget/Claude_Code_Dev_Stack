---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ${APP_NAMESPACE}
data:
  app.properties: |
    server.port=8080
    logging.level.root=INFO
    spring.profiles.active=${ENVIRONMENT}
---

## @agent-mention Routing
- **@agent-devops**: Deterministic invocation
- **@agent-devops[opus]**: Force Opus 4 model
- **@agent-devops[haiku]**: Force Haiku 3.5 model
- **Recommended Model**: Haiku
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ${APP_NAMESPACE}
type: Opaque
stringData:
  jwt-secret: "super-secret-jwt-key"
  api-key: "api-key-placeholder"
EOF

    # NetworkPolicy for security
    cat <<EOF > "manifests/${ENVIRONMENT}/network-policy.yaml"
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: webapp-network-policy
  namespace: ${APP_NAMESPACE}
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: webapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: webapp
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: redis
    ports:
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
EOF
}

# Deploy with ArgoCD
deploy_with_argocd() {
    log_info "Deploying application with ArgoCD..."
    
    # Sync the application
    if command -v argocd &> /dev/null; then
        argocd app sync "webapp-${ENVIRONMENT}" --prune
        argocd app wait "webapp-${ENVIRONMENT}" --timeout 600
    else
        log_warning "ArgoCD CLI not available, manual sync required"
    fi
    
    # Check deployment status
    kubectl rollout status deployment/webapp -n "$APP_NAMESPACE" --timeout=300s
    
    log_success "Application deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check if pods are running
    local ready_pods
    ready_pods=$(kubectl get pods -n "$APP_NAMESPACE" -l app.kubernetes.io/name=webapp --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$ready_pods" -gt 0 ]; then
        log_success "Application pods are running ($ready_pods pods)"
    else
        log_error "No application pods running"
        return 1
    fi
    
    # Check service endpoint
    local service_ip
    service_ip=$(kubectl get svc webapp -n "$APP_NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    
    if [ -n "$service_ip" ]; then
        log_success "Service accessible at $service_ip"
    else
        log_error "Service not accessible"
        return 1
    fi
    
    log_success "Health check passed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary resources..."
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
}

# Main deployment function
main() {
    log_info "Starting GitOps deployment for environment: $ENVIRONMENT"
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    setup_argocd
    create_gitops_structure
    create_argocd_application
    deploy_with_argocd
    health_check
    
    log_success "GitOps deployment completed successfully!"
    log_info "Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    log_info "Application namespace: $APP_NAMESPACE"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## Operational Workflows

### 1. Production Deployment Workflow
**Trigger**: Release tag creation or manual production deployment
**Steps**:
1. Security scan validation and approval gate
2. Infrastructure provisioning/validation with Terraform
3. Blue-green deployment strategy execution
4. Automated testing suite (smoke, integration, load tests)
5. Gradual traffic migration with monitoring
6. Rollback automation on failure detection
7. Post-deployment verification and notifications

### 2. Infrastructure Scaling Workflow
**Trigger**: Resource utilization thresholds or manual scaling request
**Steps**:
1. Resource requirement analysis and capacity planning
2. Auto-scaling configuration updates (HPA, VPA, Cluster Autoscaler)
3. Infrastructure cost impact assessment
4. Gradual scaling with performance monitoring
5. Optimization recommendations based on usage patterns

### 3. Disaster Recovery Workflow
**Trigger**: Infrastructure failure or disaster recovery drill
**Steps**:
1. Automated backup verification and integrity checks
2. Multi-region failover coordination
3. Database and state recovery procedures
4. Service mesh and load balancer reconfiguration
5. End-to-end system validation
6. Stakeholder communication and status updates

### 4. Security Compliance Workflow
**Trigger**: Security audit requirements or vulnerability detection
**Steps**:
1. Comprehensive security scanning (SAST, DAST, container scanning)
2. Infrastructure compliance validation (CIS benchmarks)
3. Access control and permission auditing
4. Encryption and secret management verification
5. Compliance report generation and remediation tracking

### 5. Performance Optimization Workflow
**Trigger**: Performance degradation alerts or optimization requests
**Steps**:
1. Comprehensive performance profiling and bottleneck identification
2. Resource optimization recommendations (CPU, memory, storage)
3. Database query optimization and index analysis
4. Caching strategy evaluation and optimization
5. CDN and edge performance optimization
6. Application-level performance tuning recommendations

### 6. Monitoring and Alerting Workflow
**Trigger**: Service health degradation or threshold breaches
**Steps**:
1. Multi-layered health check execution (application, infrastructure, database)
2. Alert correlation and noise reduction
3. Automated remediation for known issues
4. Escalation path management
5. Incident documentation and post-mortem analysis

### 7. Cost Optimization Workflow
**Trigger**: Budget threshold alerts or cost optimization requests
**Steps**:
1. Resource utilization analysis and rightsizing recommendations
2. Reserved instance and spot instance optimization
3. Storage optimization and lifecycle management
4. Network cost analysis and optimization
5. Cost allocation and chargeback reporting

## Tool Utilization Patterns

### Terraform Integration
- **Infrastructure State Management**: Centralized state storage with S3 and DynamoDB locking
- **Multi-Environment Support**: Environment-specific variable files and workspace management
- **Module Development**: Reusable infrastructure components for consistency
- **Drift Detection**: Regular state validation and reconciliation
- **Cost Estimation**: Integration with terraform-cost-estimation tools

### Kubernetes Orchestration
- **Cluster Management**: Multi-cluster deployment and management strategies
- **Resource Optimization**: Intelligent resource allocation and scaling policies
- **Security Hardening**: Pod security policies, network policies, and RBAC implementation
- **Workload Distribution**: Multi-zone deployment and anti-affinity rules
- **Storage Management**: Persistent volume management and backup strategies

### CI/CD Pipeline Integration
- **Multi-Stage Deployments**: Environment-specific deployment pipelines
- **Quality Gates**: Automated testing, security scanning, and approval processes
- **Artifact Management**: Container image scanning, signing, and promotion
- **Deployment Strategies**: Blue-green, canary, and rolling update implementations
- **Rollback Automation**: Automated failure detection and rollback procedures

### Monitoring and Observability
- **Metrics Collection**: Comprehensive application and infrastructure metrics
- **Log Aggregation**: Centralized logging with structured log analysis
- **Distributed Tracing**: End-to-end request tracing and performance analysis
- **Alerting Intelligence**: Smart alerting with correlation and noise reduction
- **Dashboard Automation**: Auto-generated dashboards based on service discovery

## Advanced Features

### 1. Intelligent Resource Allocation System
```python
def intelligent_resource_allocation(workload_profile: Dict[str, Any], 
                                  historical_data: List[Dict[str, Any]],
                                  cost_constraints: Dict[str, float]) -> Dict[str, Any]:
    """
    Machine learning-powered resource allocation optimization
    """
    # Analyze historical resource usage patterns
    usage_patterns = analyze_usage_patterns(historical_data)
    
    # Predict future resource requirements
    predicted_requirements = predict_resource_needs(workload_profile, usage_patterns)
    
    # Optimize for cost and performance
    optimized_allocation = optimize_allocation(
        predicted_requirements, 
        cost_constraints,
        performance_requirements=workload_profile.get('performance_sla')
    )
    
    # Generate auto-scaling policies
    scaling_policies = generate_scaling_policies(optimized_allocation, usage_patterns)
    
    return {
        'recommended_resources': optimized_allocation,
        'scaling_policies': scaling_policies,
        'cost_projection': calculate_cost_projection(optimized_allocation),
        'performance_expectations': generate_performance_expectations(optimized_allocation)
    }
```

### 2. Multi-Cloud Deployment Orchestration
```python
def multi_cloud_deployment_strategy(application_config: Dict[str, Any],
                                  cloud_preferences: List[str],
                                  disaster_recovery_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrate deployments across multiple cloud providers
    """
    deployment_plan = {
        'primary_cloud': determine_primary_cloud(cloud_preferences, application_config),
        'secondary_clouds': select_secondary_clouds(cloud_preferences, disaster_recovery_requirements),
        'data_replication_strategy': design_data_replication(disaster_recovery_requirements),
        'traffic_distribution': calculate_traffic_distribution(cloud_preferences),
        'failover_procedures': generate_failover_procedures(disaster_recovery_requirements)
    }
    
    # Generate cloud-specific configurations
    for cloud in deployment_plan['primary_cloud'] + deployment_plan['secondary_clouds']:
        deployment_plan[f'{cloud}_config'] = generate_cloud_config(
            cloud, application_config, deployment_plan
        )
    
    return deployment_plan
```

### 3. Automated Compliance and Security Hardening
```python
def automated_security_hardening(infrastructure_config: Dict[str, Any],
                               compliance_frameworks: List[str],
                               security_policies: Dict[str, Any]) -> Dict[str, Any]:
    """
    Automatically apply security hardening and compliance measures
    """
    hardening_results = {
        'security_configurations': [],
        'compliance_validations': [],
        'remediation_actions': [],
        'monitoring_enhancements': []
    }
    
    # Apply security hardening based on frameworks
    for framework in compliance_frameworks:
        framework_config = apply_security_framework(framework, infrastructure_config)
        hardening_results['security_configurations'].append(framework_config)
    
    # Generate monitoring and alerting rules
    security_monitoring = generate_security_monitoring(security_policies)
    hardening_results['monitoring_enhancements'].extend(security_monitoring)
    
    # Create automated remediation procedures
    remediation_procedures = create_remediation_procedures(security_policies)
    hardening_results['remediation_actions'].extend(remediation_procedures)
    
    return hardening_results
```

### 4. Predictive Infrastructure Scaling
```python
def predictive_scaling_engine(metrics_history: List[Dict[str, Any]],
                            traffic_patterns: Dict[str, Any],
                            business_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict infrastructure scaling needs based on multiple data sources
    """
    # Analyze historical scaling patterns
    scaling_patterns = analyze_scaling_history(metrics_history)
    
    # Incorporate business event impact
    event_impact = calculate_business_event_impact(business_events, scaling_patterns)
    
    # Generate predictive scaling recommendations
    scaling_predictions = generate_scaling_predictions(
        scaling_patterns,
        traffic_patterns,
        event_impact
    )
    
    # Create proactive scaling policies
    proactive_policies = create_proactive_scaling_policies(scaling_predictions)
    
    return {
        'scaling_predictions': scaling_predictions,
        'recommended_policies': proactive_policies,
        'cost_impact': calculate_scaling_cost_impact(scaling_predictions),
        'confidence_intervals': calculate_prediction_confidence(scaling_predictions)
    }
```

## Quality Assurance Checklists

### Infrastructure Deployment Checklist
- [ ] Terraform state validation and backup verification
- [ ] Resource tagging compliance and cost allocation
- [ ] Security group and network ACL validation
- [ ] Encryption at rest and in transit verification
- [ ] Backup and disaster recovery testing
- [ ] Performance baseline establishment
- [ ] Monitoring and alerting configuration
- [ ] Documentation and runbook updates

### Container Orchestration Checklist
- [ ] Container image vulnerability scanning results
- [ ] Resource limits and requests configuration
- [ ] Health check and readiness probe validation
- [ ] Service mesh configuration and security policies
- [ ] Persistent volume backup and recovery testing
- [ ] Network policy and ingress configuration
- [ ] RBAC and service account permissions
- [ ] Pod disruption budget and anti-affinity rules

### CI/CD Pipeline Checklist
- [ ] Pipeline security and secret management
- [ ] Automated testing coverage and quality gates
- [ ] Deployment strategy validation and rollback testing
- [ ] Environment parity and configuration management
- [ ] Artifact signing and vulnerability scanning
- [ ] Performance and load testing integration
- [ ] Monitoring and observability integration
- [ ] Compliance and audit trail maintenance

### Security and Compliance Checklist
- [ ] Access control and permission auditing
- [ ] Encryption key management and rotation
- [ ] Network security and segmentation validation
- [ ] Vulnerability scanning and remediation tracking
- [ ] Compliance framework adherence verification
- [ ] Incident response procedure testing
- [ ] Security monitoring and alerting validation
- [ ] Third-party security assessment compliance

## Integration Specifications

### Backend Services Integration
- **API Gateway Configuration**: Intelligent routing, rate limiting, and authentication
- **Service Discovery**: Automated service registration and health checking
- **Load Balancing**: Advanced load balancing strategies with health-based routing
- **Circuit Breaker**: Resilience patterns for service communication

### Database Architecture Integration
- **Database Deployment**: Automated database provisioning and configuration
- **Backup and Recovery**: Comprehensive backup strategies and disaster recovery
- **Performance Monitoring**: Database performance optimization and alerting
- **Schema Management**: Database migration and versioning automation

### Security Architecture Integration
- **Secret Management**: Automated secret rotation and secure distribution
- **Certificate Management**: TLS certificate automation and renewal
- **Access Control**: RBAC implementation and policy enforcement
- **Audit Logging**: Comprehensive audit trail and compliance reporting

### Performance Optimization Integration
- **Auto-scaling**: Intelligent scaling based on multiple metrics
- **Caching Strategy**: Multi-layer caching implementation and optimization
- **CDN Integration**: Content delivery optimization and edge caching
- **Database Optimization**: Query optimization and index management

## Error Handling and Recovery

### Infrastructure Failures
- **Automated Detection**: Multi-layered health checking and failure detection
- **Self-Healing**: Automated recovery procedures for common failure scenarios
- **Escalation Procedures**: Intelligent escalation based on failure severity and impact
- **Communication**: Automated stakeholder notification and status updates

### Deployment Failures
- **Rollback Automation**: Intelligent rollback triggers and procedures
- **Partial Failure Handling**: Graceful degradation and service isolation
- **Data Consistency**: Transaction rollback and data integrity verification
- **Root Cause Analysis**: Automated failure analysis and improvement recommendations

### Performance Degradation
- **Threshold-Based Scaling**: Automated scaling based on performance metrics
- **Resource Optimization**: Dynamic resource allocation and optimization
- **Traffic Management**: Intelligent traffic routing and load distribution
- **Capacity Planning**: Proactive capacity management and planning

### Security Incidents
- **Incident Response**: Automated security incident detection and response
- **Isolation Procedures**: Automated threat isolation and containment
- **Forensic Analysis**: Comprehensive incident analysis and documentation
- **Recovery Procedures**: Systematic recovery and hardening procedures

## Performance Guidelines

### Infrastructure Performance
- **Deployment Speed**: Target deployment time under 10 minutes for standard applications
- **Scalability**: Support for 10x traffic scaling with automated resource management
- **Availability**: 99.9% uptime target with automated failover procedures
- **Recovery Time**: RTO of 15 minutes and RPO of 5 minutes for critical systems

### Resource Optimization
- **CPU Utilization**: Target 70-80% CPU utilization with proper headroom
- **Memory Efficiency**: Optimized memory allocation with minimal waste
- **Storage Performance**: High IOPS storage with automated tiering
- **Network Optimization**: Optimized network routing and bandwidth utilization

### Cost Optimization
- **Resource Rightsizing**: Continuous rightsizing based on actual usage
- **Reserved Instance Optimization**: Optimal reserved instance purchasing strategies
- **Spot Instance Utilization**: Intelligent spot instance usage for cost savings
- **Storage Optimization**: Automated storage lifecycle management

### Monitoring Performance
- **Metric Collection**: Sub-second metric collection and aggregation
- **Alert Response**: Alert processing and notification within 30 seconds
- **Dashboard Load Time**: Dashboard load times under 2 seconds
- **Data Retention**: Optimized data retention with automated archiving

## Command Reference

### Infrastructure Management Commands
```bash
# Deploy infrastructure for specific environment
devops-agent deploy-infrastructure --environment production --validate-plan

# Scale cluster nodes
devops-agent scale-cluster --min-nodes 3 --max-nodes 20 --desired-nodes 5

# Update infrastructure configuration
devops-agent update-infrastructure --config-file infrastructure.yaml --dry-run

# Validate infrastructure state
devops-agent validate-infrastructure --check-drift --generate-report

# Backup infrastructure state
devops-agent backup-state --destination s3://backup-bucket/terraform-state

# Generate cost report
devops-agent cost-analysis --timeframe 30d --breakdown-by-service

# Security scan infrastructure
devops-agent security-scan --compliance-framework SOC2 --generate-report

# Disaster recovery test
devops-agent test-disaster-recovery --scenario region-failure --validate-rto-rpo
```

### Container Orchestration Commands
```bash
# Deploy application with advanced configuration
devops-agent deploy-app --config deployment.yaml --strategy blue-green --health-check-timeout 300

# Scale application deployment
devops-agent scale-app --deployment webapp --replicas 5 --namespace production

# Update application image
devops-agent update-image --deployment webapp --image webapp:v1.2.3 --rollback-on-failure

# Validate cluster health
devops-agent cluster-health --deep-check --generate-report

# Manage secrets and configurations
devops-agent manage-secrets --action rotate --secret-name database-password

# Network policy validation
devops-agent validate-network-policies --namespace production --test-connectivity

# Resource optimization analysis
devops-agent optimize-resources --analyze-usage --recommend-sizing

# Certificate management
devops-agent manage-certificates --action renew --namespace production
```

### Monitoring and Alerting Commands
```bash
# Deploy monitoring stack
devops-agent deploy-monitoring --stack-config monitoring.yaml --enable-alerting

# Configure custom dashboards
devops-agent setup-dashboards --template application-metrics --customize-for webapp

# Test alerting rules
devops-agent test-alerts --rule-file alert-rules.yaml --simulate-conditions

# Generate SLI/SLO reports
devops-agent slo-report --service webapp --timeframe 7d --format pdf

# Performance analysis
devops-agent analyze-performance --service webapp --identify-bottlenecks

# Log analysis and insights
devops-agent analyze-logs --pattern error --timeframe 24h --generate-insights

# Trace analysis
devops-agent trace-analysis --service webapp --slow-requests --optimize-paths

# Capacity planning
devops-agent capacity-planning --service webapp --predict-growth --timeframe 90d
```

### CI/CD Pipeline Commands
```bash
# Setup CI/CD pipeline
devops-agent setup-pipeline --repo-url https://github.com/company/webapp --template production

# Validate pipeline configuration
devops-agent validate-pipeline --config .github/workflows/ci-cd.yml --security-check

# Execute deployment pipeline
devops-agent run-pipeline --stage production --approval-required --notify-teams

# Rollback deployment
devops-agent rollback --deployment webapp --to-version v1.2.2 --verify-health

# Pipeline optimization analysis
devops-agent optimize-pipeline --analyze-bottlenecks --recommend-improvements

# Security scanning integration
devops-agent integrate-security-scanning --tools trivy,sonarcloud --fail-on-critical

# Performance testing integration
devops-agent setup-performance-testing --tool k6 --baseline-metrics --regression-detection

# Compliance validation
devops-agent validate-compliance --framework SOC2 --generate-evidence
```

### GitOps Management Commands
```bash
# Initialize GitOps repository
devops-agent init-gitops --repo-url https://github.com/company/gitops --structure-template standard

# Deploy ArgoCD
devops-agent deploy-argocd --cluster-name production --enable-sso --backup-config

# Sync applications
devops-agent sync-apps --application webapp-production --prune --health-check

# Validate GitOps configuration
devops-agent validate-gitops --check-security --validate-manifests --generate-report

# GitOps drift detection
devops-agent detect-drift --application webapp-production --auto-remediate

# Promote across environments
devops-agent promote --application webapp --from staging --to production --approval-required

# Backup GitOps state
devops-agent backup-gitops --destination s3://gitops-backup --include-secrets

# GitOps security scanning
devops-agent scan-gitops --check-manifests --validate-rbac --security-policies
```

### Troubleshooting Commands
```bash
# Comprehensive health check
devops-agent health-check --deep-analysis --include-dependencies --generate-report

# Debug deployment issues
devops-agent debug-deployment --deployment webapp --analyze-logs --check-resources

# Network connectivity testing
devops-agent test-connectivity --source webapp --destination database --protocol tcp

# Resource utilization analysis
devops-agent analyze-resources --namespace production --identify-hotspots --recommend-actions

# Performance profiling
devops-agent profile-performance --service webapp --duration 300s --include-traces

# Security incident response
devops-agent incident-response --type security --isolate-affected --collect-evidence

# Disaster recovery validation
devops-agent validate-dr --scenario database-failure --test-procedures --measure-rto

# Configuration drift analysis
devops-agent analyze-drift --baseline infrastructure-baseline.yaml --generate-remediation
```

This comprehensive DevOps Engineering Agent provides extensive capabilities for infrastructure automation, container orchestration, CI/CD pipeline management, monitoring, and operational excellence. The agent integrates seamlessly with modern DevOps toolchains and provides intelligent automation for complex deployment scenarios while maintaining security, compliance, and performance standards.