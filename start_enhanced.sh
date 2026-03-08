#!/bin/bash

echo "🚀 Starting Enhanced Interview Intelligence Platform..."
echo "=========================================================="
echo "🤖 AI Models: Active"
echo "🎤 ElevenLabs Voice: Ready"
echo "🧠 OpenAI Integration: Available"
echo "📊 Advanced Analytics: Enabled"
echo "🔒 Privacy-first Architecture: Active"
echo "=========================================================="

# Kill any existing processes on port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo "🌐 Starting enhanced platform on port 8080..."
echo "📱 Access the platform at: http://localhost:8080"
echo "🔄 Press Ctrl+C to stop the server"
echo "=========================================================="

# Run the enhanced application
python3 enhanced_app.py
