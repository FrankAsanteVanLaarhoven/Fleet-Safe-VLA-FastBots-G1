#!/bin/bash

# DataMinerAI Media Server Startup Script
# This script provides options to start either the simple Python server or the full Docker setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[MEDIA SERVER]${NC} $1"
}

show_menu() {
    clear
    echo "🎬 DataMinerAI Media Server"
    echo "============================"
    echo ""
    echo "Choose your media server option:"
    echo ""
    echo "1) 🐍 Simple Python Server (Recommended for quick start)"
    echo "   - No Docker required"
    echo "   - Lightweight and fast"
    echo "   - Basic streaming capabilities"
    echo "   - Web interface included"
    echo ""
    echo "2) 🐳 Full Docker Setup (Advanced)"
    echo "   - Requires Docker to be running"
    echo "   - Jellyfin, Plex, Sonarr, Radarr, etc."
    echo "   - Complete media management ecosystem"
    echo "   - Advanced features and automation"
    echo ""
    echo "3) 📖 View Documentation"
    echo "4) 🛑 Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice
}

start_python_server() {
    print_header "Starting Python Media Server..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 and try again."
        exit 1
    fi
    
    # Create media directory if it doesn't exist
    mkdir -p media
    
    print_status "Starting server on http://localhost:8080"
    print_status "Media directory: $(pwd)/media"
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the Python server
    python3 simple-media-server.py
}

start_docker_server() {
    print_header "Starting Docker Media Server..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        echo ""
        print_warning "To start Docker on macOS:"
        echo "  - Open Docker Desktop application"
        echo "  - Wait for Docker to start"
        echo "  - Run this script again"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    fi
    
    # Create network if it doesn't exist
    if ! docker network ls | grep -q dataminerai-network; then
        print_status "Creating Docker network..."
        docker network create dataminerai-network
    fi
    
    print_status "Starting Docker services..."
    print_status "This may take a few minutes on first run..."
    echo ""
    
    # Start the Docker services
    docker-compose -f media-server-docker-compose.yml up -d
    
    echo ""
    print_status "Docker services started successfully!"
    echo ""
    echo "🌐 Access your media servers:"
    echo "  • Jellyfin: http://localhost:8096"
    echo "  • Plex: http://localhost:32400/web"
    echo "  • Transmission: http://localhost:9091"
    echo "  • Sonarr: http://localhost:8989"
    echo "  • Radarr: http://localhost:7878"
    echo "  • Lidarr: http://localhost:8686"
    echo "  • Bazarr: http://localhost:6767"
    echo "  • Tautulli: http://localhost:8181"
    echo ""
    echo "📖 Management commands:"
    echo "  ./manage-media-server.sh status   # Check service status"
    echo "  ./manage-media-server.sh logs     # View logs"
    echo "  ./manage-media-server.sh stop     # Stop services"
    echo ""
}

show_documentation() {
    clear
    echo "📖 DataMinerAI Media Server Documentation"
    echo "========================================="
    echo ""
    echo "Quick Start Guide:"
    echo "=================="
    echo ""
    echo "1. Simple Python Server:"
    echo "   - Run: ./start-media-server.sh"
    echo "   - Choose option 1"
    echo "   - Add media files to ./media/ directory"
    echo "   - Access at http://localhost:8080"
    echo ""
    echo "2. Full Docker Setup:"
    echo "   - Ensure Docker is running"
    echo "   - Run: ./start-media-server.sh"
    echo "   - Choose option 2"
    echo "   - Follow setup instructions for each service"
    echo ""
    echo "Directory Structure:"
    echo "==================="
    echo "media/"
    echo "├── movies/          # Movie files"
    echo "├── tv/             # TV show files"
    echo "├── music/          # Music files"
    echo "└── photos/         # Photo files"
    echo ""
    echo "Supported Formats:"
    echo "=================="
    echo "Video: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V"
    echo "Audio: MP3, WAV, FLAC, AAC, OGG, M4A, WMA"
    echo "Image: JPG, PNG, GIF, BMP, WebP"
    echo ""
    echo "For detailed documentation, see:"
    echo "- MEDIA_SERVER_GUIDE.md"
    echo "- media-server-dashboard.html"
    echo ""
    read -p "Press Enter to continue..."
}

# Main script logic
case "${1:-}" in
    python|simple)
        start_python_server
        ;;
    docker|full)
        start_docker_server
        ;;
    *)
        # Interactive menu
        while true; do
            show_menu
            case $choice in
                1)
                    start_python_server
                    break
                    ;;
                2)
                    start_docker_server
                    break
                    ;;
                3)
                    show_documentation
                    ;;
                4)
                    print_status "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid choice. Please enter 1-4."
                    sleep 2
                    ;;
            esac
        done
        ;;
esac
