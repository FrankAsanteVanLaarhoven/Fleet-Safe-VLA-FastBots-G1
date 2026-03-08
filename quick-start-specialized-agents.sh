#!/bin/bash

# Specialized AI Agents System - Quick Start Script
# ================================================

set -e

echo "🚀 Starting Specialized AI Agents System Setup..."
echo "================================================"

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

# Check if running on macOS, Linux, or Windows
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_status "Detected OS: $OS"

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        print_status "Visit: https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) ✓"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed."
        exit 1
    fi
    
    print_success "npm $(npm --version) ✓"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION ✓"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed."
        exit 1
    fi
    
    print_success "pip3 ✓"
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend..."
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the project root."
        exit 1
    fi
    
    # Install npm dependencies
    print_status "Installing npm dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f ".env.local" ]; then
        print_status "Creating .env.local file..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
        print_success "Created .env.local"
    else
        print_warning ".env.local already exists"
    fi
    
    print_success "Frontend setup complete ✓"
}

# Install backend dependencies
setup_backend() {
    print_status "Setting up backend..."
    
    if [ ! -d "backend" ]; then
        print_error "backend directory not found. Please run this script from the project root."
        exit 1
    fi
    
    cd backend
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_status "Creating requirements.txt..."
        cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aiohttp==3.9.1
beautifulsoup4==4.12.2
requests==2.31.0
selenium==4.15.2
playwright==1.40.0
puppeteer-python==0.0.1
langgraph==0.0.20
langchain==0.0.350
openai==1.3.7
anthropic==0.7.8
redis==5.0.1
celery==5.3.4
flower==2.0.1
prometheus-client==0.19.0
structlog==23.2.0
EOF
        print_success "Created requirements.txt"
    fi
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Create environment file for backend
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
# Database configuration
DATABASE_URL=sqlite:///./specialized_agents.db

# Security settings
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Allowed hosts
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Debug mode
DEBUG=true

# API settings
API_V1_STR=/api
PROJECT_NAME=Specialized AI Agents System
EOF
        print_success "Created backend .env"
    else
        print_warning "Backend .env already exists"
    fi
    
    cd ..
    print_success "Backend setup complete ✓"
}

# Start the system
start_system() {
    print_status "Starting Specialized AI Agents System..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend
    nohup python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    sleep 5
    
    # Check if backend is running
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend server started ✓"
    else
        print_error "Backend server failed to start. Check backend.log for details."
        exit 1
    fi
    
    # Start frontend
    print_status "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    sleep 10
    
    # Check if frontend is running
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Frontend server started ✓"
    else
        print_warning "Frontend server may still be starting..."
    fi
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    print_success "🎉 Specialized AI Agents System is now running!"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the system"
    echo ""
    
    # Wait for interrupt
    trap cleanup EXIT
    wait
}

# Cleanup function
cleanup() {
    print_status "Stopping Specialized AI Agents System..."
    
    # Stop backend
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend server stopped"
        fi
        rm -f .backend.pid
    fi
    
    # Stop frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend server stopped"
        fi
        rm -f .frontend.pid
    fi
    
    print_success "System stopped successfully"
    exit 0
}

# Main execution
main() {
    case "${1:-start}" in
        "check")
            check_prerequisites
            print_success "All prerequisites are satisfied!"
            ;;
        "setup")
            check_prerequisites
            setup_frontend
            setup_backend
            print_success "Setup complete! Run './quick-start-specialized-agents.sh start' to start the system."
            ;;
        "start")
            check_prerequisites
            if [ ! -d "node_modules" ]; then
                print_warning "Dependencies not installed. Running setup first..."
                setup_frontend
                setup_backend
            fi
            start_system
            ;;
        "stop")
            cleanup
            ;;
        "restart")
            cleanup
            sleep 2
            start_system
            ;;
        "logs")
            if [ -f "backend.log" ]; then
                tail -f backend.log
            else
                print_warning "No backend logs found"
            fi
            ;;
        "help"|"-h"|"--help")
            echo "Specialized AI Agents System - Quick Start Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  check     - Check if all prerequisites are installed"
            echo "  setup     - Install dependencies and configure the system"
            echo "  start     - Start the system (default)"
            echo "  stop      - Stop the system"
            echo "  restart   - Restart the system"
            echo "  logs      - Show backend logs"
            echo "  help      - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 setup    # First time setup"
            echo "  $0 start    # Start the system"
            echo "  $0 stop     # Stop the system"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 