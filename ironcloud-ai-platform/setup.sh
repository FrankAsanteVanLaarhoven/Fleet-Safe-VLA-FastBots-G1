#!/bin/bash

# IronCloud-AI Platform Setup Script
# This script sets up the complete IronCloud-AI platform

set -e

echo "🚀 Setting up IronCloud-AI Platform..."

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

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node -v)"
        exit 1
    fi
    
    print_success "Node.js $(node -v) is installed"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python $PYTHON_VERSION is installed"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp env.example .env
        print_success "Created .env file from template"
        print_warning "Please update .env file with your API keys and configuration"
    else
        print_status ".env file already exists"
    fi
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd ironcloud-ai-frontend
    
    if [ ! -d node_modules ]; then
        print_status "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_status "Frontend dependencies already installed"
    fi
    
    cd ..
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd python
    
    if [ ! -d venv ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    print_success "Backend dependencies installed"
    
    cd ..
}

# Start services
start_services() {
    print_status "Starting IronCloud-AI services..."
    
    # Start database and Redis
    docker-compose up -d postgres redis
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Start backend
    docker-compose up -d backend
    
    print_status "Waiting for backend to be ready..."
    sleep 15
    
    print_success "All services started successfully"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    
    cd ironcloud-ai-frontend
    npm run build
    cd ..
    
    print_success "Frontend built successfully"
}

# Display status
show_status() {
    print_status "IronCloud-AI Platform Status:"
    echo ""
    echo "Services:"
    docker-compose ps
    echo ""
    echo "Access URLs:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend API: http://localhost:8000"
    echo "  MCP Server: http://localhost:8051"
    echo ""
    print_success "IronCloud-AI Platform is ready!"
}

# Main setup function
main() {
    print_status "Starting IronCloud-AI Platform setup..."
    
    # Check prerequisites
    check_docker
    check_node
    check_python
    
    # Setup environment
    setup_env
    
    # Setup frontend
    setup_frontend
    
    # Setup backend
    setup_backend
    
    # Start services
    start_services
    
    # Build frontend
    build_frontend
    
    # Show status
    show_status
}

# Run main function
main "$@"
