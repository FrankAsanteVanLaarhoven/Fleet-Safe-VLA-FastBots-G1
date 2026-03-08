#!/usr/bin/env python3
"""
Project Cleanup and Consolidation Script
========================================

This script cleans up and consolidates the existing project structure
to work with the new universal crawler system.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse

class ProjectCleanup:
    """Handles project cleanup and consolidation."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_old_structure"
        
    def create_backup(self) -> bool:
        """Create a backup of the current project structure."""
        print("📦 Creating backup of current project structure...")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup existing crawler directories
            directories_to_backup = [
                "my-crawler-py",
                "crawl-frontend/src/backend",
                "crawl-frontend/src/lib/crawler-service.ts"
            ]
            
            for dir_path in directories_to_backup:
                source = self.project_root / dir_path
                if source.exists():
                    dest = self.backup_dir / dir_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if source.is_file():
                        shutil.copy2(source, dest)
                    else:
                        shutil.copytree(source, dest, dirs_exist_ok=True)
                    print(f"✓ Backed up: {dir_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            return False
    
    def consolidate_crawler_structure(self) -> bool:
        """Consolidate the crawler structure into a unified system."""
        print("🔄 Consolidating crawler structure...")
        
        try:
            # Create new unified structure
            unified_dir = self.project_root / "universal_crawler"
            unified_dir.mkdir(exist_ok=True)
            
            # Copy core files to unified directory
            core_files = [
                "universal_crawler_system.py",
                "universal_crawler_api.py",
                "config.py",
                "requirements.txt",
                "setup.py",
                "test_universal_crawler.py"
            ]
            
            for file_name in core_files:
                source = self.project_root / file_name
                if source.exists():
                    dest = unified_dir / file_name
                    shutil.copy2(source, dest)
                    print(f"✓ Moved: {file_name}")
            
            # Create unified README
            self._create_unified_readme(unified_dir)
            
            # Create unified package structure
            package_dir = unified_dir / "universal_crawler"
            package_dir.mkdir(exist_ok=True)
            
            # Create __init__.py
            init_content = '''"""
Universal Crawler Package
========================

A comprehensive web crawling system designed to handle any website.
"""

from .crawler import UniversalCrawler, CrawlRequest, CrawlMode, CrawlResult
from .config import Config, get_config

__version__ = "1.0.0"
__author__ = "Universal Crawler Team"

__all__ = [
    "UniversalCrawler",
    "CrawlRequest", 
    "CrawlMode",
    "CrawlResult",
    "Config",
    "get_config"
]
'''
            
            with open(package_dir / "__init__.py", "w") as f:
                f.write(init_content)
            
            # Move core files to package
            shutil.move(unified_dir / "universal_crawler_system.py", 
                       package_dir / "crawler.py")
            shutil.move(unified_dir / "config.py", package_dir / "config.py")
            
            return True
            
        except Exception as e:
            print(f"✗ Consolidation failed: {e}")
            return False
    
    def _create_unified_readme(self, unified_dir: Path):
        """Create a unified README for the consolidated project."""
        readme_content = """# Universal Crawler System

A comprehensive web crawling system designed to handle any website regardless of:
- Anti-bot protection and resilience
- Dynamic content and JavaScript rendering
- Complex security setups
- Rate limiting and IP blocking
- CAPTCHA challenges

## Project Structure

```
universal_crawler/
├── universal_crawler/          # Main package
│   ├── __init__.py
│   ├── crawler.py             # Core crawler system
│   ├── config.py              # Configuration system
│   └── api.py                 # API server
├── tests/                     # Test suite
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── requirements.txt           # Dependencies
├── setup.py                   # Setup script
└── README.md                  # This file
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run setup**:
   ```bash
   python setup.py
   ```

3. **Start the API server**:
   ```bash
   python universal_crawler_api.py
   ```

4. **Access the API**:
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Features

- **Universal Compatibility**: Crawl any website regardless of its resilience
- **Multiple Crawling Modes**: Basic, Enhanced, Full Site, Deep, Stealth, Enterprise
- **Advanced Extraction**: Images, links, forms, scripts, styles, metadata
- **Compliance Ready**: GDPR, CCPA, robots.txt compliance
- **Real-time Monitoring**: WebSocket updates and comprehensive logging
- **Export Options**: JSON, CSV, ZIP, and custom formats
- **API-First Design**: RESTful API with comprehensive endpoints

## Integration with Frontend

The universal crawler system is designed to integrate seamlessly with the existing frontend:

- **API Compatibility**: Maintains compatibility with existing frontend API calls
- **WebSocket Support**: Real-time updates for the frontend
- **Export Formats**: Supports all existing export formats
- **Configuration**: Environment-based configuration for different deployments

## Migration from Old System

The old crawler system has been backed up to `backup_old_structure/`. The new system provides:

- **Enhanced Capabilities**: More robust crawling with better error handling
- **Better Performance**: Optimized for speed and resource usage
- **Improved Monitoring**: Comprehensive logging and metrics
- **Extensible Architecture**: Easy to extend with new features

## Development

### Running Tests

```bash
python test_universal_crawler.py
```

### Code Quality

```bash
black .
isort .
flake8 .
mypy .
```

## License

This project is licensed under the MIT License.
"""
        
        with open(unified_dir / "README.md", "w") as f:
            f.write(readme_content)
    
    def update_frontend_integration(self) -> bool:
        """Update frontend to work with the new universal crawler."""
        print("🎨 Updating frontend integration...")
        
        try:
            # Update the crawler service to use the new API
            crawler_service_path = self.project_root / "crawl-frontend/src/lib/crawler-service.ts"
            
            if crawler_service_path.exists():
                # Backup the original
                backup_path = self.backup_dir / "crawl-frontend/src/lib/crawler-service.ts"
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(crawler_service_path, backup_path)
                
                # Update the service to use the new universal crawler API
                new_service_content = '''// Universal Crawler Service
// ============================

// Types for universal crawler functionality
export interface CrawlRequest {
  url: string
  mode: 'basic' | 'enhanced' | 'full_site' | 'deep' | 'stealth' | 'enterprise'
  max_depth?: number
  max_pages?: number
  delay?: number
  timeout?: number
  user_agent?: string
  headers?: Record<string, string>
  cookies?: Record<string, string>
  proxy?: string
  extract_images?: boolean
  extract_links?: boolean
  extract_forms?: boolean
  extract_scripts?: boolean
  extract_styles?: boolean
  extract_meta?: boolean
  ocr_enabled?: boolean
  ast_analysis?: boolean
  network_analysis?: boolean
  compliance_mode?: boolean
  stealth_mode?: boolean
  custom_js?: string
  wait_for_selectors?: string[]
  screenshot?: boolean
  pdf_export?: boolean
}

export interface CrawlResult {
  id: string
  url: string
  status: 'running' | 'completed' | 'failed' | 'stopped'
  start_time: string
  end_time?: string
  total_pages: number
  successful_pages: number
  failed_pages: number
  total_size: number
  error?: string
  metadata?: Record<string, any>
}

export interface CrawlStats {
  total_crawls: number
  active_crawls: number
  completed_crawls: number
  failed_crawls: number
  total_pages_crawled: number
  total_size_crawled: number
  average_crawl_time: number
}

export interface CrawlHistory {
  id: string
  url: string
  status: string
  start_time: string
  end_time?: string
  total_pages: number
  successful_pages: number
  failed_pages: number
}

// API base URL - points to the universal crawler API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class UniversalCrawlerService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health')
  }

  // Start a new crawl
  async startCrawl(request: CrawlRequest): Promise<CrawlResult> {
    return this.request('/crawl', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // Get crawl status
  async getCrawlStatus(crawlId: string): Promise<CrawlResult> {
    return this.request(`/status/${crawlId}`)
  }

  // Get crawl results
  async getCrawlResults(crawlId: string): Promise<any> {
    return this.request(`/results/${crawlId}`)
  }

  // Get crawl statistics
  async getCrawlStats(): Promise<CrawlStats> {
    return this.request('/stats')
  }

  // Get crawl history
  async getCrawlHistory(): Promise<CrawlHistory[]> {
    return this.request('/crawls')
  }

  // Stop a crawl
  async stopCrawl(crawlId: string): Promise<{ status: string }> {
    return this.request(`/stop/${crawlId}`, {
      method: 'POST',
    })
  }

  // Delete a crawl
  async deleteCrawl(crawlId: string): Promise<{ status: string }> {
    return this.request(`/crawl/${crawlId}`, {
      method: 'DELETE',
    })
  }

  // Export crawl data
  async exportCrawlData(crawlId: string, format: 'json' | 'zip'): Promise<any> {
    return this.request(`/export/${crawlId}/${format}`)
  }

  // Get available crawling modes
  async getAvailableModes(): Promise<any> {
    return this.request('/modes')
  }

  // Poll crawl status (for real-time updates)
  async pollCrawlStatus(crawlId: string, onUpdate?: (result: CrawlResult) => void): Promise<void> {
    const poll = async () => {
      try {
        const result = await this.getCrawlStatus(crawlId)
        onUpdate?.(result)
        
        if (result.status === 'running') {
          setTimeout(poll, 2000) // Poll every 2 seconds
        }
      } catch (error) {
        console.error('Error polling crawl status:', error)
      }
    }
    
    poll()
  }

  // WebSocket connection for real-time updates
  connectWebSocket(onMessage?: (data: any) => void): WebSocket | null {
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws`)
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage?.(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      return ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      return null
    }
  }
}

// Export singleton instance
export const crawlerService = new UniversalCrawlerService()

// Utility functions
export const formatCrawlTime = (startTime: string, endTime?: string): string => {
  const start = new Date(startTime)
  const end = endTime ? new Date(endTime) : new Date()
  const duration = end.getTime() - start.getTime()
  
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}

export const getCrawlProgress = (result: CrawlResult): number => {
  if (result.total_pages === 0) return 0
  return Math.round((result.successful_pages + result.failed_pages) / result.total_pages * 100)
}

export const getCrawlStatusColor = (status: string): string => {
  switch (status) {
    case 'running':
      return 'text-blue-500'
    case 'completed':
      return 'text-green-500'
    case 'failed':
      return 'text-red-500'
    case 'stopped':
      return 'text-yellow-500'
    default:
      return 'text-gray-500'
  }
}
'''
                
                with open(crawler_service_path, "w") as f:
                    f.write(new_service_content)
                
                print("✓ Updated crawler service")
            
            return True
            
        except Exception as e:
            print(f"✗ Frontend integration update failed: {e}")
            return False
    
    def create_migration_guide(self) -> bool:
        """Create a migration guide for users."""
        print("📖 Creating migration guide...")
        
        migration_content = """# Migration Guide: Universal Crawler System

## Overview

This guide helps you migrate from the old crawler system to the new Universal Crawler System.

## What's Changed

### 1. Architecture
- **Old**: Multiple separate crawler implementations
- **New**: Unified, extensible crawler system

### 2. API Endpoints
- **Old**: Various endpoints across different services
- **New**: Unified REST API with comprehensive endpoints

### 3. Configuration
- **Old**: Scattered configuration files
- **New**: Centralized configuration system with environment support

### 4. Capabilities
- **Old**: Limited crawling modes
- **New**: 6 different crawling modes with advanced features

## Migration Steps

### 1. Backup Your Data
The old system has been automatically backed up to `backup_old_structure/`.

### 2. Install the New System
```bash
# Run the setup script
python setup.py

# Or install manually
pip install -r requirements.txt
```

### 3. Update Configuration
The new system uses a different configuration format:

**Old**: Multiple config files
**New**: Single `config.json` file with environment variable support

### 4. Update API Calls
The API endpoints have changed:

| Old Endpoint | New Endpoint | Notes |
|--------------|--------------|-------|
| `/api/crawler/start` | `/crawl` | POST request |
| `/api/crawler/status/{id}` | `/status/{id}` | GET request |
| `/api/crawler/results/{id}` | `/results/{id}` | GET request |
| `/api/crawler/stats` | `/stats` | GET request |

### 5. Update Frontend
The frontend has been automatically updated to work with the new API.

## New Features

### Crawling Modes
1. **Basic**: Simple HTML extraction
2. **Enhanced**: OCR, AST, Network analysis
3. **Full Site**: Complete source extraction
4. **Deep**: Multi-level crawling
5. **Stealth**: Anti-detection mode
6. **Enterprise**: Full compliance and audit

### Advanced Capabilities
- Real-time WebSocket updates
- Comprehensive export options (JSON, ZIP)
- Better error handling and retry logic
- Compliance features (GDPR, CCPA)
- Performance monitoring and metrics

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if the universal crawler API is running on port 8000
   - Verify the API_BASE_URL in your frontend configuration

2. **Configuration Errors**
   - Run `python config.py` to create a default configuration
   - Check the configuration validation in the logs

3. **Permission Errors**
   - Ensure the crawler has write permissions to the data directories
   - Check file system permissions

### Getting Help

- Check the logs in the `logs/` directory
- Review the API documentation at `http://localhost:8000/docs`
- Create an issue on the project repository

## Rollback

If you need to rollback to the old system:

1. Stop the new universal crawler
2. Restore from `backup_old_structure/`
3. Restart the old services

## Support

For migration support:
- Review this guide thoroughly
- Check the API documentation
- Create an issue with specific error details
"""
        
        migration_path = self.project_root / "MIGRATION_GUIDE.md"
        with open(migration_path, "w") as f:
            f.write(migration_content)
        
        print("✓ Created migration guide")
        return True
    
    def cleanup_old_files(self) -> bool:
        """Clean up old files that are no longer needed."""
        print("🧹 Cleaning up old files...")
        
        try:
            # Files to remove (after backup)
            files_to_remove = [
                "my-crawler-py",
                "crawl-frontend/src/backend",
                "start_all.sh",
                "start_backend.sh", 
                "start_frontend.sh",
                "start_python.sh",
                "start_security.sh",
                "stop_all.sh",
                "stop_security.sh",
                "status.sh"
            ]
            
            for file_path in files_to_remove:
                full_path = self.project_root / file_path
                if full_path.exists():
                    if full_path.is_file():
                        full_path.unlink()
                    else:
                        shutil.rmtree(full_path)
                    print(f"✓ Removed: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Cleanup failed: {e}")
            return False
    
    def create_new_startup_scripts(self) -> bool:
        """Create new startup scripts for the consolidated system."""
        print("🚀 Creating new startup scripts...")
        
        try:
            # Main startup script
            main_startup = """#!/bin/bash
# Universal Crawler System Startup Script
# ======================================

echo "Starting Universal Crawler System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if universal crawler is installed
if [ ! -f "universal_crawler/universal_crawler/__init__.py" ]; then
    echo "Universal crawler not found. Running setup..."
    python setup.py
fi

# Start the universal crawler API
echo "Starting Universal Crawler API..."
python universal_crawler_api.py
"""
            
            with open(self.project_root / "start_universal_crawler.sh", "w") as f:
                f.write(main_startup)
            
            os.chmod(self.project_root / "start_universal_crawler.sh", 0o755)
            
            # Frontend startup script
            frontend_startup = """#!/bin/bash
# Frontend Startup Script
# =======================

echo "Starting Frontend..."

cd crawl-frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start the development server
echo "Starting Next.js development server..."
npm run dev
"""
            
            with open(self.project_root / "start_frontend.sh", "w") as f:
                f.write(frontend_startup)
            
            os.chmod(self.project_root / "start_frontend.sh", 0o755)
            
            # Combined startup script
            combined_startup = """#!/bin/bash
# Combined Startup Script
# =======================

echo "Starting Universal Crawler System with Frontend..."

# Start the universal crawler API in the background
echo "Starting Universal Crawler API..."
python universal_crawler_api.py &
CRAWLER_PID=$!

# Wait a moment for the API to start
sleep 3

# Start the frontend
echo "Starting Frontend..."
cd crawl-frontend
npm run dev &
FRONTEND_PID=$!

echo "Universal Crawler System started!"
echo "API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping services...'; kill $CRAWLER_PID $FRONTEND_PID; exit" INT
wait
"""
            
            with open(self.project_root / "start_all.sh", "w") as f:
                f.write(combined_startup)
            
            os.chmod(self.project_root / "start_all.sh", 0o755)
            
            print("✓ Created new startup scripts")
            return True
            
        except Exception as e:
            print(f"✗ Startup script creation failed: {e}")
            return False
    
    def run_cleanup(self, skip_backup: bool = False) -> bool:
        """Run the complete cleanup and consolidation process."""
        print("🔄 Starting project cleanup and consolidation...")
        
        success = True
        
        # Create backup
        if not skip_backup:
            if not self.create_backup():
                print("⚠️  Backup failed, but continuing...")
        
        # Consolidate structure
        if not self.consolidate_crawler_structure():
            success = False
        
        # Update frontend integration
        if not self.update_frontend_integration():
            success = False
        
        # Create migration guide
        if not self.create_migration_guide():
            success = False
        
        # Create new startup scripts
        if not self.create_new_startup_scripts():
            success = False
        
        # Clean up old files (only if everything else succeeded)
        if success:
            if not self.cleanup_old_files():
                print("⚠️  Cleanup failed, but consolidation completed")
        
        return success

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Project Cleanup and Consolidation")
    parser.add_argument("--skip-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    cleanup = ProjectCleanup(args.project_root)
    
    if cleanup.run_cleanup(skip_backup=args.skip_backup):
        print("\n🎉 Cleanup and consolidation completed successfully!")
        print("\nNext steps:")
        print("1. Review the migration guide: MIGRATION_GUIDE.md")
        print("2. Start the universal crawler: ./start_universal_crawler.sh")
        print("3. Start the frontend: ./start_frontend.sh")
        print("4. Or start both: ./start_all.sh")
        print("5. Access the API: http://localhost:8000/docs")
        print("6. Access the frontend: http://localhost:3000")
    else:
        print("\n❌ Cleanup and consolidation failed!")
        print("Check the error messages above and try again.")

if __name__ == "__main__":
    main() 