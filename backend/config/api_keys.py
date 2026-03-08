#!/usr/bin/env python3
"""
Iron Cloud API Keys Configuration
================================

Centralized configuration for all API keys and environment variables
used in the Iron Cloud penetration system.
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

class APIType(Enum):
    """Supported API types with their configuration."""
    THE_ODDS_API = "the_odds_api"
    API_FOOTBALL = "api_football"
    SPORTRADAR = "sportradar"
    LSPORTS = "lsports"
    STATS_PERFORM = "stats_perform"
    BETFAIR = "betfair"
    PINNACLE = "pinnacle"
    LIVESCORE = "livescore"
    ESPN = "espn"
    SPORTMONKS = "sportmonks"
    GOALSERVE = "goalserve"
    BALLDONTLIE = "balldontlie"

@dataclass
class APIConfig:
    """API configuration with key and settings."""
    name: str
    api_key: Optional[str] = None
    base_url: str = ""
    rate_limit: int = 100
    enabled: bool = False
    requires_auth: bool = True
    working: bool = False

class APIKeyManager:
    """Manages API keys and configurations for all providers."""
    
    def __init__(self):
        self.api_configs = self._initialize_api_configs()
        self._load_environment_variables()
    
    def _initialize_api_configs(self) -> Dict[str, APIConfig]:
        """Initialize API configurations."""
        return {
            APIType.THE_ODDS_API.value: APIConfig(
                name="The Odds API",
                base_url="https://api.the-odds-api.com/v4",
                rate_limit=500,
                requires_auth=True
            ),
            APIType.API_FOOTBALL.value: APIConfig(
                name="API-Football",
                base_url="https://api-football-v1.p.rapidapi.com/v3",
                rate_limit=100,
                requires_auth=True
            ),
            APIType.SPORTRADAR.value: APIConfig(
                name="Sportradar",
                base_url="https://api.sportradar.com",
                rate_limit=300,
                requires_auth=True
            ),
            APIType.LSPORTS.value: APIConfig(
                name="LSports",
                base_url="https://api.lsports.eu/v1",
                rate_limit=1000,
                requires_auth=True
            ),
            APIType.STATS_PERFORM.value: APIConfig(
                name="Stats Perform",
                base_url="https://api.statsperform.com",
                rate_limit=500,
                requires_auth=True
            ),
            APIType.BETFAIR.value: APIConfig(
                name="Betfair",
                base_url="https://api.betfair.com/exchange/betting/json",
                rate_limit=1000,
                requires_auth=True
            ),
            APIType.PINNACLE.value: APIConfig(
                name="Pinnacle",
                base_url="https://api.pinnacle.com/v1",
                rate_limit=200,
                requires_auth=True
            ),
            APIType.LIVESCORE.value: APIConfig(
                name="LiveScore",
                base_url="https://api.livescore.com/v1/api/app",
                rate_limit=200,
                requires_auth=True
            ),
            APIType.ESPN.value: APIConfig(
                name="ESPN",
                base_url="https://site.api.espn.com/apis/site/v2/sports",
                rate_limit=100,
                requires_auth=False
            ),
            APIType.SPORTMONKS.value: APIConfig(
                name="SportMonks",
                base_url="https://api.sportmonks.com/v3/football",
                rate_limit=1000,
                requires_auth=True
            ),
            APIType.GOALSERVE.value: APIConfig(
                name="Goalserve",
                base_url="https://www.goalserve.com/getfeed",
                rate_limit=100,
                requires_auth=True
            ),
            APIType.BALLDONTLIE.value: APIConfig(
                name="BALLDONTLIE",
                base_url="https://www.balldontlie.io/api/v1",
                rate_limit=1000,
                requires_auth=False,
                working=True,
                enabled=True
            )
        }
    
    def _load_environment_variables(self):
        """Load API keys from environment variables."""
        # Map environment variables to API configs
        env_mapping = {
            'THE_ODDS_API_KEY': APIType.THE_ODDS_API.value,
            'API_FOOTBALL_KEY': APIType.API_FOOTBALL.value,
            'SPORTRADAR_API_KEY': APIType.SPORTRADAR.value,
            'LSPORTS_API_KEY': APIType.LSPORTS.value,
            'STATS_PERFORM_API_KEY': APIType.STATS_PERFORM.value,
            'BETFAIR_APP_KEY': APIType.BETFAIR.value,
            'PINNACLE_API_KEY': APIType.PINNACLE.value,
            'LIVESCORE_API_KEY': APIType.LIVESCORE.value,
            'ESPN_API_KEY': APIType.ESPN.value,
            'SPORTMONKS_API_KEY': APIType.SPORTMONKS.value,
            'GOALSERVE_API_KEY': APIType.GOALSERVE.value,
        }
        
        for env_var, api_type in env_mapping.items():
            api_key = os.getenv(env_var)
            if api_key and api_key != "your-api-key-here":
                self.api_configs[api_type].api_key = api_key
                self.api_configs[api_type].enabled = True
                self.api_configs[api_type].working = True
    
    def get_api_config(self, api_type: str) -> Optional[APIConfig]:
        """Get API configuration for a specific type."""
        return self.api_configs.get(api_type)
    
    def get_working_apis(self) -> Dict[str, APIConfig]:
        """Get all working APIs."""
        return {k: v for k, v in self.api_configs.items() if v.working}
    
    def get_enabled_apis(self) -> Dict[str, APIConfig]:
        """Get all enabled APIs."""
        return {k: v for k, v in self.api_configs.items() if v.enabled}
    
    def has_api_key(self, api_type: str) -> bool:
        """Check if API key is available for a specific type."""
        config = self.get_api_config(api_type)
        return config is not None and config.api_key is not None
    
    def get_api_key(self, api_type: str) -> Optional[str]:
        """Get API key for a specific type."""
        config = self.get_api_config(api_type)
        return config.api_key if config else None

# Global API key manager instance
api_key_manager = APIKeyManager()

# Sports Coverage Configuration
SPORTS_COVERAGE = {
    "basketball": {
        "enabled": True,
        "leagues": ["NBA", "WNBA", "EuroLeague", "CBA"],
        "apis": [APIType.ESPN.value, APIType.BALLDONTLIE.value]
    },
    "football": {
        "enabled": True,
        "leagues": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
        "apis": [APIType.API_FOOTBALL.value, APIType.SPORTMONKS.value, APIType.GOALSERVE.value]
    },
    "american_football": {
        "enabled": True,
        "leagues": ["NFL", "NCAA"],
        "apis": [APIType.ESPN.value]
    },
    "baseball": {
        "enabled": True,
        "leagues": ["MLB", "NPB"],
        "apis": [APIType.ESPN.value]
    },
    "hockey": {
        "enabled": True,
        "leagues": ["NHL", "KHL"],
        "apis": [APIType.ESPN.value]
    },
    "tennis": {
        "enabled": True,
        "leagues": ["ATP", "WTA", "Grand Slams"],
        "apis": [APIType.ESPN.value]
    },
    "cricket": {
        "enabled": True,
        "leagues": ["IPL", "International"],
        "apis": [APIType.ESPN.value]
    },
    "rugby": {
        "enabled": True,
        "leagues": ["Six Nations", "Rugby Championship"],
        "apis": [APIType.ESPN.value]
    },
    "motorsport": {
        "enabled": True,
        "leagues": ["F1", "NASCAR", "MotoGP"],
        "apis": [APIType.ESPN.value]
    },
    "combat_sports": {
        "enabled": True,
        "leagues": ["UFC", "Boxing"],
        "apis": [APIType.ESPN.value]
    },
    "esports": {
        "enabled": True,
        "leagues": ["CS:GO", "LoL", "Dota 2"],
        "apis": [APIType.ESPN.value]
    }
}

# Machine Learning Configuration
ML_CONFIG = {
    "enabled": os.getenv("ML_ENABLED", "true").lower() == "true",
    "model_path": os.getenv("ML_MODEL_PATH", "./models/"),
    "prediction_threshold": float(os.getenv("ML_PREDICTION_THRESHOLD", "0.7")),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "betting_analysis_enabled": os.getenv("BETTING_ANALYSIS_ENABLED", "true").lower() == "true",
    "prediction_accuracy_threshold": float(os.getenv("BETTING_PREDICTION_ACCURACY_THRESHOLD", "0.75"))
}

# Advanced Penetration Configuration
PENETRATION_CONFIG = {
    "enabled": os.getenv("IRON_CLOUD_ENABLED", "true").lower() == "true",
    "max_retries": int(os.getenv("IRON_CLOUD_MAX_RETRIES", "5")),
    "timeout": int(os.getenv("IRON_CLOUD_TIMEOUT", "30")),
    "user_agent_rotation": os.getenv("IRON_CLOUD_USER_AGENT_ROTATION", "true").lower() == "true",
    "proxy_enabled": os.getenv("IRON_CLOUD_PROXY_ENABLED", "false").lower() == "true",
    "scraping_enabled": os.getenv("SCRAPING_ENABLED", "true").lower() == "true",
    "selenium_enabled": os.getenv("SELENIUM_ENABLED", "true").lower() == "true",
    "network_analysis_enabled": os.getenv("NETWORK_ANALYSIS_ENABLED", "true").lower() == "true"
}

# Mobile App Configuration
MOBILE_CONFIG = {
    "enabled": os.getenv("MOBILE_APP_ENABLED", "true").lower() == "true",
    "expo_access_token": os.getenv("EXPO_ACCESS_TOKEN"),
    "firebase_server_key": os.getenv("FIREBASE_SERVER_KEY"),
    "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "analytics_enabled": os.getenv("ANALYTICS_ENABLED", "true").lower() == "true",
    "push_notifications_enabled": os.getenv("PUSH_NOTIFICATIONS_ENABLED", "true").lower() == "true"
} 