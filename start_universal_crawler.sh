#!/bin/bash
# Universal Crawler System Startup Script
# ======================================

echo "Starting Universal Crawler System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if universal crawler is installed
if [ ! -f "universal_crawler/universal_crawler/__init__.py" ]; then
    echo "Universal crawler not found. Running setup..."
    python setup.py
fi

# Start the universal crawler API
echo "Starting Universal Crawler API..."
python universal_crawler_api.py
