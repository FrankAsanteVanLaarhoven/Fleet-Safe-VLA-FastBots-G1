#!/bin/bash

# DataMinerAI Platform Setup Script
# This script helps you set up the DataMinerAI platform with your Supabase project

echo "🚀 DataMinerAI Platform Setup"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if required tools are installed
check_requirements() {
    print_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Setup Supabase database
setup_supabase() {
    print_info "Setting up Supabase database..."
    
    echo ""
    echo "📋 Supabase Setup Instructions:"
    echo "1. Go to your Supabase project: https://supabase.com/dashboard/project/rwjuwwagiqgmdfmorysk"
    echo "2. Navigate to the SQL Editor"
    echo "3. Copy the contents of 'dataminerAI_setup.sql'"
    echo "4. Paste and run the SQL script"
    echo "5. This will create all necessary tables and initial data"
    echo ""
    
    read -p "Have you run the SQL script in Supabase? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Supabase database setup completed"
    else
        print_warning "Please run the SQL script in Supabase before continuing"
        exit 1
    fi
}

# Setup environment variables
setup_environment() {
    print_info "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
# DataMinerAI Environment Variables
SUPABASE_URL=https://rwjuwwagiqgmdfmorysk.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ3anV3d2FnaXFnbWRmbW9yeXNrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0MzkwODcsImV4cCI6MjA3MTAxNTA4N30.-2LIENAiCbxudZFdBvmKIlDHiq-yCuUUe89FaesLphg

# Server Ports
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
DATAMINERAI_FRONTEND_PORT=3737

# AI Configuration
AI_OS_LLM_PROVIDER=ollama
AI_OS_CACHE_PROVIDER=redis
AI_OS_VECTOR_DB_PROVIDER=chroma

# Features
PROJECTS_ENABLED=true
LOGFIRE_ENABLED=false

# Add your API keys here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
EOF
        print_status "Created .env file with default configuration"
    else
        print_warning ".env file already exists"
    fi
}

# Start services with Docker Compose
start_services() {
    print_info "Starting DataMinerAI services..."
    
    echo ""
    echo "🐳 Starting Docker services..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_status "Docker services started successfully"
    else
        print_error "Failed to start Docker services"
        exit 1
    fi
}

# Check service status
check_services() {
    print_info "Checking service status..."
    
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Service URLs:"
    echo "Frontend: http://localhost:3737"
    echo "Backend API: http://localhost:8181"
    echo "MCP Server: http://localhost:8051"
    echo "Ollama: http://localhost:11434"
    echo "ChromaDB: http://localhost:8000"
    echo "Redis: localhost:6379"
}

# Setup Ollama models
setup_ollama() {
    print_info "Setting up Ollama models..."
    
    echo ""
    echo "🤖 Ollama Model Setup:"
    echo "1. Wait for Ollama service to start (check with: docker-compose ps)"
    echo "2. Pull a model: docker exec dataminerai-ollama ollama pull llama2"
    echo "3. Or pull a smaller model: docker exec dataminerai-ollama ollama pull llama2:7b"
    echo ""
    
    read -p "Would you like to pull a model now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Pulling llama2:7b model..."
        docker exec dataminerai-ollama ollama pull llama2:7b
        if [ $? -eq 0 ]; then
            print_status "Model pulled successfully"
        else
            print_error "Failed to pull model"
        fi
    fi
}

# Main setup flow
main() {
    echo "Welcome to DataMinerAI Platform Setup!"
    echo ""
    
    check_requirements
    setup_supabase
    setup_environment
    start_services
    
    # Wait a moment for services to start
    echo ""
    print_info "Waiting for services to start..."
    sleep 10
    
    check_services
    setup_ollama
    
    echo ""
    print_status "DataMinerAI Platform setup completed!"
    echo ""
    echo "🎉 Next steps:"
    echo "1. Open http://localhost:3737 in your browser"
    echo "2. Add your API keys in the Settings section"
    echo "3. Start using the platform!"
    echo ""
    echo "📚 Documentation: Check the README for more information"
    echo "🛠️  Troubleshooting: Use 'docker-compose logs' to check service logs"
}

# Run main function
main
