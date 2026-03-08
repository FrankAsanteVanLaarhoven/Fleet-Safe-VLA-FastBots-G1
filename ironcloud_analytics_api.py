"""
IronCloud AI Analytics API

This module provides comprehensive analytics API endpoints including:
- Real-time system metrics
- Performance monitoring
- User behavior analytics
- AI model performance tracking
- Predictive analytics
- Business intelligence dashboards
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from ironcloud_analytics_service import analytics_service, PerformanceMetrics, MetricType

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Request Models
class MetricRecordRequest(BaseModel):
    name: str
    value: float
    labels: Optional[Dict[str, str]] = None
    metric_type: str = "gauge"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "response_time_ms",
                "value": 150.5,
                "labels": {"service": "rag", "endpoint": "search"},
                "metric_type": "gauge"
            }
        }


class EventRecordRequest(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "rag_search",
                "user_id": "user123",
                "session_id": "session456",
                "data": {"query": "IronCloud AI features", "results_count": 5},
                "metadata": {"source": "web_interface"}
            }
        }


class PerformanceMetricsRequest(BaseModel):
    response_time: float
    throughput: float
    error_rate: float
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "response_time": 150.5,
                "throughput": 100.0,
                "error_rate": 0.5,
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1
            }
        }


# Response Models
class AnalyticsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: Optional[str] = None


class MetricsResponse(BaseModel):
    metric_name: str
    value: float
    timestamp: str
    labels: Dict[str, str]
    metric_type: str


class PerformanceResponse(BaseModel):
    time_range: str
    data_points: int
    response_time: Dict[str, float]
    throughput: Dict[str, float]
    error_rate: Dict[str, float]
    performance_score: float


# API Endpoints
@router.get("/status")
async def get_analytics_status():
    """Get analytics service status and availability."""
    try:
        return {
            "service": "ironcloud-analytics",
            "status": "healthy",
            "available": True,
            "features": {
                "real_time_metrics": True,
                "performance_monitoring": True,
                "user_analytics": True,
                "ai_model_analytics": True,
                "predictive_analytics": True,
                "business_intelligence": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics service error: {str(e)}")


@router.get("/system", response_model=AnalyticsResponse)
async def get_system_analytics():
    """Get comprehensive system analytics."""
    try:
        analytics_data = await analytics_service.get_system_analytics()
        
        return AnalyticsResponse(
            success=True,
            data=analytics_data,
            timestamp=datetime.now().isoformat(),
            message="System analytics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system analytics: {str(e)}")


@router.get("/performance", response_model=PerformanceResponse)
async def get_performance_analytics(
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d")
):
    """Get detailed performance analytics."""
    try:
        performance_data = await analytics_service.get_performance_analytics(time_range)
        
        if "error" in performance_data:
            raise HTTPException(status_code=400, detail=performance_data["error"])
        
        return PerformanceResponse(
            time_range=performance_data["time_range"],
            data_points=performance_data["data_points"],
            response_time=performance_data["response_time"],
            throughput=performance_data["throughput"],
            error_rate=performance_data["error_rate"],
            performance_score=performance_data["performance_score"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")


@router.get("/users")
async def get_user_analytics(user_id: Optional[str] = Query(None, description="Specific user ID")):
    """Get user analytics."""
    try:
        user_data = await analytics_service.get_user_analytics(user_id)
        
        if "error" in user_data:
            raise HTTPException(status_code=404, detail=user_data["error"])
        
        return AnalyticsResponse(
            success=True,
            data=user_data,
            timestamp=datetime.now().isoformat(),
            message="User analytics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")


@router.get("/ai-models")
async def get_ai_model_analytics(model_name: Optional[str] = Query(None, description="Specific model name")):
    """Get AI model analytics."""
    try:
        model_data = await analytics_service.get_ai_model_analytics(model_name)
        
        if "error" in model_data:
            raise HTTPException(status_code=404, detail=model_data["error"])
        
        return AnalyticsResponse(
            success=True,
            data=model_data,
            timestamp=datetime.now().isoformat(),
            message="AI model analytics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI model analytics: {str(e)}")


@router.get("/predictive")
async def get_predictive_analytics():
    """Get predictive analytics and trends."""
    try:
        predictive_data = await analytics_service.get_predictive_analytics()
        
        if "error" in predictive_data:
            raise HTTPException(status_code=500, detail=predictive_data["error"])
        
        return AnalyticsResponse(
            success=True,
            data=predictive_data,
            timestamp=datetime.now().isoformat(),
            message="Predictive analytics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get predictive analytics: {str(e)}")


@router.post("/metrics")
async def record_metric(request: MetricRecordRequest):
    """Record a metric point."""
    try:
        metric_type = MetricType(request.metric_type)
        await analytics_service.record_metric(
            name=request.name,
            value=request.value,
            labels=request.labels,
            metric_type=metric_type
        )
        
        return AnalyticsResponse(
            success=True,
            data={"metric_name": request.name, "value": request.value},
            timestamp=datetime.now().isoformat(),
            message="Metric recorded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record metric: {str(e)}")


@router.post("/events")
async def record_event(request: EventRecordRequest):
    """Record an analytics event."""
    try:
        await analytics_service.record_event(
            event_type=request.event_type,
            user_id=request.user_id,
            session_id=request.session_id,
            data=request.data,
            metadata=request.metadata
        )
        
        return AnalyticsResponse(
            success=True,
            data={"event_type": request.event_type},
            timestamp=datetime.now().isoformat(),
            message="Event recorded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record event: {str(e)}")


@router.post("/performance")
async def record_performance_metrics(request: PerformanceMetricsRequest):
    """Record performance metrics."""
    try:
        performance_metrics = PerformanceMetrics(
            response_time=request.response_time,
            throughput=request.throughput,
            error_rate=request.error_rate,
            cpu_usage=request.cpu_usage or 0.0,
            memory_usage=request.memory_usage or 0.0,
            disk_usage=request.disk_usage or 0.0
        )
        
        analytics_service.performance_history.append(performance_metrics)
        
        return AnalyticsResponse(
            success=True,
            data={
                "response_time": request.response_time,
                "throughput": request.throughput,
                "error_rate": request.error_rate
            },
            timestamp=datetime.now().isoformat(),
            message="Performance metrics recorded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record performance metrics: {str(e)}")


@router.get("/metrics/{metric_name}")
async def get_metric_history(
    metric_name: str = Path(..., description="Name of the metric"),
    limit: int = Query(100, description="Number of data points to return")
):
    """Get metric history for a specific metric."""
    try:
        if metric_name not in analytics_service.metrics:
            raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
        
        metric_data = list(analytics_service.metrics[metric_name])[-limit:]
        
        return AnalyticsResponse(
            success=True,
            data={
                "metric_name": metric_name,
                "data_points": len(metric_data),
                "history": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "labels": point.labels,
                        "metric_type": point.metric_type.value
                    }
                    for point in metric_data
                ]
            },
            timestamp=datetime.now().isoformat(),
            message=f"Metric history for '{metric_name}' retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metric history: {str(e)}")


@router.get("/alerts")
async def get_alerts(limit: int = Query(50, description="Number of alerts to return")):
    """Get recent alerts."""
    try:
        recent_alerts = list(analytics_service.alerts)[-limit:]
        
        return AnalyticsResponse(
            success=True,
            data={
                "total_alerts": len(analytics_service.alerts),
                "recent_alerts": recent_alerts,
                "alert_summary": {
                    "critical": len([a for a in recent_alerts if a.get("level") == "critical"]),
                    "warning": len([a for a in recent_alerts if a.get("level") == "warning"]),
                    "info": len([a for a in recent_alerts if a.get("level") == "info"])
                }
            },
            timestamp=datetime.now().isoformat(),
            message="Alerts retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.get("/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data."""
    try:
        # Gather all analytics data
        system_analytics = await analytics_service.get_system_analytics()
        performance_analytics = await analytics_service.get_performance_analytics("1h")
        predictive_analytics = await analytics_service.get_predictive_analytics()
        user_analytics = await analytics_service.get_user_analytics()
        ai_model_analytics = await analytics_service.get_ai_model_analytics()
        
        dashboard_data = {
            "overview": {
                "system_status": system_analytics.get("services", {}),
                "real_time_metrics": system_analytics.get("real_time", {}),
                "performance_summary": {
                    "score": performance_analytics.get("performance_score", 0),
                    "response_time_avg": performance_analytics.get("response_time", {}).get("average", 0),
                    "throughput_avg": performance_analytics.get("throughput", {}).get("average", 0)
                }
            },
            "trends": {
                "current_trend": predictive_analytics.get("current_trend", "stable"),
                "predicted_requests": predictive_analytics.get("predicted_requests_next_hour", 0),
                "recommendations": predictive_analytics.get("recommendations", [])
            },
            "users": {
                "total_users": user_analytics.get("total_users", 0),
                "active_users": system_analytics.get("real_time", {}).get("active_users", 0),
                "average_engagement": user_analytics.get("average_engagement_score", 0)
            },
            "ai_models": {
                "total_models": ai_model_analytics.get("total_models", 0),
                "total_requests": ai_model_analytics.get("total_requests_per_minute", 0),
                "average_success_rate": ai_model_analytics.get("average_success_rate", 0)
            },
            "alerts": {
                "total_alerts": len(analytics_service.alerts),
                "recent_alerts": list(analytics_service.alerts)[-10:],
                "alert_levels": system_analytics.get("alerts", {}).get("alert_levels", {})
            }
        }
        
        return AnalyticsResponse(
            success=True,
            data=dashboard_data,
            timestamp=datetime.now().isoformat(),
            message="Analytics dashboard data retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics dashboard: {str(e)}")


@router.get("/health")
async def analytics_health_check():
    """Analytics service health check."""
    try:
        return {
            "status": "healthy",
            "service": "ironcloud-analytics",
            "timestamp": datetime.now().isoformat(),
            "available": True,
            "metrics_count": len(analytics_service.metrics),
            "events_count": len(analytics_service.events),
            "alerts_count": len(analytics_service.alerts),
            "ready": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "ironcloud-analytics",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "ready": False
        }
