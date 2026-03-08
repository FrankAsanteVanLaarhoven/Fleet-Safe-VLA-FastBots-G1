# Universal Crawler System

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
