#!/bin/bash
# Health Check Script for Claude Code Dev Stack V3.6.9
# Monitors all services and reports their status

set -e

# Configuration
LOG_FILE="/var/log/healthcheck.log"
SERVICES_CONFIG="/app/config/services.json"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"
CHECK_INTERVAL=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check HTTP service health
check_http_service() {
    local name=$1
    local url=$2
    local timeout=${3:-10}
    
    if curl -f -s --max-time "$timeout" "$url" > /dev/null; then
        echo "${GREEN}✓${NC} $name: Healthy"
        return 0
    else
        echo "${RED}✗${NC} $name: Unhealthy"
        return 1
    fi
}

# Check TCP service health
check_tcp_service() {
    local name=$1
    local host=$2
    local port=$3
    local timeout=${4:-5}
    
    if timeout "$timeout" bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        echo "${GREEN}✓${NC} $name: Healthy"
        return 0
    else
        echo "${RED}✗${NC} $name: Unhealthy"
        return 1
    fi
}

# Check Docker container health
check_container_health() {
    local container_name=$1
    
    local status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "not found")
    
    case "$status" in
        "healthy")
            echo "${GREEN}✓${NC} $container_name: Healthy"
            return 0
            ;;
        "unhealthy")
            echo "${RED}✗${NC} $container_name: Unhealthy"
            return 1
            ;;
        "starting")
            echo "${YELLOW}⚠${NC} $container_name: Starting"
            return 2
            ;;
        "not found")
            echo "${RED}✗${NC} $container_name: Container not found"
            return 1
            ;;
        *)
            echo "${YELLOW}?${NC} $container_name: Unknown status ($status)"
            return 2
            ;;
    esac
}

# Check system resources
check_system_resources() {
    local cpu_usage=$(awk '{print $1+$2+$3}' /proc/loadavg)
    local mem_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
    local disk_usage=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
    
    echo "System Resources:"
    echo "  CPU Load: $cpu_usage"
    echo "  Memory Usage: ${mem_usage}%"
    echo "  Disk Usage: ${disk_usage}%"
    
    # Alert thresholds
    if (( $(echo "$mem_usage > 80" | bc -l) )); then
        echo "${YELLOW}⚠${NC} High memory usage: ${mem_usage}%"
    fi
    
    if (( disk_usage > 80 )); then
        echo "${YELLOW}⚠${NC} High disk usage: ${disk_usage}%"
    fi
}

# Send alert notification
send_alert() {
    local message=$1
    local severity=${2:-"warning"}
    
    if [[ -n "$ALERT_WEBHOOK" ]]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"Claude Dev Stack Alert [$severity]: $message\", \"severity\": \"$severity\"}" \
            &> /dev/null || true
    fi
}

# Main health check function
perform_health_check() {
    local failed_services=0
    local total_services=0
    
    log "Starting health check..."
    
    echo "================================================"
    echo "Claude Code Dev Stack V3.6.9 - Health Check"
    echo "================================================"
    
    # Check core application services
    echo -e "\n${YELLOW}Core Application Services:${NC}"
    ((total_services++))
    if ! check_http_service "Main App" "http://claude-dev-stack:3000/health"; then
        ((failed_services++))
    fi
    
    ((total_services++))
    if ! check_http_service "Semantic API" "http://semantic-api:3001/health"; then
        ((failed_services++))
    fi
    
    ((total_services++))
    if ! check_http_service "UI/PWA" "http://claude-ui:5173"; then
        ((failed_services++))
    fi
    
    # Check database services
    echo -e "\n${YELLOW}Database Services:${NC}"
    ((total_services++))
    if ! check_tcp_service "PostgreSQL" "postgres" "5432"; then
        ((failed_services++))
    fi
    
    ((total_services++))
    if ! check_tcp_service "Redis" "redis" "6379"; then
        ((failed_services++))
    fi
    
    # Check monitoring services
    echo -e "\n${YELLOW}Monitoring Services:${NC}"
    ((total_services++))
    if ! check_http_service "Prometheus" "http://prometheus:9090/-/healthy"; then
        ((failed_services++))
    fi
    
    ((total_services++))
    if ! check_http_service "Grafana" "http://grafana:3000/api/health"; then
        ((failed_services++))
    fi
    
    # Check infrastructure services
    echo -e "\n${YELLOW}Infrastructure Services:${NC}"
    ((total_services++))
    if ! check_http_service "Traefik" "http://traefik:8080/ping"; then
        ((failed_services++))
    fi
    
    ((total_services++))
    if ! check_http_service "Consul" "http://consul:8500/v1/status/leader"; then
        ((failed_services++))
    fi
    
    ((total_services++))
    if ! check_http_service "NGROK" "http://ngrok:4040/api/tunnels"; then
        ((failed_services++))
    fi
    
    # Check MCP servers
    echo -e "\n${YELLOW}MCP Servers:${NC}"
    ((total_services++))
    if ! check_http_service "GitHub MCP" "http://github-mcp-server:3333/health"; then
        ((failed_services++))
    fi
    
    # System resources
    echo -e "\n${YELLOW}System Resources:${NC}"
    check_system_resources
    
    # Summary
    echo -e "\n================================================"
    local healthy_services=$((total_services - failed_services))
    echo "Health Check Summary:"
    echo "  Total Services: $total_services"
    echo "  Healthy: ${GREEN}$healthy_services${NC}"
    echo "  Failed: ${RED}$failed_services${NC}"
    echo "  Success Rate: $(( healthy_services * 100 / total_services ))%"
    echo "================================================"
    
    # Send alerts if needed
    if (( failed_services > 0 )); then
        local message="$failed_services out of $total_services services are unhealthy"
        log "ALERT: $message"
        send_alert "$message" "critical"
        return 1
    else
        log "All services healthy"
        return 0
    fi
}

# Continuous monitoring mode
monitor_mode() {
    log "Starting continuous monitoring mode (interval: ${CHECK_INTERVAL}s)"
    while true; do
        perform_health_check
        sleep "$CHECK_INTERVAL"
    done
}

# Main execution
case "${1:-check}" in
    "monitor")
        monitor_mode
        ;;
    "check")
        perform_health_check
        ;;
    "container")
        if [[ -n "$2" ]]; then
            check_container_health "$2"
        else
            echo "Usage: $0 container <container_name>"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 [check|monitor|container <name>]"
        echo "  check    - Run a single health check (default)"
        echo "  monitor  - Run continuous health monitoring"
        echo "  container - Check specific container health"
        exit 1
        ;;
esac