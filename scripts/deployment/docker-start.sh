#!/bin/bash

# Claude Code Dev Stack V3.0 - Docker Startup Script
set -e

echo "🚀 Starting Claude Code Dev Stack V3.0..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

print_status "Docker is running and Docker Compose is available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your specific configuration"
fi

# Build and start services
print_status "Building Docker images..."
docker-compose build --parallel

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."

# Function to wait for service
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "$service is ready!"
            return 0
        fi
        
        if [ $attempt -eq 1 ]; then
            echo -n "    "
        fi
        echo -n "."
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo ""
    print_warning "$service may not be ready yet (timeout after 60 seconds)"
    return 1
}

# Wait for core services
wait_for_service "Redis" 6379 &
wait_for_service "PostgreSQL" 5432 &
wait_for_service "Main Application" 3000 &
wait_for_service "Semantic API" 3002 &
wait_for_service "React UI" 5173 &

# Wait for all background jobs to complete
wait

# Install MCP server dependencies
print_status "Installing MCP server dependencies..."
docker-compose exec -T code-sandbox-mcp npm install || print_warning "Failed to install code-sandbox-mcp dependencies"
docker-compose exec -T playwright-mcp npm install || print_warning "Failed to install playwright-mcp dependencies"
docker-compose exec -T playwright-mcp npx playwright install || print_warning "Failed to install Playwright browsers"

# Show service status
print_status "Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "🎉 Claude Code Dev Stack V3.0 is now running!"
echo ""
echo "📊 Access URLs:"
echo "   • Main Application: http://localhost:3000"
echo "   • React UI: http://localhost:5173"
echo "   • Semantic API: http://localhost:3002"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3030 (admin/admin)"
echo ""
echo "🔧 MCP Servers:"
echo "   • GitHub MCP: http://localhost:3333"
echo "   • Code Sandbox MCP: http://localhost:3334"
echo "   • Playwright MCP: http://localhost:3335"
echo ""
echo "💾 Database:"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "📝 Logs:"
echo "   • View all logs: docker-compose logs -f"
echo "   • View specific service: docker-compose logs -f <service-name>"
echo ""
echo "🛑 To stop:"
echo "   • Stop all services: docker-compose down"
echo "   • Stop and remove volumes: docker-compose down -v"
echo ""

print_success "Claude Code Dev Stack V3.0 startup complete!"