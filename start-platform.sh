#!/bin/bash

# Iron Cloud AI Platform - Quick Start Script
# This script sets up and starts the complete Iron Cloud AI Platform

set -e

echo "🌟 Iron Cloud AI Platform - Quick Start"
echo "========================================"

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if required ports are available
check_ports() {
    local ports=("3000" "8000" "5432" "6379" "9090" "3001" "5601")
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use. Please stop the service using this port."
        fi
    done
}

# Create environment file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file with default values..."
        cat > .env << EOF
# Iron Cloud AI Platform Environment Variables

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Security
JWT_SECRET=your_jwt_secret_here_change_this_in_production

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ironcloud

# Redis
REDIS_URL=redis://localhost:6379

# Environment
NODE_ENV=development
ENVIRONMENT=development

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
ELASTICSEARCH_ENABLED=true
EOF
        print_success "Created .env file. Please update it with your actual API keys."
    else
        print_status ".env file already exists"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting Iron Cloud AI Platform..."
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "All services started successfully!"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    print_status "Waiting for backend API..."
    until curl -s http://localhost:8000/health > /dev/null 2>&1; do
        sleep 2
    done
    print_success "Backend API is ready"
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    until curl -s http://localhost:3000 > /dev/null 2>&1; do
        sleep 2
    done
    print_success "Frontend is ready"
    
    # Wait for database
    print_status "Waiting for database..."
    until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
        sleep 2
    done
    print_success "Database is ready"
}

# Display service information
show_service_info() {
    echo ""
    echo "🎉 Iron Cloud AI Platform is now running!"
    echo "=========================================="
    echo ""
    echo "🌐 Services:"
    echo "  • Frontend:     http://localhost:3000"
    echo "  • Backend API:  http://localhost:8000"
    echo "  • API Docs:     http://localhost:8000/docs"
    echo "  • Grafana:      http://localhost:3001 (admin/admin)"
    echo "  • Prometheus:   http://localhost:9090"
    echo "  • Kibana:       http://localhost:5601"
    echo ""
    echo "🗄️  Database:"
    echo "  • PostgreSQL:   localhost:5432"
    echo "  • Redis:        localhost:6379"
    echo ""
    echo "📊 Monitoring:"
    echo "  • System Status: http://localhost:8000/api/system/status"
    echo "  • Health Check:  http://localhost:8000/health"
    echo ""
    echo "🔧 Management:"
    echo "  • View logs:    docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart:      docker-compose restart"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Explore the AI agent categories"
    echo "  3. Test the API endpoints"
    echo "  4. Check the monitoring dashboards"
    echo ""
}

# Main execution
main() {
    echo "Starting Iron Cloud AI Platform setup..."
    echo ""
    
    # Check prerequisites
    check_docker
    check_ports
    
    # Create environment file
    create_env_file
    
    # Start services
    start_services
    
    # Wait for services
    wait_for_services
    
    # Show service information
    show_service_info
}

# Handle script interruption
trap 'print_error "Setup interrupted. Run 'docker-compose down' to clean up."; exit 1' INT

# Run main function
main "$@"
