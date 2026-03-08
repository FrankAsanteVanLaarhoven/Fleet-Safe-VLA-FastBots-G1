#!/bin/bash
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
