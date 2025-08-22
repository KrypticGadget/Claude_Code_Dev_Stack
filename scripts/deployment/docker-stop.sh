#!/bin/bash

# Claude Code Dev Stack V3.0 - Docker Stop Script
set -e

echo "🛑 Stopping Claude Code Dev Stack V3.0..."

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

# Parse command line arguments
REMOVE_VOLUMES=false
REMOVE_IMAGES=false
FORCE_CLEANUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--volumes)
            REMOVE_VOLUMES=true
            shift
            ;;
        -i|--images)
            REMOVE_IMAGES=true
            shift
            ;;
        -f|--force)
            FORCE_CLEANUP=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --volumes    Remove volumes (database data will be lost)"
            echo "  -i, --images     Remove built images"
            echo "  -f, --force      Force cleanup (combine -v and -i)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                # Stop services only"
            echo "  $0 -v            # Stop services and remove volumes"
            echo "  $0 -i            # Stop services and remove images"
            echo "  $0 -f            # Full cleanup (stop, remove volumes and images)"
            exit 0
            ;;
        *)
            print_error "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ "$FORCE_CLEANUP" = true ]; then
    REMOVE_VOLUMES=true
    REMOVE_IMAGES=true
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running."
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    print_error "docker-compose.yml not found in current directory"
    exit 1
fi

print_status "Stopping Claude Code Dev Stack services..."

# Stop services gracefully
if docker-compose ps -q | grep -q .; then
    print_status "Stopping running services..."
    docker-compose stop
    print_success "Services stopped"
else
    print_warning "No running services found"
fi

# Remove containers
print_status "Removing containers..."
docker-compose down --remove-orphans

if [ "$REMOVE_VOLUMES" = true ]; then
    print_warning "Removing volumes (this will delete all data)..."
    if [ "$FORCE_CLEANUP" = true ] || read -p "Are you sure you want to delete all data? (y/N): " -n 1 -r; then
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            print_success "Volumes removed"
        else
            print_status "Volume removal cancelled"
        fi
    else
        echo
        print_status "Volume removal cancelled"
    fi
fi

if [ "$REMOVE_IMAGES" = true ]; then
    print_status "Removing built images..."
    
    # Get image names from docker-compose
    IMAGES=$(docker-compose config --services | while read service; do
        docker-compose images -q $service 2>/dev/null
    done | sort -u | grep -v '^$')
    
    if [ ! -z "$IMAGES" ]; then
        echo "$IMAGES" | while read image; do
            if [ ! -z "$image" ]; then
                print_status "Removing image: $image"
                docker rmi "$image" 2>/dev/null || print_warning "Failed to remove image: $image"
            fi
        done
        print_success "Images removed"
    else
        print_warning "No images found to remove"
    fi
fi

# Clean up any orphaned containers
print_status "Cleaning up orphaned containers..."
ORPHANED=$(docker ps -a --filter "label=com.docker.compose.project=claude-dev-stack" --format "table {{.ID}}" | tail -n +2)
if [ ! -z "$ORPHANED" ]; then
    echo "$ORPHANED" | xargs docker rm -f 2>/dev/null || true
    print_success "Orphaned containers cleaned up"
fi

# Clean up unused networks
print_status "Cleaning up unused networks..."
docker network prune -f > /dev/null 2>&1 || true

# Show final status
echo ""
print_success "Claude Code Dev Stack V3.0 has been stopped!"

if [ "$REMOVE_VOLUMES" = true ]; then
    print_warning "All data has been removed. Next startup will create fresh databases."
fi

if [ "$REMOVE_IMAGES" = true ]; then
    print_warning "Images have been removed. Next startup will rebuild from scratch."
fi

echo ""
echo "📝 To start again:"
echo "   ./docker-start.sh"
echo ""
echo "📊 To view remaining Docker resources:"
echo "   docker system df"
echo ""
echo "🧹 To clean up all unused Docker resources:"
echo "   docker system prune -a"
echo ""