#!/usr/bin/env python3
"""
Advanced Crawler Orchestrator
=============================

Multi-agent orchestration system using LangGraph for intelligent crawling decisions.
This implements the breakthrough workflow architecture described in the blueprint.

Key Features:
1. Multi-agent decision making with specialized roles
2. Intelligent workflow routing and conditional execution
3. Real-time adaptation to crawling conditions
4. Comprehensive state management and monitoring
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import aiohttp
from urllib.parse import urlparse
import hashlib
import re

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LangGraph not available - using simplified workflow")

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of specialized crawling agents."""
    TARGET_ANALYZER = "target_analyzer"
    FRAMEWORK_SELECTOR = "framework_selector"
    EXTRACTION_PLANNER = "extraction_planner"
    QUALITY_VALIDATOR = "quality_validator"
    CONTEXT_OPTIMIZER = "context_optimizer"
    COMPLIANCE_CHECKER = "compliance_checker"
    PERFORMANCE_MONITOR = "performance_monitor"

@dataclass
class CrawlState:
    """Comprehensive state for crawling workflow."""
    # Input parameters
    url: str
    mode: str = "enhanced"
    max_depth: int = 3
    max_pages: int = 100
    
    # Analysis results
    target_analysis: Optional[Dict[str, Any]] = None
    framework_decision: Optional[Dict[str, Any]] = None
    extraction_plan: Optional[Dict[str, Any]] = None
    context_optimization: Optional[Dict[str, Any]] = None
    
    # Execution state
    current_depth: int = 0
    pages_crawled: int = 0
    pages_failed: int = 0
    total_size: int = 0
    
    # Quality metrics
    quality_scores: Dict[str, float] = field(default_factory=dict)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    crawled_pages: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Workflow control
    workflow_step: str = "initialized"
    should_continue: bool = True
    next_action: Optional[str] = None
    
    # Metadata
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class TargetAnalysisAgent:
    """
    Specialized agent for analyzing crawl targets and determining optimal strategies.
    """
    
    def __init__(self):
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        self.domain_patterns: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_target(self, state: CrawlState) -> CrawlState:
        """Analyze the target URL and update state with analysis results."""
        logger.info(f"Target analysis agent analyzing: {state.url}")
        
        # Check cache first
        cache_key = hashlib.md5(state.url.encode()).hexdigest()
        if cache_key in self.analysis_cache:
            state.target_analysis = self.analysis_cache[cache_key]
            logger.info("Using cached target analysis")
            return state
        
        # Perform comprehensive analysis
        analysis = await self._perform_target_analysis(state.url)
        
        # Cache the result
        self.analysis_cache[cache_key] = analysis
        state.target_analysis = analysis
        
        # Update workflow state
        state.workflow_step = "target_analyzed"
        state.last_update = time.time()
        
        logger.info(f"Target analysis completed: {analysis.get('complexity_level', 'unknown')}")
        return state
    
    async def _perform_target_analysis(self, url: str) -> Dict[str, Any]:
        """Perform comprehensive target analysis."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Basic URL analysis
            analysis = {
                'url': url,
                'domain': domain,
                'protocol': parsed_url.scheme,
                'path_depth': len([p for p in parsed_url.path.split('/') if p]),
                'has_query': bool(parsed_url.query),
                'has_fragment': bool(parsed_url.fragment)
            }
            
            # Domain-specific analysis
            domain_analysis = await self._analyze_domain(domain)
            analysis.update(domain_analysis)
            
            # Content complexity analysis
            content_analysis = await self._analyze_content_complexity(url)
            analysis.update(content_analysis)
            
            # Security and protection analysis
            security_analysis = await self._analyze_security_protection(url)
            analysis.update(security_analysis)
            
            # Determine overall complexity level
            analysis['complexity_level'] = self._calculate_complexity_level(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Target analysis failed: {e}")
            return {
                'url': url,
                'error': str(e),
                'complexity_level': 'unknown'
            }
    
    async def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain characteristics."""
        # Known domain patterns
        known_patterns = {
            'amazon.com': {'type': 'ecommerce', 'complexity': 'high', 'protection': 'high'},
            'linkedin.com': {'type': 'social', 'complexity': 'very_high', 'protection': 'very_high'},
            'github.com': {'type': 'developer', 'complexity': 'medium', 'protection': 'medium'},
            'stackoverflow.com': {'type': 'community', 'complexity': 'medium', 'protection': 'medium'},
            'wikipedia.org': {'type': 'encyclopedia', 'complexity': 'low', 'protection': 'low'}
        }
        
        if domain in known_patterns:
            return known_patterns[domain]
        
        # Generic domain analysis
        return {
            'type': 'unknown',
            'complexity': 'medium',
            'protection': 'medium'
        }
    
    async def _analyze_content_complexity(self, url: str) -> Dict[str, Any]:
        """Analyze content complexity of the target URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Analyze HTML complexity
                        script_count = len(re.findall(r'<script[^>]*>', html, re.IGNORECASE))
                        style_count = len(re.findall(r'<style[^>]*>', html, re.IGNORECASE))
                        link_count = len(re.findall(r'<link[^>]*>', html, re.IGNORECASE))
                        img_count = len(re.findall(r'<img[^>]*>', html, re.IGNORECASE))
                        
                        # Calculate complexity score
                        complexity_score = min(1.0, (script_count + style_count + link_count + img_count) / 100.0)
                        
                        return {
                            'html_complexity': complexity_score,
                            'script_count': script_count,
                            'style_count': style_count,
                            'link_count': link_count,
                            'img_count': img_count,
                            'content_size': len(html)
                        }
        except Exception as e:
            logger.warning(f"Content complexity analysis failed: {e}")
        
        return {
            'html_complexity': 0.5,
            'script_count': 0,
            'style_count': 0,
            'link_count': 0,
            'img_count': 0,
            'content_size': 0
        }
    
    async def _analyze_security_protection(self, url: str) -> Dict[str, Any]:
        """Analyze security and anti-bot protection."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    headers = response.headers
                    
                    # Check for security headers
                    security_headers = {
                        'X-Frame-Options': headers.get('X-Frame-Options'),
                        'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                        'X-XSS-Protection': headers.get('X-XSS-Protection'),
                        'Content-Security-Policy': headers.get('Content-Security-Policy'),
                        'Strict-Transport-Security': headers.get('Strict-Transport-Security')
                    }
                    
                    # Check for anti-bot indicators
                    anti_bot_indicators = [
                        'cloudflare' in headers.get('Server', '').lower(),
                        'captcha' in response.text.lower(),
                        'bot' in headers.get('User-Agent', '').lower(),
                        'blocked' in response.text.lower()
                    ]
                    
                    protection_level = sum(anti_bot_indicators) / len(anti_bot_indicators)
                    
                    return {
                        'security_headers': security_headers,
                        'protection_level': protection_level,
                        'has_captcha': 'captcha' in response.text.lower(),
                        'has_cloudflare': 'cloudflare' in headers.get('Server', '').lower()
                    }
        except Exception as e:
            logger.warning(f"Security analysis failed: {e}")
        
        return {
            'security_headers': {},
            'protection_level': 0.0,
            'has_captcha': False,
            'has_cloudflare': False
        }
    
    def _calculate_complexity_level(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall complexity level."""
        complexity_factors = []
        
        # Domain complexity
        domain_complexity_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'very_high': 1.0}
        domain_complexity = domain_complexity_map.get(analysis.get('complexity', 'medium'), 0.5)
        complexity_factors.append(domain_complexity)
        
        # HTML complexity
        html_complexity = analysis.get('html_complexity', 0.5)
        complexity_factors.append(html_complexity)
        
        # Protection level
        protection_level = analysis.get('protection_level', 0.0)
        complexity_factors.append(protection_level)
        
        # Calculate average complexity
        avg_complexity = sum(complexity_factors) / len(complexity_factors)
        
        if avg_complexity < 0.3:
            return 'low'
        elif avg_complexity < 0.6:
            return 'medium'
        elif avg_complexity < 0.8:
            return 'high'
        else:
            return 'very_high'

class FrameworkSelectorAgent:
    """
    Specialized agent for selecting optimal crawling frameworks.
    Integrates with the Adaptive Framework Router.
    """
    
    def __init__(self):
        self.framework_router = None  # Will be initialized with AdaptiveFrameworkRouter
        self.selection_history: List[Dict[str, Any]] = []
        
    async def select_framework(self, state: CrawlState) -> CrawlState:
        """Select optimal framework based on target analysis."""
        logger.info(f"Framework selector agent analyzing: {state.url}")
        
        if not state.target_analysis:
            state.errors.append("Target analysis not available for framework selection")
            return state
        
        # Create target characteristics
        target_characteristics = self._create_target_characteristics(state)
        
        # Select framework (simplified for now)
        framework_decision = await self._select_optimal_framework(target_characteristics)
        
        # Update state
        state.framework_decision = framework_decision
        state.workflow_step = "framework_selected"
        state.last_update = time.time()
        
        # Store selection history
        self.selection_history.append({
            'url': state.url,
            'decision': framework_decision,
            'timestamp': time.time()
        })
        
        logger.info(f"Framework selected: {framework_decision.get('selected_framework', 'unknown')}")
        return state
    
    def _create_target_characteristics(self, state: CrawlState) -> Dict[str, Any]:
        """Create target characteristics for framework selection."""
        analysis = state.target_analysis
        
        return {
            'url': state.url,
            'domain': analysis.get('domain', ''),
            'protection_level': analysis.get('protection_level', 0.0),
            'js_intensity': analysis.get('html_complexity', 0.5),
            'speed_requirements': 0.7 if state.mode in ['enhanced', 'enterprise'] else 0.5,
            'compatibility_needs': 0.8 if analysis.get('complexity_level') == 'very_high' else 0.5,
            'stealth_requirements': 0.9 if analysis.get('protection_level', 0.0) > 0.5 else 0.3
        }
    
    async def _select_optimal_framework(self, target_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal framework based on characteristics."""
        # Simplified framework selection logic
        protection_level = target_characteristics.get('protection_level', 0.0)
        js_intensity = target_characteristics.get('js_intensity', 0.5)
        stealth_requirements = target_characteristics.get('stealth_requirements', 0.3)
        
        if protection_level > 0.7 or stealth_requirements > 0.7:
            selected_framework = 'playwright'
            confidence = 0.9
            reasoning = "High protection/stealth requirements - Playwright excels at anti-detection"
        elif js_intensity > 0.7:
            selected_framework = 'playwright'
            confidence = 0.85
            reasoning = "High JavaScript complexity - Playwright has superior JS handling"
        elif target_characteristics.get('compatibility_needs', 0.5) > 0.7:
            selected_framework = 'selenium'
            confidence = 0.8
            reasoning = "High compatibility requirements - Selenium supports all browsers"
        else:
            selected_framework = 'puppeteer'
            confidence = 0.75
            reasoning = "Balanced requirements - Puppeteer offers good performance"
        
        return {
            'selected_framework': selected_framework,
            'confidence_score': confidence,
            'reasoning': reasoning,
            'target_characteristics': target_characteristics,
            'fallback_framework': 'selenium' if selected_framework != 'selenium' else 'playwright'
        }

class ExtractionPlannerAgent:
    """
    Specialized agent for planning optimal extraction strategies.
    """
    
    def __init__(self):
        self.extraction_templates: Dict[str, Dict[str, Any]] = {}
        self.planning_history: List[Dict[str, Any]] = []
        
    async def plan_extraction(self, state: CrawlState) -> CrawlState:
        """Plan optimal extraction strategy based on target analysis."""
        logger.info(f"Extraction planner agent planning for: {state.url}")
        
        if not state.target_analysis:
            state.errors.append("Target analysis not available for extraction planning")
            return state
        
        # Create extraction plan
        extraction_plan = await self._create_extraction_plan(state)
        
        # Update state
        state.extraction_plan = extraction_plan
        state.workflow_step = "extraction_planned"
        state.last_update = time.time()
        
        # Store planning history
        self.planning_history.append({
            'url': state.url,
            'plan': extraction_plan,
            'timestamp': time.time()
        })
        
        logger.info(f"Extraction plan created: {extraction_plan.get('strategy', 'unknown')}")
        return state
    
    async def _create_extraction_plan(self, state: CrawlState) -> Dict[str, Any]:
        """Create comprehensive extraction plan."""
        analysis = state.target_analysis
        
        # Determine extraction strategy
        if analysis.get('complexity_level') == 'very_high':
            strategy = 'comprehensive'
            selectors = self._get_comprehensive_selectors()
        elif analysis.get('complexity_level') == 'high':
            strategy = 'enhanced'
            selectors = self._get_enhanced_selectors()
        else:
            strategy = 'standard'
            selectors = self._get_standard_selectors()
        
        # Plan based on content type
        content_type = analysis.get('type', 'unknown')
        content_specific_plan = self._get_content_specific_plan(content_type)
        
        # Create comprehensive plan
        plan = {
            'strategy': strategy,
            'selectors': selectors,
            'content_specific': content_specific_plan,
            'wait_conditions': self._get_wait_conditions(analysis),
            'extraction_rules': self._get_extraction_rules(analysis),
            'quality_thresholds': self._get_quality_thresholds(analysis),
            'retry_strategy': self._get_retry_strategy(analysis),
            'rate_limiting': self._get_rate_limiting(analysis)
        }
        
        return plan
    
    def _get_comprehensive_selectors(self) -> Dict[str, List[str]]:
        """Get comprehensive CSS selectors for extraction."""
        return {
            'text_content': [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'div', 'span', 'article', 'section'
            ],
            'links': ['a[href]'],
            'images': ['img[src]', 'img[data-src]'],
            'forms': ['form', 'input', 'textarea', 'select'],
            'metadata': ['meta', 'title', 'link[rel]'],
            'scripts': ['script[src]', 'script:not([src])'],
            'styles': ['link[rel="stylesheet"]', 'style']
        }
    
    def _get_enhanced_selectors(self) -> Dict[str, List[str]]:
        """Get enhanced CSS selectors for extraction."""
        return {
            'text_content': ['h1', 'h2', 'h3', 'p', 'div'],
            'links': ['a[href]'],
            'images': ['img[src]'],
            'forms': ['form'],
            'metadata': ['meta', 'title']
        }
    
    def _get_standard_selectors(self) -> Dict[str, List[str]]:
        """Get standard CSS selectors for extraction."""
        return {
            'text_content': ['h1', 'h2', 'p'],
            'links': ['a[href]'],
            'images': ['img[src]'],
            'metadata': ['title']
        }
    
    def _get_content_specific_plan(self, content_type: str) -> Dict[str, Any]:
        """Get content-specific extraction plan."""
        plans = {
            'ecommerce': {
                'product_selectors': ['.product', '.item', '[data-product]'],
                'price_selectors': ['.price', '.cost', '[data-price]'],
                'rating_selectors': ['.rating', '.stars', '[data-rating]'],
                'reviews_selectors': ['.reviews', '.comments', '[data-reviews]']
            },
            'social': {
                'post_selectors': ['.post', '.tweet', '.status'],
                'user_selectors': ['.user', '.author', '[data-user]'],
                'engagement_selectors': ['.likes', '.shares', '.comments']
            },
            'news': {
                'article_selectors': ['.article', '.story', '.news-item'],
                'headline_selectors': ['.headline', '.title', 'h1'],
                'date_selectors': ['.date', '.timestamp', '[data-date]']
            }
        }
        
        return plans.get(content_type, {})
    
    def _get_wait_conditions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get wait conditions based on analysis."""
        complexity = analysis.get('complexity_level', 'medium')
        
        if complexity == 'very_high':
            return {
                'page_load_timeout': 30,
                'element_wait_timeout': 10,
                'dynamic_content_wait': 5,
                'retry_attempts': 3
            }
        elif complexity == 'high':
            return {
                'page_load_timeout': 20,
                'element_wait_timeout': 8,
                'dynamic_content_wait': 3,
                'retry_attempts': 2
            }
        else:
            return {
                'page_load_timeout': 15,
                'element_wait_timeout': 5,
                'dynamic_content_wait': 2,
                'retry_attempts': 1
            }
    
    def _get_extraction_rules(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get extraction rules based on analysis."""
        return {
            'extract_text': True,
            'extract_links': True,
            'extract_images': analysis.get('img_count', 0) > 0,
            'extract_forms': True,
            'extract_scripts': analysis.get('script_count', 0) > 5,
            'extract_styles': analysis.get('style_count', 0) > 0,
            'extract_metadata': True,
            'screenshot': analysis.get('complexity_level') in ['high', 'very_high']
        }
    
    def _get_quality_thresholds(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Get quality thresholds based on analysis."""
        complexity = analysis.get('complexity_level', 'medium')
        
        if complexity == 'very_high':
            return {
                'min_text_length': 100,
                'min_links': 5,
                'min_images': 1,
                'success_rate_threshold': 0.8
            }
        elif complexity == 'high':
            return {
                'min_text_length': 50,
                'min_links': 3,
                'min_images': 0,
                'success_rate_threshold': 0.7
            }
        else:
            return {
                'min_text_length': 20,
                'min_links': 1,
                'min_images': 0,
                'success_rate_threshold': 0.6
            }
    
    def _get_retry_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get retry strategy based on analysis."""
        protection_level = analysis.get('protection_level', 0.0)
        
        if protection_level > 0.7:
            return {
                'max_retries': 5,
                'retry_delay': 10,
                'exponential_backoff': True,
                'change_user_agent': True
            }
        elif protection_level > 0.3:
            return {
                'max_retries': 3,
                'retry_delay': 5,
                'exponential_backoff': True,
                'change_user_agent': False
            }
        else:
            return {
                'max_retries': 2,
                'retry_delay': 2,
                'exponential_backoff': False,
                'change_user_agent': False
            }
    
    def _get_rate_limiting(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get rate limiting strategy based on analysis."""
        protection_level = analysis.get('protection_level', 0.0)
        
        if protection_level > 0.7:
            return {
                'requests_per_minute': 10,
                'delay_between_requests': 6,
                'randomize_delay': True
            }
        elif protection_level > 0.3:
            return {
                'requests_per_minute': 30,
                'delay_between_requests': 2,
                'randomize_delay': True
            }
        else:
            return {
                'requests_per_minute': 60,
                'delay_between_requests': 1,
                'randomize_delay': False
            }

class QualityValidationAgent:
    """
    Specialized agent for validating crawl quality and results.
    """
    
    def __init__(self):
        self.quality_metrics: Dict[str, float] = {}
        self.validation_history: List[Dict[str, Any]] = []
        
    async def validate_quality(self, state: CrawlState) -> CrawlState:
        """Validate crawl quality and update state."""
        logger.info(f"Quality validator agent validating: {state.url}")
        
        # Calculate quality scores
        quality_scores = await self._calculate_quality_scores(state)
        
        # Update state
        state.quality_scores = quality_scores
        state.workflow_step = "quality_validated"
        state.last_update = time.time()
        
        # Store validation history
        self.validation_history.append({
            'url': state.url,
            'scores': quality_scores,
            'timestamp': time.time()
        })
        
        # Determine if crawl should continue
        overall_score = quality_scores.get('overall', 0.0)
        if overall_score < 0.5:
            state.warnings.append(f"Low quality score: {overall_score:.2f}")
        
        logger.info(f"Quality validation completed: {overall_score:.2f}")
        return state
    
    async def _calculate_quality_scores(self, state: CrawlState) -> Dict[str, float]:
        """Calculate comprehensive quality scores."""
        scores = {}
        
        # Content quality
        scores['content_quality'] = self._calculate_content_quality(state)
        
        # Structure quality
        scores['structure_quality'] = self._calculate_structure_quality(state)
        
        # Completeness quality
        scores['completeness_quality'] = self._calculate_completeness_quality(state)
        
        # Performance quality
        scores['performance_quality'] = self._calculate_performance_quality(state)
        
        # Overall quality
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _calculate_content_quality(self, state: CrawlState) -> float:
        """Calculate content quality score."""
        if not state.crawled_pages:
            return 0.0
        
        # Analyze content characteristics
        total_text_length = sum(len(page.get('text_content', '')) for page in state.crawled_pages)
        total_links = sum(len(page.get('links', [])) for page in state.crawled_pages)
        total_images = sum(len(page.get('images', [])) for page in state.crawled_pages)
        
        # Calculate quality factors
        text_quality = min(1.0, total_text_length / (state.pages_crawled * 100))
        link_quality = min(1.0, total_links / (state.pages_crawled * 5))
        image_quality = min(1.0, total_images / (state.pages_crawled * 2))
        
        return (text_quality + link_quality + image_quality) / 3.0
    
    def _calculate_structure_quality(self, state: CrawlState) -> float:
        """Calculate structure quality score."""
        if not state.crawled_pages:
            return 0.0
        
        # Analyze HTML structure
        structure_scores = []
        for page in state.crawled_pages:
            html = page.get('html_content', '')
            
            # Check for proper HTML structure
            has_doctype = '<!DOCTYPE' in html
            has_html_tag = '<html' in html
            has_head_tag = '<head' in html
            has_body_tag = '<body' in html
            
            structure_score = sum([has_doctype, has_html_tag, has_head_tag, has_body_tag]) / 4.0
            structure_scores.append(structure_score)
        
        return sum(structure_scores) / len(structure_scores) if structure_scores else 0.0
    
    def _calculate_completeness_quality(self, state: CrawlState) -> float:
        """Calculate completeness quality score."""
        if state.max_pages == 0:
            return 1.0
        
        # Calculate completion ratio
        completion_ratio = state.pages_crawled / state.max_pages
        
        # Consider error rate
        error_rate = state.pages_failed / max(state.pages_crawled, 1)
        error_penalty = 1.0 - error_rate
        
        return completion_ratio * error_penalty
    
    def _calculate_performance_quality(self, state: CrawlState) -> float:
        """Calculate performance quality score."""
        if not state.crawled_pages:
            return 0.0
        
        # Calculate performance metrics
        total_time = time.time() - state.start_time
        pages_per_second = state.pages_crawled / max(total_time, 1)
        
        # Normalize performance (target: 1 page per second)
        performance_score = min(1.0, pages_per_second)
        
        # Consider size efficiency
        avg_size_per_page = state.total_size / max(state.pages_crawled, 1)
        size_efficiency = max(0.0, 1.0 - (avg_size_per_page / 100000))  # Normalize to 100KB
        
        return (performance_score + size_efficiency) / 2.0

class ContextOptimizerAgent:
    """
    Specialized agent for context optimization using DCO.
    """
    
    def __init__(self):
        self.context_optimizer = None  # Will be initialized with DynamicContextOptimizer
        self.optimization_history: List[Dict[str, Any]] = []
        
    async def optimize_context(self, state: CrawlState) -> CrawlState:
        """Optimize context strategy using DCO."""
        logger.info(f"Context optimizer agent optimizing for: {state.url}")
        
        # Create crawl target for DCO
        crawl_target = self._create_crawl_target(state)
        
        # Optimize context (simplified for now)
        context_optimization = await self._optimize_context_strategy(crawl_target)
        
        # Update state
        state.context_optimization = context_optimization
        state.workflow_step = "context_optimized"
        state.last_update = time.time()
        
        # Store optimization history
        self.optimization_history.append({
            'url': state.url,
            'optimization': context_optimization,
            'timestamp': time.time()
        })
        
        logger.info(f"Context optimization completed: {context_optimization.get('selected_mode', 'unknown')}")
        return state
    
    def _create_crawl_target(self, state: CrawlState) -> Dict[str, Any]:
        """Create crawl target for context optimization."""
        return {
            'url': state.url,
            'domain': state.target_analysis.get('domain', '') if state.target_analysis else '',
            'content_type': state.target_analysis.get('type', 'unknown') if state.target_analysis else 'unknown',
            'context_size': state.total_size,
            'historical_changes': [],  # Would be populated from database
            'network_conditions': {
                'latency': 100,  # ms
                'bandwidth': 10,  # Mbps
                'reliability': 0.95
            },
            'computation_resources': {
                'cpu_available': 1.0,
                'memory_available': 8.0,  # GB
                'gpu_available': False
            }
        }
    
    async def _optimize_context_strategy(self, crawl_target: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context strategy using DCO."""
        # Simplified context optimization
        content_type = crawl_target.get('content_type', 'unknown')
        
        if content_type in ['static', 'documentation']:
            mode = 'cag'
            reasoning = "Static content - using CAG for efficient caching"
        elif content_type in ['social', 'news']:
            mode = 'rag'
            reasoning = "Dynamic content - using RAG for real-time retrieval"
        else:
            mode = 'hybrid'
            reasoning = "Mixed content - using hybrid approach"
        
        return {
            'selected_mode': mode,
            'reasoning': reasoning,
            'confidence_score': 0.8,
            'cache_strategy': {
                'strategy': 'adaptive_caching',
                'cache_duration': 3600,
                'cache_size_limit': 500000
            }
        }

class AdvancedCrawlerOrchestrator:
    """
    Main orchestrator class that manages the multi-agent workflow.
    """
    
    def __init__(self):
        self.crawler_agents = {
            'target_analyzer': TargetAnalysisAgent(),
            'framework_selector': FrameworkSelectorAgent(),
            'extraction_planner': ExtractionPlannerAgent(),
            'quality_validator': QualityValidationAgent(),
            'context_optimizer': ContextOptimizerAgent()
        }
        
        self.workflow_graph = None
        self.checkpoint_memory = None
        
        if LANGGRAPH_AVAILABLE:
            self._build_workflow_graph()
        
        logger.info("Advanced Crawler Orchestrator initialized")
    
    def _build_workflow_graph(self):
        """Build the LangGraph workflow."""
        # Create state graph
        workflow = StateGraph(CrawlState)
        
        # Add nodes
        workflow.add_node("analyze_target", self.crawler_agents['target_analyzer'].analyze_target)
        workflow.add_node("select_framework", self.crawler_agents['framework_selector'].select_framework)
        workflow.add_node("plan_extraction", self.crawler_agents['extraction_planner'].plan_extraction)
        workflow.add_node("optimize_context", self.crawler_agents['context_optimizer'].optimize_context)
        workflow.add_node("validate_quality", self.crawler_agents['quality_validator'].validate_quality)
        
        # Set entry point
        workflow.set_entry_point("analyze_target")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_target",
            self._should_use_cag_or_rag,
            {
                "use_cag": "optimize_context",
                "use_rag": "plan_extraction",
                "use_hybrid": "select_framework"
            }
        )
        
        # Add standard edges
        workflow.add_edge("select_framework", "plan_extraction")
        workflow.add_edge("plan_extraction", "validate_quality")
        workflow.add_edge("optimize_context", "select_framework")
        workflow.add_edge("validate_quality", END)
        
        # Compile workflow
        self.workflow_graph = workflow.compile()
        
        # Initialize checkpoint memory
        self.checkpoint_memory = MemorySaver()
    
    def _should_use_cag_or_rag(self, state: CrawlState) -> str:
        """Determine whether to use CAG or RAG based on state."""
        if not state.target_analysis:
            return "use_hybrid"
        
        complexity = state.target_analysis.get('complexity_level', 'medium')
        content_type = state.target_analysis.get('type', 'unknown')
        
        if content_type in ['static', 'documentation'] or complexity == 'low':
            return "use_cag"
        elif content_type in ['social', 'news'] or complexity == 'very_high':
            return "use_rag"
        else:
            return "use_hybrid"
    
    async def execute_workflow(self, initial_state: CrawlState) -> CrawlState:
        """Execute the complete workflow."""
        logger.info(f"Executing workflow for: {initial_state.url}")
        
        if LANGGRAPH_AVAILABLE and self.workflow_graph:
            # Use LangGraph workflow
            config = {"configurable": {"thread_id": f"crawl_{initial_state.url}"}}
            final_state = await self.workflow_graph.ainvoke(initial_state, config)
            return final_state
        else:
            # Fallback to sequential execution
            return await self._execute_sequential_workflow(initial_state)
    
    async def _execute_sequential_workflow(self, state: CrawlState) -> CrawlState:
        """Execute workflow sequentially as fallback."""
        logger.info("Using sequential workflow execution")
        
        # Execute each step
        state = await self.crawler_agents['target_analyzer'].analyze_target(state)
        
        # Determine next step based on analysis
        if state.target_analysis:
            complexity = state.target_analysis.get('complexity_level', 'medium')
            content_type = state.target_analysis.get('type', 'unknown')
            
            if content_type in ['static', 'documentation'] or complexity == 'low':
                # Use CAG path
                state = await self.crawler_agents['context_optimizer'].optimize_context(state)
                state = await self.crawler_agents['framework_selector'].select_framework(state)
                state = await self.crawler_agents['extraction_planner'].plan_extraction(state)
            elif content_type in ['social', 'news'] or complexity == 'very_high':
                # Use RAG path
                state = await self.crawler_agents['extraction_planner'].plan_extraction(state)
            else:
                # Use hybrid path
                state = await self.crawler_agents['framework_selector'].select_framework(state)
                state = await self.crawler_agents['extraction_planner'].plan_extraction(state)
        
        # Final validation
        state = await self.crawler_agents['quality_validator'].validate_quality(state)
        
        return state
    
    def get_workflow_status(self, state: "CrawlState | dict") -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        # Support both CrawlState objects and dicts
        if isinstance(state, dict):
            get = state.get
            url = get('url')
            workflow_step = get('workflow_step')
            quality_scores = get('quality_scores', {})
            performance_metrics = get('performance_metrics', {})
            errors = get('errors', [])
            warnings = get('warnings', [])
            start_time = get('start_time', 0)
        else:
            url = state.url
            workflow_step = state.workflow_step
            quality_scores = state.quality_scores
            performance_metrics = state.performance_metrics
            errors = state.errors
            warnings = state.warnings
            start_time = state.start_time
        return {
            'url': url,
            'workflow_step': workflow_step,
            'progress': self._calculate_progress(state),
            'quality_scores': quality_scores,
            'performance_metrics': performance_metrics,
            'errors': errors,
            'warnings': warnings,
            'execution_time': time.time() - start_time
        }
    
    def _calculate_progress(self, state: "CrawlState | dict") -> float:
        """Calculate workflow progress."""
        step_progress = {
            'initialized': 0.0,
            'target_analyzed': 0.2,
            'framework_selected': 0.4,
            'extraction_planned': 0.6,
            'context_optimized': 0.7,
            'quality_validated': 1.0
        }
        if isinstance(state, dict):
            workflow_step = state.get('workflow_step', 'initialized')
        else:
            workflow_step = state.workflow_step
        return step_progress.get(workflow_step, 0.0) 