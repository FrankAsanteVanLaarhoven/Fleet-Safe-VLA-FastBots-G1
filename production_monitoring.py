"""
Production-Ready Monitoring and Observability System
Implements comprehensive monitoring with Prometheus metrics, health checks, and performance tracking
"""

import asyncio
import logging
import time
import json
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
import sqlite3
import os

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    details: Dict[str, Any] = None

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = None

class ProductionMonitoring:
    """
    Production-ready monitoring system with comprehensive observability.
    
    Features:
    - Prometheus metrics collection and export
    - Real-time health checks and status monitoring
    - Performance tracking and alerting
    - System resource monitoring
    - Custom metric collection
    - Historical data storage and analysis
    """
    
    def __init__(self, service_name: str = "universal_crawler"):
        self.service_name = service_name
        self.start_time = time.time()
        
        # Initialize Prometheus metrics
        self.metrics = self._initialize_prometheus_metrics()
        
        # Health check registry
        self.health_checks = {}
        self.health_status = HealthStatus.HEALTHY
        
        # Performance tracking
        self.performance_metrics = []
        self.alert_thresholds = {}
        
        # System monitoring
        self.system_metrics = {}
        self.monitoring_db = self._initialize_monitoring_db()
        
        # Background tasks
        self.monitoring_task = None
        self.health_check_task = None
        self.alert_task = None
        
        # Custom metric collectors
        self.custom_collectors = {}
        
        logger.info(f"Production Monitoring initialized for {service_name}")
    
    def _initialize_prometheus_metrics(self) -> Dict[str, Any]:
        """Initialize Prometheus metrics for comprehensive monitoring."""
        return {
            # Crawler-specific metrics
            "crawl_requests_total": Counter(
                'crawl_requests_total', 
                'Total crawl requests',
                ['target_domain', 'framework', 'status']
            ),
            "crawl_duration_seconds": Histogram(
                'crawl_duration_seconds', 
                'Crawl processing time',
                ['target_domain', 'framework'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            ),
            "active_agents": Gauge(
                'active_agents', 
                'Number of active crawler agents',
                ['agent_type']
            ),
            "crawl_success_rate": Gauge(
                'crawl_success_rate', 
                'Crawl success rate percentage',
                ['target_domain']
            ),
            "data_extracted_bytes": Counter(
                'data_extracted_bytes', 
                'Total bytes of data extracted',
                ['content_type', 'source_domain']
            ),
            
            # System metrics
            "cpu_usage_percent": Gauge(
                'cpu_usage_percent', 
                'CPU usage percentage'
            ),
            "memory_usage_bytes": Gauge(
                'memory_usage_bytes', 
                'Memory usage in bytes'
            ),
            "disk_usage_percent": Gauge(
                'disk_usage_percent', 
                'Disk usage percentage'
            ),
            "network_io_bytes": Counter(
                'network_io_bytes', 
                'Network I/O in bytes',
                ['direction']
            ),
            
            # Business metrics
            "llm_requests_total": Counter(
                'llm_requests_total', 
                'Total LLM requests',
                ['model', 'provider', 'status']
            ),
            "llm_cost_dollars": Counter(
                'llm_cost_dollars', 
                'Total LLM cost in dollars',
                ['model', 'provider']
            ),
            "storage_usage_bytes": Gauge(
                'storage_usage_bytes', 
                'Storage usage in bytes',
                ['tier', 'provider']
            ),
            "storage_cost_dollars": Counter(
                'storage_cost_dollars', 
                'Total storage cost in dollars',
                ['tier', 'provider']
            ),
            
            # Error tracking
            "errors_total": Counter(
                'errors_total', 
                'Total errors',
                ['error_type', 'component', 'severity']
            ),
            "warnings_total": Counter(
                'warnings_total', 
                'Total warnings',
                ['warning_type', 'component']
            ),
            
            # Performance metrics
            "response_time_seconds": Histogram(
                'response_time_seconds', 
                'API response time',
                ['endpoint', 'method'],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
            ),
            "queue_size": Gauge(
                'queue_size', 
                'Queue size',
                ['queue_name']
            ),
            "cache_hit_rate": Gauge(
                'cache_hit_rate', 
                'Cache hit rate percentage',
                ['cache_name']
            )
        }
    
    def _initialize_monitoring_db(self) -> str:
        """Initialize SQLite database for monitoring data."""
        db_path = "monitoring_data.db"
        
        with sqlite3.connect(db_path) as conn:
            # Health checks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TEXT NOT NULL,
                    response_time_ms REAL,
                    details TEXT
                )
            """)
            
            # Performance metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    timestamp TEXT NOT NULL,
                    labels TEXT
                )
            """)
            
            # System metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Alerts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_checks(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
        
        return db_path
    
    async def start_monitoring(self):
        """Start all monitoring background tasks."""
        self.monitoring_task = asyncio.create_task(self._system_monitoring_worker())
        self.health_check_task = asyncio.create_task(self._health_check_worker())
        self.alert_task = asyncio.create_task(self._alert_monitoring_worker())
        
        logger.info("Monitoring background tasks started")
    
    async def stop_monitoring(self):
        """Stop all monitoring background tasks."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.health_check_task:
            self.health_check_task.cancel()
        if self.alert_task:
            self.alert_task.cancel()
        
        logger.info("Monitoring background tasks stopped")
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a custom health check function."""
        self.health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    def record_crawl_metric(self, target_domain: str, framework: str, 
                          duration: float, status: str, data_size: int = 0):
        """Record crawl-related metrics."""
        # Increment request counter
        self.metrics["crawl_requests_total"].labels(
            target_domain=target_domain,
            framework=framework,
            status=status
        ).inc()
        
        # Record duration histogram
        self.metrics["crawl_duration_seconds"].labels(
            target_domain=target_domain,
            framework=framework
        ).observe(duration)
        
        # Record data size if provided
        if data_size > 0:
            self.metrics["data_extracted_bytes"].labels(
                content_type="html",
                source_domain=target_domain
            ).inc(data_size)
        
        # Update success rate
        if status == "success":
            # This is a simplified success rate calculation
            # In production, you'd want to track this over time windows
            pass
    
    def record_llm_metric(self, model: str, provider: str, status: str, cost: float = 0.0):
        """Record LLM-related metrics."""
        self.metrics["llm_requests_total"].labels(
            model=model,
            provider=provider,
            status=status
        ).inc()
        
        if cost > 0:
            self.metrics["llm_cost_dollars"].labels(
                model=model,
                provider=provider
            ).inc(cost)
    
    def record_storage_metric(self, tier: str, provider: str, usage_bytes: int, cost: float = 0.0):
        """Record storage-related metrics."""
        self.metrics["storage_usage_bytes"].labels(
            tier=tier,
            provider=provider
        ).set(usage_bytes)
        
        if cost > 0:
            self.metrics["storage_cost_dollars"].labels(
                tier=tier,
                provider=provider
            ).inc(cost)
    
    def record_error(self, error_type: str, component: str, severity: str = "error"):
        """Record error metrics."""
        self.metrics["errors_total"].labels(
            error_type=error_type,
            component=component,
            severity=severity
        ).inc()
    
    def record_warning(self, warning_type: str, component: str):
        """Record warning metrics."""
        self.metrics["warnings_total"].labels(
            warning_type=warning_type,
            component=component
        ).inc()
    
    def set_active_agents(self, agent_type: str, count: int):
        """Set the number of active agents."""
        self.metrics["active_agents"].labels(agent_type=agent_type).set(count)
    
    def set_queue_size(self, queue_name: str, size: int):
        """Set queue size metric."""
        self.metrics["queue_size"].labels(queue_name=queue_name).set(size)
    
    def set_cache_hit_rate(self, cache_name: str, hit_rate: float):
        """Set cache hit rate metric."""
        self.metrics["cache_hit_rate"].labels(cache_name=cache_name).set(hit_rate)
    
    async def _system_monitoring_worker(self):
        """Background worker for system metrics collection."""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics["cpu_usage_percent"].set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics["memory_usage_bytes"].set(memory.used)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.metrics["disk_usage_percent"].set(disk.percent)
        
        # Network I/O
        network = psutil.net_io_counters()
        self.metrics["network_io_bytes"].labels(direction="bytes_sent").inc(network.bytes_sent)
        self.metrics["network_io_bytes"].labels(direction="bytes_recv").inc(network.bytes_recv)
        
        # Store in database
        await self._store_system_metrics({
            "cpu_usage_percent": cpu_percent,
            "memory_usage_bytes": memory.used,
            "disk_usage_percent": disk.percent,
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_recv": network.bytes_recv
        })
    
    async def _health_check_worker(self):
        """Background worker for health checks."""
        while True:
            try:
                await self._run_health_checks()
                await asyncio.sleep(60)  # Run every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _run_health_checks(self):
        """Run all registered health checks."""
        health_results = []
        
        # Run custom health checks
        for name, check_func in self.health_checks.items():
            try:
                start_time = time.time()
                result = await check_func()
                response_time = (time.time() - start_time) * 1000
                
                health_check = HealthCheck(
                    name=name,
                    status=result.get("status", HealthStatus.HEALTHY),
                    message=result.get("message", "OK"),
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details=result.get("details", {})
                )
                
                health_results.append(health_check)
                
            except Exception as e:
                health_check = HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {e}",
                    timestamp=datetime.now(),
                    response_time_ms=0,
                    details={"error": str(e)}
                )
                health_results.append(health_check)
        
        # Run built-in health checks
        built_in_checks = await self._run_built_in_health_checks()
        health_results.extend(built_in_checks)
        
        # Update overall health status
        await self._update_health_status(health_results)
        
        # Store health check results
        await self._store_health_checks(health_results)
    
    async def _run_built_in_health_checks(self) -> List[HealthCheck]:
        """Run built-in system health checks."""
        checks = []
        
        # CPU usage check
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            status = HealthStatus.CRITICAL
            message = f"CPU usage critical: {cpu_percent}%"
        elif cpu_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"CPU usage high: {cpu_percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"CPU usage normal: {cpu_percent}%"
        
        checks.append(HealthCheck(
            name="cpu_usage",
            status=status,
            message=message,
            timestamp=datetime.now(),
            response_time_ms=0,
            details={"cpu_percent": cpu_percent}
        ))
        
        # Memory usage check
        memory = psutil.virtual_memory()
        if memory.percent > 95:
            status = HealthStatus.CRITICAL
            message = f"Memory usage critical: {memory.percent}%"
        elif memory.percent > 85:
            status = HealthStatus.DEGRADED
            message = f"Memory usage high: {memory.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory usage normal: {memory.percent}%"
        
        checks.append(HealthCheck(
            name="memory_usage",
            status=status,
            message=message,
            timestamp=datetime.now(),
            response_time_ms=0,
            details={"memory_percent": memory.percent}
        ))
        
        # Disk usage check
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            status = HealthStatus.CRITICAL
            message = f"Disk usage critical: {disk.percent}%"
        elif disk.percent > 85:
            status = HealthStatus.DEGRADED
            message = f"Disk usage high: {disk.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk usage normal: {disk.percent}%"
        
        checks.append(HealthCheck(
            name="disk_usage",
            status=status,
            message=message,
            timestamp=datetime.now(),
            response_time_ms=0,
            details={"disk_percent": disk.percent}
        ))
        
        return checks
    
    async def _update_health_status(self, health_checks: List[HealthCheck]):
        """Update overall health status based on individual checks."""
        critical_count = sum(1 for check in health_checks if check.status == HealthStatus.CRITICAL)
        unhealthy_count = sum(1 for check in health_checks if check.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for check in health_checks if check.status == HealthStatus.DEGRADED)
        
        if critical_count > 0:
            self.health_status = HealthStatus.CRITICAL
        elif unhealthy_count > 0:
            self.health_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            self.health_status = HealthStatus.DEGRADED
        else:
            self.health_status = HealthStatus.HEALTHY
    
    async def _alert_monitoring_worker(self):
        """Background worker for alert monitoring."""
        while True:
            try:
                await self._check_alert_conditions()
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
    
    async def _check_alert_conditions(self):
        """Check for alert conditions and trigger alerts."""
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            await self._trigger_alert("high_cpu_usage", "critical", 
                                    f"CPU usage is critically high: {cpu_percent}%")
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 95:
            await self._trigger_alert("high_memory_usage", "critical",
                                    f"Memory usage is critically high: {memory.percent}%")
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            await self._trigger_alert("high_disk_usage", "critical",
                                    f"Disk usage is critically high: {disk.percent}%")
        
        # Check for high error rates (simplified)
        # In production, you'd track error rates over time windows
    
    async def _trigger_alert(self, alert_name: str, severity: str, message: str):
        """Trigger an alert."""
        alert = {
            "alert_name": alert_name,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        }
        
        await self._store_alert(alert)
        logger.warning(f"ALERT: {severity.upper()} - {message}")
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest()
    
    def get_health_status(self) -> Dict:
        """Get current health status."""
        return {
            "status": self.health_status.value,
            "service": self.service_name,
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_detailed_health(self) -> Dict:
        """Get detailed health information."""
        # Get recent health checks
        recent_checks = await self._get_recent_health_checks(limit=10)
        
        return {
            "overall_status": self.health_status.value,
            "service": self.service_name,
            "uptime_seconds": time.time() - self.start_time,
            "recent_health_checks": [asdict(check) for check in recent_checks],
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_performance_metrics(self, hours: int = 24) -> Dict:
        """Get performance metrics for the specified time period."""
        since = datetime.now() - timedelta(hours=hours)
        
        # Get system metrics
        system_metrics = await self._get_system_metrics_since(since)
        
        # Get performance metrics
        perf_metrics = await self._get_performance_metrics_since(since)
        
        return {
            "system_metrics": system_metrics,
            "performance_metrics": perf_metrics,
            "time_period_hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _store_system_metrics(self, metrics: Dict[str, float]):
        """Store system metrics in database."""
        with sqlite3.connect(self.monitoring_db) as conn:
            for metric_name, value in metrics.items():
                conn.execute("""
                    INSERT INTO system_metrics (metric_name, value, timestamp)
                    VALUES (?, ?, ?)
                """, (metric_name, value, datetime.now().isoformat()))
    
    async def _store_health_checks(self, health_checks: List[HealthCheck]):
        """Store health check results in database."""
        with sqlite3.connect(self.monitoring_db) as conn:
            for check in health_checks:
                conn.execute("""
                    INSERT INTO health_checks 
                    (name, status, message, timestamp, response_time_ms, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    check.name, check.status.value, check.message,
                    check.timestamp.isoformat(), check.response_time_ms,
                    json.dumps(check.details) if check.details else None
                ))
    
    async def _store_alert(self, alert: Dict):
        """Store alert in database."""
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                INSERT INTO alerts (alert_name, severity, message, timestamp, resolved)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert["alert_name"], alert["severity"], alert["message"],
                alert["timestamp"], alert["resolved"]
            ))
    
    async def _get_recent_health_checks(self, limit: int = 10) -> List[HealthCheck]:
        """Get recent health check results."""
        with sqlite3.connect(self.monitoring_db) as conn:
            cursor = conn.execute("""
                SELECT name, status, message, timestamp, response_time_ms, details
                FROM health_checks 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [
                HealthCheck(
                    name=row[0],
                    status=HealthStatus(row[1]),
                    message=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    response_time_ms=row[4],
                    details=json.loads(row[5]) if row[5] else {}
                )
                for row in rows
            ]
    
    async def _get_system_metrics_since(self, since: datetime) -> Dict:
        """Get system metrics since the specified time."""
        with sqlite3.connect(self.monitoring_db) as conn:
            cursor = conn.execute("""
                SELECT metric_name, AVG(value) as avg_value, MAX(value) as max_value, MIN(value) as min_value
                FROM system_metrics 
                WHERE timestamp >= ?
                GROUP BY metric_name
            """, (since.isoformat(),))
            
            rows = cursor.fetchall()
            return {
                row[0]: {
                    "average": row[1],
                    "maximum": row[2],
                    "minimum": row[3]
                }
                for row in rows
            }
    
    async def _get_performance_metrics_since(self, since: datetime) -> List[Dict]:
        """Get performance metrics since the specified time."""
        with sqlite3.connect(self.monitoring_db) as conn:
            cursor = conn.execute("""
                SELECT name, value, unit, timestamp, labels
                FROM performance_metrics 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (since.isoformat(),))
            
            rows = cursor.fetchall()
            return [
                {
                    "name": row[0],
                    "value": row[1],
                    "unit": row[2],
                    "timestamp": row[3],
                    "labels": json.loads(row[4]) if row[4] else {}
                }
                for row in rows
            ]

# Example usage
async def main():
    """Example usage of the Production Monitoring system."""
    monitoring = ProductionMonitoring("universal_crawler")
    await monitoring.start_monitoring()
    
    # Register custom health checks
    async def database_health_check():
        # Simulate database health check
        await asyncio.sleep(0.1)
        return {
            "status": HealthStatus.HEALTHY,
            "message": "Database connection OK",
            "details": {"connection_pool_size": 10}
        }
    
    async def api_health_check():
        # Simulate API health check
        await asyncio.sleep(0.05)
        return {
            "status": HealthStatus.HEALTHY,
            "message": "API endpoints responding",
            "details": {"response_time_ms": 45}
        }
    
    monitoring.register_health_check("database", database_health_check)
    monitoring.register_health_check("api", api_health_check)
    
    # Record some metrics
    monitoring.record_crawl_metric("github.com", "playwright", 2.5, "success", 1024)
    monitoring.record_llm_metric("deepseek_r1", "deepseek", "success", 0.001)
    monitoring.set_active_agents("crawler", 5)
    monitoring.set_queue_size("crawl_queue", 25)
    
    # Wait for some monitoring data
    await asyncio.sleep(5)
    
    # Get monitoring data
    health_status = monitoring.get_health_status()
    detailed_health = await monitoring.get_detailed_health()
    performance_metrics = await monitoring.get_performance_metrics(hours=1)
    
    print(f"Health Status: {health_status}")
    print(f"Detailed Health: {detailed_health}")
    print(f"Performance Metrics: {performance_metrics}")
    
    # Get Prometheus metrics
    prometheus_metrics = monitoring.get_metrics()
    print(f"Prometheus Metrics:\n{prometheus_metrics}")
    
    await monitoring.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 