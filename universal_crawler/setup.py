#!/usr/bin/env python3
"""
Universal Crawler Setup Script
==============================

Comprehensive setup script for the universal crawler system.
Handles installation, configuration, and initialization.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
import argparse

def run_command(command: List[str], cwd: Optional[str] = None) -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {command[0]} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command[0]} failed: {e.stderr}")
        return False

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies() -> bool:
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]):
        return False
    
    # Install requirements
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        return False
    
    return True

def install_playwright() -> bool:
    """Install Playwright browsers."""
    print("\n🌐 Installing Playwright browsers...")
    return run_command([sys.executable, "-m", "playwright", "install", "--with-deps"])

def create_directories() -> bool:
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "crawl_data",
        "logs",
        "backups",
        "config",
        "tests",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    return True

def create_config_files() -> bool:
    """Create configuration files."""
    print("\n⚙️  Creating configuration files...")
    
    # Import config module
    try:
        from config import create_default_config
        create_default_config("config.json")
        print("✓ Created config.json")
    except Exception as e:
        print(f"✗ Failed to create config.json: {e}")
        return False
    
    # Create .env file
    env_content = """# Universal Crawler Environment Variables
# ================================================

# Environment
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database Configuration
DATABASE_URL=sqlite:///crawler.db

# Storage Configuration
STORAGE_PATH=crawl_data
STORAGE_MAX_SIZE_GB=100

# Network Configuration
NETWORK_TIMEOUT=30
NETWORK_MAX_RETRIES=3
NETWORK_RATE_LIMIT=60

# Security Configuration
# ENCRYPTION_KEY=your-secret-key-here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/crawler.log

# Optional: Proxy Configuration
# PROXY_URL=http://proxy.example.com:8080

# Optional: External API Keys
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("✓ Created .env file")
    
    return True

def create_startup_scripts() -> bool:
    """Create startup scripts for different platforms."""
    print("\n🚀 Creating startup scripts...")
    
    # Unix/Linux/macOS startup script
    unix_script = """#!/bin/bash
# Universal Crawler Startup Script
# ================================

echo "Starting Universal Crawler..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the API server
python universal_crawler_api.py
"""
    
    with open("start_crawler.sh", "w") as f:
        f.write(unix_script)
    
    # Make executable
    os.chmod("start_crawler.sh", 0o755)
    print("✓ Created start_crawler.sh")
    
    # Windows startup script
    windows_script = """@echo off
REM Universal Crawler Startup Script
REM ================================

echo Starting Universal Crawler...

REM Activate virtual environment if it exists
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
)

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start the API server
python universal_crawler_api.py
"""
    
    with open("start_crawler.bat", "w") as f:
        f.write(windows_script)
    print("✓ Created start_crawler.bat")
    
    return True

def create_docker_files() -> bool:
    """Create Docker configuration files."""
    print("\n🐳 Creating Docker files...")
    
    # Dockerfile
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \\
    && apt-get update \\
    && apt-get install -y \\
    google-chrome-stable \\
    fonts-ipafont-gothic \\
    fonts-wqy-zenhei \\
    fonts-thai-tlwg \\
    fonts-kacst \\
    fonts-freefont-ttf \\
    libxss1 \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p crawl_data logs backups

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "universal_crawler_api.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("✓ Created Dockerfile")
    
    # docker-compose.yml
    compose_content = """version: '3.8'

services:
  crawler-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./crawl_data:/app/crawl_data
      - ./logs:/app/logs
      - ./config.json:/app/config.json
    environment:
      - ENVIRONMENT=production
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    print("✓ Created docker-compose.yml")
    
    return True

def create_documentation() -> bool:
    """Create basic documentation."""
    print("\n📚 Creating documentation...")
    
    # README.md
    readme_content = """# Universal Crawler System

A comprehensive web crawling system designed to handle any website regardless of:
- Anti-bot protection and resilience
- Dynamic content and JavaScript rendering
- Complex security setups
- Rate limiting and IP blocking
- CAPTCHA challenges

## Features

- **Universal Compatibility**: Crawl any website regardless of its resilience
- **Multiple Crawling Modes**: Basic, Enhanced, Full Site, Deep, Stealth, Enterprise
- **Advanced Extraction**: Images, links, forms, scripts, styles, metadata
- **Compliance Ready**: GDPR, CCPA, robots.txt compliance
- **Real-time Monitoring**: WebSocket updates and comprehensive logging
- **Export Options**: JSON, CSV, ZIP, and custom formats
- **API-First Design**: RESTful API with comprehensive endpoints

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd universal-crawler
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Start the crawler**:
   ```bash
   # Unix/Linux/macOS
   ./start_crawler.sh
   
   # Windows
   start_crawler.bat
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Installation

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Access the API**:
   - API Documentation: http://localhost:8000/docs

## Usage

### Basic Crawling

```python
import asyncio
from universal_crawler_system import UniversalCrawler, CrawlRequest, CrawlMode

async def main():
    async with UniversalCrawler() as crawler:
        request = CrawlRequest(
            url="https://example.com",
            mode=CrawlMode.ENHANCED,
            max_depth=2,
            max_pages=10
        )
        
        result = await crawler.start_crawl(request)
        print(f"Started crawl: {result.id}")

asyncio.run(main())
```

### API Usage

```bash
# Start a crawl
curl -X POST "http://localhost:8000/crawl" \\
     -H "Content-Type: application/json" \\
     -d '{
       "url": "https://example.com",
       "mode": "enhanced",
       "max_depth": 2,
       "max_pages": 10
     }'

# Get crawl status
curl "http://localhost:8000/status/{crawl_id}"

# Get crawl results
curl "http://localhost:8000/results/{crawl_id}"

# Export results
curl "http://localhost:8000/export/{crawl_id}/json" -o results.json
```

## Configuration

The system uses a comprehensive configuration system:

- **Environment Variables**: Set via `.env` file or system environment
- **Configuration File**: `config.json` for detailed settings
- **Runtime Configuration**: API endpoints for dynamic configuration

### Key Configuration Options

- **Network**: Timeouts, retries, rate limiting
- **Storage**: Data retention, compression, backup
- **Security**: SSL verification, encryption, compliance
- **API**: CORS, authentication, rate limiting
- **Logging**: Levels, formats, file rotation

## Crawling Modes

1. **Basic**: Simple HTML extraction
2. **Enhanced**: OCR, AST, Network analysis
3. **Full Site**: Complete source extraction
4. **Deep**: Multi-level crawling
5. **Stealth**: Anti-detection mode
6. **Enterprise**: Full compliance and audit

## API Endpoints

- `POST /crawl` - Start a new crawl
- `GET /status/{crawl_id}` - Get crawl status
- `GET /results/{crawl_id}` - Get crawl results
- `POST /stop/{crawl_id}` - Stop a crawl
- `DELETE /crawl/{crawl_id}` - Delete a crawl
- `GET /crawls` - Get all crawls
- `GET /stats` - Get crawling statistics
- `GET /export/{crawl_id}/{format}` - Export results
- `WS /ws` - Real-time updates

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `/docs`
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✓ Created README.md")
    
    return True

def run_tests() -> bool:
    """Run basic tests to verify installation."""
    print("\n🧪 Running basic tests...")
    
    # Test imports
    try:
        import aiohttp
        import fastapi
        import uvicorn
        import pydantic
        from bs4 import BeautifulSoup
        print("✓ All core dependencies imported successfully")
    except ImportError as e:
        print(f"✗ Import test failed: {e}")
        return False
    
    # Test configuration
    try:
        from config import get_config
        config = get_config()
        print("✓ Configuration system working")
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Universal Crawler Setup")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-playwright", action="store_true", help="Skip Playwright installation")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker files creation")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    
    args = parser.parse_args()
    
    print("🚀 Universal Crawler Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Install Playwright
    if not args.skip_playwright:
        if not install_playwright():
            print("⚠️  Playwright installation failed, but continuing...")
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Create configuration files
    if not create_config_files():
        sys.exit(1)
    
    # Create startup scripts
    if not create_startup_scripts():
        sys.exit(1)
    
    # Create Docker files
    if not args.skip_docker:
        if not create_docker_files():
            print("⚠️  Docker files creation failed, but continuing...")
    
    # Create documentation
    if not create_documentation():
        print("⚠️  Documentation creation failed, but continuing...")
    
    # Run tests
    if not args.skip_tests:
        if not run_tests():
            print("⚠️  Tests failed, but setup completed")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Review and customize config.json")
    print("2. Start the crawler: ./start_crawler.sh")
    print("3. Access the API: http://localhost:8000/docs")
    print("4. Check the documentation: README.md")

if __name__ == "__main__":
    main() 