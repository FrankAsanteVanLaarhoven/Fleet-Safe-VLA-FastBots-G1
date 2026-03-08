#!/bin/bash

# Interview Intelligence Platform - Web Application Startup Script

echo "🚀 Starting Interview Intelligence Platform (Web Version)..."
echo "=========================================================="
echo "🎯 Real-time Company Research & Analysis"
echo "🤖 Avatar Mock Interviews with Voice Synthesis"
echo "📝 Live Interview Teleprompter"
echo "📊 Comprehensive Analytics & Reporting"
echo "🔒 Privacy-first Architecture"
echo "=========================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installing Flask..."
    pip3 install flask
fi

# Create necessary directories
mkdir -p templates static/css static/js data/company_database

echo "🌐 Starting web server..."
echo "📱 Access the platform at: http://localhost:5000"
echo "🔄 Press Ctrl+C to stop the server"
echo "=========================================================="

# Start the web application
python3 web_app.py
