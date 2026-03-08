#!/usr/bin/env python3
"""
DataMinerAI Simple Media Server
A lightweight Python-based media server for streaming your personal media files.
"""

import os
import sys
import json
import mimetypes
import argparse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote
import threading
import webbrowser
import time
from datetime import datetime

class MediaServerHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for media streaming."""
    
    def __init__(self, *args, media_root=None, **kwargs):
        self.media_root = media_root or "./media"
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests for media files."""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = unquote(parsed_url.path)
            
            # Handle root path - show media browser
            if path == "/" or path == "":
                self.send_media_browser()
                return
            
            # Handle API requests
            if path.startswith("/api/"):
                self.handle_api_request(path)
                return
            
            # Handle static files (CSS, JS, etc.)
            if path.startswith("/static/"):
                self.serve_static_file(path)
                return
            
            # Handle media files
            self.serve_media_file(path)
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def send_media_browser(self):
        """Send the main media browser HTML page."""
        html_content = self.get_media_browser_html()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content)))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_api_request(self, path):
        """Handle API requests for media information."""
        if path == "/api/media":
            self.send_media_list()
        elif path.startswith("/api/media/"):
            media_id = path.split("/")[-1]
            self.send_media_info(media_id)
        else:
            self.send_error(404, "API endpoint not found")
    
    def send_media_list(self):
        """Send JSON list of available media."""
        media_list = self.scan_media_directory()
        response = {
            "status": "success",
            "data": media_list,
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def send_media_info(self, media_id):
        """Send information about a specific media file."""
        media_path = os.path.join(self.media_root, media_id)
        if not os.path.exists(media_path):
            self.send_error(404, "Media file not found")
            return
        
        file_info = self.get_file_info(media_path)
        response = {
            "status": "success",
            "data": file_info,
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def serve_media_file(self, path):
        """Serve a media file with proper headers."""
        # Remove leading slash and decode URL
        file_path = unquote(path.lstrip('/'))
        full_path = os.path.join(self.media_root, file_path)
        
        if not os.path.exists(full_path):
            self.send_error(404, "File not found")
            return
        
        if not os.path.isfile(full_path):
            self.send_error(400, "Not a file")
            return
        
        # Get file info
        file_size = os.path.getsize(full_path)
        mime_type, _ = mimetypes.guess_type(full_path)
        
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Handle range requests for video streaming
        range_header = self.headers.get('Range')
        if range_header and mime_type.startswith('video/'):
            self.handle_range_request(full_path, mime_type, file_size, range_header)
        else:
            self.serve_full_file(full_path, mime_type, file_size)
    
    def handle_range_request(self, file_path, mime_type, file_size, range_header):
        """Handle HTTP range requests for video streaming."""
        try:
            # Parse range header
            range_str = range_header.replace('bytes=', '')
            start, end = range_str.split('-')
            start = int(start) if start else 0
            end = int(end) if end else file_size - 1
            
            # Calculate content length
            content_length = end - start + 1
            
            # Read file chunk
            with open(file_path, 'rb') as f:
                f.seek(start)
                data = f.read(content_length)
            
            # Send response
            self.send_response(206)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(content_length))
            self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            self.wfile.write(data)
            
        except Exception as e:
            self.send_error(500, f"Error handling range request: {str(e)}")
    
    def serve_full_file(self, file_path, mime_type, file_size):
        """Serve a complete file."""
        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Length', str(file_size))
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                
                # Stream the file in chunks
                chunk_size = 8192
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def serve_static_file(self, path):
        """Serve static files (CSS, JS, etc.)."""
        static_dir = "./static"
        file_path = os.path.join(static_dir, path.replace("/static/", ""))
        
        if not os.path.exists(file_path):
            self.send_error(404, "Static file not found")
            return
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        with open(file_path, 'rb') as f:
            data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    
    def scan_media_directory(self):
        """Scan the media directory and return file information."""
        media_list = []
        media_root = Path(self.media_root)
        
        if not media_root.exists():
            return media_list
        
        # Supported media extensions
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(media_root))
                file_ext = file_path.suffix.lower()
                
                # Determine media type
                media_type = "unknown"
                if file_ext in video_extensions:
                    media_type = "video"
                elif file_ext in audio_extensions:
                    media_type = "audio"
                elif file_ext in image_extensions:
                    media_type = "image"
                
                file_info = {
                    "id": relative_path,
                    "name": file_path.name,
                    "path": relative_path,
                    "type": media_type,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "mime_type": mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
                }
                
                media_list.append(file_info)
        
        # Sort by name
        media_list.sort(key=lambda x: x['name'].lower())
        return media_list
    
    def get_file_info(self, file_path):
        """Get detailed information about a file."""
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        file_info = {
            "name": file_path.name,
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "mime_type": mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        }
        
        return file_info
    
    def get_media_browser_html(self):
        """Generate the main media browser HTML page."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataMinerAI Media Server</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .controls {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }}
        
        .controls h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        
        .control-buttons {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .btn {{
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
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .media-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .media-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .media-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .media-card h3 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1rem;
            word-break: break-word;
        }}
        
        .media-info {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }}
        
        .media-type {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .type-video {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .type-audio {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .type-image {{
            background: #e8f5e8;
            color: #388e3c;
        }}
        
        .loading {{
            text-align: center;
            color: white;
            font-size: 1.2rem;
            padding: 40px;
        }}
        
        .error {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            color: #d32f2f;
            text-align: center;
        }}
        
        .stats {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }}
        
        .stats h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 DataMinerAI Media Server</h1>
            <p>Stream your personal media library</p>
        </div>
        
        <div class="controls">
            <h2>🚀 Controls</h2>
            <div class="control-buttons">
                <button class="btn" onclick="refreshMedia()">Refresh Media</button>
                <button class="btn" onclick="openMediaDirectory()">Open Media Folder</button>
                <button class="btn" onclick="showStats()">Show Statistics</button>
            </div>
        </div>
        
        <div id="stats" class="stats" style="display: none;">
            <h2>📊 Media Statistics</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number" id="total-files">0</div>
                    <div class="stat-label">Total Files</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="total-size">0 MB</div>
                    <div class="stat-label">Total Size</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="video-count">0</div>
                    <div class="stat-label">Videos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="audio-count">0</div>
                    <div class="stat-label">Audio Files</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="image-count">0</div>
                    <div class="stat-label">Images</div>
                </div>
            </div>
        </div>
        
        <div id="loading" class="loading">
            Loading media files...
        </div>
        
        <div id="error" class="error" style="display: none;">
            Error loading media files. Please check the server logs.
        </div>
        
        <div id="media-grid" class="media-grid" style="display: none;">
            <!-- Media cards will be populated here -->
        </div>
    </div>
    
    <script>
        let mediaData = [];
        
        // Load media on page load
        document.addEventListener('DOMContentLoaded', function() {{
            loadMedia();
        }});
        
        async function loadMedia() {{
            try {{
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                document.getElementById('media-grid').style.display = 'none';
                
                const response = await fetch('/api/media');
                const data = await response.json();
                
                if (data.status === 'success') {{
                    mediaData = data.data;
                    displayMedia(mediaData);
                    updateStats(mediaData);
                }} else {{
                    throw new Error('Failed to load media');
                }}
            }} catch (error) {{
                console.error('Error loading media:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
            }}
        }}
        
        function displayMedia(mediaList) {{
            const grid = document.getElementById('media-grid');
            grid.innerHTML = '';
            
            if (mediaList.length === 0) {{
                grid.innerHTML = '<div class="error">No media files found. Please add files to the media directory.</div>';
                grid.style.display = 'block';
                document.getElementById('loading').style.display = 'none';
                return;
            }}
            
            mediaList.forEach(media => {{
                const card = createMediaCard(media);
                grid.appendChild(card);
            }});
            
            grid.style.display = 'grid';
            document.getElementById('loading').style.display = 'none';
        }}
        
        function createMediaCard(media) {{
            const card = document.createElement('div');
            card.className = 'media-card';
            
            const size = formatFileSize(media.size);
            const typeClass = `type-${{media.type}}`;
            
            card.innerHTML = `
                <h3>${{media.name}}</h3>
                <div class="media-info">
                    <span class="media-type ${{typeClass}}">${{media.type}}</span>
                    <br>
                    Size: ${{size}}<br>
                    Modified: ${{new Date(media.modified).toLocaleDateString()}}
                </div>
                <button class="btn" onclick="playMedia('${{media.path}}')">Play/View</button>
            `;
            
            return card;
        }}
        
        function formatFileSize(bytes) {{
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }}
        
        function playMedia(path) {{
            window.open(`/${{path}}`, '_blank');
        }}
        
        function refreshMedia() {{
            loadMedia();
        }}
        
        function openMediaDirectory() {{
            alert('Please open the media directory manually: ./media');
        }}
        
        function showStats() {{
            const stats = document.getElementById('stats');
            stats.style.display = stats.style.display === 'none' ? 'block' : 'none';
        }}
        
        function updateStats(mediaList) {{
            const totalFiles = mediaList.length;
            const totalSize = mediaList.reduce((sum, media) => sum + media.size, 0);
            const videoCount = mediaList.filter(media => media.type === 'video').length;
            const audioCount = mediaList.filter(media => media.type === 'audio').length;
            const imageCount = mediaList.filter(media => media.type === 'image').length;
            
            document.getElementById('total-files').textContent = totalFiles;
            document.getElementById('total-size').textContent = formatFileSize(totalSize);
            document.getElementById('video-count').textContent = videoCount;
            document.getElementById('audio-count').textContent = audioCount;
            document.getElementById('image-count').textContent = imageCount;
        }}
    </script>
</body>
</html>
"""

class MediaServer:
    """Main media server class."""
    
    def __init__(self, host='localhost', port=8080, media_root='./media'):
        self.host = host
        self.port = port
        self.media_root = media_root
        self.server = None
        
    def start(self):
        """Start the media server."""
        # Create media directory if it doesn't exist
        os.makedirs(self.media_root, exist_ok=True)
        
        # Create static directory for CSS/JS files
        os.makedirs('./static', exist_ok=True)
        
        # Create custom handler class with media root
        handler_class = type('MediaHandler', (MediaServerHandler,), {
            'media_root': self.media_root
        })
        
        try:
            self.server = HTTPServer((self.host, self.port), handler_class)
            print(f"🎬 DataMinerAI Media Server starting...")
            print(f"📍 Server: http://{self.host}:{self.port}")
            print(f"📁 Media Directory: {os.path.abspath(self.media_root)}")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔄 Press Ctrl+C to stop the server")
            print()
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                webbrowser.open(f"http://{self.host}:{self.port}")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Start the server
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
        finally:
            if self.server:
                self.server.server_close()
    
    def stop(self):
        """Stop the media server."""
        if self.server:
            self.server.shutdown()

def main():
    """Main function to run the media server."""
    parser = argparse.ArgumentParser(description='DataMinerAI Simple Media Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--media-root', default='./media', help='Media directory path (default: ./media)')
    
    args = parser.parse_args()
    
    # Create and start the server
    server = MediaServer(args.host, args.port, args.media_root)
    server.start()

if __name__ == '__main__':
    main()
