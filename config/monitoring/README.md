# Claude Code V3.6.9 Monitoring Infrastructure

## Overview

This monitoring infrastructure provides comprehensive real-time monitoring, alerting, and performance analysis for Claude Code V3.6.9. It includes Prometheus metrics collection, Grafana dashboards, log aggregation with Loki, and intelligent alerting with Alertmanager.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude Code   │────│   Metrics       │────│   Prometheus    │
│   V3.6.9        │    │   Collector     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Log Files     │────│   Promtail      │────│     Loki        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alerts &      │────│  Alertmanager   │────│    Grafana      │
│   Notifications │    │                 │    │   Dashboards    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

### 🎯 Agent Performance Tracking
- **Execution Time Monitoring**: Track agent execution times with P50, P95, P99 percentiles
- **Success Rate Analysis**: Monitor agent success/failure rates
- **Token Usage Tracking**: Real-time token consumption monitoring
- **Agent Comparison**: Compare performance across different agents

### 📊 Session Management Monitoring
- **Session Load/Save Performance**: Monitor session operation times
- **Session Size Tracking**: Track session sizes and detect large sessions
- **Active Session Monitoring**: Real-time active session counts
- **Session Health**: Detect session corruption or performance issues

### 🖥️ System Health Visualization
- **Resource Usage**: CPU, Memory, Disk usage monitoring
- **Process Monitoring**: Track Claude Code process health
- **Network I/O**: Monitor network traffic and latency
- **System Load**: Track system load averages

### 🔧 Hook Execution Metrics
- **Hook Performance**: Monitor individual hook execution times
- **Hook Success Rates**: Track hook failure rates
- **Resource Usage**: Memory usage per hook
- **Hook Dependencies**: Visualize hook execution chains

### 🚨 Intelligent Alerting
- **Performance Thresholds**: Automated alerts for slow operations
- **Resource Warnings**: Proactive alerts for resource exhaustion
- **Error Detection**: Immediate alerts for failures and errors
- **Custom Notifications**: Desktop notifications and webhooks

### 📈 Performance Baselines
- **Adaptive Baselines**: Automatically updated performance baselines
- **Trend Analysis**: Long-term performance trend tracking
- **Anomaly Detection**: Detect performance anomalies
- **Capacity Planning**: Resource usage forecasting

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher
- At least 4GB RAM available for monitoring stack
- 10GB disk space for logs and metrics storage

### Automatic Setup

```bash
# Navigate to monitoring directory
cd /path/to/Claude_Code_Agents/V3.6.9/monitoring

# Run complete setup
python setup_monitoring.py full
```

### Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements-monitoring.txt
   ```

2. **Start Monitoring Stack**
   ```bash
   docker-compose up -d
   ```

3. **Start Metrics Collector**
   ```bash
   python enhanced_performance_monitor.py start
   ```

## Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | Dashboards and visualization |
| Prometheus | http://localhost:9090 | Metrics database and queries |
| Alertmanager | http://localhost:9093 | Alert management |
| Loki | http://localhost:3100 | Log aggregation |
| Metrics Collector | http://localhost:8001 | Claude Code metrics endpoint |
| Node Exporter | http://localhost:9100 | System metrics |

### Default Credentials

- **Grafana**: admin / admin (change on first login)

## Dashboards

### 1. Agent Performance Dashboard
- Agent execution success rates
- Average execution times by agent
- Token usage trends
- Agent comparison metrics
- Failed executions analysis

### 2. Session Monitoring Dashboard
- Active session counts
- Session size distribution
- Load/save performance
- Session operations by type
- Session health indicators

### 3. System Health Dashboard
- CPU, Memory, Disk usage gauges
- System load averages
- Process counts and file descriptors
- Network I/O statistics
- Service status overview

### 4. Resource Usage Dashboard
- Token usage rates and daily totals
- Memory usage by component
- Storage breakdown by type
- Resource cleanup operations
- Performance issue tracking

### 5. Hook Execution Dashboard
- Hook success rates
- Execution time distributions
- Hook failure analysis
- Resource usage by hook
- Recent hook errors

## Alerting Rules

### Critical Alerts
- **Agent Failure Rate > 10%**: Immediate notification
- **System Memory > 90%**: Critical resource alert
- **Disk Space < 5%**: Storage critical
- **Service Down**: Integration service failures

### Warning Alerts
- **Agent Execution > 30s**: Performance warning
- **Token Usage > 10k/min**: High usage warning
- **Memory Usage > 85%**: Resource warning
- **Session Size > 10MB**: Large session warning

### Custom Alerts
Configure custom alerts in `prometheus/alert_rules.yml`:

```yaml
- alert: CustomMetricHigh
  expr: your_custom_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom metric is high"
    description: "Your custom metric has been above threshold for 5 minutes"
```

## Configuration

### Metrics Collection Intervals
- **System Metrics**: Every 15 seconds
- **Agent Metrics**: Every 15 seconds  
- **Session Metrics**: Every 10 seconds
- **Performance Baselines**: Every hour

### Retention Policies
- **Metrics**: 30 days
- **Logs**: 7 days
- **Performance Snapshots**: 100 most recent

### Customization

#### Adding Custom Metrics
1. Edit `enhanced_performance_monitor.py`
2. Add metric definition to `prometheus_metrics`
3. Implement collection logic
4. Restart metrics collector

#### Custom Dashboards
1. Create JSON dashboard in `grafana/dashboards/`
2. Restart Grafana or import manually
3. Configure data sources and queries

#### Alert Configuration
1. Edit `prometheus/alert_rules.yml`
2. Define alert conditions and thresholds
3. Configure notification channels in `alerting/alertmanager.yml`
4. Restart Prometheus and Alertmanager

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker Compose logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

#### Metrics Not Appearing
```bash
# Check metrics collector status
curl http://localhost:8001/metrics

# Check Prometheus targets
# Visit: http://localhost:9090/targets
```

#### Dashboards Not Loading
```bash
# Check Grafana logs
docker-compose logs grafana

# Verify data source configuration
# Visit: http://localhost:3000/datasources
```

#### High Resource Usage
```bash
# Check resource consumption
docker stats

# Reduce retention periods in configuration files
# Restart services after configuration changes
```

### Performance Optimization

#### For High-Volume Environments
1. **Increase collection intervals**:
   ```python
   self.collection_interval = 30  # seconds
   ```

2. **Reduce metrics retention**:
   ```yaml
   # In prometheus.yml
   - '--storage.tsdb.retention.time=7d'
   ```

3. **Optimize log collection**:
   ```yaml
   # In promtail_config.yml
   batch_wait: 5s
   batch_size: 1048576
   ```

#### For Development Environments
1. **Reduce resource allocation**:
   ```yaml
   # In docker-compose.yml
   mem_limit: 1g
   cpus: 1.0
   ```

2. **Use shorter retention periods**:
   ```yaml
   retention_period: 24h
   ```

## Integration with Claude Code

### Automatic Integration
The monitoring system automatically integrates with:
- Existing performance monitors
- Hook execution tracking
- Session management
- Resource monitoring

### Manual Integration
Add to your Claude Code hooks:

```python
from monitoring.enhanced_performance_monitor import get_monitor

monitor = get_monitor()

# Record agent execution
monitor.record_agent_execution(
    agent_name="my-agent",
    duration=5.2,
    tokens_used=1500,
    success=True
)

# Record hook execution
monitor.record_hook_execution(
    hook_name="my-hook",
    duration=0.5,
    success=True
)
```

## Maintenance

### Daily Tasks
- Check dashboard for anomalies
- Review recent alerts
- Verify service health

### Weekly Tasks
- Review performance baselines
- Clean up old logs (automated)
- Check disk space usage

### Monthly Tasks
- Update alert thresholds
- Review metric retention policies
- Backup monitoring configuration

## Advanced Configuration

### Custom Metrics Export
```python
# In enhanced_performance_monitor.py
def export_custom_metric(name, value, labels=None):
    self.update_prometheus_metric(f"claude_custom_{name}", value, labels)
```

### Integration with External Systems
```python
# Send metrics to external systems
def send_to_external(metrics):
    # InfluxDB
    # Datadog
    # New Relic
    # Custom endpoints
    pass
```

### High Availability Setup
For production environments:
1. Use external storage for Prometheus
2. Configure Grafana with external database
3. Set up Alertmanager clustering
4. Use load balancers for services

## Support and Contributing

### Getting Help
1. Check logs in Claude directory: `~/.claude/logs/`
2. Review setup report: `monitoring/setup_report.json`
3. Use status check: `python scripts/check_status.py`

### Contributing
1. Fork the repository
2. Add your monitoring enhancements
3. Test with the provided test suite
4. Submit a pull request

## License

This monitoring infrastructure is part of Claude Code V3.6.9 and follows the same licensing terms.

---

**Version**: 3.6.9  
**Last Updated**: $(date)  
**Maintained By**: Claude Code Performance Engineering Team