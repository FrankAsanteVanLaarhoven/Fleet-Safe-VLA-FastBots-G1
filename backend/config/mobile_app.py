#!/usr/bin/env python3
"""
Mobile App Configuration for iOS/Android
=======================================

Configuration for native mobile applications:
- Push notifications
- Real-time updates
- Offline support
- Analytics
- Cross-platform features
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio

# Mobile app imports
try:
    from expo_server_sdk import PushClient, PushMessage
    from firebase_admin import credentials, messaging, initialize_app
    MOBILE_AVAILABLE = True
except ImportError:
    MOBILE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MobileAppConfig:
    """Mobile app configuration."""
    enabled: bool = False
    platform: str = "both"  # ios, android, both
    push_notifications: bool = False
    analytics: bool = False
    offline_support: bool = False
    real_time_updates: bool = False

@dataclass
class PushNotificationConfig:
    """Push notification configuration."""
    title: str
    body: str
    data: Dict[str, Any]
    sound: str = "default"
    badge: int = 1
    priority: str = "high"
    ttl: int = 3600

class MobileAppManager:
    """Mobile app manager for iOS/Android applications."""
    
    def __init__(self):
        self.config = self._load_config()
        self.push_client = None
        self.firebase_app = None
        self.device_tokens = {}  # Store device tokens by user
        self.notification_history = []
        
        if MOBILE_AVAILABLE and self.config.enabled:
            self._initialize_services()
    
    def _load_config(self) -> MobileAppConfig:
        """Load mobile app configuration from environment."""
        return MobileAppConfig(
            enabled=os.getenv("MOBILE_APP_ENABLED", "true").lower() == "true",
            platform=os.getenv("MOBILE_PLATFORM", "both"),
            push_notifications=os.getenv("PUSH_NOTIFICATIONS_ENABLED", "true").lower() == "true",
            analytics=os.getenv("ANALYTICS_ENABLED", "true").lower() == "true",
            offline_support=os.getenv("OFFLINE_SUPPORT_ENABLED", "true").lower() == "true",
            real_time_updates=os.getenv("REAL_TIME_UPDATES_ENABLED", "true").lower() == "true"
        )
    
    def _initialize_services(self):
        """Initialize mobile services."""
        # Initialize Expo push client
        try:
            expo_token = os.getenv("EXPO_ACCESS_TOKEN")
            if expo_token:
                self.push_client = PushClient(access_token=expo_token)
                logger.info("✅ Expo push client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Expo push client: {e}")
        
        # Initialize Firebase
        try:
            firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
            if firebase_credentials:
                cred = credentials.Certificate(json.loads(firebase_credentials))
                self.firebase_app = initialize_app(cred)
                logger.info("✅ Firebase initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase: {e}")
    
    async def register_device(self, user_id: str, device_token: str, platform: str = "both") -> bool:
        """Register a device for push notifications."""
        try:
            if user_id not in self.device_tokens:
                self.device_tokens[user_id] = []
            
            device_info = {
                "token": device_token,
                "platform": platform,
                "registered_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
            
            # Check if device already registered
            existing_devices = [d for d in self.device_tokens[user_id] if d["token"] == device_token]
            if existing_devices:
                # Update existing device
                existing_devices[0].update(device_info)
            else:
                # Add new device
                self.device_tokens[user_id].append(device_info)
            
            logger.info(f"Device registered for user {user_id}: {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register device: {e}")
            return False
    
    async def unregister_device(self, user_id: str, device_token: str) -> bool:
        """Unregister a device."""
        try:
            if user_id in self.device_tokens:
                self.device_tokens[user_id] = [
                    d for d in self.device_tokens[user_id] 
                    if d["token"] != device_token
                ]
                logger.info(f"Device unregistered for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister device: {e}")
            return False
    
    async def send_push_notification(self, user_id: str, notification: PushNotificationConfig) -> bool:
        """Send push notification to user's devices."""
        if not self.config.push_notifications:
            return False
        
        try:
            if user_id not in self.device_tokens:
                logger.warning(f"No devices registered for user {user_id}")
                return False
            
            devices = self.device_tokens[user_id]
            if not devices:
                logger.warning(f"No active devices for user {user_id}")
                return False
            
            success_count = 0
            
            for device in devices:
                try:
                    if device["platform"] in ["ios", "both"] and self.push_client:
                        # Send via Expo
                        expo_message = PushMessage(
                            to=device["token"],
                            title=notification.title,
                            body=notification.body,
                            data=notification.data,
                            sound=notification.sound,
                            badge=notification.badge,
                            priority=notification.priority,
                            ttl=notification.ttl
                        )
                        
                        response = await asyncio.to_thread(
                            self.push_client.send,
                            expo_message
                        )
                        
                        if response.is_success():
                            success_count += 1
                            logger.info(f"Expo notification sent to {device['token']}")
                        else:
                            logger.warning(f"Expo notification failed: {response.errors}")
                    
                    elif device["platform"] in ["android", "both"] and self.firebase_app:
                        # Send via Firebase
                        firebase_message = messaging.Message(
                            notification=messaging.Notification(
                                title=notification.title,
                                body=notification.body
                            ),
                            data=notification.data,
                            token=device["token"],
                            android=messaging.AndroidConfig(
                                priority="high",
                                notification=messaging.AndroidNotification(
                                    sound="default",
                                    priority="high"
                                )
                            )
                        )
                        
                        response = await asyncio.to_thread(
                            messaging.send,
                            firebase_message
                        )
                        
                        success_count += 1
                        logger.info(f"Firebase notification sent: {response}")
                    
                    # Update last active timestamp
                    device["last_active"] = datetime.now().isoformat()
                    
                except Exception as e:
                    logger.error(f"Failed to send notification to device {device['token']}: {e}")
                    continue
            
            # Log notification
            self.notification_history.append({
                "user_id": user_id,
                "notification": {
                    "title": notification.title,
                    "body": notification.body,
                    "data": notification.data
                },
                "devices_targeted": len(devices),
                "successful_sends": success_count,
                "timestamp": datetime.now().isoformat()
            })
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
    
    async def send_match_update(self, user_id: str, match_data: Dict[str, Any]) -> bool:
        """Send match update notification."""
        notification = PushNotificationConfig(
            title=f"Match Update: {match_data.get('home_team', '')} vs {match_data.get('away_team', '')}",
            body=f"Score: {match_data.get('home_score', 0)} - {match_data.get('away_score', 0)}",
            data={
                "type": "match_update",
                "match_id": match_data.get("id", ""),
                "sport": match_data.get("sport", ""),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return await self.send_push_notification(user_id, notification)
    
    async def send_prediction_alert(self, user_id: str, prediction_data: Dict[str, Any]) -> bool:
        """Send prediction alert notification."""
        notification = PushNotificationConfig(
            title="New Betting Prediction",
            body=f"{prediction_data.get('prediction', '')} - Confidence: {prediction_data.get('confidence', 0):.1%}",
            data={
                "type": "prediction_alert",
                "prediction": prediction_data.get("prediction", ""),
                "confidence": prediction_data.get("confidence", 0),
                "risk_level": prediction_data.get("risk_level", ""),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return await self.send_push_notification(user_id, notification)
    
    async def send_odds_update(self, user_id: str, odds_data: Dict[str, Any]) -> bool:
        """Send odds update notification."""
        notification = PushNotificationConfig(
            title="Odds Update",
            body=f"New odds available for your tracked matches",
            data={
                "type": "odds_update",
                "odds": odds_data,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return await self.send_push_notification(user_id, notification)
    
    def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's registered devices."""
        return self.device_tokens.get(user_id, [])
    
    def get_notification_history(self, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notification history."""
        history = self.notification_history
        
        if user_id:
            history = [n for n in history if n["user_id"] == user_id]
        
        return history[-limit:] if history else []
    
    def get_mobile_stats(self) -> Dict[str, Any]:
        """Get mobile app statistics."""
        total_users = len(self.device_tokens)
        total_devices = sum(len(devices) for devices in self.device_tokens.values())
        total_notifications = len(self.notification_history)
        
        platform_stats = {"ios": 0, "android": 0, "both": 0}
        for devices in self.device_tokens.values():
            for device in devices:
                platform = device.get("platform", "both")
                platform_stats[platform] += 1
        
        return {
            "total_users": total_users,
            "total_devices": total_devices,
            "total_notifications": total_notifications,
            "platform_distribution": platform_stats,
            "config": {
                "enabled": self.config.enabled,
                "push_notifications": self.config.push_notifications,
                "analytics": self.config.analytics,
                "offline_support": self.config.offline_support,
                "real_time_updates": self.config.real_time_updates
            },
            "services": {
                "expo_available": self.push_client is not None,
                "firebase_available": self.firebase_app is not None
            }
        }

# Global mobile app manager instance
mobile_app_manager = MobileAppManager()

# Mobile app API endpoints
async def send_bulk_notification(user_ids: List[str], notification: PushNotificationConfig) -> Dict[str, int]:
    """Send notification to multiple users."""
    results = {"success": 0, "failed": 0}
    
    for user_id in user_ids:
        success = await mobile_app_manager.send_push_notification(user_id, notification)
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
    
    return results

async def cleanup_inactive_devices(days_inactive: int = 30) -> int:
    """Clean up devices that haven't been active for specified days."""
    cutoff_date = datetime.now() - timedelta(days=days_inactive)
    removed_count = 0
    
    for user_id, devices in mobile_app_manager.device_tokens.items():
        original_count = len(devices)
        mobile_app_manager.device_tokens[user_id] = [
            device for device in devices
            if datetime.fromisoformat(device["last_active"]) > cutoff_date
        ]
        removed_count += original_count - len(mobile_app_manager.device_tokens[user_id])
    
    return removed_count 