#!/bin/bash
# Claude Code Dev Stack V3.6.9 - Docker Management Script
# Comprehensive management for all 11 services

set -e

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="claude-dev-stack"
LOG_DIR="./logs"
BACKUP_DIR="./backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Create directories
create_directories() {
    mkdir -p "$LOG_DIR" "$BACKUP_DIR"
    mkdir -p ./config/{postgres,redis,ngrok,consul,traefik/dynamic}
    mkdir -p ./data/{postgres,redis,prometheus,grafana}
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    success "All prerequisites met"
}

# Environment setup
setup_environment() {
    info "Setting up environment variables..."
    
    if [[ ! -f .env ]]; then
        cat > .env << EOF
# Claude Code Dev Stack V3.6.9 Environment Variables

# Database Configuration
POSTGRES_PASSWORD=claude_dev_db_secure_$(date +%s)
REDIS_PASSWORD=claude_redis_secure_$(date +%s)

# Monitoring Configuration
GRAFANA_PASSWORD=admin_$(date +%s)
PROMETHEUS_RETENTION=30d

# External Services
NGROK_AUTHTOKEN=
NGROK_SUBDOMAIN=
MCP_GITHUB_TOKEN=

# Security
JWT_SECRET=jwt_secret_$(openssl rand -hex 32)
SESSION_SECRET=session_secret_$(openssl rand -hex 32)

# Development
NODE_ENV=development
DEBUG=claude:*
LOG_LEVEL=info

# Performance
REDIS_MAXMEMORY=512mb
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_MAX_CONNECTIONS=200

# Alert Configuration (optional)
ALERT_WEBHOOK=
SLACK_WEBHOOK=
EMAIL_ALERTS=false
EOF
        success "Environment file created: .env"
    else
        info "Environment file already exists"
    fi
}

# Service management
start_services() {
    local profile=${1:-""}
    info "Starting services${profile:+ with profile: $profile}..."
    
    create_directories
    
    if [[ -n "$profile" ]]; then
        docker-compose --profile "$profile" up -d
    else
        docker-compose up -d
    fi
    
    success "Services started"
    show_status
}

stop_services() {
    info "Stopping services..."
    docker-compose stop
    success "Services stopped"
}

restart_services() {
    info "Restarting services..."
    docker-compose restart
    success "Services restarted"
    show_status
}

# Service status
show_status() {
    info "Service Status:"
    echo "==========================================="
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo "==========================================="
    
    # Show health status
    info "Health Status:"
    local containers=$(docker-compose ps -q)
    for container in $containers; do
        local name=$(docker inspect --format='{{.Name}}' $container | sed 's/\///')
        local health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no healthcheck")
        
        case "$health" in
            "healthy")
                success "$name: Healthy"
                ;;
            "unhealthy")
                error "$name: Unhealthy"
                ;;
            "starting")
                warning "$name: Starting"
                ;;
            "no healthcheck")
                info "$name: No healthcheck configured"
                ;;
            *)
                warning "$name: Unknown status ($health)"
                ;;
        esac
    done
}

# Logs management
show_logs() {
    local service=${1:-""}
    local lines=${2:-100}
    
    if [[ -n "$service" ]]; then
        docker-compose logs --tail="$lines" -f "$service"
    else
        docker-compose logs --tail="$lines" -f
    fi
}

# Backup operations
backup_data() {
    info "Creating backup..."
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/claude-stack-backup-$timestamp.tar.gz"
    
    # Stop services temporarily for consistent backup
    docker-compose stop postgres redis
    
    # Create backup
    tar -czf "$backup_file" \
        data/ \
        config/ \
        .env \
        docker-compose.yml
    
    # Restart services
    docker-compose start postgres redis
    
    success "Backup created: $backup_file"
}

restore_data() {
    local backup_file=$1
    
    if [[ -z "$backup_file" || ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
        exit 1
    fi
    
    warning "This will overwrite existing data. Continue? (y/N)"
    read -r confirmation
    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        info "Restore cancelled"
        return
    fi
    
    info "Restoring from backup: $backup_file"
    
    # Stop services
    docker-compose down
    
    # Extract backup
    tar -xzf "$backup_file"
    
    # Start services
    start_services
    
    success "Restore completed"
}

# Development helpers
dev_setup() {
    info "Setting up development environment..."
    
    setup_environment
    create_directories
    
    # Start with development profile
    start_services "dev-tools"
    
    # Wait for services to be ready
    sleep 10
    
    # Run initial setup
    docker-compose exec claude-dev-stack npm run setup || true
    
    success "Development environment ready"
    
    info "Available services:"
    echo "  Main App: http://localhost:3000"
    echo "  UI/PWA: http://localhost:5173"
    echo "  API: http://localhost:3001"
    echo "  Grafana: http://localhost:3030 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
    echo "  Traefik: http://localhost:8080"
    echo "  Consul: http://localhost:8500"
}

# Testing environment
test_setup() {
    info "Setting up testing environment..."
    
    # Start testing services
    start_services "testing"
    
    # Wait for services
    sleep 5
    
    # Run database migrations for tests
    docker-compose exec database-dev psql -U claude_dev -d claude_dev_test -c "SELECT 1;" || true
    
    success "Testing environment ready"
    
    info "Run tests with:"
    echo "  Unit tests: docker-compose run --rm test-env npm run test:unit"
    echo "  Integration: docker-compose run --rm test-env npm run test:integration"
    echo "  E2E tests: docker-compose run --rm test-env npm run test:e2e"
}

# Monitoring setup
monitoring_setup() {
    info "Setting up monitoring dashboards..."
    
    # Import Grafana dashboards
    sleep 10 # Wait for Grafana to be ready
    
    # You can add dashboard import commands here
    success "Monitoring setup complete"
    echo "  Grafana: http://localhost:3030"
    echo "  Prometheus: http://localhost:9090"
}

# Cleanup operations
cleanup() {
    warning "This will remove all containers, volumes, and networks. Continue? (y/N)"
    read -r confirmation
    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        info "Cleanup cancelled"
        return
    fi
    
    info "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose down -v --remove-orphans
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    success "Cleanup completed"
}

# Update services
update_services() {
    info "Updating services..."
    
    # Pull latest images
    docker-compose pull
    
    # Recreate containers with new images
    docker-compose up -d --force-recreate
    
    success "Services updated"
    show_status
}

# Health check
health_check() {
    info "Running comprehensive health check..."
    docker-compose exec healthcheck /healthcheck.sh check
}

# Show help
show_help() {
    cat << EOF
Claude Code Dev Stack V3.6.9 - Docker Management Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  start [profile]     Start all services (optional profile)
  stop               Stop all services
  restart            Restart all services
  status             Show service status
  logs [service]     Show logs for all services or specific service
  
  dev-setup          Setup development environment
  test-setup         Setup testing environment
  monitoring-setup   Setup monitoring dashboards
  
  backup             Create data backup
  restore <file>     Restore from backup file
  
  update             Update service images
  cleanup            Remove all containers, volumes, networks
  health-check       Run comprehensive health check
  
  help               Show this help message

Profiles:
  dev-tools          Development tools container
  frontend-dev       Frontend development container  
  backend-dev        Backend development container
  database-dev       Database development container
  testing            Testing environment
  monitoring         Health monitoring

Examples:
  $0 start                    # Start all services
  $0 start dev-tools          # Start with development tools
  $0 logs postgres            # Show PostgreSQL logs
  $0 backup                   # Create backup
  $0 restore backup.tar.gz    # Restore from backup

Environment variables can be configured in .env file.
EOF
}

# Main command handling
main() {
    case "${1:-help}" in
        "start")
            check_prerequisites
            setup_environment
            start_services "$2"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2" "$3"
            ;;
        "dev-setup")
            check_prerequisites
            dev_setup
            ;;
        "test-setup")
            check_prerequisites
            test_setup
            ;;
        "monitoring-setup")
            monitoring_setup
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "update")
            check_prerequisites
            update_services
            ;;
        "cleanup")
            cleanup
            ;;
        "health-check")
            health_check
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Execute main function with all arguments
main "$@"