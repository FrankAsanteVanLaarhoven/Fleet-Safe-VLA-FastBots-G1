#!/usr/bin/env python3
"""
Universal Crawler Configuration
==============================

Comprehensive configuration system for the universal crawler.
Supports environment variables, configuration files, and runtime settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///crawler.db"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class StorageConfig:
    """Storage configuration."""
    base_path: str = "crawl_data"
    max_size_gb: int = 100
    compression_enabled: bool = True
    retention_days: int = 30
    backup_enabled: bool = True
    backup_path: str = "backups"

@dataclass
class NetworkConfig:
    """Network configuration."""
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 10
    rate_limit_requests_per_minute: int = 60
    user_agent_rotation: bool = True
    proxy_enabled: bool = False
    proxy_list: List[str] = None

@dataclass
class SecurityConfig:
    """Security configuration."""
    ssl_verify: bool = True
    allow_self_signed: bool = False
    certificate_path: Optional[str] = None
    key_path: Optional[str] = None
    encryption_enabled: bool = False
    encryption_key: Optional[str] = None

@dataclass
class ComplianceConfig:
    """Compliance and privacy configuration."""
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    respect_robots_txt: bool = True
    respect_rate_limits: bool = True
    data_retention_days: int = 30
    anonymize_data: bool = True
    audit_logging: bool = True

@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    cors_origins: List[str] = None
    api_key_required: bool = False
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/crawler.log"
    max_file_size_mb: int = 100
    backup_count: int = 5
    console_enabled: bool = True

@dataclass
class CrawlerConfig:
    """Crawler-specific configuration."""
    default_mode: str = "enhanced"
    default_max_depth: int = 3
    default_max_pages: int = 100
    default_delay: float = 1.0
    extract_images: bool = True
    extract_links: bool = True
    extract_forms: bool = True
    extract_scripts: bool = True
    extract_styles: bool = True
    extract_meta: bool = True
    ocr_enabled: bool = False
    ast_analysis: bool = False
    network_analysis: bool = False
    screenshot_enabled: bool = False
    pdf_export_enabled: bool = False

@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    metrics_enabled: bool = True
    prometheus_enabled: bool = False
    health_check_interval: int = 30
    performance_monitoring: bool = True
    alerting_enabled: bool = False
    alert_email: Optional[str] = None

class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.json"
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        
        # Initialize default configurations
        self.database = DatabaseConfig()
        self.storage = StorageConfig()
        self.network = NetworkConfig()
        self.security = SecurityConfig()
        self.compliance = ComplianceConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()
        self.crawler = CrawlerConfig()
        self.monitoring = MonitoringConfig()
        
        # Load configuration
        self.load_config()
        self.load_environment_variables()
        
    def load_config(self):
        """Load configuration from file."""
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def load_environment_variables(self):
        """Load configuration from environment variables."""
        # Database
        if os.getenv("DATABASE_URL"):
            self.database.url = os.getenv("DATABASE_URL")
        
        # Storage
        if os.getenv("STORAGE_PATH"):
            self.storage.base_path = os.getenv("STORAGE_PATH")
        if os.getenv("STORAGE_MAX_SIZE_GB"):
            self.storage.max_size_gb = int(os.getenv("STORAGE_MAX_SIZE_GB"))
        
        # Network
        if os.getenv("NETWORK_TIMEOUT"):
            self.network.timeout = int(os.getenv("NETWORK_TIMEOUT"))
        if os.getenv("NETWORK_MAX_RETRIES"):
            self.network.max_retries = int(os.getenv("NETWORK_MAX_RETRIES"))
        if os.getenv("NETWORK_RATE_LIMIT"):
            self.network.rate_limit_requests_per_minute = int(os.getenv("NETWORK_RATE_LIMIT"))
        
        # API
        if os.getenv("API_HOST"):
            self.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self.api.port = int(os.getenv("API_PORT"))
        if os.getenv("API_WORKERS"):
            self.api.workers = int(os.getenv("API_WORKERS"))
        
        # Security
        if os.getenv("ENCRYPTION_KEY"):
            self.security.encryption_key = os.getenv("ENCRYPTION_KEY")
            self.security.encryption_enabled = True
        
        # Logging
        if os.getenv("LOG_LEVEL"):
            self.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.logging.file_path = os.getenv("LOG_FILE")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary."""
        for section, data in config_data.items():
            if hasattr(self, section) and isinstance(data, dict):
                section_obj = getattr(self, section)
                for key, value in data.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def save_config(self):
        """Save current configuration to file."""
        config_data = {
            "database": asdict(self.database),
            "storage": asdict(self.storage),
            "network": asdict(self.network),
            "security": asdict(self.security),
            "compliance": asdict(self.compliance),
            "api": asdict(self.api),
            "logging": asdict(self.logging),
            "crawler": asdict(self.crawler),
            "monitoring": asdict(self.monitoring)
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_storage_path(self) -> Path:
        """Get the storage base path."""
        return Path(self.storage.base_path)
    
    def get_log_path(self) -> Path:
        """Get the log file path."""
        return Path(self.logging.file_path)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate storage path
        storage_path = self.get_storage_path()
        if not storage_path.parent.exists():
            try:
                storage_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create storage directory: {e}")
        
        # Validate log path
        log_path = self.get_log_path()
        if not log_path.parent.exists():
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create log directory: {e}")
        
        # Validate network settings
        if self.network.timeout <= 0:
            errors.append("Network timeout must be positive")
        if self.network.max_retries < 0:
            errors.append("Max retries cannot be negative")
        if self.network.rate_limit_requests_per_minute <= 0:
            errors.append("Rate limit must be positive")
        
        # Validate API settings
        if self.api.port <= 0 or self.api.port > 65535:
            errors.append("API port must be between 1 and 65535")
        if self.api.workers <= 0:
            errors.append("API workers must be positive")
        
        # Validate storage settings
        if self.storage.max_size_gb <= 0:
            errors.append("Storage max size must be positive")
        if self.storage.retention_days < 0:
            errors.append("Retention days cannot be negative")
        
        return errors

# Default configuration
DEFAULT_CONFIG = {
    "database": {
        "url": "sqlite:///crawler.db",
        "pool_size": 10,
        "max_overflow": 20,
        "echo": False
    },
    "storage": {
        "base_path": "crawl_data",
        "max_size_gb": 100,
        "compression_enabled": True,
        "retention_days": 30,
        "backup_enabled": True,
        "backup_path": "backups"
    },
    "network": {
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 1.0,
        "max_concurrent_requests": 10,
        "rate_limit_requests_per_minute": 60,
        "user_agent_rotation": True,
        "proxy_enabled": False,
        "proxy_list": []
    },
    "security": {
        "ssl_verify": True,
        "allow_self_signed": False,
        "certificate_path": None,
        "key_path": None,
        "encryption_enabled": False,
        "encryption_key": None
    },
    "compliance": {
        "gdpr_compliant": True,
        "ccpa_compliant": True,
        "respect_robots_txt": True,
        "respect_rate_limits": True,
        "data_retention_days": 30,
        "anonymize_data": True,
        "audit_logging": True
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,
        "cors_origins": ["*"],
        "api_key_required": False,
        "rate_limit_enabled": True,
        "rate_limit_requests_per_minute": 100
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_enabled": True,
        "file_path": "logs/crawler.log",
        "max_file_size_mb": 100,
        "backup_count": 5,
        "console_enabled": True
    },
    "crawler": {
        "default_mode": "enhanced",
        "default_max_depth": 3,
        "default_max_pages": 100,
        "default_delay": 1.0,
        "extract_images": True,
        "extract_links": True,
        "extract_forms": True,
        "extract_scripts": True,
        "extract_styles": True,
        "extract_meta": True,
        "ocr_enabled": False,
        "ast_analysis": False,
        "network_analysis": False,
        "screenshot_enabled": False,
        "pdf_export_enabled": False
    },
    "monitoring": {
        "metrics_enabled": True,
        "prometheus_enabled": False,
        "health_check_interval": 30,
        "performance_monitoring": True,
        "alerting_enabled": False,
        "alert_email": None
    }
}

def create_default_config(config_path: str = "config.json"):
    """Create a default configuration file."""
    with open(config_path, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    print(f"Created default configuration file: {config_path}")

def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or create default."""
    config = Config(config_path)
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("Invalid configuration")
    
    return config

# Global configuration instance
config: Optional[Config] = None

def get_config() -> Config:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = load_config()
    return config

if __name__ == "__main__":
    # Create default configuration if run directly
    create_default_config()
    print("Default configuration created successfully!") 