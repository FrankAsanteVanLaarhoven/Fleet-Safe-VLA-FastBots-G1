# Migration Guide: Universal Crawler System

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
