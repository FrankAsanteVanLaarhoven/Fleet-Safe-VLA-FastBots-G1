#!/bin/bash

# DataMinerAI Media Server Setup Script
# This script sets up a complete media server ecosystem

set -e

echo "🎬 DataMinerAI Media Server Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_header "Creating media server directories..."

# Create necessary directories
mkdir -p media/{movies,tv,music,photos}
mkdir -p downloads/{movies,tv,music,complete,incomplete}
mkdir -p logs/media-server

print_status "Created media directories:"
echo "  📁 media/movies - Store your movie files"
echo "  📁 media/tv - Store your TV show files"
echo "  📁 media/music - Store your music files"
echo "  📁 media/photos - Store your photo files"
echo "  📁 downloads/ - Temporary download location"

# Set proper permissions
print_header "Setting directory permissions..."
chmod -R 755 media downloads
print_status "Set permissions for media and downloads directories"

# Create network if it doesn't exist
print_header "Creating Docker network..."
if ! docker network ls | grep -q dataminerai-network; then
    docker network create dataminerai-network
    print_status "Created dataminerai-network"
else
    print_status "dataminerai-network already exists"
fi

# Create environment file for media server
print_header "Creating environment configuration..."
cat > .env.media << EOF
# Media Server Environment Variables
PUID=1000
PGID=1000
TZ=UTC

# Transmission Settings
TRANSMISSION_USER=admin
TRANSMISSION_PASS=password123

# Plex Settings (Optional - get claim token from https://www.plex.tv/claim/)
PLEX_CLAIM=

# Jellyfin Settings
JELLYFIN_PublishedServerUrl=http://localhost:8096
JELLYFIN_EnableRemoteAccess=true

# Media Paths
MEDIA_PATH=./media
DOWNLOADS_PATH=./downloads
EOF

print_status "Created .env.media file with default settings"

# Create a simple media server management script
print_header "Creating management scripts..."

cat > manage-media-server.sh << 'EOF'
#!/bin/bash

# DataMinerAI Media Server Management Script

case "$1" in
    start)
        echo "Starting media server..."
        docker-compose -f media-server-docker-compose.yml up -d
        ;;
    stop)
        echo "Stopping media server..."
        docker-compose -f media-server-docker-compose.yml down
        ;;
    restart)
        echo "Restarting media server..."
        docker-compose -f media-server-docker-compose.yml restart
        ;;
    logs)
        docker-compose -f media-server-docker-compose.yml logs -f
        ;;
    status)
        docker-compose -f media-server-docker-compose.yml ps
        ;;
    update)
        echo "Updating media server containers..."
        docker-compose -f media-server-docker-compose.yml pull
        docker-compose -f media-server-docker-compose.yml up -d
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|update}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all media server services"
        echo "  stop    - Stop all media server services"
        echo "  restart - Restart all media server services"
        echo "  logs    - Show logs from all services"
        echo "  status  - Show status of all services"
        echo "  update  - Update and restart all services"
        exit 1
        ;;
esac
EOF

chmod +x manage-media-server.sh

# Create a quick start guide
print_header "Creating documentation..."

cat > MEDIA_SERVER_GUIDE.md << 'EOF'
# DataMinerAI Media Server Guide

## Quick Start

1. **Start the media server:**
   ```bash
   ./manage-media-server.sh start
   ```

2. **Access your media servers:**
   - **Jellyfin**: http://localhost:8096
   - **Plex**: http://localhost:32400/web
   - **Emby**: http://localhost:8096 (if not using Jellyfin)
   - **Transmission**: http://localhost:9091
   - **Sonarr**: http://localhost:8989
   - **Radarr**: http://localhost:7878
   - **Lidarr**: http://localhost:8686
   - **Bazarr**: http://localhost:6767
   - **Tautulli**: http://localhost:8181

## Media Server Options

### Jellyfin (Recommended)
- **Completely free and open source**
- **No subscription required**
- **Excellent transcoding capabilities**
- **Modern web interface**

### Plex
- **Feature-rich with premium features**
- **Requires Plex account**
- **Excellent mobile apps**
- **Some features require Plex Pass**

### Emby
- **Similar to Plex**
- **One-time license for premium features**
- **Good transcoding support**

## Management Tools

### Sonarr (TV Shows)
- Automatically downloads TV shows
- Monitors for new episodes
- Integrates with Transmission

### Radarr (Movies)
- Automatically downloads movies
- Monitors for new releases
- Integrates with Transmission

### Lidarr (Music)
- Automatically downloads music
- Monitors for new albums
- Integrates with Transmission

### Bazarr (Subtitles)
- Automatically downloads subtitles
- Supports multiple languages
- Integrates with Sonarr and Radarr

### Transmission (BitTorrent)
- BitTorrent client for downloads
- Web interface for management
- Integrates with all *arr applications

## Directory Structure

```
media/
├── movies/          # Movie files
├── tv/             # TV show files
├── music/          # Music files
└── photos/         # Photo files

downloads/
├── movies/         # Movie downloads
├── tv/            # TV show downloads
├── music/         # Music downloads
├── complete/      # Completed downloads
└── incomplete/    # In-progress downloads
```

## Configuration

### Initial Setup

1. **Jellyfin Setup:**
   - Access http://localhost:8096
   - Create admin account
   - Add media libraries (Movies, TV, Music)
   - Configure transcoding settings

2. **Plex Setup:**
   - Access http://localhost:32400/web
   - Sign in with Plex account
   - Add media libraries
   - Configure server settings

3. **Sonarr/Radarr Setup:**
   - Add indexers (torrent sites)
   - Configure download clients (Transmission)
   - Add media paths
   - Set quality profiles

### Security Notes

- Change default passwords in .env.media
- Use strong passwords for all services
- Consider using HTTPS with reverse proxy
- Keep containers updated regularly

## Troubleshooting

### Common Issues

1. **Permission Issues:**
   ```bash
   sudo chown -R 1000:1000 media downloads
   ```

2. **Port Conflicts:**
   - Check if ports are already in use
   - Modify ports in docker-compose file

3. **Container Won't Start:**
   ```bash
   docker-compose -f media-server-docker-compose.yml logs [service-name]
   ```

### Useful Commands

```bash
# View all logs
./manage-media-server.sh logs

# Check service status
./manage-media-server.sh status

# Update containers
./manage-media-server.sh update

# Access container shell
docker exec -it dataminerai-jellyfin /bin/bash
```

## Integration with DataMinerAI

The media server integrates with your existing DataMinerAI infrastructure:

- Uses the same Docker network
- Shares configuration patterns
- Can be managed through the main dashboard
- Logs are centralized

## Next Steps

1. Start with Jellyfin for a simple setup
2. Add Sonarr/Radarr for automated downloads
3. Configure Transmission for downloads
4. Set up Bazarr for subtitles
5. Consider Plex if you want premium features

## Support

For issues with specific media server applications, check their official documentation:
- [Jellyfin Documentation](https://jellyfin.org/docs/)
- [Plex Documentation](https://support.plex.tv/)
- [Sonarr Documentation](https://wiki.servarr.com/sonarr)
- [Radarr Documentation](https://wiki.servarr.com/radarr)
EOF

print_status "Created MEDIA_SERVER_GUIDE.md with comprehensive documentation"

# Create a simple web interface for media server management
print_header "Creating web interface..."

cat > media-server-dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataMinerAI Media Server Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .service-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .service-card h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.3rem;
        }
        
        .service-card p {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        
        .service-card .url {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.9rem;
            color: #495057;
            margin-bottom: 15px;
            word-break: break-all;
        }
        
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #28a745;
        }
        
        .status-offline {
            background: #dc3545;
        }
        
        .controls {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        
        .controls h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .control-buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .info-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .info-section h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        
        .info-item h4 {
            color: #495057;
            margin-bottom: 8px;
        }
        
        .info-item p {
            color: #6c757d;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 DataMinerAI Media Server</h1>
            <p>Complete media server ecosystem for your personal media library</p>
        </div>
        
        <div class="controls">
            <h2>🚀 Quick Controls</h2>
            <div class="control-buttons">
                <button class="btn" onclick="checkStatus()">Check Status</button>
                <button class="btn btn-secondary" onclick="openAll()">Open All Services</button>
                <button class="btn btn-secondary" onclick="showLogs()">View Logs</button>
            </div>
        </div>
        
        <div class="services-grid">
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Jellyfin</h3>
                <p>Open source media server with no subscription required. Perfect for personal media libraries.</p>
                <div class="url">http://localhost:8096</div>
                <a href="http://localhost:8096" target="_blank" class="btn">Open Jellyfin</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Plex</h3>
                <p>Feature-rich media server with excellent mobile apps and premium features.</p>
                <div class="url">http://localhost:32400/web</div>
                <a href="http://localhost:32400/web" target="_blank" class="btn">Open Plex</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Transmission</h3>
                <p>BitTorrent client for downloading media files with web interface.</p>
                <div class="url">http://localhost:9091</div>
                <a href="http://localhost:9091" target="_blank" class="btn">Open Transmission</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Sonarr</h3>
                <p>TV show management - automatically downloads and organizes TV shows.</p>
                <div class="url">http://localhost:8989</div>
                <a href="http://localhost:8989" target="_blank" class="btn">Open Sonarr</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Radarr</h3>
                <p>Movie management - automatically downloads and organizes movies.</p>
                <div class="url">http://localhost:7878</div>
                <a href="http://localhost:7878" target="_blank" class="btn">Open Radarr</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Lidarr</h3>
                <p>Music management - automatically downloads and organizes music.</p>
                <div class="url">http://localhost:8686</div>
                <a href="http://localhost:8686" target="_blank" class="btn">Open Lidarr</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Bazarr</h3>
                <p>Subtitle management - automatically downloads subtitles for your media.</p>
                <div class="url">http://localhost:6767</div>
                <a href="http://localhost:6767" target="_blank" class="btn">Open Bazarr</a>
            </div>
            
            <div class="service-card">
                <h3><span class="status-indicator status-online"></span>Tautulli</h3>
                <p>Plex statistics and monitoring - track your media usage and statistics.</p>
                <div class="url">http://localhost:8181</div>
                <a href="http://localhost:8181" target="_blank" class="btn">Open Tautulli</a>
            </div>
        </div>
        
        <div class="info-section">
            <h2>📋 Quick Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <h4>Media Directory</h4>
                    <p>./media/</p>
                </div>
                <div class="info-item">
                    <h4>Downloads Directory</h4>
                    <p>./downloads/</p>
                </div>
                <div class="info-item">
                    <h4>Management Script</h4>
                    <p>./manage-media-server.sh</p>
                </div>
                <div class="info-item">
                    <h4>Documentation</h4>
                    <p>MEDIA_SERVER_GUIDE.md</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function checkStatus() {
            alert('Status check functionality would be implemented here. Check the terminal for actual status.');
        }
        
        function openAll() {
            const urls = [
                'http://localhost:8096',
                'http://localhost:32400/web',
                'http://localhost:9091',
                'http://localhost:8989',
                'http://localhost:7878',
                'http://localhost:8686',
                'http://localhost:6767',
                'http://localhost:8181'
            ];
            
            urls.forEach(url => {
                window.open(url, '_blank');
            });
        }
        
        function showLogs() {
            alert('Log viewing functionality would be implemented here. Use ./manage-media-server.sh logs in terminal.');
        }
    </script>
</body>
</html>
EOF

print_status "Created media-server-dashboard.html web interface"

# Make scripts executable
chmod +x manage-media-server.sh

print_header "Setup Complete! 🎉"

echo ""
print_status "Your DataMinerAI Media Server is ready to use!"
echo ""
echo "📁 Directory Structure Created:"
echo "  ├── media/ (for your media files)"
echo "  ├── downloads/ (for temporary downloads)"
echo "  └── logs/media-server/ (for logs)"
echo ""
echo "🚀 Quick Start Commands:"
echo "  ./manage-media-server.sh start    # Start all services"
echo "  ./manage-media-server.sh stop     # Stop all services"
echo "  ./manage-media-server.sh status   # Check service status"
echo ""
echo "🌐 Access Your Media Servers:"
echo "  • Jellyfin: http://localhost:8096"
echo "  • Plex: http://localhost:32400/web"
echo "  • Transmission: http://localhost:9091"
echo "  • Sonarr: http://localhost:8989"
echo "  • Radarr: http://localhost:7878"
echo ""
echo "📖 Documentation:"
echo "  • MEDIA_SERVER_GUIDE.md - Complete setup guide"
echo "  • media-server-dashboard.html - Web dashboard"
echo ""
print_warning "⚠️  Important: Change default passwords in .env.media file!"
echo ""
print_status "Ready to start? Run: ./manage-media-server.sh start"
