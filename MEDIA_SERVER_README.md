# 🎬 DataMinerAI Media Server

A comprehensive media server solution for streaming your personal media library. This setup provides both a simple Python-based server and a full Docker-based ecosystem with advanced media management tools.

## 🚀 Quick Start

### Option 1: Simple Python Server (Recommended for beginners)

```bash
# Start the simple media server
./start-media-server.sh python

# Or use the interactive menu
./start-media-server.sh
```

**Features:**
- ✅ No Docker required
- ✅ Lightweight and fast
- ✅ Web-based interface
- ✅ Video streaming with range requests
- ✅ Support for videos, audio, and images
- ✅ Real-time media scanning

**Access:** http://localhost:8080

### Option 2: Full Docker Ecosystem (Advanced)

```bash
# Start the full Docker-based media server
./start-media-server.sh docker
```

**Features:**
- 🎬 **Jellyfin** - Open source media server
- 🎬 **Plex** - Feature-rich media server
- 📺 **Sonarr** - TV show management
- 🎥 **Radarr** - Movie management
- 🎵 **Lidarr** - Music management
- 📝 **Bazarr** - Subtitle management
- 📊 **Tautulli** - Statistics and monitoring
- ⬇️ **Transmission** - BitTorrent client

## 📁 Directory Structure

```
dataminerAI/
├── media/                    # Your media files
│   ├── movies/              # Movie files
│   ├── tv/                  # TV show files
│   ├── music/               # Music files
│   └── photos/              # Photo files
├── downloads/               # Temporary downloads
├── simple-media-server.py   # Python media server
├── media-server-docker-compose.yml  # Docker setup
├── start-media-server.sh    # Startup script
├── manage-media-server.sh   # Docker management
└── MEDIA_SERVER_GUIDE.md    # Detailed documentation
```

## 🎯 Supported Media Formats

### Video Formats
- MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V

### Audio Formats
- MP3, WAV, FLAC, AAC, OGG, M4A, WMA

### Image Formats
- JPG, JPEG, PNG, GIF, BMP, WebP

## 🛠️ Installation & Setup

### Prerequisites

#### For Simple Python Server:
- Python 3.6 or higher
- No additional dependencies required

#### For Docker Setup:
- Docker Desktop
- docker-compose

### Setup Steps

1. **Clone or navigate to your DataMinerAI directory**
   ```bash
   cd /path/to/dataminerAI
   ```

2. **Create media directories**
   ```bash
   mkdir -p media/{movies,tv,music,photos}
   mkdir -p downloads
   ```

3. **Start the media server**
   ```bash
   ./start-media-server.sh
   ```

4. **Add your media files**
   - Copy your media files to the appropriate directories
   - The server will automatically scan and index them

## 🌐 Accessing Your Media Server

### Simple Python Server
- **Web Interface:** http://localhost:8080
- **API Endpoint:** http://localhost:8080/api/media

### Docker Services
- **Jellyfin:** http://localhost:8096
- **Plex:** http://localhost:32400/web
- **Transmission:** http://localhost:9091
- **Sonarr:** http://localhost:8989
- **Radarr:** http://localhost:7878
- **Lidarr:** http://localhost:8686
- **Bazarr:** http://localhost:6767
- **Tautulli:** http://localhost:8181

## 📖 Management Commands

### Simple Python Server
```bash
# Start server
python3 simple-media-server.py

# Start with custom options
python3 simple-media-server.py --host 0.0.0.0 --port 9000 --media-root ./my-media
```

### Docker Services
```bash
# Check service status
./manage-media-server.sh status

# View logs
./manage-media-server.sh logs

# Stop services
./manage-media-server.sh stop

# Restart services
./manage-media-server.sh restart

# Update containers
./manage-media-server.sh update
```

## 🔧 Configuration

### Environment Variables
Create a `.env.media` file for Docker services:

```bash
# Media Server Environment Variables
PUID=1000
PGID=1000
TZ=UTC

# Transmission Settings
TRANSMISSION_USER=admin
TRANSMISSION_PASS=your_secure_password

# Plex Settings (Optional)
PLEX_CLAIM=your_plex_claim_token

# Jellyfin Settings
JELLYFIN_PublishedServerUrl=http://localhost:8096
JELLYFIN_EnableRemoteAccess=true
```

### Custom Ports
Edit `media-server-docker-compose.yml` to change ports:

```yaml
services:
  jellyfin:
    ports:
      - "8096:8096"  # Change 8096 to your preferred port
```

## 🎨 Features

### Simple Python Server
- **Modern Web Interface** - Beautiful, responsive design
- **Media Streaming** - HTTP range requests for video streaming
- **File Browser** - Browse and organize your media
- **Statistics** - View media library statistics
- **Real-time Scanning** - Automatic media detection
- **Cross-platform** - Works on Windows, macOS, and Linux

### Docker Ecosystem
- **Jellyfin** - Completely free, open-source media server
- **Plex** - Feature-rich with premium capabilities
- **Sonarr** - Automatic TV show downloading and management
- **Radarr** - Automatic movie downloading and management
- **Lidarr** - Automatic music downloading and management
- **Bazarr** - Automatic subtitle downloading
- **Transmission** - BitTorrent client for downloads
- **Tautulli** - Media usage statistics and monitoring

## 🔒 Security Considerations

1. **Change Default Passwords**
   - Update passwords in `.env.media`
   - Use strong, unique passwords

2. **Network Security**
   - Only expose necessary ports
   - Use HTTPS in production
   - Consider VPN access for remote streaming

3. **File Permissions**
   - Ensure proper file permissions
   - Use dedicated user accounts

## 🐛 Troubleshooting

### Common Issues

#### Python Server Issues
```bash
# Check if Python is installed
python3 --version

# Check if port is in use
lsof -i :8080

# Check file permissions
ls -la media/
```

#### Docker Issues
```bash
# Check Docker status
docker info

# Check container logs
docker-compose -f media-server-docker-compose.yml logs

# Restart containers
docker-compose -f media-server-docker-compose.yml restart
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R 1000:1000 media downloads
chmod -R 755 media downloads
```

#### Port Conflicts
```bash
# Check what's using a port
lsof -i :8096

# Change ports in docker-compose.yml
```

### Getting Help

1. **Check the logs:**
   ```bash
   ./manage-media-server.sh logs
   ```

2. **Verify configuration:**
   ```bash
   ./manage-media-server.sh status
   ```

3. **Restart services:**
   ```bash
   ./manage-media-server.sh restart
   ```

## 📚 Additional Resources

### Documentation
- [MEDIA_SERVER_GUIDE.md](MEDIA_SERVER_GUIDE.md) - Detailed setup guide
- [media-server-dashboard.html](media-server-dashboard.html) - Web dashboard

### Official Documentation
- [Jellyfin Documentation](https://jellyfin.org/docs/)
- [Plex Documentation](https://support.plex.tv/)
- [Sonarr Documentation](https://wiki.servarr.com/sonarr)
- [Radarr Documentation](https://wiki.servarr.com/radarr)

### Community Support
- [Jellyfin Forums](https://forum.jellyfin.org/)
- [Plex Forums](https://forums.plex.tv/)
- [Reddit r/selfhosted](https://reddit.com/r/selfhosted)

## 🤝 Contributing

This media server setup is part of the DataMinerAI project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Jellyfin](https://jellyfin.org/) - Open source media server
- [Plex](https://www.plex.tv/) - Media server platform
- [Sonarr](https://sonarr.tv/) - TV show management
- [Radarr](https://radarr.video/) - Movie management
- [Lidarr](https://lidarr.audio/) - Music management
- [Bazarr](https://www.bazarr.media/) - Subtitle management

---

**🎬 Enjoy your personal media server!**

For support or questions, please refer to the documentation or create an issue in the repository.
