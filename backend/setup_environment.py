#!/usr/bin/env python3
"""
Iron Cloud Environment Setup Script
==================================

Interactive setup script for configuring all API keys and environment variables
for the enhanced Iron Cloud system.
"""

import os
import sys
import json
import getpass
from pathlib import Path
from typing import Dict, List, Any

def print_banner():
    """Print setup banner."""
    print("=" * 80)
    print("🚀 IRON CLOUD AUTONOMOUS CRAWLER SYSTEM - ENVIRONMENT SETUP")
    print("=" * 80)
    print("This script will help you configure all API keys and settings")
    print("for the enhanced Iron Cloud system with advanced features.")
    print("=" * 80)

def get_user_input(prompt: str, default: str = "", password: bool = False) -> str:
    """Get user input with optional default value."""
    if default:
        prompt = f"{prompt} (default: {default}): "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default

def get_yes_no(prompt: str, default: str = "y") -> bool:
    """Get yes/no input from user."""
    while True:
        response = get_user_input(f"{prompt} (y/n)", default).lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'")

def setup_database_config() -> Dict[str, str]:
    """Setup database configuration."""
    print("\n📊 DATABASE CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["DATABASE_URL"] = get_user_input(
        "PostgreSQL Database URL",
        "postgresql://user:password@localhost:5432/dataminer_ai"
    )
    
    config["REDIS_URL"] = get_user_input(
        "Redis URL",
        "redis://localhost:6379"
    )
    
    return config

def setup_security_config() -> Dict[str, str]:
    """Setup security configuration."""
    print("\n🔐 SECURITY CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["SECRET_KEY"] = get_user_input(
        "Secret Key (for JWT tokens)",
        "your-super-secret-key-here-change-this-in-production"
    )
    
    config["JWT_SECRET"] = get_user_input(
        "JWT Secret Key",
        "your-jwt-secret-key-here"
    )
    
    config["ACCESS_TOKEN_EXPIRE_MINUTES"] = get_user_input(
        "Access Token Expire Minutes",
        "30"
    )
    
    config["REFRESH_TOKEN_EXPIRE_DAYS"] = get_user_input(
        "Refresh Token Expire Days",
        "7"
    )
    
    return config

def setup_sports_api_keys() -> Dict[str, str]:
    """Setup sports API keys."""
    print("\n⚽ SPORTS API KEYS")
    print("-" * 40)
    print("Configure API keys for sports data providers.")
    print("Leave blank if you don't have the API key.")
    
    config = {}
    
    apis = [
        ("THE_ODDS_API_KEY", "The Odds API (https://the-odds-api.com)"),
        ("API_FOOTBALL_KEY", "API-Football (RapidAPI)"),
        ("SPORTRADAR_API_KEY", "Sportradar"),
        ("LSPORTS_API_KEY", "LSports"),
        ("STATS_PERFORM_API_KEY", "Stats Perform (Opta)"),
        ("BETFAIR_APP_KEY", "Betfair App Key"),
        ("BETFAIR_SESSION_TOKEN", "Betfair Session Token"),
        ("PINNACLE_API_KEY", "Pinnacle"),
        ("LIVESCORE_API_KEY", "LiveScore"),
        ("ESPN_API_KEY", "ESPN API"),
        ("SPORTMONKS_API_KEY", "SportMonks"),
        ("GOALSERVE_API_KEY", "Goalserve"),
    ]
    
    for key, description in apis:
        print(f"\n{description}")
        config[key] = get_user_input(f"API Key for {key}", password=True)
    
    return config

def setup_ai_ml_config() -> Dict[str, str]:
    """Setup AI/ML configuration."""
    print("\n🤖 AI & MACHINE LEARNING CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["OPENAI_API_KEY"] = get_user_input(
        "OpenAI API Key (for enhanced predictions)",
        password=True
    )
    
    config["ML_ENABLED"] = "true" if get_yes_no("Enable Machine Learning predictions", "y") else "false"
    config["ML_PREDICTION_THRESHOLD"] = get_user_input("ML Prediction Threshold", "0.7")
    config["BETTING_ANALYSIS_ENABLED"] = "true" if get_yes_no("Enable Betting Analysis", "y") else "false"
    config["BETTING_PREDICTION_ACCURACY_THRESHOLD"] = get_user_input("Betting Prediction Accuracy Threshold", "0.75")
    
    return config

def setup_penetration_config() -> Dict[str, str]:
    """Setup penetration configuration."""
    print("\n🛡️ ADVANCED PENETRATION CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["IRON_CLOUD_ENABLED"] = "true" if get_yes_no("Enable Iron Cloud Penetration", "y") else "false"
    config["IRON_CLOUD_MAX_RETRIES"] = get_user_input("Max Penetration Retries", "5")
    config["IRON_CLOUD_TIMEOUT"] = get_user_input("Penetration Timeout (seconds)", "30")
    config["IRON_CLOUD_USER_AGENT_ROTATION"] = "true" if get_yes_no("Enable User-Agent Rotation", "y") else "false"
    config["IRON_CLOUD_PROXY_ENABLED"] = "true" if get_yes_no("Enable Proxy Support", "n") else "false"
    
    if config["IRON_CLOUD_PROXY_ENABLED"] == "true":
        config["PROXY_LIST"] = get_user_input("Proxy List (comma-separated)")
        config["PROXY_USERNAME"] = get_user_input("Proxy Username")
        config["PROXY_PASSWORD"] = get_user_input("Proxy Password", password=True)
    
    config["SCRAPING_ENABLED"] = "true" if get_yes_no("Enable Web Scraping", "y") else "false"
    config["SELENIUM_ENABLED"] = "true" if get_yes_no("Enable Selenium Browser Automation", "y") else "false"
    config["NETWORK_ANALYSIS_ENABLED"] = "true" if get_yes_no("Enable Network Analysis", "y") else "false"
    
    return config

def setup_mobile_config() -> Dict[str, str]:
    """Setup mobile app configuration."""
    print("\n📱 MOBILE APP CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["MOBILE_APP_ENABLED"] = "true" if get_yes_no("Enable Mobile App Support", "y") else "false"
    
    if config["MOBILE_APP_ENABLED"] == "true":
        config["EXPO_ACCESS_TOKEN"] = get_user_input("Expo Access Token", password=True)
        config["FIREBASE_SERVER_KEY"] = get_user_input("Firebase Server Key", password=True)
        config["FIREBASE_PROJECT_ID"] = get_user_input("Firebase Project ID")
        config["ANALYTICS_ENABLED"] = "true" if get_yes_no("Enable Analytics", "y") else "false"
        config["PUSH_NOTIFICATIONS_ENABLED"] = "true" if get_yes_no("Enable Push Notifications", "y") else "false"
        config["OFFLINE_SUPPORT_ENABLED"] = "true" if get_yes_no("Enable Offline Support", "y") else "false"
        config["REAL_TIME_UPDATES_ENABLED"] = "true" if get_yes_no("Enable Real-time Updates", "y") else "false"
    
    return config

def setup_sports_coverage() -> Dict[str, str]:
    """Setup sports coverage configuration."""
    print("\n🏆 SPORTS COVERAGE CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    sports = [
        "basketball", "football", "american_football", "baseball", "hockey",
        "tennis", "cricket", "rugby", "motorsport", "combat_sports", "esports"
    ]
    
    for sport in sports:
        enabled = get_yes_no(f"Enable {sport.title()} coverage", "y")
        config[f"{sport.upper()}_ENABLED"] = "true" if enabled else "false"
    
    return config

def setup_performance_config() -> Dict[str, str]:
    """Setup performance and monitoring configuration."""
    print("\n⚡ PERFORMANCE & MONITORING CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["LOG_LEVEL"] = get_user_input("Log Level", "INFO")
    config["LOG_FILE"] = get_user_input("Log File Path", "./logs/iron_cloud.log")
    
    config["PROMETHEUS_ENABLED"] = "true" if get_yes_no("Enable Prometheus Monitoring", "n") else "false"
    config["GRAFANA_ENABLED"] = "true" if get_yes_no("Enable Grafana Dashboards", "n") else "false"
    
    config["RATE_LIMIT_ENABLED"] = "true" if get_yes_no("Enable Rate Limiting", "y") else "false"
    config["RATE_LIMIT_REQUESTS_PER_MINUTE"] = get_user_input("Rate Limit Requests per Minute", "100")
    config["RATE_LIMIT_BURST_SIZE"] = get_user_input("Rate Limit Burst Size", "20")
    
    config["CACHE_ENABLED"] = "true" if get_yes_no("Enable Caching", "y") else "false"
    config["CACHE_TTL_SECONDS"] = get_user_input("Cache TTL (seconds)", "300")
    config["CACHE_MAX_SIZE"] = get_user_input("Cache Max Size", "1000")
    
    return config

def setup_development_config() -> Dict[str, str]:
    """Setup development configuration."""
    print("\n🛠️ DEVELOPMENT CONFIGURATION")
    print("-" * 40)
    
    config = {}
    
    config["DEBUG"] = "true" if get_yes_no("Enable Debug Mode", "n") else "false"
    config["TESTING_MODE"] = "true" if get_yes_no("Enable Testing Mode", "n") else "false"
    
    config["MOCK_DATA_ENABLED"] = "true" if get_yes_no("Enable Mock Data", "n") else "false"
    config["MOCK_DATA_PATH"] = get_user_input("Mock Data Path", "./mock_data/")
    
    config["SWAGGER_ENABLED"] = "true" if get_yes_no("Enable Swagger Documentation", "y") else "false"
    config["REDOC_ENABLED"] = "true" if get_yes_no("Enable ReDoc Documentation", "y") else "false"
    
    config["HEALTH_CHECK_ENABLED"] = "true" if get_yes_no("Enable Health Checks", "y") else "false"
    config["HEALTH_CHECK_INTERVAL_SECONDS"] = get_user_input("Health Check Interval (seconds)", "60")
    
    return config

def create_env_file(config: Dict[str, str], env_file_path: str = ".env"):
    """Create .env file with configuration."""
    print(f"\n📝 Creating {env_file_path} file...")
    
    with open(env_file_path, "w") as f:
        f.write("# Iron Cloud API Penetration System - Environment Configuration\n")
        f.write("# ==============================================================\n\n")
        
        # Group configurations
        sections = [
            ("Database Configuration", ["DATABASE_URL", "REDIS_URL"]),
            ("Security & Authentication", ["SECRET_KEY", "JWT_SECRET", "ACCESS_TOKEN_EXPIRE_MINUTES", "REFRESH_TOKEN_EXPIRE_DAYS"]),
            ("Iron Cloud Penetration Configuration", [k for k in config.keys() if k.startswith("IRON_CLOUD_")]),
            ("Proxy Configuration", [k for k in config.keys() if k.startswith("PROXY_")]),
            ("Sports API Keys", [k for k in config.keys() if k.endswith("_API_KEY") or k.endswith("_KEY") or k.endswith("_TOKEN")]),
            ("Machine Learning Configuration", [k for k in config.keys() if k.startswith("ML_") or k.startswith("BETTING_") or k == "OPENAI_API_KEY"]),
            ("Advanced Penetration Techniques", [k for k in config.keys() if k.startswith("SCRAPING_") or k.startswith("SELENIUM_") or k.startswith("NETWORK_")]),
            ("Mobile App Configuration", [k for k in config.keys() if k.startswith("MOBILE_") or k.startswith("EXPO_") or k.startswith("FIREBASE_") or k.startswith("PUSH_") or k.startswith("OFFLINE_") or k.startswith("REAL_TIME_") or k.startswith("ANALYTICS_")]),
            ("Sports Coverage Configuration", [k for k in config.keys() if k.endswith("_ENABLED") and not k.startswith(("MOBILE_", "IRON_CLOUD_", "ML_", "SCRAPING_", "SELENIUM_", "NETWORK_", "PROMETHEUS_", "GRAFANA_", "RATE_LIMIT_", "CACHE_", "DEBUG_", "TESTING_", "MOCK_", "SWAGGER_", "REDOC_", "HEALTH_CHECK_"))]),
            ("Performance & Monitoring", [k for k in config.keys() if k.startswith(("LOG_", "PROMETHEUS_", "GRAFANA_", "RATE_LIMIT_", "CACHE_"))]),
            ("Development & Testing", [k for k in config.keys() if k.startswith(("DEBUG", "TESTING_", "MOCK_", "SWAGGER_", "REDOC_", "HEALTH_CHECK_"))])
        ]
        
        for section_name, keys in sections:
            section_keys = [k for k in keys if k in config]
            if section_keys:
                f.write(f"\n# {section_name}\n")
                f.write("# " + "=" * (len(section_name) + 1) + "\n")
                for key in section_keys:
                    value = config[key]
                    if value:
                        f.write(f"{key}={value}\n")
                f.write("\n")
    
    print(f"✅ Environment file created: {env_file_path}")

def create_env_example():
    """Create .env.example file."""
    print("\n📝 Creating .env.example file...")
    
    example_config = {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/dataminer_ai",
        "REDIS_URL": "redis://localhost:6379",
        "SECRET_KEY": "your-super-secret-key-here-change-this-in-production",
        "JWT_SECRET": "your-jwt-secret-key-here",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "IRON_CLOUD_ENABLED": "true",
        "IRON_CLOUD_MAX_RETRIES": "5",
        "IRON_CLOUD_TIMEOUT": "30",
        "IRON_CLOUD_USER_AGENT_ROTATION": "true",
        "IRON_CLOUD_PROXY_ENABLED": "false",
        "THE_ODDS_API_KEY": "your-the-odds-api-key-here",
        "API_FOOTBALL_KEY": "your-rapidapi-key-here",
        "SPORTRADAR_API_KEY": "your-sportradar-api-key-here",
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "ML_ENABLED": "true",
        "ML_PREDICTION_THRESHOLD": "0.7",
        "BETTING_ANALYSIS_ENABLED": "true",
        "BETTING_PREDICTION_ACCURACY_THRESHOLD": "0.75",
        "SCRAPING_ENABLED": "true",
        "SELENIUM_ENABLED": "true",
        "NETWORK_ANALYSIS_ENABLED": "true",
        "MOBILE_APP_ENABLED": "true",
        "EXPO_ACCESS_TOKEN": "your-expo-access-token-here",
        "FIREBASE_SERVER_KEY": "your-firebase-server-key-here",
        "FIREBASE_PROJECT_ID": "your-firebase-project-id-here",
        "ANALYTICS_ENABLED": "true",
        "PUSH_NOTIFICATIONS_ENABLED": "true",
        "OFFLINE_SUPPORT_ENABLED": "true",
        "REAL_TIME_UPDATES_ENABLED": "true",
        "BASKETBALL_ENABLED": "true",
        "FOOTBALL_ENABLED": "true",
        "AMERICAN_FOOTBALL_ENABLED": "true",
        "BASEBALL_ENABLED": "true",
        "HOCKEY_ENABLED": "true",
        "TENNIS_ENABLED": "true",
        "CRICKET_ENABLED": "true",
        "RUGBY_ENABLED": "true",
        "MOTORSPORT_ENABLED": "true",
        "COMBAT_SPORTS_ENABLED": "true",
        "ESPORTS_ENABLED": "true",
        "LOG_LEVEL": "INFO",
        "LOG_FILE": "./logs/iron_cloud.log",
        "PROMETHEUS_ENABLED": "true",
        "GRAFANA_ENABLED": "true",
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_REQUESTS_PER_MINUTE": "100",
        "RATE_LIMIT_BURST_SIZE": "20",
        "CACHE_ENABLED": "true",
        "CACHE_TTL_SECONDS": "300",
        "CACHE_MAX_SIZE": "1000",
        "DEBUG": "true",
        "TESTING_MODE": "false",
        "MOCK_DATA_ENABLED": "false",
        "MOCK_DATA_PATH": "./mock_data/",
        "SWAGGER_ENABLED": "true",
        "REDOC_ENABLED": "true",
        "HEALTH_CHECK_ENABLED": "true",
        "HEALTH_CHECK_INTERVAL_SECONDS": "60"
    }
    
    create_env_file(example_config, ".env.example")
    print("✅ Example environment file created: .env.example")

def main():
    """Main setup function."""
    print_banner()
    
    print("This setup will configure your Iron Cloud system with:")
    print("✅ Real API keys for sports data providers")
    print("✅ Advanced penetration techniques")
    print("✅ Machine learning prediction algorithms")
    print("✅ Mobile app support (iOS/Android)")
    print("✅ Expanded sports coverage")
    print("✅ Performance monitoring and caching")
    print("✅ Development and testing tools")
    
    if not get_yes_no("\nDo you want to proceed with the setup?", "y"):
        print("Setup cancelled.")
        return
    
    # Collect all configurations
    config = {}
    
    config.update(setup_database_config())
    config.update(setup_security_config())
    config.update(setup_sports_api_keys())
    config.update(setup_ai_ml_config())
    config.update(setup_penetration_config())
    config.update(setup_mobile_config())
    config.update(setup_sports_coverage())
    config.update(setup_performance_config())
    config.update(setup_development_config())
    
    # Create environment files
    create_env_file(config)
    create_env_example()
    
    print("\n" + "=" * 80)
    print("🎉 ENVIRONMENT SETUP COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review the generated .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start the backend: python main.py")
    print("4. Start the frontend: npm run dev")
    print("\nFor more information, check the documentation in the docs/ folder.")
    print("=" * 80)

if __name__ == "__main__":
    main() 