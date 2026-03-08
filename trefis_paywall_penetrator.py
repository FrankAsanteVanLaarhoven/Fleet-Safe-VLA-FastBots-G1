#!/usr/bin/env python3
"""
Trefis Paywall Penetrator
Advanced paywall bypass system for Trefis.com premium content
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
from dataclasses import dataclass
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import cloudscraper
# import cfscrape  # Removed due to compatibility issues
from urllib.parse import urljoin, urlparse
import hashlib
import pickle
import os
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PaywallContent:
    """Paywall-protected content"""
    url: str
    title: str
    content: str
    content_type: str
    bypass_method: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class TrefisPaywallPenetrator:
    """Advanced paywall penetration system for Trefis.com"""
    
    def __init__(self):
        self.base_url = "https://www.trefis.com"
        self.desktop_path = Path.home() / "Desktop"
        self.output_dir = self.desktop_path / "trefis_paywall_content"
        self.session = None
        self.driver = None
        self.scraper = None
        self.ua = UserAgent()
        self.extracted_content = []
        self.bypass_methods = [
            self._bypass_cloudflare_protection,
            self._bypass_js_challenges,
            self._bypass_session_tracking,
            self._bypass_user_agent_detection,
            self._bypass_rate_limiting,
            self._bypass_cookie_tracking,
            self._bypass_fingerprinting,
            self._bypass_subscription_checks,
            self._bypass_content_encryption,
            self._bypass_api_restrictions
        ]
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Premium content URLs to target
        self.premium_urls = [
            "/premium/analysis",
            "/premium/reports",
            "/premium/data",
            "/premium/insights",
            "/premium/forecasts",
            "/premium/ratings",
            "/premium/valuation",
            "/premium/earnings",
            "/premium/guidance",
            "/premium/risk-analysis"
        ]
    
    async def initialize_penetration_tools(self):
        """Initialize all penetration tools"""
        logger.info("Initializing paywall penetration tools")
        
        # Initialize cloudscraper
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Initialize undetected Chrome
        await self._initialize_undetected_chrome()
        
        # Initialize aiohttp session
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_stealth_headers()
        )
        
        logger.info("Paywall penetration tools initialized")
    
    async def _initialize_undetected_chrome(self):
        """Initialize undetected Chrome for stealth browsing"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument(f'--user-agent={self.ua.random}')
            
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Additional stealth measures
            self.driver.execute_script("""
                // Override webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            logger.info("Undetected Chrome initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize undetected Chrome: {e}")
            self.driver = None
    
    def _get_stealth_headers(self) -> Dict[str, str]:
        """Get stealth headers for bypassing detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.trefis.com',
            'X-Forwarded-For': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        }
    
    async def penetrate_all_paywalls(self):
        """Attempt to penetrate all paywall-protected content"""
        logger.info("Starting comprehensive paywall penetration")
        
        await self.initialize_penetration_tools()
        
        try:
            # Phase 1: Discover premium content URLs
            premium_urls = await self._discover_premium_content()
            
            # Phase 2: Attempt penetration with each method
            for url in premium_urls:
                await self._penetrate_single_paywall(url)
                await asyncio.sleep(random.uniform(2, 5))  # Rate limiting
            
            # Phase 3: Extract additional premium content
            await self._extract_additional_premium_content()
            
            # Phase 4: Process and save all extracted content
            await self._process_and_save_content()
            
        finally:
            await self._cleanup()
    
    async def _discover_premium_content(self) -> List[str]:
        """Discover premium content URLs"""
        logger.info("Discovering premium content URLs")
        
        discovered_urls = []
        
        # Start with known premium URLs
        for url in self.premium_urls:
            discovered_urls.append(urljoin(self.base_url, url))
        
        # Try to discover additional premium URLs
        try:
            # Crawl main pages to find premium links
            main_pages = [
                "/data/home",
                "/data/companies",
                "/data/markets"
            ]
            
            for page in main_pages:
                page_url = urljoin(self.base_url, page)
                content = await self._fetch_with_stealth(page_url)
                
                if content:
                    # Look for premium links
                    premium_links = re.findall(r'href=["\']([^"\']*premium[^"\']*)["\']', content)
                    for link in premium_links:
                        full_url = urljoin(self.base_url, link)
                        if full_url not in discovered_urls:
                            discovered_urls.append(full_url)
        
        except Exception as e:
            logger.warning(f"Error discovering premium content: {e}")
        
        logger.info(f"Discovered {len(discovered_urls)} premium URLs")
        return discovered_urls
    
    async def _penetrate_single_paywall(self, url: str):
        """Attempt to penetrate a single paywall"""
        logger.info(f"Attempting to penetrate paywall: {url}")
        
        for i, bypass_method in enumerate(self.bypass_methods):
            try:
                logger.info(f"Trying bypass method {i+1}/{len(self.bypass_methods)}: {bypass_method.__name__}")
                
                content = await bypass_method(url)
                if content and self._is_valid_content(content):
                    # Extract and save content
                    extracted_content = await self._extract_content_from_page(url, content, bypass_method.__name__)
                    if extracted_content:
                        self.extracted_content.append(extracted_content)
                        logger.info(f"Successfully penetrated paywall using {bypass_method.__name__}")
                        break
                
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.warning(f"Bypass method {bypass_method.__name__} failed: {e}")
                continue
    
    async def _bypass_cloudflare_protection(self, url: str) -> Optional[str]:
        """Bypass Cloudflare protection"""
        logger.info("Attempting Cloudflare bypass")
        
        if self.scraper:
            try:
                response = self.scraper.get(url)
                if response.status_code == 200:
                    return response.text
            except Exception as e:
                logger.warning(f"Cloudflare bypass failed: {e}")
        
        return None
    
    async def _bypass_js_challenges(self, url: str) -> Optional[str]:
        """Bypass JavaScript challenges"""
        logger.info("Attempting JavaScript challenge bypass")
        
        if self.driver:
            try:
                self.driver.get(url)
                await asyncio.sleep(5)  # Wait for page to load
                
                # Execute JavaScript to bypass challenges
                self.driver.execute_script("""
                    // Remove paywall overlays
                    document.querySelectorAll('.paywall, .premium-overlay, .subscription-required, .locked-content').forEach(el => {
                        el.style.display = 'none';
                        el.remove();
                    });
                    
                    // Enable all content
                    document.querySelectorAll('.premium-content, .locked-content, [data-premium]').forEach(el => {
                        el.style.display = 'block';
                        el.style.visibility = 'visible';
                        el.removeAttribute('data-premium');
                    });
                    
                    // Remove subscription prompts
                    document.querySelectorAll('.subscription-prompt, .upgrade-prompt, .paywall-message').forEach(el => {
                        el.remove();
                    });
                    
                    // Enable all scripts
                    document.querySelectorAll('script').forEach(el => {
                        el.removeAttribute('disabled');
                    });
                """)
                
                # Wait for content to load
                await asyncio.sleep(3)
                
                return self.driver.page_source
                
            except Exception as e:
                logger.warning(f"JavaScript bypass failed: {e}")
        
        return None
    
    async def _bypass_session_tracking(self, url: str) -> Optional[str]:
        """Bypass session tracking"""
        logger.info("Attempting session tracking bypass")
        
        # Clear cookies and use fresh session
        if self.session:
            self.session.cookie_jar.clear()
        
        # Create new session with different fingerprint
        new_headers = self._get_stealth_headers()
        new_headers['X-Forwarded-For'] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        try:
            async with aiohttp.ClientSession(headers=new_headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as e:
            logger.warning(f"Session tracking bypass failed: {e}")
        
        return None
    
    async def _bypass_user_agent_detection(self, url: str) -> Optional[str]:
        """Bypass user agent detection"""
        logger.info("Attempting user agent detection bypass")
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        for ua in user_agents:
            headers = self._get_stealth_headers()
            headers['User-Agent'] = ua
            
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            if self._is_valid_content(content):
                                return content
            except Exception as e:
                logger.debug(f"User agent {ua} failed: {e}")
                continue
        
        return None
    
    async def _bypass_rate_limiting(self, url: str) -> Optional[str]:
        """Bypass rate limiting"""
        logger.info("Attempting rate limiting bypass")
        
        # Use different timing patterns
        delays = [0.5, 1, 1.5, 2, 2.5, 3]
        
        for delay in delays:
            await asyncio.sleep(delay)
            
            try:
                content = await self._fetch_with_stealth(url)
                if content and self._is_valid_content(content):
                    return content
            except Exception as e:
                logger.debug(f"Rate limiting bypass attempt failed: {e}")
                continue
        
        return None
    
    async def _bypass_cookie_tracking(self, url: str) -> Optional[str]:
        """Bypass cookie tracking"""
        logger.info("Attempting cookie tracking bypass")
        
        # Set fake premium cookies
        fake_cookies = {
            'premium_user': 'true',
            'subscription_active': 'true',
            'user_type': 'premium',
            'access_level': 'full',
            'trial_active': 'true'
        }
        
        try:
            async with aiohttp.ClientSession(cookies=fake_cookies) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as e:
            logger.warning(f"Cookie tracking bypass failed: {e}")
        
        return None
    
    async def _bypass_fingerprinting(self, url: str) -> Optional[str]:
        """Bypass browser fingerprinting"""
        logger.info("Attempting fingerprinting bypass")
        
        if self.driver:
            try:
                # Execute fingerprinting bypass scripts
                self.driver.execute_script("""
                    // Override canvas fingerprinting
                    const originalGetContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                        const context = originalGetContext.apply(this, [type, ...args]);
                        if (type === '2d') {
                            const originalFillText = context.fillText;
                            context.fillText = function(...args) {
                                return originalFillText.apply(this, args);
                            };
                        }
                        return context;
                    };
                    
                    // Override WebGL fingerprinting
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine';
                        }
                        return getParameter.apply(this, [parameter]);
                    };
                    
                    // Override audio fingerprinting
                    const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                    AudioBuffer.prototype.getChannelData = function(channel) {
                        const data = originalGetChannelData.apply(this, [channel]);
                        return data;
                    };
                """)
                
                self.driver.get(url)
                await asyncio.sleep(5)
                
                return self.driver.page_source
                
            except Exception as e:
                logger.warning(f"Fingerprinting bypass failed: {e}")
        
        return None
    
    async def _bypass_subscription_checks(self, url: str) -> Optional[str]:
        """Bypass subscription checks"""
        logger.info("Attempting subscription check bypass")
        
        # Try to access with subscription headers
        subscription_headers = {
            'X-Subscription-Type': 'premium',
            'X-User-Level': 'full',
            'X-Access-Token': 'premium_access',
            'Authorization': 'Bearer premium_user_token'
        }
        
        try:
            headers = {**self._get_stealth_headers(), **subscription_headers}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as e:
            logger.warning(f"Subscription check bypass failed: {e}")
        
        return None
    
    async def _bypass_content_encryption(self, url: str) -> Optional[str]:
        """Bypass content encryption"""
        logger.info("Attempting content encryption bypass")
        
        if self.driver:
            try:
                self.driver.get(url)
                await asyncio.sleep(3)
                
                # Try to decrypt content
                self.driver.execute_script("""
                    // Attempt to decrypt encrypted content
                    document.querySelectorAll('[data-encrypted], .encrypted-content').forEach(el => {
                        try {
                            // Remove encryption attributes
                            el.removeAttribute('data-encrypted');
                            el.classList.remove('encrypted-content');
                            
                            // Show content
                            el.style.display = 'block';
                            el.style.visibility = 'visible';
                        } catch(e) {
                            console.log('Decryption attempt failed:', e);
                        }
                    });
                """)
                
                await asyncio.sleep(2)
                return self.driver.page_source
                
            except Exception as e:
                logger.warning(f"Content encryption bypass failed: {e}")
        
        return None
    
    async def _bypass_api_restrictions(self, url: str) -> Optional[str]:
        """Bypass API restrictions"""
        logger.info("Attempting API restriction bypass")
        
        # Try different API endpoints
        api_variants = [
            url.replace('/premium/', '/api/premium/'),
            url.replace('/premium/', '/data/premium/'),
            url.replace('/premium/', '/v1/premium/'),
            url + '?format=json',
            url + '?api_key=premium'
        ]
        
        for api_url in api_variants:
            try:
                content = await self._fetch_with_stealth(api_url)
                if content and self._is_valid_content(content):
                    return content
            except Exception as e:
                logger.debug(f"API variant {api_url} failed: {e}")
                continue
        
        return None
    
    async def _fetch_with_stealth(self, url: str) -> Optional[str]:
        """Fetch URL with stealth techniques"""
        try:
            headers = self._get_stealth_headers()
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as e:
            logger.debug(f"Stealth fetch failed for {url}: {e}")
        
        return None
    
    def _is_valid_content(self, content: str) -> bool:
        """Check if content is valid (not paywall page)"""
        if not content:
            return False
        
        # Check for paywall indicators
        paywall_indicators = [
            'paywall',
            'premium',
            'subscription',
            'upgrade',
            'locked',
            'access denied',
            'please subscribe'
        ]
        
        content_lower = content.lower()
        for indicator in paywall_indicators:
            if indicator in content_lower:
                return False
        
        # Check for actual content
        content_indicators = [
            'analysis',
            'report',
            'data',
            'financial',
            'earnings',
            'revenue',
            'stock',
            'market'
        ]
        
        for indicator in content_indicators:
            if indicator in content_lower:
                return True
        
        return len(content) > 1000  # Minimum content length
    
    async def _extract_content_from_page(self, url: str, content: str, bypass_method: str) -> Optional[PaywallContent]:
        """Extract structured content from page"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else url.split('/')[-1]
            
            # Extract main content
            main_content = ""
            
            # Try different content selectors
            content_selectors = [
                '.content',
                '.main-content',
                '.article-content',
                '.report-content',
                '.analysis-content',
                'main',
                'article',
                '.premium-content'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element.get_text(strip=True)
                    break
            
            # If no specific content found, get body text
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(strip=True)
            
            # Determine content type
            content_type = self._determine_content_type(url, title_text, main_content)
            
            return PaywallContent(
                url=url,
                title=title_text,
                content=main_content,
                content_type=content_type,
                bypass_method=bypass_method,
                timestamp=datetime.now(),
                metadata={
                    'content_length': len(main_content),
                    'has_charts': bool(soup.find_all(['canvas', 'svg'])),
                    'has_tables': bool(soup.find_all('table')),
                    'has_images': bool(soup.find_all('img'))
                }
            )
            
        except Exception as e:
            logger.warning(f"Error extracting content from {url}: {e}")
            return None
    
    def _determine_content_type(self, url: str, title: str, content: str) -> str:
        """Determine the type of content"""
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        if 'analysis' in url_lower or 'analysis' in title_lower:
            return 'analysis'
        elif 'report' in url_lower or 'report' in title_lower:
            return 'report'
        elif 'data' in url_lower or 'metrics' in url_lower:
            return 'data'
        elif 'earnings' in url_lower or 'earnings' in content_lower:
            return 'earnings'
        elif 'forecast' in url_lower or 'forecast' in content_lower:
            return 'forecast'
        elif 'rating' in url_lower or 'rating' in content_lower:
            return 'rating'
        else:
            return 'premium_content'
    
    async def _extract_additional_premium_content(self):
        """Extract additional premium content"""
        logger.info("Extracting additional premium content")
        
        # Look for premium content in JavaScript
        if self.driver:
            try:
                # Execute script to find premium content
                premium_data = self.driver.execute_script("""
                    // Look for premium data in JavaScript variables
                    const premiumData = {};
                    
                    // Check for common variable names
                    const variableNames = ['premiumData', 'premiumContent', 'lockedContent', 'subscriptionData'];
                    
                    variableNames.forEach(name => {
                        if (window[name]) {
                            premiumData[name] = window[name];
                        }
                    });
                    
                    // Look for data in script tags
                    document.querySelectorAll('script').forEach(script => {
                        const content = script.textContent;
                        if (content.includes('premium') || content.includes('subscription')) {
                            premiumData['script_' + script.src] = content;
                        }
                    });
                    
                    return premiumData;
                """)
                
                if premium_data:
                    # Save premium data
                    self._save_json("premium_data_from_js", premium_data)
                    logger.info("Extracted premium data from JavaScript")
                
            except Exception as e:
                logger.warning(f"Error extracting premium data from JavaScript: {e}")
    
    async def _process_and_save_content(self):
        """Process and save all extracted content"""
        logger.info("Processing and saving extracted content")
        
        # Save individual content files
        for i, content in enumerate(self.extracted_content):
            filename = f"paywall_content_{i+1}_{content.content_type}"
            self._save_content(filename, content)
        
        # Create summary
        await self._create_penetration_summary()
        
        # Save to database
        self._save_to_database()
        
        logger.info(f"Saved {len(self.extracted_content)} pieces of paywall content")
    
    def _save_content(self, filename: str, content: PaywallContent):
        """Save content to file"""
        # Save as text
        text_path = self.output_dir / f"{filename}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {content.title}\n")
            f.write(f"URL: {content.url}\n")
            f.write(f"Content Type: {content.content_type}\n")
            f.write(f"Bypass Method: {content.bypass_method}\n")
            f.write(f"Timestamp: {content.timestamp}\n")
            f.write(f"Content Length: {len(content.content)}\n")
            f.write("\n" + "="*50 + "\n\n")
            f.write(content.content)
        
        # Save as JSON
        json_path = self.output_dir / f"{filename}.json"
        self._save_json(filename, {
            'url': content.url,
            'title': content.title,
            'content': content.content,
            'content_type': content.content_type,
            'bypass_method': content.bypass_method,
            'timestamp': content.timestamp.isoformat(),
            'metadata': content.metadata
        })
    
    async def _create_penetration_summary(self):
        """Create penetration summary"""
        summary = {
            'penetration_date': datetime.now().isoformat(),
            'total_content_extracted': len(self.extracted_content),
            'bypass_methods_used': list(set(content.bypass_method for content in self.extracted_content)),
            'content_types': list(set(content.content_type for content in self.extracted_content)),
            'successful_urls': [content.url for content in self.extracted_content],
            'statistics': {
                'total_content_length': sum(len(content.content) for content in self.extracted_content),
                'average_content_length': sum(len(content.content) for content in self.extracted_content) / len(self.extracted_content) if self.extracted_content else 0,
                'bypass_method_effectiveness': {}
            }
        }
        
        # Calculate bypass method effectiveness
        method_counts = {}
        for content in self.extracted_content:
            method_counts[content.bypass_method] = method_counts.get(content.bypass_method, 0) + 1
        
        summary['statistics']['bypass_method_effectiveness'] = method_counts
        
        self._save_json("penetration_summary", summary)
        
        # Create human-readable summary
        summary_text = f"""
TREFIS PAYWALL PENETRATION SUMMARY
==================================

Penetration Date: {summary['penetration_date']}
Total Content Extracted: {summary['total_content_extracted']}

BYPASS METHODS USED:
{chr(10).join(f"- {method}" for method in summary['bypass_methods_used'])}

CONTENT TYPES EXTRACTED:
{chr(10).join(f"- {content_type}" for content_type in summary['content_types'])}

SUCCESSFUL URLS:
{chr(10).join(f"- {url}" for url in summary['successful_urls'][:10])}
{'...' if len(summary['successful_urls']) > 10 else ''}

STATISTICS:
- Total Content Length: {summary['statistics']['total_content_length']:,} characters
- Average Content Length: {summary['statistics']['average_content_length']:.0f} characters

BYPASS METHOD EFFECTIVENESS:
{chr(10).join(f"- {method}: {count} successful extractions" for method, count in summary['statistics']['bypass_method_effectiveness'].items())}

OUTPUT LOCATION: {self.output_dir}
        """
        
        with open(self.output_dir / "penetration_summary.txt", 'w') as f:
            f.write(summary_text)
    
    def _save_to_database(self):
        """Save content to SQLite database"""
        db_path = self.output_dir / "paywall_content.db"
        
        with sqlite3.connect(db_path) as conn:
            # Create paywall content table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS paywall_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    content_type TEXT,
                    bypass_method TEXT,
                    timestamp TEXT,
                    content_length INTEGER,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert content
            for content in self.extracted_content:
                conn.execute("""
                    INSERT INTO paywall_content 
                    (url, title, content, content_type, bypass_method, timestamp, content_length, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content.url,
                    content.title,
                    content.content,
                    content.content_type,
                    content.bypass_method,
                    content.timestamp.isoformat(),
                    len(content.content),
                    json.dumps(content.metadata) if content.metadata else None
                ))
            
            conn.commit()
        
        logger.info(f"Saved paywall content to database: {db_path}")
    
    def _save_json(self, filename: str, data: Any):
        """Save JSON data"""
        file_path = self.output_dir / f"{filename}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def _cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        
        if self.driver:
            self.driver.quit()

async def main():
    """Main execution function"""
    penetrator = TrefisPaywallPenetrator()
    await penetrator.penetrate_all_paywalls()

if __name__ == "__main__":
    asyncio.run(main()) 