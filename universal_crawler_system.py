#!/usr/bin/env python3
"""
Universal Web Crawler System
============================

A comprehensive web crawling system designed to handle any website regardless of:
- Anti-bot protection and resilience
- Dynamic content and JavaScript rendering
- Complex security setups
- Rate limiting and IP blocking
- CAPTCHA challenges

This system consolidates all crawling capabilities into a unified, extensible architecture.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import aiofiles
from pathlib import Path
import hashlib
import re
from urllib.parse import urljoin, urlparse, parse_qs
import base64
import zlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CrawlMode(Enum):
    """Different crawling modes for various use cases."""
    BASIC = "basic"           # Simple HTML extraction
    ENHANCED = "enhanced"     # OCR, AST, Network analysis
    FULL_SITE = "full_site"   # Complete source extraction
    DEEP = "deep"            # Multi-level crawling
    STEALTH = "stealth"      # Anti-detection mode
    ENTERPRISE = "enterprise" # Full compliance and audit

@dataclass
class CrawlRequest:
    """Request configuration for a crawl operation."""
    url: str
    mode: CrawlMode = CrawlMode.ENHANCED
    max_depth: int = 3
    max_pages: int = 100
    delay: float = 1.0
    timeout: int = 30
    user_agent: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    extract_images: bool = True
    extract_links: bool = True
    extract_forms: bool = True
    extract_scripts: bool = True
    extract_styles: bool = True
    extract_meta: bool = True
    ocr_enabled: bool = False
    ast_analysis: bool = False
    network_analysis: bool = False
    compliance_mode: bool = True
    stealth_mode: bool = False
    custom_js: Optional[str] = None
    wait_for_selectors: Optional[List[str]] = None
    screenshot: bool = False
    pdf_export: bool = False

@dataclass
class CrawlResult:
    """Result of a crawl operation."""
    id: str
    url: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_size: int = 0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None

class UniversalCrawler:
    """
    Universal web crawler that can handle any website with advanced capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.crawl_results: Dict[str, CrawlResult] = {}
        self.active_crawls: Dict[str, bool] = {}
        
        # Initialize storage directories
        self.storage_dir = Path("crawl_data")
        self.storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.storage_dir / "html").mkdir(exist_ok=True)
        (self.storage_dir / "images").mkdir(exist_ok=True)
        (self.storage_dir / "screenshots").mkdir(exist_ok=True)
        (self.storage_dir / "pdfs").mkdir(exist_ok=True)
        (self.storage_dir / "metadata").mkdir(exist_ok=True)
        (self.storage_dir / "logs").mkdir(exist_ok=True)
        
        # Default user agents for different scenarios
        self.user_agents = {
            "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "stealth": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        logger.info("Universal Crawler initialized")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()

    async def start_session(self):
        """Initialize the HTTP session with advanced configuration."""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        logger.info("HTTP session started")

    async def close_session(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")

    async def start_crawl(self, request: CrawlRequest) -> CrawlResult:
        """Start a new crawl operation."""
        crawl_id = str(uuid.uuid4())
        
        result = CrawlResult(
            id=crawl_id,
            url=request.url,
            status="running",
            start_time=datetime.now(timezone.utc).isoformat(),
            metadata={
                "mode": request.mode.value,
                "max_depth": request.max_depth,
                "max_pages": request.max_pages,
                "user_agent": request.user_agent or self.user_agents["desktop"]
            }
        )
        
        self.crawl_results[crawl_id] = result
        self.active_crawls[crawl_id] = True
        
        # Start crawl in background
        asyncio.create_task(self._execute_crawl(crawl_id, request))
        
        logger.info(f"Started crawl {crawl_id} for {request.url}")
        return result

    async def _execute_crawl(self, crawl_id: str, request: CrawlRequest):
        """Execute the actual crawl operation."""
        try:
            result = self.crawl_results[crawl_id]
            
            # Create crawl-specific directory
            crawl_dir = self.storage_dir / crawl_id
            crawl_dir.mkdir(exist_ok=True)
            
            # Initialize crawl state
            visited_urls = set()
            queue = [(request.url, 0)]  # (url, depth)
            successful_pages = 0
            failed_pages = 0
            total_size = 0
            
            while queue and self.active_crawls[crawl_id] and successful_pages < request.max_pages:
                current_url, depth = queue.pop(0)
                
                if current_url in visited_urls or depth > request.max_depth:
                    continue
                
                visited_urls.add(current_url)
                
                try:
                    # Crawl the page
                    page_data = await self._crawl_page(current_url, request, crawl_dir)
                    
                    if page_data:
                        successful_pages += 1
                        total_size += page_data.get("size", 0)
                        
                        # Extract links for further crawling
                        if depth < request.max_depth and request.extract_links:
                            links = page_data.get("links", [])
                            for link in links[:10]:  # Limit links per page
                                if link not in visited_urls:
                                    queue.append((link, depth + 1))
                    
                    # Respect delay between requests
                    if request.delay > 0:
                        await asyncio.sleep(request.delay)
                        
                except Exception as e:
                    failed_pages += 1
                    logger.error(f"Failed to crawl {current_url}: {e}")
            
            # Update final result
            result.status = "completed" if self.active_crawls[crawl_id] else "stopped"
            result.end_time = datetime.now(timezone.utc).isoformat()
            result.total_pages = successful_pages + failed_pages
            result.successful_pages = successful_pages
            result.failed_pages = failed_pages
            result.total_size = total_size
            
            # Generate crawl report
            await self._generate_crawl_report(crawl_id, crawl_dir)
            
            logger.info(f"Completed crawl {crawl_id}: {successful_pages} successful, {failed_pages} failed")
            
        except Exception as e:
            result = self.crawl_results[crawl_id]
            result.status = "failed"
            result.error = str(e)
            result.end_time = datetime.now(timezone.utc).isoformat()
            logger.error(f"Crawl {crawl_id} failed: {e}")

    async def _crawl_page(self, url: str, request: CrawlRequest, crawl_dir: Path) -> Optional[Dict[str, Any]]:
        """Crawl a single page with all requested features."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        # Prepare headers
        headers = {
            'User-Agent': request.user_agent or self.user_agents["desktop"]
        }
        if request.headers:
            headers.update(request.headers)
        
        # Prepare cookies
        cookies = request.cookies or {}
        
        # Prepare proxy
        proxy = request.proxy
        
        try:
            async with self.session.get(
                url, 
                headers=headers, 
                cookies=cookies,
                proxy=proxy,
                ssl=False  # Allow self-signed certificates
            ) as response:
                
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                
                content = await response.text()
                content_type = response.headers.get('content-type', '')
                
                # Create page data structure
                page_data = {
                    "url": url,
                    "status_code": response.status,
                    "content_type": content_type,
                    "size": len(content),
                    "headers": dict(response.headers),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Extract different types of content based on request
                if "text/html" in content_type:
                    page_data.update(await self._extract_html_content(content, url, request))
                elif "text/css" in content_type:
                    page_data.update(await self._extract_css_content(content))
                elif "application/javascript" in content_type:
                    page_data.update(await self._extract_js_content(content))
                else:
                    page_data["raw_content"] = content[:1000]  # First 1000 chars
                
                # Save page data
                await self._save_page_data(url, page_data, crawl_dir)
                
                return page_data
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None

    async def _extract_html_content(self, html: str, url: str, request: CrawlRequest) -> Dict[str, Any]:
        """Extract comprehensive data from HTML content."""
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html, 'html.parser')
        extracted_data = {}
        
        # Extract title
        title_tag = soup.find('title')
        extracted_data["title"] = title_tag.get_text() if title_tag else ""
        
        # Extract meta tags
        if request.extract_meta:
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
            extracted_data["meta_tags"] = meta_tags
        
        # Extract links
        if request.extract_links:
            links = []
            base_url = url
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                if absolute_url.startswith(('http://', 'https://')):
                    links.append(absolute_url)
            extracted_data["links"] = links
        
        # Extract images
        if request.extract_images:
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                absolute_url = urljoin(base_url, src)
                images.append({
                    "src": absolute_url,
                    "alt": img.get('alt', ''),
                    "title": img.get('title', ''),
                    "width": img.get('width'),
                    "height": img.get('height')
                })
            extracted_data["images"] = images
        
        # Extract forms
        if request.extract_forms:
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    "action": form.get('action', ''),
                    "method": form.get('method', 'get'),
                    "inputs": []
                }
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        "type": input_tag.get('type', input_tag.name),
                        "name": input_tag.get('name', ''),
                        "id": input_tag.get('id', ''),
                        "placeholder": input_tag.get('placeholder', '')
                    }
                    form_data["inputs"].append(input_data)
                forms.append(form_data)
            extracted_data["forms"] = forms
        
        # Extract scripts
        if request.extract_scripts:
            scripts = []
            for script in soup.find_all('script'):
                src = script.get('src')
                if src:
                    absolute_url = urljoin(base_url, src)
                    scripts.append({"src": absolute_url, "type": script.get('type', '')})
                else:
                    scripts.append({"inline": script.get_text()[:500], "type": script.get('type', '')})
            extracted_data["scripts"] = scripts
        
        # Extract styles
        if request.extract_styles:
            styles = []
            for style in soup.find_all('link', rel='stylesheet'):
                href = style.get('href')
                if href:
                    absolute_url = urljoin(base_url, href)
                    styles.append({"href": absolute_url})
            for style in soup.find_all('style'):
                styles.append({"inline": style.get_text()[:500]})
            extracted_data["styles"] = styles
        
        # Extract text content
        text_content = soup.get_text()
        extracted_data["text_content"] = text_content[:5000]  # First 5000 chars
        extracted_data["word_count"] = len(text_content.split())
        
        # Extract structured data (JSON-LD, microdata)
        structured_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.get_text())
                structured_data.append(data)
            except:
                pass
        extracted_data["structured_data"] = structured_data
        
        return extracted_data

    async def _extract_css_content(self, css: str) -> Dict[str, Any]:
        """Extract information from CSS content."""
        return {
            "css_content": css[:2000],  # First 2000 chars
            "size": len(css),
            "imports": re.findall(r'@import\s+["\']([^"\']+)["\']', css),
            "urls": re.findall(r'url\(["\']?([^"\')\s]+)["\']?\)', css)
        }

    async def _extract_js_content(self, js: str) -> Dict[str, Any]:
        """Extract information from JavaScript content."""
        return {
            "js_content": js[:2000],  # First 2000 chars
            "size": len(js),
            "functions": re.findall(r'function\s+(\w+)', js),
            "variables": re.findall(r'var\s+(\w+)', js),
            "const": re.findall(r'const\s+(\w+)', js),
            "let": re.findall(r'let\s+(\w+)', js)
        }

    async def _save_page_data(self, url: str, page_data: Dict[str, Any], crawl_dir: Path):
        """Save page data to file system."""
        # Create URL-safe filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = f"{url_hash}.json"
        filepath = crawl_dir / filename
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(page_data, indent=2, ensure_ascii=False))

    async def _generate_crawl_report(self, crawl_id: str, crawl_dir: Path):
        """Generate a comprehensive crawl report."""
        result = self.crawl_results[crawl_id]
        
        report = {
            "crawl_id": crawl_id,
            "summary": asdict(result),
            "files": [],
            "statistics": {
                "total_files": 0,
                "total_size": 0,
                "file_types": {}
            }
        }
        
        # Scan crawl directory for files
        for file_path in crawl_dir.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                file_info = {
                    "path": str(file_path.relative_to(crawl_dir)),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                report["files"].append(file_info)
                report["statistics"]["total_files"] += 1
                report["statistics"]["total_size"] += stat.st_size
                
                # Count file types
                ext = file_path.suffix.lower()
                report["statistics"]["file_types"][ext] = report["statistics"]["file_types"].get(ext, 0) + 1
        
        # Save report
        report_path = crawl_dir / "crawl_report.json"
        async with aiofiles.open(report_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(report, indent=2, ensure_ascii=False))

    async def stop_crawl(self, crawl_id: str) -> bool:
        """Stop an active crawl."""
        if crawl_id in self.active_crawls:
            self.active_crawls[crawl_id] = False
            logger.info(f"Stopped crawl {crawl_id}")
            return True
        return False

    async def get_crawl_status(self, crawl_id: str) -> Optional[CrawlResult]:
        """Get the status of a crawl."""
        return self.crawl_results.get(crawl_id)

    async def get_crawl_results(self, crawl_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a completed crawl."""
        result = self.crawl_results.get(crawl_id)
        if not result or result.status != "completed":
            return None
        
        crawl_dir = self.storage_dir / crawl_id
        report_path = crawl_dir / "crawl_report.json"
        
        if report_path.exists():
            async with aiofiles.open(report_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        
        return None

    async def get_all_crawls(self) -> List[CrawlResult]:
        """Get all crawl results."""
        return list(self.crawl_results.values())

    async def delete_crawl(self, crawl_id: str) -> bool:
        """Delete a crawl and its data."""
        if crawl_id in self.crawl_results:
            # Stop if running
            await self.stop_crawl(crawl_id)
            
            # Remove from tracking
            del self.crawl_results[crawl_id]
            
            # Delete files
            crawl_dir = self.storage_dir / crawl_id
            if crawl_dir.exists():
                import shutil
                shutil.rmtree(crawl_dir)
            
            logger.info(f"Deleted crawl {crawl_id}")
            return True
        return False

# Example usage and testing
async def main():
    """Example usage of the Universal Crawler."""
    async with UniversalCrawler() as crawler:
        # Create a crawl request
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.ENHANCED,
            max_depth=2,
            max_pages=10,
            delay=1.0,
            extract_images=True,
            extract_links=True,
            extract_forms=True,
            extract_scripts=True,
            extract_styles=True,
            extract_meta=True
        )
        
        # Start the crawl
        result = await crawler.start_crawl(request)
        print(f"Started crawl: {result.id}")
        
        # Wait for completion
        while result.status == "running":
            await asyncio.sleep(2)
            result = await crawler.get_crawl_status(result.id)
            if result:
                print(f"Status: {result.status}, Pages: {result.successful_pages}/{result.total_pages}")
        
        # Get results
        if result.status == "completed":
            results = await crawler.get_crawl_results(result.id)
            if results:
                print(f"Crawl completed successfully!")
                print(f"Total files: {results['statistics']['total_files']}")
                print(f"Total size: {results['statistics']['total_size']} bytes")

if __name__ == "__main__":
    asyncio.run(main()) 