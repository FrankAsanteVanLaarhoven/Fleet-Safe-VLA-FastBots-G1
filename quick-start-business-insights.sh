#!/bin/bash

# Business Insights Agent - Quick Start Script
# ===========================================
# 
# This script sets up and starts the Business Insights Agent system
# with all necessary components for comprehensive business intelligence extraction.

set -e

echo "🚀 Business Insights Agent - Quick Start"
echo "========================================"
echo ""

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check system requirements
print_status "Checking system requirements..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_error "Node.js is required but not installed"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    print_success "Docker found"
    DOCKER_AVAILABLE=true
else
    print_warning "Docker not found - some features may be limited"
    DOCKER_AVAILABLE=false
fi

echo ""

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data/business_insights
mkdir -p cache
mkdir -p config

print_success "Directories created"

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found - installing basic dependencies"
    pip3 install fastapi uvicorn aiohttp beautifulsoup4 asyncio
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
if [ -f "package.json" ]; then
    npm install
    print_success "Node.js dependencies installed"
else
    print_warning "package.json not found - skipping Node.js dependencies"
fi

echo ""

# Create configuration file
print_status "Creating configuration file..."
cat > config/business_insights_config.json << EOF
{
  "crawling": {
    "stealth_mode": true,
    "max_depth": 5,
    "delay_range": [1, 3],
    "user_agents": [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ],
    "proxy_rotation": true
  },
  "mcp_services": {
    "enable_figma": true,
    "enable_web_search": true,
    "enable_document_analysis": true,
    "enable_image_analysis": true,
    "enable_code_analysis": true,
    "enable_data_extraction": true,
    "figma_config": {
      "api_key": "YOUR_FIGMA_API_KEY"
    }
  },
  "data_sources": {
    "financial": [
      "yahoo_finance",
      "marketwatch",
      "seeking_alpha",
      "finviz"
    ],
    "social_media": [
      "linkedin",
      "twitter",
      "facebook",
      "instagram",
      "youtube"
    ],
    "technology": [
      "builtwith",
      "wappalyzer",
      "similar_tech"
    ]
  },
  "extraction": {
    "max_concurrent": 10,
    "timeout": 30,
    "retry_attempts": 3,
    "cache_duration": 3600
  }
}
EOF

print_success "Configuration file created: config/business_insights_config.json"

# Create environment file
print_status "Creating environment file..."
cat > .env << EOF
# Business Insights Agent Environment Variables
DATABASE_URL=sqlite:///./data/business_insights.db
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=true
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Crawling Configuration
CRAWLER_TIMEOUT=30
CRAWLER_MAX_RETRIES=3
CRAWLER_DELAY=2

# MCP Services Configuration
FIGMA_API_KEY=your-figma-api-key
OPENAI_API_KEY=your-openai-api-key

# Data Storage
DATA_DIR=./data/business_insights
CACHE_DIR=./cache
LOG_DIR=./logs
EOF

print_success "Environment file created: .env"

echo ""

# Start the backend server
print_status "Starting Business Insights Agent backend..."
echo ""

# Check if backend directory exists
if [ -d "backend" ]; then
    cd backend
    
    # Start the FastAPI server
    print_status "Starting FastAPI server on http://localhost:8000"
    print_status "API Documentation will be available at http://localhost:8000/docs"
    echo ""
    
    # Start the server in the background
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    # Wait a moment for the server to start
    sleep 3
    
    # Check if server started successfully
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "Backend server started successfully"
    else
        print_error "Failed to start backend server"
        exit 1
    fi
    
    cd ..
else
    print_error "Backend directory not found"
    exit 1
fi

echo ""

# Start the frontend (if available)
if [ -d "src" ] && [ -f "package.json" ]; then
    print_status "Starting frontend development server..."
    print_status "Frontend will be available at http://localhost:3000"
    echo ""
    
    # Start the Next.js development server
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait a moment for the server to start
    sleep 5
    
    print_success "Frontend server started successfully"
else
    print_warning "Frontend not found - only backend is running"
fi

echo ""

# Display system information
print_status "System Information:"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo "  Frontend: http://localhost:3000 (if available)"
echo "  Data Directory: ./data/business_insights"
echo "  Logs Directory: ./logs"
echo "  Configuration: ./config/business_insights_config.json"
echo ""

# Display usage examples
print_status "Usage Examples:"
echo ""
echo "1. Extract comprehensive business insights:"
echo "   curl -X POST http://localhost:8000/api/business-insights/extract-business-insights \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"company_name\": \"Apple Inc.\", \"domain\": \"apple.com\"}'"
echo ""
echo "2. Extract specific aspect (financial data):"
echo "   curl -X POST http://localhost:8000/api/business-insights/extract-specific-aspect \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"company_name\": \"Tesla\", \"aspect\": \"finances\"}'"
echo ""
echo "3. Get supported business aspects:"
echo "   curl http://localhost:8000/api/business-insights/supported-aspects"
echo ""
echo "4. Get system capabilities:"
echo "   curl http://localhost:8000/api/business-insights/capabilities"
echo ""

# Display business aspects
print_status "Supported Business Aspects:"
echo "  • Business Model, Trading, Operations, Supply Chain"
echo "  • Finances, Timeseries, Balances, Forecasting, Profit"
echo "  • Ownership, Stakeholders, Directors, Staff, Senior Members"
echo "  • Filings, Standings, Compliance, Certifications, Policies"
echo "  • IPO, Ticker, Trading History, Acquisitions"
echo "  • Software, Tech, BuiltWith, Cloud Providers"
echo "  • Blockchain, Crypto, DeFi, Smart Contracts"
echo "  • LinkedIn, Twitter, Social Media, YouTube, Influence"
echo "  • Location, Region, Global, Properties"
echo "  • Insurance, Banking, Hedge Funds"
echo "  • Sister Companies, Mother Companies"
echo "  • Products, Services, Manufacturing, Procurements"
echo "  • News, Publications, Documentation"
echo "  • Data, Metadata, Statistics"
echo "  • Applications, Expirations"
echo "  • Startup Year, Term"
echo ""

# Display capabilities
print_status "System Capabilities:"
echo "  ✅ Military-grade stealth crawling"
echo "  ✅ Paywall penetration"
echo "  ✅ Undetected operation"
echo "  ✅ Deep crawling with multiple depths"
echo "  ✅ Proxy rotation and user agent rotation"
echo "  ✅ Rate limiting bypass"
echo "  ✅ MCP services integration (Figma, Web Search, etc.)"
echo "  ✅ Multi-source data extraction"
echo "  ✅ Real-time financial data"
echo "  ✅ Social media intelligence"
echo "  ✅ Technology stack analysis"
echo "  ✅ Blockchain and crypto analysis"
echo "  ✅ Competitive intelligence"
echo "  ✅ Risk assessment and compliance monitoring"
echo ""

# Create a stop script
print_status "Creating stop script..."
cat > stop-business-insights.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Business Insights Agent..."

# Kill backend process
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
    echo "Backend server stopped"
fi

# Kill frontend process
if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
    echo "Frontend server stopped"
fi

# Kill any remaining processes
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null

echo "✅ Business Insights Agent stopped"
EOF

chmod +x stop-business-insights.sh
print_success "Stop script created: stop-business-insights.sh"

echo ""

# Final status
print_success "🎉 Business Insights Agent is ready!"
echo ""
echo "The system is now running with:"
echo "  • Comprehensive business intelligence extraction"
echo "  • Military-grade crawling capabilities"
echo "  • MCP services integration"
echo "  • Multi-source data analysis"
echo "  • Real-time monitoring capabilities"
echo ""
echo "To stop the system, run: ./stop-business-insights.sh"
echo ""
echo "For more information, see: BUSINESS_INSIGHTS_AGENT.md"
echo ""

# Keep the script running
print_status "Press Ctrl+C to stop the system"
echo ""

# Wait for user input
wait 