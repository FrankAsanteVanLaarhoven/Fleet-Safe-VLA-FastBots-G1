#!/usr/bin/env python3
"""
Real Sports APIs Integration with Advanced Features
==================================================

Enhanced sports API integration with:
- Real API key management
- Advanced penetration techniques
- Machine learning predictions
- Expanded sports coverage
- Mobile app support
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
import random
import json

# Import our new advanced systems
from config.api_keys import api_key_manager, SPORTS_COVERAGE, ML_CONFIG, PENETRATION_CONFIG, MOBILE_CONFIG
from services.advanced_penetration import penetration_engine
from services.ml_predictions import prediction_engine

logger = logging.getLogger(__name__)
router = APIRouter()

class EnhancedSportsAPIIntegration:
    """Enhanced sports API integration with advanced features."""
    
    def __init__(self):
        self.session = None
        self.api_key_manager = api_key_manager
        self.penetration_engine = penetration_engine
        self.prediction_engine = prediction_engine
        self.live_simulator = LiveSportsDataSimulator()
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None:
            connector = aiohttp.TCPConnector(ssl=False, limit=100)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def make_enhanced_request(self, api_type: str, endpoint: str, params: Dict = None, use_penetration: bool = True) -> Dict[str, Any]:
        """Make enhanced API request with penetration fallback."""
        api_config = self.api_key_manager.get_api_config(api_type)
        if not api_config:
            raise ValueError(f"API type '{api_type}' not supported")
        
        # Try with real API key first
        if api_config.api_key and api_config.working:
            try:
                session = await self.get_session()
                headers = {"X-API-Key": api_config.api_key}
                
                url = f"{api_config.base_url}/{endpoint}"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "api": api_config.name,
                            "method": "authenticated",
                            "timestamp": datetime.now().isoformat()
                        }
            except Exception as e:
                logger.warning(f"Authenticated request failed for {api_config.name}: {e}")
        
        # Try penetration if enabled and no API key
        if use_penetration and PENETRATION_CONFIG["enabled"]:
            try:
                url = f"{api_config.base_url}/{endpoint}"
                penetration_results = await self.penetration_engine.comprehensive_penetration(url, api_type)
                
                for result in penetration_results:
                    if result.success:
                        return {
                            "success": True,
                            "data": result.data,
                            "api": api_config.name,
                            "method": f"penetration_{result.technique}",
                            "timestamp": datetime.now().isoformat(),
                            "penetration_details": {
                                "technique": result.technique,
                                "response_time": result.response_time,
                                "status_code": result.status_code
                            }
                        }
            except Exception as e:
                logger.warning(f"Penetration failed for {api_config.name}: {e}")
        
        # Fallback to simulator
        return await self._get_simulator_data(api_type, endpoint)
    
    async def _get_simulator_data(self, api_type: str, endpoint: str) -> Dict[str, Any]:
        """Get data from simulator as fallback."""
        # Map API types to sports
        sport_mapping = {
            "the_odds_api": "football",
            "api_football": "football", 
            "sportradar": "basketball",
            "lsports": "football",
            "stats_perform": "football",
            "betfair": "football",
            "pinnacle": "football",
            "livescore": "football",
            "espn": "basketball",
            "sportmonks": "football",
            "goalserve": "football",
            "balldontlie": "basketball"
        }
        
        sport = sport_mapping.get(api_type, "basketball")
        matches = self.live_simulator.get_live_matches(sport)
        
        return {
            "success": True,
            "data": {
                "matches": matches,
                "total": len(matches),
                "sport": sport
            },
            "api": "LiveSportsSimulator",
            "method": "simulator",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_live_matches_enhanced(self, sport: str = "basketball") -> Dict[str, Any]:
        """Get live matches with enhanced features."""
        # Get available APIs for this sport
        sport_config = SPORTS_COVERAGE.get(sport, {})
        available_apis = sport_config.get("apis", [])
        
        # Try each available API
        for api_type in available_apis:
            try:
                result = await self.make_enhanced_request(api_type, "live")
                if result["success"]:
                    # Add ML predictions if enabled
                    if ML_CONFIG["enabled"] and result["data"].get("matches"):
                        for match in result["data"]["matches"]:
                            prediction = await self.prediction_engine.predict_match_winner(match, sport)
                            match["ml_prediction"] = {
                                "prediction": prediction.prediction,
                                "confidence": prediction.confidence,
                                "probability": prediction.probability,
                                "risk_level": prediction.risk_level,
                                "reasoning": prediction.reasoning
                            }
                    
                    return result
            except Exception as e:
                logger.warning(f"API {api_type} failed for {sport}: {e}")
                continue
        
        # Fallback to simulator
        return await self._get_simulator_data("balldontlie", "live")
    
    async def get_odds_enhanced(self, match_id: str, sport: str = "basketball") -> Dict[str, Any]:
        """Get odds with enhanced features."""
        # Try odds-specific APIs
        odds_apis = ["the_odds_api", "betfair", "pinnacle"]
        
        for api_type in odds_apis:
            try:
                result = await self.make_enhanced_request(api_type, f"odds/{match_id}")
                if result["success"]:
                    return result
            except Exception as e:
                logger.warning(f"Odds API {api_type} failed: {e}")
                continue
        
        # Fallback to simulator
        odds = self.live_simulator.get_odds(match_id)
        if odds:
            return {
                "success": True,
                "data": odds,
                "api": "LiveSportsSimulator",
                "method": "simulator",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"No odds found for match {match_id}",
                "api": "LiveSportsSimulator",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_comprehensive_analysis(self, match_id: str, sport: str) -> Dict[str, Any]:
        """Get comprehensive match analysis with ML predictions."""
        # Get match data
        matches = self.live_simulator.get_live_matches(sport)
        match = next((m for m in matches if m["id"] == match_id), None)
        
        if not match:
            return {"success": False, "error": "Match not found"}
        
        # Get odds
        odds = self.live_simulator.get_odds(match_id)
        
        # Get ML predictions
        predictions = {}
        if ML_CONFIG["enabled"]:
            predictions["match_winner"] = await self.prediction_engine.predict_match_winner(match, sport)
            predictions["goal_totals"] = await self.prediction_engine.predict_goal_totals(match, sport)
            predictions["both_teams_score"] = await self.prediction_engine.predict_both_teams_score(match, sport)
        
        # Get AI enhanced prediction if available
        ai_prediction = None
        if ML_CONFIG.get("openai_api_key"):
            ai_prediction = await self.prediction_engine.get_ai_enhanced_prediction(match, sport)
        
        return {
            "success": True,
            "data": {
                "match": match,
                "odds": odds,
                "predictions": predictions,
                "ai_enhanced": ai_prediction,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "api": "EnhancedAnalysis",
            "method": "comprehensive",
            "timestamp": datetime.now().isoformat()
        }

class LiveSportsDataSimulator:
    """Enhanced live sports data simulator with expanded coverage."""
    
    def __init__(self):
        self.teams = self._initialize_teams()
        self.live_matches = self._initialize_live_matches()
        self.odds_data = self._initialize_odds()
        self.scores = {}
    
    def _initialize_teams(self) -> Dict[str, List[Dict]]:
        """Initialize teams for all sports."""
        return {
            "basketball": [
                {"id": 1, "name": "Lakers", "city": "Los Angeles", "conference": "Western"},
                {"id": 2, "name": "Warriors", "city": "Golden State", "conference": "Western"},
                {"id": 3, "name": "Celtics", "city": "Boston", "conference": "Eastern"},
                {"id": 4, "name": "Heat", "city": "Miami", "conference": "Eastern"},
                {"id": 5, "name": "Bulls", "city": "Chicago", "conference": "Eastern"},
                {"id": 6, "name": "Knicks", "city": "New York", "conference": "Eastern"}
            ],
            "football": [
                {"id": 1, "name": "Manchester United", "city": "Manchester", "league": "Premier League"},
                {"id": 2, "name": "Liverpool", "city": "Liverpool", "league": "Premier League"},
                {"id": 3, "name": "Arsenal", "city": "London", "league": "Premier League"},
                {"id": 4, "name": "Chelsea", "city": "London", "league": "Premier League"},
                {"id": 5, "name": "Barcelona", "city": "Barcelona", "league": "La Liga"},
                {"id": 6, "name": "Real Madrid", "city": "Madrid", "league": "La Liga"}
            ],
            "american_football": [
                {"id": 1, "name": "Patriots", "city": "New England", "conference": "AFC"},
                {"id": 2, "name": "Cowboys", "city": "Dallas", "conference": "NFC"},
                {"id": 3, "name": "Packers", "city": "Green Bay", "conference": "NFC"},
                {"id": 4, "name": "Chiefs", "city": "Kansas City", "conference": "AFC"}
            ],
            "baseball": [
                {"id": 1, "name": "Yankees", "city": "New York", "league": "AL"},
                {"id": 2, "name": "Red Sox", "city": "Boston", "league": "AL"},
                {"id": 3, "name": "Dodgers", "city": "Los Angeles", "league": "NL"},
                {"id": 4, "name": "Giants", "city": "San Francisco", "league": "NL"}
            ],
            "hockey": [
                {"id": 1, "name": "Bruins", "city": "Boston", "conference": "Eastern"},
                {"id": 2, "name": "Blackhawks", "city": "Chicago", "conference": "Western"},
                {"id": 3, "name": "Rangers", "city": "New York", "conference": "Eastern"},
                {"id": 4, "name": "Kings", "city": "Los Angeles", "conference": "Western"}
            ],
            "tennis": [
                {"id": 1, "name": "Djokovic", "country": "Serbia", "ranking": 1},
                {"id": 2, "name": "Nadal", "country": "Spain", "ranking": 2},
                {"id": 3, "name": "Federer", "country": "Switzerland", "ranking": 3},
                {"id": 4, "name": "Medvedev", "country": "Russia", "ranking": 4}
            ]
        }
    
    def _initialize_live_matches(self) -> Dict[str, List[Dict]]:
        """Initialize live matches for all sports."""
        return {
            "basketball": [
                {
                    "id": "BASK_001",
                    "home_team": "Lakers",
                    "away_team": "Warriors",
                    "home_score": 108,
                    "away_score": 102,
                    "quarter": 4,
                    "time_remaining": "2:34",
                    "venue": "Crypto.com Arena",
                    "attendance": 18997,
                    "status": "live"
                },
                {
                    "id": "BASK_002",
                    "home_team": "Celtics",
                    "away_team": "Heat",
                    "home_score": 95,
                    "away_score": 98,
                    "quarter": 3,
                    "time_remaining": "8:45",
                    "venue": "TD Garden",
                    "attendance": 19156,
                    "status": "live"
                }
            ],
            "football": [
                {
                    "id": "FOOT_001",
                    "home_team": "Manchester United",
                    "away_team": "Liverpool",
                    "home_score": 2,
                    "away_score": 1,
                    "minute": 67,
                    "venue": "Old Trafford",
                    "attendance": 74140,
                    "status": "live"
                },
                {
                    "id": "FOOT_002",
                    "home_team": "Arsenal",
                    "away_team": "Chelsea",
                    "home_score": 1,
                    "away_score": 1,
                    "minute": 45,
                    "venue": "Emirates Stadium",
                    "attendance": 60260,
                    "status": "live"
                }
            ],
            "american_football": [
                {
                    "id": "NFL_001",
                    "home_team": "Patriots",
                    "away_team": "Cowboys",
                    "home_score": 24,
                    "away_score": 21,
                    "quarter": 4,
                    "time_remaining": "1:23",
                    "venue": "Gillette Stadium",
                    "attendance": 65878,
                    "status": "live"
                }
            ],
            "baseball": [
                {
                    "id": "MLB_001",
                    "home_team": "Yankees",
                    "away_team": "Red Sox",
                    "home_score": 5,
                    "away_score": 3,
                    "inning": 8,
                    "venue": "Yankee Stadium",
                    "attendance": 46537,
                    "status": "live"
                }
            ],
            "hockey": [
                {
                    "id": "NHL_001",
                    "home_team": "Bruins",
                    "away_team": "Blackhawks",
                    "home_score": 3,
                    "away_score": 2,
                    "period": 3,
                    "time_remaining": "5:42",
                    "venue": "TD Garden",
                    "attendance": 17565,
                    "status": "live"
                }
            ],
            "tennis": [
                {
                    "id": "TENNIS_001",
                    "player1": "Djokovic",
                    "player2": "Nadal",
                    "player1_score": "6-4, 3-6, 4-3",
                    "player2_score": "4-6, 6-3, 3-4",
                    "set": 3,
                    "venue": "Wimbledon",
                    "status": "live"
                }
            ]
        }
    
    def _initialize_odds(self) -> Dict[str, Dict]:
        """Initialize odds data."""
        return {
            "BASK_001": {
                "home_win": 2.15,
                "away_win": 1.85,
                "draw": None,
                "bookmakers": ["Bet365", "William Hill", "SkyBet"],
                "last_updated": datetime.now().isoformat()
            },
            "FOOT_001": {
                "home_win": 2.80,
                "away_win": 2.40,
                "draw": 3.20,
                "bookmakers": ["Bet365", "William Hill", "SkyBet"],
                "last_updated": datetime.now().isoformat()
            },
            "NFL_001": {
                "home_win": 1.95,
                "away_win": 1.95,
                "draw": None,
                "bookmakers": ["Bet365", "William Hill", "SkyBet"],
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def get_live_matches(self, sport: str) -> List[Dict]:
        """Get live matches for a sport."""
        return self.live_matches.get(sport, [])
    
    def get_odds(self, match_id: str) -> Optional[Dict]:
        """Get odds for a specific match."""
        return self.odds_data.get(match_id)
    
    def get_teams(self, sport: str) -> List[Dict]:
        """Get teams for a sport."""
        return self.teams.get(sport, [])
    
    def update_scores(self, match_id: str, home_score: int, away_score: int):
        """Update live scores."""
        self.scores[match_id] = {"home": home_score, "away": away_score}
        
        # Update match data
        for sport_matches in self.live_matches.values():
            for match in sport_matches:
                if match["id"] == match_id:
                    match["home_score"] = home_score
                    match["away_score"] = away_score
                    break

# Global enhanced API integration instance
enhanced_api_integration = EnhancedSportsAPIIntegration()

@router.get("/providers")
async def get_available_providers():
    """Get list of available API providers with enhanced status."""
    providers = []
    for api_type, config in enhanced_api_integration.api_key_manager.api_configs.items():
        providers.append({
            "name": config.name,
            "type": api_type,
            "base_url": config.base_url,
            "rate_limit": config.rate_limit,
            "requires_auth": config.requires_auth,
            "working": config.working,
            "has_api_key": bool(config.api_key),
            "enabled": config.enabled
        })
    
    return {
        "success": True,
        "providers": providers,
        "total_providers": len(providers),
        "working_providers": len([p for p in providers if p["working"]]),
        "enabled_providers": len([p for p in providers if p["enabled"]]),
        "penetration_enabled": PENETRATION_CONFIG["enabled"],
        "ml_enabled": ML_CONFIG["enabled"],
        "mobile_enabled": MOBILE_CONFIG["enabled"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/sports-coverage")
async def get_sports_coverage():
    """Get available sports coverage."""
    return {
        "success": True,
        "sports_coverage": SPORTS_COVERAGE,
        "total_sports": len(SPORTS_COVERAGE),
        "enabled_sports": len([s for s in SPORTS_COVERAGE.values() if s["enabled"]]),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/live-matches/{sport}")
async def get_live_matches_enhanced(sport: str = "basketball"):
    """Get live matches with enhanced features."""
    return await enhanced_api_integration.get_live_matches_enhanced(sport)

@router.get("/odds/{match_id}")
async def get_odds_enhanced(match_id: str, sport: str = "basketball"):
    """Get odds with enhanced features."""
    return await enhanced_api_integration.get_odds_enhanced(match_id, sport)

@router.get("/teams/{sport}")
async def get_teams(sport: str = "basketball"):
    """Get teams for a sport."""
    teams = enhanced_api_integration.live_simulator.get_teams(sport)
    return {
        "success": True,
        "data": {
            "teams": teams,
            "total": len(teams),
            "sport": sport
        },
        "api": "LiveSportsSimulator",
        "method": "simulator",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/analysis/{match_id}")
async def get_comprehensive_analysis(match_id: str, sport: str = "basketball"):
    """Get comprehensive match analysis with ML predictions."""
    return await enhanced_api_integration.get_comprehensive_analysis(match_id, sport)

@router.get("/penetration/{api_type}")
async def attempt_api_penetration(api_type: str, endpoint: str = ""):
    """Attempt advanced penetration on specific API."""
    try:
        url = f"{enhanced_api_integration.api_key_manager.get_api_config(api_type).base_url}/{endpoint}" if endpoint else enhanced_api_integration.api_key_manager.get_api_config(api_type).base_url
        results = await enhanced_api_integration.penetration_engine.comprehensive_penetration(url, api_type)
        
        successful_results = [r for r in results if r.success]
        
        return {
            "success": len(successful_results) > 0,
            "api": api_type,
            "url": url,
            "total_techniques": len(results),
            "successful_techniques": len(successful_results),
            "results": [
                {
                    "technique": r.technique,
                    "success": r.success,
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "error": r.error
                } for r in results
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Penetration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/history")
async def get_prediction_history(limit: int = 10):
    """Get prediction history."""
    history = enhanced_api_integration.prediction_engine.get_prediction_history(limit)
    return {
        "success": True,
        "predictions": [
            {
                "prediction_type": pred.prediction_type,
                "prediction": pred.prediction,
                "confidence": pred.confidence,
                "probability": pred.probability,
                "risk_level": pred.risk_level,
                "model_used": pred.model_used,
                "timestamp": pred.timestamp.isoformat(),
                "historical_accuracy": pred.historical_accuracy
            } for pred in history
        ],
        "total_predictions": len(history),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/predictions/accuracy")
async def get_prediction_accuracy():
    """Get prediction accuracy by type."""
    accuracy = enhanced_api_integration.prediction_engine.get_prediction_accuracy()
    return {
        "success": True,
        "accuracy_by_type": accuracy,
        "overall_accuracy": sum(accuracy.values()) / len(accuracy) if accuracy else 0,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/mobile/status")
async def get_mobile_status():
    """Get mobile app status and configuration."""
    return {
        "success": True,
        "mobile_config": {
            "enabled": MOBILE_CONFIG["enabled"],
            "analytics_enabled": MOBILE_CONFIG["analytics_enabled"],
            "push_notifications_enabled": MOBILE_CONFIG["push_notifications_enabled"],
            "has_expo_token": bool(MOBILE_CONFIG["expo_access_token"]),
            "has_firebase_config": bool(MOBILE_CONFIG["firebase_server_key"])
        },
        "supported_platforms": ["iOS", "Android"],
        "features": [
            "Live match tracking",
            "Real-time odds",
            "ML predictions",
            "Push notifications",
            "Offline support"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/simulator/update-score")
async def update_live_score(match_id: str, home_score: int, away_score: int):
    """Update live score in simulator."""
    enhanced_api_integration.live_simulator.update_scores(match_id, home_score, away_score)
    return {
        "success": True,
        "message": f"Updated score for {match_id}: {home_score}-{away_score}",
        "timestamp": datetime.now().isoformat()
    }

@router.on_event("shutdown")
async def shutdown_event():
    await enhanced_api_integration.close_session()
    await enhanced_api_integration.penetration_engine.shutdown() 