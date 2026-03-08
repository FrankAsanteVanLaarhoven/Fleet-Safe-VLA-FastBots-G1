#!/bin/bash

# Iron Cloud Nexus AI - Stealth Service Deployment Script
# Complete stealth assistance system for proctored screenings

echo "🔧 Iron Cloud Nexus AI - Stealth Service Deployment"
echo "=================================================="
echo "🎯 Complete stealth assistance system"
echo "⚡ Ready for any proctored screening"
echo "🔒 Professional deployment package"
echo "=================================================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Check tkinter availability
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter is required but not available."
    echo "Please install tkinter and try again."
    exit 1
fi

echo "✅ Python 3 and tkinter are available"
echo ""

# Display deployment options
echo "🚀 Deployment Options:"
echo "1. Complete Service System (Recommended)"
echo "2. High Contrast Calculator (Glasses-friendly)"
echo "3. Simple Calculator (Basic)"
echo "4. Multi-Mode Stealth System (Advanced)"
echo "5. View deployment guide"
echo ""

read -p "Select option (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching Complete Service System..."
        echo "💡 Service control panel will appear"
        echo "🔍 Select tool and skill, then start service"
        echo ""
        python3 iron_cloud_stealth_service.py
        ;;
    2)
        echo ""
        echo "🚀 Launching High Contrast Calculator..."
        echo "💡 High contrast calculator for glasses wearers"
        echo "🔒 Always visible buttons"
        echo ""
        python3 git_high_contrast_calculator.py
        ;;
    3)
        echo ""
        echo "🚀 Launching Simple Calculator..."
        echo "💡 Simple, reliable calculator"
        echo "🔒 No button issues"
        echo ""
        python3 git_simple_calculator.py
        ;;
    4)
        echo ""
        echo "🚀 Launching Multi-Mode Stealth System..."
        echo "💡 Advanced stealth with multiple modes"
        echo "🔒 System Monitor appearance"
        echo ""
        python3 outlier_stealth_master_system.py
        ;;
    5)
        echo ""
        echo "📖 Opening deployment guide..."
        if command -v open &> /dev/null; then
            open STEALTH_SERVICE_DEPLOYMENT.md
        elif command -v xdg-open &> /dev/null; then
            xdg-open STEALTH_SERVICE_DEPLOYMENT.md
        else
            echo "📄 Deployment guide: STEALTH_SERVICE_DEPLOYMENT.md"
            echo "Please open this file to view the complete guide."
        fi
        ;;
    *)
        echo "❌ Invalid option. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment complete!"
echo "🔒 Remember to use emergency procedures if needed"
echo "🎯 Good luck with your screening!"
