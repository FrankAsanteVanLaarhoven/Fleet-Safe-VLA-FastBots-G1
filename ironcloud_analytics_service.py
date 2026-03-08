"""
IronCloud AI Advanced Analytics Service

This service provides comprehensive analytics capabilities including:
- Real-time system metrics
- Performance monitoring
- User behavior analytics
- AI model performance tracking
- Predictive analytics
- Business intelligence dashboards
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from collections import defaultdict, deque
import statistics
import math

from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AnalyticsEvent(Enum):
    USER_LOGIN = "user_login"
    API_CALL = "api_call"
    RAG_SEARCH = "rag_search"
    AI_GENERATION = "ai_generation"
    MCP_EXECUTION = "mcp_execution"
    LANGGRAPH_WORKFLOW = "langgraph_workflow"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_ALERT = "performance_alert"


@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: Dict[str, str]
    metric_type: MetricType


@dataclass
class AnalyticsEvent:
    event_type: str
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class PerformanceMetrics:
    response_time: float
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float


@dataclass
class AIModelMetrics:
    model_name: str
    requests_per_minute: float
    average_response_time: float
    success_rate: float
    token_usage: int
    cost_per_request: float


@dataclass
class UserAnalytics:
    user_id: str
    session_count: int
    total_requests: int
    favorite_features: List[str]
    usage_patterns: Dict[str, Any]
    engagement_score: float


class IronCloudAnalyticsService:
    """Advanced analytics service for IronCloud AI platform"""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.events: deque = deque(maxlen=50000)
        self.performance_history: deque = deque(maxlen=1000)
        self.ai_model_metrics: Dict[str, AIModelMetrics] = {}
        self.user_analytics: Dict[str, UserAnalytics] = {}
        self.alerts: deque = deque(maxlen=1000)
        
        # Real-time counters
        self.request_counter = 0
        self.error_counter = 0
        self.active_users = set()
        self.active_sessions = set()
        
        # Performance thresholds
        self.performance_thresholds = {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0
        }
    
    async def record_metric(self, name: str, value: float, labels: Dict[str, str] = None, metric_type: MetricType = MetricType.GAUGE):
        """Record a metric point"""
        try:
            metric_point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {},
                metric_type=metric_type
            )
            self.metrics[name].append(metric_point)
            
            # Check for performance alerts
            await self._check_performance_alerts(name, value)
            
            logger.debug(f"Recorded metric: {name} = {value}")
            
        except Exception as e:
            logger.error(f"Error recording metric {name}: {str(e)}")
    
    async def record_event(self, event_type: str, user_id: str = None, session_id: str = None, data: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        """Record an analytics event"""
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id,
                data=data or {},
                metadata=metadata or {}
            )
            self.events.append(event)
            
            # Update counters
            self.request_counter += 1
            if user_id:
                self.active_users.add(user_id)
            if session_id:
                self.active_sessions.add(session_id)
            
            logger.debug(f"Recorded event: {event_type}")
            
        except Exception as e:
            logger.error(f"Error recording event {event_type}: {str(e)}")
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        try:
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)
            
            # Calculate metrics
            hourly_requests = len([e for e in self.events if e.timestamp >= last_hour])
            daily_requests = len([e for e in self.events if e.timestamp >= last_24h])
            
            # Performance metrics
            recent_performance = list(self.performance_history)[-100:] if self.performance_history else []
            avg_response_time = statistics.mean([p.response_time for p in recent_performance]) if recent_performance else 0
            avg_error_rate = statistics.mean([p.error_rate for p in recent_performance]) if recent_performance else 0
            
            # AI model analytics
            ai_analytics = {}
            for model_name, metrics in self.ai_model_metrics.items():
                ai_analytics[model_name] = {
                    "requests_per_minute": metrics.requests_per_minute,
                    "average_response_time": metrics.average_response_time,
                    "success_rate": metrics.success_rate,
                    "total_tokens": metrics.token_usage,
                    "estimated_cost": metrics.cost_per_request * metrics.requests_per_minute
                }
            
            # User analytics
            user_analytics = {}
            for user_id, analytics in self.user_analytics.items():
                user_analytics[user_id] = {
                    "session_count": analytics.session_count,
                    "total_requests": analytics.total_requests,
                    "favorite_features": analytics.favorite_features,
                    "engagement_score": analytics.engagement_score
                }
            
            return {
                "system": "ironcloud-ai-analytics",
                "version": "2.0.0",
                "timestamp": now.isoformat(),
                
                # Real-time metrics
                "real_time": {
                    "active_users": len(self.active_users),
                    "active_sessions": len(self.active_sessions),
                    "total_requests": self.request_counter,
                    "total_errors": self.error_counter,
                    "uptime_seconds": (now - datetime(2025, 1, 1)).total_seconds()
                },
                
                # Performance metrics
                "performance": {
                    "average_response_time_ms": round(avg_response_time, 2),
                    "average_error_rate_percent": round(avg_error_rate, 2),
                    "requests_per_hour": hourly_requests,
                    "requests_per_day": daily_requests,
                    "throughput_rps": round(hourly_requests / 3600, 2)
                },
                
                # Service health
                "services": {
                    "rag": {"status": "healthy", "documents": 100, "searches_per_hour": hourly_requests // 4},
                    "mcp": {"status": "healthy", "tools": 4, "executions_per_hour": hourly_requests // 4},
                    "ai": {"status": "healthy", "agents": 3, "generations_per_hour": hourly_requests // 4},
                    "langgraph": {"status": "healthy", "workflows": 3, "executions_per_hour": hourly_requests // 4}
                },
                
                # AI model analytics
                "ai_models": ai_analytics,
                
                # User analytics
                "users": user_analytics,
                
                # Alerts
                "alerts": {
                    "total_alerts": len(self.alerts),
                    "recent_alerts": list(self.alerts)[-10:],
                    "alert_levels": {
                        "critical": len([a for a in self.alerts if a.get("level") == "critical"]),
                        "warning": len([a for a in self.alerts if a.get("level") == "warning"]),
                        "info": len([a for a in self.alerts if a.get("level") == "info"])
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_performance_analytics(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get detailed performance analytics"""
        try:
            now = datetime.now()
            
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(hours=24)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(hours=1)
            
            # Filter recent performance data
            recent_performance = [p for p in self.performance_history if p.timestamp >= start_time]
            
            if not recent_performance:
                return {"message": "No performance data available for the specified time range"}
            
            # Calculate performance statistics
            response_times = [p.response_time for p in recent_performance]
            throughputs = [p.throughput for p in recent_performance]
            error_rates = [p.error_rate for p in recent_performance]
            
            return {
                "time_range": time_range,
                "data_points": len(recent_performance),
                "response_time": {
                    "min": min(response_times),
                    "max": max(response_times),
                    "average": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                    "p95": sorted(response_times)[int(len(response_times) * 0.95)],
                    "p99": sorted(response_times)[int(len(response_times) * 0.99)]
                },
                "throughput": {
                    "min": min(throughputs),
                    "max": max(throughputs),
                    "average": statistics.mean(throughputs),
                    "trend": "increasing" if throughputs[-1] > throughputs[0] else "decreasing"
                },
                "error_rate": {
                    "min": min(error_rates),
                    "max": max(error_rates),
                    "average": statistics.mean(error_rates),
                    "trend": "decreasing" if error_rates[-1] < error_rates[0] else "increasing"
                },
                "performance_score": self._calculate_performance_score(recent_performance)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_user_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Get user analytics"""
        try:
            if user_id:
                if user_id not in self.user_analytics:
                    return {"error": "User not found"}
                
                analytics = self.user_analytics[user_id]
                return {
                    "user_id": user_id,
                    "analytics": asdict(analytics),
                    "recent_activity": [
                        {"event_type": e.event_type, "timestamp": e.timestamp.isoformat()}
                        for e in list(self.events)[-50:]
                        if e.user_id == user_id
                    ]
                }
            else:
                # Return aggregated user analytics
                total_users = len(self.user_analytics)
                total_sessions = sum(a.session_count for a in self.user_analytics.values())
                total_requests = sum(a.total_requests for a in self.user_analytics.values())
                avg_engagement = statistics.mean([a.engagement_score for a in self.user_analytics.values()]) if self.user_analytics else 0
                
                return {
                    "total_users": total_users,
                    "total_sessions": total_sessions,
                    "total_requests": total_requests,
                    "average_engagement_score": round(avg_engagement, 2),
                    "top_users": sorted(
                        [(uid, a.engagement_score) for uid, a in self.user_analytics.items()],
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                }
                
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_ai_model_analytics(self, model_name: str = None) -> Dict[str, Any]:
        """Get AI model analytics"""
        try:
            if model_name:
                if model_name not in self.ai_model_metrics:
                    return {"error": "Model not found"}
                
                metrics = self.ai_model_metrics[model_name]
                return {
                    "model_name": model_name,
                    "metrics": asdict(metrics),
                    "efficiency_score": self._calculate_model_efficiency(metrics)
                }
            else:
                # Return aggregated AI model analytics
                total_models = len(self.ai_model_metrics)
                total_requests = sum(m.requests_per_minute for m in self.ai_model_metrics.values())
                avg_response_time = statistics.mean([m.average_response_time for m in self.ai_model_metrics.values()]) if self.ai_model_metrics else 0
                avg_success_rate = statistics.mean([m.success_rate for m in self.ai_model_metrics.values()]) if self.ai_model_metrics else 0
                
                return {
                    "total_models": total_models,
                    "total_requests_per_minute": total_requests,
                    "average_response_time": round(avg_response_time, 2),
                    "average_success_rate": round(avg_success_rate, 2),
                    "models": {
                        name: {
                            "requests_per_minute": metrics.requests_per_minute,
                            "success_rate": metrics.success_rate,
                            "efficiency_score": self._calculate_model_efficiency(metrics)
                        }
                        for name, metrics in self.ai_model_metrics.items()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting AI model analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_predictive_analytics(self) -> Dict[str, Any]:
        """Get predictive analytics and trends"""
        try:
            # Simple trend analysis
            recent_events = list(self.events)[-1000:] if len(self.events) > 1000 else list(self.events)
            
            if len(recent_events) < 10:
                return {"message": "Insufficient data for predictive analytics"}
            
            # Analyze trends
            hourly_counts = defaultdict(int)
            for event in recent_events:
                hour = event.timestamp.replace(minute=0, second=0, microsecond=0)
                hourly_counts[hour] += 1
            
            # Calculate trend
            sorted_hours = sorted(hourly_counts.keys())
            if len(sorted_hours) >= 2:
                recent_trend = hourly_counts[sorted_hours[-1]] - hourly_counts[sorted_hours[-2]]
                trend_direction = "increasing" if recent_trend > 0 else "decreasing" if recent_trend < 0 else "stable"
            else:
                trend_direction = "stable"
            
            # Predict next hour
            if len(sorted_hours) >= 3:
                recent_avg = statistics.mean([hourly_counts[h] for h in sorted_hours[-3:]])
                prediction = round(recent_avg * 1.1 if trend_direction == "increasing" else recent_avg * 0.9, 2)
            else:
                prediction = hourly_counts[sorted_hours[-1]] if sorted_hours else 0
            
            return {
                "current_trend": trend_direction,
                "predicted_requests_next_hour": prediction,
                "confidence_level": "medium",
                "trend_analysis": {
                    "data_points": len(sorted_hours),
                    "average_requests_per_hour": round(statistics.mean(hourly_counts.values()), 2),
                    "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0].isoformat() if hourly_counts else None
                },
                "recommendations": self._generate_recommendations(hourly_counts, trend_direction)
            }
            
        except Exception as e:
            logger.error(f"Error getting predictive analytics: {str(e)}")
            return {"error": str(e)}
    
    async def _check_performance_alerts(self, metric_name: str, value: float):
        """Check for performance alerts"""
        try:
            threshold = self.performance_thresholds.get(metric_name)
            if threshold and value > threshold:
                alert = {
                    "level": "warning" if value < threshold * 1.5 else "critical",
                    "metric": metric_name,
                    "value": value,
                    "threshold": threshold,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"{metric_name} exceeded threshold: {value} > {threshold}"
                }
                self.alerts.append(alert)
                logger.warning(f"Performance alert: {alert['message']}")
                
        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")
    
    def _calculate_performance_score(self, performance_data: List[PerformanceMetrics]) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            if not performance_data:
                return 0.0
            
            # Calculate individual scores
            response_time_score = max(0, 100 - statistics.mean([p.response_time for p in performance_data]) / 10)
            error_rate_score = max(0, 100 - statistics.mean([p.error_rate for p in performance_data]) * 10)
            throughput_score = min(100, statistics.mean([p.throughput for p in performance_data]) * 10)
            
            # Weighted average
            return round((response_time_score * 0.4 + error_rate_score * 0.4 + throughput_score * 0.2), 2)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0.0
    
    def _calculate_model_efficiency(self, metrics: AIModelMetrics) -> float:
        """Calculate AI model efficiency score (0-100)"""
        try:
            # Higher success rate and lower response time = better efficiency
            success_score = metrics.success_rate * 100
            speed_score = max(0, 100 - metrics.average_response_time / 10)
            
            return round((success_score * 0.7 + speed_score * 0.3), 2)
            
        except Exception as e:
            logger.error(f"Error calculating model efficiency: {str(e)}")
            return 0.0
    
    def _generate_recommendations(self, hourly_counts: Dict, trend_direction: str) -> List[str]:
        """Generate recommendations based on analytics"""
        recommendations = []
        
        if trend_direction == "increasing":
            recommendations.append("Consider scaling up resources to handle increased load")
            recommendations.append("Monitor system performance closely")
        elif trend_direction == "decreasing":
            recommendations.append("Consider optimizing resource usage")
            recommendations.append("Review user engagement strategies")
        
        avg_requests = statistics.mean(hourly_counts.values()) if hourly_counts else 0
        if avg_requests > 1000:
            recommendations.append("High traffic detected - consider load balancing")
        
        return recommendations
    
    async def update_ai_model_metrics(self, model_name: str, response_time: float, success: bool, tokens_used: int = 0):
        """Update AI model metrics"""
        try:
            if model_name not in self.ai_model_metrics:
                self.ai_model_metrics[model_name] = AIModelMetrics(
                    model_name=model_name,
                    requests_per_minute=0,
                    average_response_time=0,
                    success_rate=0,
                    token_usage=0,
                    cost_per_request=0.01  # Default cost
                )
            
            metrics = self.ai_model_metrics[model_name]
            
            # Update metrics (simplified rolling average)
            metrics.average_response_time = (metrics.average_response_time + response_time) / 2
            metrics.success_rate = (metrics.success_rate + (1.0 if success else 0.0)) / 2
            metrics.token_usage += tokens_used
            metrics.requests_per_minute = min(metrics.requests_per_minute + 1, 60)  # Cap at 60
            
        except Exception as e:
            logger.error(f"Error updating AI model metrics: {str(e)}")
    
    async def update_user_analytics(self, user_id: str, event_type: str, feature_used: str = None):
        """Update user analytics"""
        try:
            if user_id not in self.user_analytics:
                self.user_analytics[user_id] = UserAnalytics(
                    user_id=user_id,
                    session_count=0,
                    total_requests=0,
                    favorite_features=[],
                    usage_patterns={},
                    engagement_score=0.0
                )
            
            analytics = self.user_analytics[user_id]
            analytics.total_requests += 1
            
            if feature_used:
                if feature_used not in analytics.favorite_features:
                    analytics.favorite_features.append(feature_used)
                analytics.favorite_features = analytics.favorite_features[-5:]  # Keep top 5
            
            # Update engagement score
            analytics.engagement_score = min(100, analytics.engagement_score + 1)
            
        except Exception as e:
            logger.error(f"Error updating user analytics: {str(e)}")


# Global analytics service instance
analytics_service = IronCloudAnalyticsService()
