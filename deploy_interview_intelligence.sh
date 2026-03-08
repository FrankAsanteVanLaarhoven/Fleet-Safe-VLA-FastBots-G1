#!/bin/bash

# Iron Cloud Nexus AI - Live Interview Intelligence Deployment Script
# Real-time teleprompter for live interviews

echo "🔧 Iron Cloud Nexus AI - Live Interview Intelligence System"
echo "=========================================================="
echo "🎯 Real-time teleprompter for live interviews"
echo "⚡ Domain-specific expertise and intelligent responses"
echo "🔒 Professional appearance for stealth operation"
echo "=========================================================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Check for speech recognition
echo "🔍 Checking for speech recognition dependencies..."
python3 -c "import speech_recognition" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  SpeechRecognition not found. Installing dependencies..."
    pip3 install SpeechRecognition pyaudio
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install speech recognition dependencies."
        echo "Please install manually: pip install SpeechRecognition pyaudio"
        exit 1
    fi
fi

echo "✅ Dependencies are available"
echo ""

# Display deployment options
echo "🚀 Live Interview Intelligence Options:"
echo "1. Basic Interview Intelligence (Simple)"
echo "2. Advanced Interview Intelligence (Recommended)"
echo "3. Install Dependencies Only"
echo "4. View Interview Intelligence Guide"
echo ""

read -p "Select option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching Basic Interview Intelligence..."
        echo "💡 Real-time speech recognition and domain expertise"
        echo "🎤 Select domain and click 'Start Listening'"
        echo "🔒 Professional appearance as 'Meeting Notes'"
        echo ""
        python3 live_interview_intelligence_system.py
        ;;
    2)
        echo ""
        echo "🚀 Launching Advanced Interview Intelligence..."
        echo "💡 Advanced features: Sentiment Analysis, Context Awareness"
        echo "🎤 Real-time suggestions and interview progress tracking"
        echo "🔒 Professional teleprompter for live interviews"
        echo ""
        python3 advanced_interview_intelligence.py
        ;;
    3)
        echo ""
        echo "📦 Installing Interview Intelligence Dependencies..."
        pip3 install SpeechRecognition pyaudio
        echo "✅ Dependencies installed successfully"
        echo "💡 You can now run the interview intelligence systems"
        ;;
    4)
        echo ""
        echo "📖 Opening Interview Intelligence Guide..."
        if command -v open &> /dev/null; then
            open LIVE_INTERVIEW_INTELLIGENCE_GUIDE.md
        elif command -v xdg-open &> /dev/null; then
            xdg-open LIVE_INTERVIEW_INTELLIGENCE_GUIDE.md
        else
            echo "📄 Interview Intelligence Guide: LIVE_INTERVIEW_INTELLIGENCE_GUIDE.md"
            echo "Please open this file to view the complete guide."
        fi
        ;;
    *)
        echo "❌ Invalid option. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Interview Intelligence deployment complete!"
echo "🎯 Ready for live interviews on Zoom, Teams, etc."
echo "🔒 Remember to position window strategically"
echo "💡 Good luck with your interview!"
