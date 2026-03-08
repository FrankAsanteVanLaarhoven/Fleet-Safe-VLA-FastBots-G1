#!/bin/bash

# Interview Intelligence Platform - Deployment Script
# Complete system deployment with all dependencies and configurations

echo "🚀 Interview Intelligence Platform - Deployment Script"
echo "======================================================"
echo "🎯 Real-time Company Research & Analysis"
echo "🤖 Avatar Mock Interviews with Voice Synthesis"
echo "📝 Live Interview Teleprompter"
echo "📊 Comprehensive Analytics & Reporting"
echo "🔒 Privacy-first Architecture"
echo "======================================================"

# Check Python version
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/company_database
mkdir -p data/interview_patterns
mkdir -p logs
mkdir -p cache

# Create configuration file
echo "⚙️ Creating configuration file..."
cat > config.env << EOF
# Interview Intelligence Platform Configuration
# API Keys (Replace with your actual keys)

# News API for company news and sentiment analysis
NEWS_API_KEY=your_news_api_key_here

# Crunchbase API for company information
CRUNCHBASE_API_KEY=your_crunchbase_key_here

# LinkedIn API for company and people data
LINKEDIN_API_KEY=your_linkedin_key_here

# Glassdoor API for company reviews
GLASSDOOR_API_KEY=your_glassdoor_key_here

# SEC API for financial data
SEC_API_KEY=your_sec_api_key_here

# ElevenLabs API for voice synthesis
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# OpenAI API for AI assistance
OPENAI_API_KEY=your_openai_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
CACHE_ENABLED=true
PRIVACY_MODE=true

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
CACHE_TTL=3600

# Compliance Settings
GDPR_COMPLIANCE=true
DATA_RETENTION_DAYS=30
AUDIT_LOGGING=true
EOF

echo "✅ Configuration file created: config.env"
echo "⚠️  Please edit config.env with your actual API keys"

# Create startup script
echo "🔧 Creating startup script..."
cat > start_platform.sh << 'EOF'
#!/bin/bash

# Interview Intelligence Platform - Startup Script

echo "🚀 Starting Interview Intelligence Platform..."
echo "=============================================="

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f "config.env" ]; then
    export $(cat config.env | grep -v '^#' | xargs)
fi

# Start the application
python3 main.py
EOF

chmod +x start_platform.sh

# Create development startup script
echo "🔧 Creating development startup script..."
cat > start_dev.sh << 'EOF'
#!/bin/bash

# Interview Intelligence Platform - Development Startup Script

echo "🚀 Starting Interview Intelligence Platform (Development Mode)..."
echo "================================================================"

# Activate virtual environment
source venv/bin/activate

# Set development environment
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Load environment variables
if [ -f "config.env" ]; then
    export $(cat config.env | grep -v '^#' | xargs)
fi

# Start the application with development settings
python3 main.py
EOF

chmod +x start_dev.sh

# Create API key setup script
echo "🔧 Creating API key setup script..."
cat > setup_api_keys.sh << 'EOF'
#!/bin/bash

# API Key Setup Script for Interview Intelligence Platform

echo "🔑 Setting up API keys for Interview Intelligence Platform"
echo "=========================================================="

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "❌ config.env not found. Please run deploy.sh first."
    exit 1
fi

echo "📝 Please enter your API keys (press Enter to skip any):"
echo ""

# News API
read -p "News API Key: " news_key
if [ ! -z "$news_key" ]; then
    sed -i.bak "s/NEWS_API_KEY=.*/NEWS_API_KEY=$news_key/" config.env
fi

# Crunchbase API
read -p "Crunchbase API Key: " crunchbase_key
if [ ! -z "$crunchbase_key" ]; then
    sed -i.bak "s/CRUNCHBASE_API_KEY=.*/CRUNCHBASE_API_KEY=$crunchbase_key/" config.env
fi

# LinkedIn API
read -p "LinkedIn API Key: " linkedin_key
if [ ! -z "$linkedin_key" ]; then
    sed -i.bak "s/LINKEDIN_API_KEY=.*/LINKEDIN_API_KEY=$linkedin_key/" config.env
fi

# Glassdoor API
read -p "Glassdoor API Key: " glassdoor_key
if [ ! -z "$glassdoor_key" ]; then
    sed -i.bak "s/GLASSDOOR_API_KEY=.*/GLASSDOOR_API_KEY=$glassdoor_key/" config.env
fi

# SEC API
read -p "SEC API Key: " sec_key
if [ ! -z "$sec_key" ]; then
    sed -i.bak "s/SEC_API_KEY=.*/SEC_API_KEY=$sec_key/" config.env
fi

# ElevenLabs API
read -p "ElevenLabs API Key: " elevenlabs_key
if [ ! -z "$elevenlabs_key" ]; then
    sed -i.bak "s/ELEVENLABS_API_KEY=.*/ELEVENLABS_API_KEY=$elevenlabs_key/" config.env
fi

# OpenAI API
read -p "OpenAI API Key: " openai_key
if [ ! -z "$openai_key" ]; then
    sed -i.bak "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_key/" config.env
fi

# Clean up backup file
rm -f config.env.bak

echo ""
echo "✅ API keys configured successfully!"
echo "🚀 You can now start the platform with: ./start_platform.sh"
EOF

chmod +x setup_api_keys.sh

# Create test script
echo "🔧 Creating test script..."
cat > test_platform.sh << 'EOF'
#!/bin/bash

# Test Script for Interview Intelligence Platform

echo "🧪 Testing Interview Intelligence Platform"
echo "=========================================="

# Activate virtual environment
source venv/bin/activate

# Test Python imports
echo "🔍 Testing Python imports..."
python3 -c "
try:
    import tkinter
    import asyncio
    import aiohttp
    import json
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test company researcher
echo "🔍 Testing company researcher..."
python3 -c "
import sys
sys.path.append('.')
try:
    from core.intelligence_engine.company_researcher import CompanyIntelligenceEngine
    print('✅ Company researcher import successful')
except ImportError as e:
    print(f'❌ Company researcher import error: {e}')
    exit(1)
"

# Test main application
echo "🔍 Testing main application..."
python3 -c "
import sys
sys.path.append('.')
try:
    from main import InterviewIntelligencePlatform
    print('✅ Main application import successful')
except ImportError as e:
    print(f'❌ Main application import error: {e}')
    exit(1)
"

echo ""
echo "✅ All tests passed!"
echo "🚀 Platform is ready to use"
EOF

chmod +x test_platform.sh

# Create uninstall script
echo "🔧 Creating uninstall script..."
cat > uninstall.sh << 'EOF'
#!/bin/bash

# Uninstall Script for Interview Intelligence Platform

echo "🗑️ Uninstalling Interview Intelligence Platform"
echo "==============================================="

read -p "Are you sure you want to uninstall? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "❌ Uninstall cancelled"
    exit 0
fi

echo "🧹 Cleaning up..."

# Remove virtual environment
if [ -d "venv" ]; then
    echo "Removing virtual environment..."
    rm -rf venv
fi

# Remove data directories
if [ -d "data" ]; then
    echo "Removing data directories..."
    rm -rf data
fi

# Remove cache
if [ -d "cache" ]; then
    echo "Removing cache..."
    rm -rf cache
fi

# Remove logs
if [ -d "logs" ]; then
    echo "Removing logs..."
    rm -rf logs
fi

# Remove configuration files
echo "Removing configuration files..."
rm -f config.env
rm -f start_platform.sh
rm -f start_dev.sh
rm -f setup_api_keys.sh
rm -f test_platform.sh

echo "✅ Uninstall completed"
EOF

chmod +x uninstall.sh

echo ""
echo "🎉 Deployment completed successfully!"
echo "====================================="
echo ""
echo "📋 Next steps:"
echo "1. Configure API keys: ./setup_api_keys.sh"
echo "2. Test the platform: ./test_platform.sh"
echo "3. Start the platform: ./start_platform.sh"
echo "4. Start in development mode: ./start_dev.sh"
echo ""
echo "📚 Documentation:"
echo "- README.md: Complete platform documentation"
echo "- config.env: Configuration settings"
echo "- requirements.txt: Python dependencies"
echo ""
echo "🔧 Available scripts:"
echo "- start_platform.sh: Start the platform"
echo "- start_dev.sh: Start in development mode"
echo "- setup_api_keys.sh: Configure API keys"
echo "- test_platform.sh: Test the installation"
echo "- uninstall.sh: Remove the platform"
echo ""
echo "🚀 Interview Intelligence Platform is ready!"
echo "============================================="
