#!/bin/bash

# Iron Cloud Nexus AI - Ultimate Interview Intelligence System Deployment
# Complete deployment script for all interview intelligence systems

echo "🔧 Iron Cloud Nexus AI - Ultimate Interview Intelligence System"
echo "=============================================================="
echo "🎯 Target: Complete Interview Intelligence with Pre-Analysis"
echo "⚡ Pre-interview company and interviewer analysis"
echo "📊 Real-time interview assistance and analysis"
echo "💰 Salary negotiation and offer recommendations"
echo "🎓 PhD-level topic analysis and insights"
echo "=============================================================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for speech recognition
echo "🔍 Checking for speech recognition dependencies..."
python3 -c "import speech_recognition" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  SpeechRecognition not found. Installing dependencies..."
    pip3 install SpeechRecognition pyaudio
    if [ $? -ne 0 ]; then
        echo "⚠️  PyAudio installation may require system dependencies."
        echo "   For macOS: brew install portaudio"
        echo "   For Ubuntu: sudo apt-get install python3-pyaudio"
        echo "   For Windows: pip install pyaudio"
    fi
else
    echo "✅ SpeechRecognition found"
fi

echo ""
echo "🚀 Ultimate Interview Intelligence Options:"
echo "1. Ultimate System (Complete with Pre-Analysis)"
echo "2. Pre-Interview Analyzer Only"
echo "3. Comprehensive Interview System (Advanced)"
echo "4. Advanced Interview System (Enhanced)"
echo "5. Basic Interview System (Simple)"
echo "6. Install Dependencies Only"
echo "7. View Ultimate System Guide"
echo "8. View Complete System Summary"

read -p "Select option (1-8): " choice

case $choice in
    1)
        echo "🚀 Launching Ultimate Interview Intelligence System..."
        python3 ultimate_interview_intelligence_system.py
        ;;
    2)
        echo "🔍 Launching Pre-Interview Analyzer..."
        python3 pre_interview_analyzer.py
        ;;
    3)
        echo "📊 Launching Comprehensive Interview System..."
        python3 comprehensive_interview_intelligence.py
        ;;
    4)
        echo "⚡ Launching Advanced Interview System..."
        python3 advanced_interview_intelligence.py
        ;;
    5)
        echo "🎤 Launching Basic Interview System..."
        python3 live_interview_intelligence_system.py
        ;;
    6)
        echo "📦 Installing dependencies..."
        pip3 install SpeechRecognition pyaudio
        echo "✅ Dependencies installed"
        ;;
    7)
        echo "📖 Opening Ultimate System Guide..."
        if command -v open &> /dev/null; then
            open ULTIMATE_INTERVIEW_INTELLIGENCE_GUIDE.md
        elif command -v xdg-open &> /dev/null; then
            xdg-open ULTIMATE_INTERVIEW_INTELLIGENCE_GUIDE.md
        else
            echo "Please open ULTIMATE_INTERVIEW_INTELLIGENCE_GUIDE.md"
        fi
        ;;
    8)
        echo "📋 Opening Complete System Summary..."
        if command -v open &> /dev/null; then
            open COMPLETE_ULTIMATE_INTERVIEW_SYSTEM_SUMMARY.md
        elif command -v xdg-open &> /dev/null; then
            xdg-open COMPLETE_ULTIMATE_INTERVIEW_SYSTEM_SUMMARY.md
        else
            echo "Please open COMPLETE_ULTIMATE_INTERVIEW_SYSTEM_SUMMARY.md"
        fi
        ;;
    *)
        echo "❌ Invalid option. Please select 1-8."
        exit 1
        ;;
esac

echo ""
echo "🎯 Mission Status: COMPLETE"
echo "The Ultimate Interview Intelligence System is ready for deployment!"
echo "Deploy with confidence for any interview with ultimate intelligence and analysis! 🚀"
