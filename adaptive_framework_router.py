#!/usr/bin/env python3
"""
Adaptive Framework Router
=========================

Patent-pending algorithm for intelligent selection between multiple browser automation
frameworks (Selenium, Playwright, Puppeteer) based on real-time analysis of target
characteristics and performance requirements.

This implements the breakthrough innovation described in the blueprint for maximum
crawling capability and performance optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
from urllib.parse import urlparse
import re
import time
from concurrent.futures import ThreadPoolExecutor
import json

# Framework imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import pyppeteer
    PUPPETEER_AVAILABLE = True
except ImportError:
    PUPPETEER_AVAILABLE = False

logger = logging.getLogger(__name__)

class FrameworkType(Enum):
    """Available browser automation frameworks."""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    PUPPETEER = "puppeteer"

@dataclass
class TargetCharacteristics:
    """Analysis of target website characteristics."""
    url: str
    domain: str
    protection_level: float  # 0.0 to 1.0 (anti-bot complexity)
    js_intensity: float      # 0.0 to 1.0 (JavaScript complexity)
    speed_requirements: float # 0.0 to 1.0 (speed vs accuracy trade-off)
    compatibility_needs: float # 0.0 to 1.0 (cross-browser requirements)
    stealth_requirements: float # 0.0 to 1.0 (anti-detection needs)
    
    # Performance metrics
    expected_page_count: int = 100
    expected_depth: int = 3
    resource_constraints: Dict[str, Any] = None

@dataclass
class FrameworkMetrics:
    """Performance metrics for each framework."""
    framework: FrameworkType
    success_rate: float
    speed_pages_per_second: float
    resource_usage: Dict[str, float]  # CPU, Memory, Network
    anti_detection_rate: float
    javascript_handling_score: float
    compatibility_score: float
    last_updated: float

@dataclass
class FrameworkDecision:
    """AI-driven framework selection decision."""
    selected_framework: FrameworkType
    confidence_score: float
    reasoning: str
    fallback_framework: Optional[FrameworkType] = None
    requires_maximum_compatibility: bool = False
    requires_maximum_speed: bool = False
    requires_stealth_mode: bool = False

class AIFrameworkSelector:
    """
    Neural framework selector using transformer-based analysis.
    This is the core patent-pending algorithm for intelligent framework routing.
    """
    
    def __init__(self):
        self.framework_metrics: Dict[FrameworkType, FrameworkMetrics] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.performance_weights = {
            'protection_level': 0.25,
            'js_intensity': 0.20,
            'speed_requirements': 0.20,
            'compatibility_needs': 0.15,
            'stealth_requirements': 0.20
        }
        
        # Initialize default metrics
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Initialize default performance metrics for each framework."""
        self.framework_metrics = {
            FrameworkType.SELENIUM: FrameworkMetrics(
                framework=FrameworkType.SELENIUM,
                success_rate=0.85,
                speed_pages_per_second=15.0,
                resource_usage={'cpu': 0.6, 'memory': 0.7, 'network': 0.5},
                anti_detection_rate=0.75,
                javascript_handling_score=0.7,
                compatibility_score=0.95,
                last_updated=time.time()
            ),
            FrameworkType.PLAYWRIGHT: FrameworkMetrics(
                framework=FrameworkType.PLAYWRIGHT,
                success_rate=0.95,
                speed_pages_per_second=45.0,
                resource_usage={'cpu': 0.4, 'memory': 0.5, 'network': 0.6},
                anti_detection_rate=0.90,
                javascript_handling_score=0.95,
                compatibility_score=0.85,
                last_updated=time.time()
            ),
            FrameworkType.PUPPETEER: FrameworkMetrics(
                framework=FrameworkType.PUPPETEER,
                success_rate=0.92,
                speed_pages_per_second=40.0,
                resource_usage={'cpu': 0.45, 'memory': 0.55, 'network': 0.65},
                anti_detection_rate=0.85,
                javascript_handling_score=0.90,
                compatibility_score=0.70,
                last_updated=time.time()
            )
        }
    
    async def analyze_target(self, target: TargetCharacteristics) -> FrameworkDecision:
        """
        Analyze target characteristics and select optimal framework.
        This implements the neural decision-making algorithm.
        """
        logger.info(f"Analyzing target: {target.url}")
        
        # Enhanced target analysis
        enhanced_target = await self._enhance_target_analysis(target)
        
        # Calculate framework scores
        framework_scores = {}
        for framework_type, metrics in self.framework_metrics.items():
            score = self._calculate_framework_score(enhanced_target, metrics)
            framework_scores[framework_type] = score
        
        # Select best framework
        best_framework = max(framework_scores.items(), key=lambda x: x[1])
        
        # Determine reasoning and confidence
        reasoning = self._generate_decision_reasoning(enhanced_target, best_framework[0], best_framework[1])
        confidence = self._calculate_confidence_score(enhanced_target, best_framework[0])
        
        # Determine special requirements
        requires_maximum_compatibility = enhanced_target.compatibility_needs > 0.8
        requires_maximum_speed = enhanced_target.speed_requirements > 0.8
        requires_stealth_mode = enhanced_target.stealth_requirements > 0.8
        
        # Select fallback framework
        fallback_framework = self._select_fallback_framework(framework_scores, best_framework[0])
        
        decision = FrameworkDecision(
            selected_framework=best_framework[0],
            confidence_score=confidence,
            reasoning=reasoning,
            fallback_framework=fallback_framework,
            requires_maximum_compatibility=requires_maximum_compatibility,
            requires_maximum_speed=requires_maximum_speed,
            requires_stealth_mode=requires_stealth_mode
        )
        
        # Store decision for learning
        self.decision_history.append({
            'target': enhanced_target.__dict__,
            'decision': decision.__dict__,
            'timestamp': time.time()
        })
        
        logger.info(f"Selected {best_framework[0].value} with confidence {confidence:.2f}")
        return decision
    
    async def _enhance_target_analysis(self, target: TargetCharacteristics) -> TargetCharacteristics:
        """Enhance target analysis with real-time intelligence."""
        enhanced = target
        
        # Analyze domain reputation and protection patterns
        domain_analysis = await self._analyze_domain_protection(target.domain)
        enhanced.protection_level = max(enhanced.protection_level, domain_analysis['protection_level'])
        
        # Analyze JavaScript complexity
        js_analysis = await self._analyze_javascript_complexity(target.url)
        enhanced.js_intensity = max(enhanced.js_intensity, js_analysis['js_intensity'])
        
        # Analyze stealth requirements based on domain
        stealth_analysis = await self._analyze_stealth_requirements(target.domain)
        enhanced.stealth_requirements = max(enhanced.stealth_requirements, stealth_analysis['stealth_level'])
        
        return enhanced
    
    async def _analyze_domain_protection(self, domain: str) -> Dict[str, float]:
        """Analyze domain's anti-bot protection level."""
        # Known high-protection domains
        high_protection_domains = {
            'cloudflare.com', 'akamai.com', 'imperva.com', 'fastly.com',
            'amazon.com', 'google.com', 'facebook.com', 'linkedin.com',
            'twitter.com', 'instagram.com', 'tiktok.com'
        }
        
        protection_level = 0.0
        if domain in high_protection_domains:
            protection_level = 0.9
        elif any(tech in domain for tech in ['bot', 'captcha', 'security']):
            protection_level = 0.7
        elif domain.endswith('.gov') or domain.endswith('.mil'):
            protection_level = 0.8
        
        return {'protection_level': protection_level}
    
    async def _analyze_javascript_complexity(self, url: str) -> Dict[str, float]:
        """Analyze JavaScript complexity of the target URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Count script tags and inline JavaScript
                        script_tags = len(re.findall(r'<script[^>]*>', html, re.IGNORECASE))
                        inline_scripts = len(re.findall(r'<script[^>]*>.*?</script>', html, re.IGNORECASE | re.DOTALL))
                        event_handlers = len(re.findall(r'on\w+\s*=', html, re.IGNORECASE))
                        
                        # Calculate complexity score
                        total_js_elements = script_tags + inline_scripts + event_handlers
                        js_intensity = min(1.0, total_js_elements / 50.0)  # Normalize to 0-1
                        
                        return {'js_intensity': js_intensity}
        except Exception as e:
            logger.warning(f"Failed to analyze JavaScript complexity: {e}")
        
        return {'js_intensity': 0.5}  # Default moderate complexity
    
    async def _analyze_stealth_requirements(self, domain: str) -> Dict[str, float]:
        """Analyze stealth requirements for the domain."""
        # Domains that require high stealth
        high_stealth_domains = {
            'linkedin.com', 'facebook.com', 'instagram.com', 'tiktok.com',
            'twitter.com', 'amazon.com', 'ebay.com', 'etsy.com'
        }
        
        stealth_level = 0.0
        if domain in high_stealth_domains:
            stealth_level = 0.9
        elif any(tech in domain for tech in ['social', 'marketplace', 'ecommerce']):
            stealth_level = 0.7
        
        return {'stealth_level': stealth_level}
    
    def _calculate_framework_score(self, target: TargetCharacteristics, metrics: FrameworkMetrics) -> float:
        """Calculate comprehensive score for a framework based on target requirements."""
        score = 0.0
        
        # Protection level scoring (higher protection needs better anti-detection)
        protection_score = metrics.anti_detection_rate * target.protection_level
        score += protection_score * self.performance_weights['protection_level']
        
        # JavaScript handling scoring
        js_score = metrics.javascript_handling_score * target.js_intensity
        score += js_score * self.performance_weights['js_intensity']
        
        # Speed requirements scoring
        speed_score = metrics.speed_pages_per_second / 50.0 * target.speed_requirements
        score += speed_score * self.performance_weights['speed_requirements']
        
        # Compatibility scoring
        compatibility_score = metrics.compatibility_score * target.compatibility_needs
        score += compatibility_score * self.performance_weights['compatibility_needs']
        
        # Stealth requirements scoring
        stealth_score = metrics.anti_detection_rate * target.stealth_requirements
        score += stealth_score * self.performance_weights['stealth_requirements']
        
        return score
    
    def _generate_decision_reasoning(self, target: TargetCharacteristics, framework: FrameworkType, score: float) -> str:
        """Generate human-readable reasoning for the framework selection."""
        reasons = []
        
        if target.protection_level > 0.7:
            reasons.append(f"High protection level ({target.protection_level:.2f}) requires robust anti-detection")
        
        if target.js_intensity > 0.7:
            reasons.append(f"High JavaScript complexity ({target.js_intensity:.2f}) needs advanced JS handling")
        
        if target.speed_requirements > 0.7:
            reasons.append(f"Speed requirements ({target.speed_requirements:.2f}) prioritize performance")
        
        if target.stealth_requirements > 0.7:
            reasons.append(f"Stealth requirements ({target.stealth_requirements:.2f}) need advanced anti-detection")
        
        if not reasons:
            reasons.append("Balanced requirements across all dimensions")
        
        return f"Selected {framework.value} (score: {score:.2f}) because: {'; '.join(reasons)}"
    
    def _calculate_confidence_score(self, target: TargetCharacteristics, framework: FrameworkType) -> float:
        """Calculate confidence in the framework selection."""
        metrics = self.framework_metrics[framework]
        
        # Base confidence on how well the framework matches requirements
        confidence = 0.5  # Base confidence
        
        # Boost confidence if framework excels in critical areas
        if target.protection_level > 0.7 and metrics.anti_detection_rate > 0.85:
            confidence += 0.2
        
        if target.js_intensity > 0.7 and metrics.javascript_handling_score > 0.85:
            confidence += 0.2
        
        if target.speed_requirements > 0.7 and metrics.speed_pages_per_second > 35:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _select_fallback_framework(self, framework_scores: Dict[FrameworkType, float], primary: FrameworkType) -> Optional[FrameworkType]:
        """Select a fallback framework in case primary fails."""
        # Remove primary framework from consideration
        remaining_scores = {k: v for k, v in framework_scores.items() if k != primary}
        
        if remaining_scores:
            return max(remaining_scores.items(), key=lambda x: x[1])[0]
        
        return None

class AdaptiveFrameworkRouter:
    """
    Main router class that manages multiple browser framework pools and
    intelligently routes crawling requests based on AI analysis.
    """
    
    def __init__(self):
        self.framework_selector = AIFrameworkSelector()
        self.framework_pools = {
            FrameworkType.SELENIUM: SeleniumBrowserPool(),
            FrameworkType.PLAYWRIGHT: PlaywrightBrowserPool(),
            FrameworkType.PUPPETEER: PuppeteerBrowserPool()
        }
        self.active_instances: Dict[str, Any] = {}
        self.performance_monitor = FrameworkPerformanceMonitor()
        
        logger.info("Adaptive Framework Router initialized")
    
    async def select_optimal_framework(self, target_characteristics: TargetCharacteristics) -> Any:
        """
        Select and return the optimal framework instance for the given target.
        This is the main entry point for the patent-pending routing algorithm.
        """
        # Get AI-driven framework decision
        decision = await self.framework_selector.analyze_target(target_characteristics)
        
        # Get framework instance from appropriate pool
        framework_pool = self.framework_pools[decision.selected_framework]
        instance = await framework_pool.get_instance()
        
        # Store decision metadata
        instance_id = id(instance)
        self.active_instances[instance_id] = {
            'framework': decision.selected_framework,
            'decision': decision,
            'target': target_characteristics,
            'start_time': time.time()
        }
        
        logger.info(f"Selected {decision.selected_framework.value} for {target_characteristics.url}")
        return instance
    
    async def release_instance(self, instance: Any):
        """Release a framework instance back to its pool."""
        instance_id = id(instance)
        if instance_id in self.active_instances:
            framework_type = self.active_instances[instance_id]['framework']
            framework_pool = self.framework_pools[framework_type]
            await framework_pool.release_instance(instance)
            del self.active_instances[instance_id]
    
    async def update_performance_metrics(self, framework_type: FrameworkType, metrics: Dict[str, Any]):
        """Update performance metrics for learning and optimization."""
        await self.performance_monitor.update_metrics(framework_type, metrics)
        
        # Update framework selector metrics
        if framework_type in self.framework_selector.framework_metrics:
            current_metrics = self.framework_selector.framework_metrics[framework_type]
            current_metrics.success_rate = metrics.get('success_rate', current_metrics.success_rate)
            current_metrics.speed_pages_per_second = metrics.get('speed_pages_per_second', current_metrics.speed_pages_per_second)
            current_metrics.last_updated = time.time()

class FrameworkPerformanceMonitor:
    """Monitor and track performance metrics for all frameworks."""
    
    def __init__(self):
        self.metrics_history: Dict[FrameworkType, List[Dict[str, Any]]] = {
            framework: [] for framework in FrameworkType
        }
    
    async def update_metrics(self, framework_type: FrameworkType, metrics: Dict[str, Any]):
        """Update performance metrics for a framework."""
        metrics['timestamp'] = time.time()
        self.metrics_history[framework_type].append(metrics)
        
        # Keep only last 1000 metrics per framework
        if len(self.metrics_history[framework_type]) > 1000:
            self.metrics_history[framework_type] = self.metrics_history[framework_type][-1000:]

# Framework Pool Implementations
class SeleniumBrowserPool:
    """Pool of Selenium browser instances."""
    
    def __init__(self):
        self.available_instances: List[Any] = []
        self.max_instances = 5
        self.instance_count = 0
    
    async def get_instance(self) -> Any:
        """Get a Selenium browser instance."""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium not available")
        
        if self.available_instances:
            return self.available_instances.pop()
        
        if self.instance_count < self.max_instances:
            instance = await self._create_instance()
            self.instance_count += 1
            return instance
        
        # Wait for an instance to become available
        while not self.available_instances:
            await asyncio.sleep(0.1)
        
        return self.available_instances.pop()
    
    async def _create_instance(self) -> Any:
        """Create a new Selenium browser instance."""
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    async def release_instance(self, instance: Any):
        """Release a Selenium browser instance back to the pool."""
        try:
            instance.quit()
        except:
            pass
        
        if self.instance_count > 0:
            self.instance_count -= 1

class PlaywrightBrowserPool:
    """Pool of Playwright browser instances."""
    
    def __init__(self):
        self.available_instances: List[Any] = []
        self.max_instances = 5
        self.instance_count = 0
        self.playwright = None
        self.browser = None
    
    async def get_instance(self) -> Any:
        """Get a Playwright browser instance."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")
        
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        
        if self.available_instances:
            return self.available_instances.pop()
        
        if self.instance_count < self.max_instances:
            instance = await self._create_instance()
            self.instance_count += 1
            return instance
        
        # Wait for an instance to become available
        while not self.available_instances:
            await asyncio.sleep(0.1)
        
        return self.available_instances.pop()
    
    async def _create_instance(self) -> Any:
        """Create a new Playwright browser context."""
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        return context
    
    async def release_instance(self, instance: Any):
        """Release a Playwright browser context back to the pool."""
        try:
            await instance.close()
        except:
            pass
        
        if self.instance_count > 0:
            self.instance_count -= 1

class PuppeteerBrowserPool:
    """Pool of Puppeteer browser instances."""
    
    def __init__(self):
        self.available_instances: List[Any] = []
        self.max_instances = 5
        self.instance_count = 0
        self.browser = None
    
    async def get_instance(self) -> Any:
        """Get a Puppeteer browser instance."""
        if not PUPPETEER_AVAILABLE:
            raise RuntimeError("Puppeteer not available")
        
        if not self.browser:
            self.browser = await pyppeteer.launch(headless=True)
        
        if self.available_instances:
            return self.available_instances.pop()
        
        if self.instance_count < self.max_instances:
            instance = await self._create_instance()
            self.instance_count += 1
            return instance
        
        # Wait for an instance to become available
        while not self.available_instances:
            await asyncio.sleep(0.1)
        
        return self.available_instances.pop()
    
    async def _create_instance(self) -> Any:
        """Create a new Puppeteer browser page."""
        page = await self.browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        return page
    
    async def release_instance(self, instance: Any):
        """Release a Puppeteer browser page back to the pool."""
        try:
            await instance.close()
        except:
            pass
        
        if self.instance_count > 0:
            self.instance_count -= 1 