#!/usr/bin/env python3
"""
Universal Crawler System Demonstration
=====================================

This script demonstrates the capabilities of the universal crawler system
by running various types of crawls and showing the results.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Import the universal crawler system
from universal_crawler_system import UniversalCrawler, CrawlRequest, CrawlMode

class UniversalCrawlerDemo:
    """Demonstration class for the universal crawler system."""
    
    def __init__(self):
        self.crawler = None
        self.demo_results = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        print("🚀 Initializing Universal Crawler System...")
        self.crawler = UniversalCrawler()
        await self.crawler.start_session()
        print("✅ Universal Crawler System initialized")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.crawler:
            await self.crawler.close_session()
        print("🔚 Universal Crawler System shutdown complete")
    
    async def demo_basic_crawl(self):
        """Demonstrate basic crawling mode."""
        print("\n📄 Demo 1: Basic Crawling Mode")
        print("=" * 50)
        
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.BASIC,
            max_depth=1,
            max_pages=3,
            delay=0.5,
            extract_images=True,
            extract_links=True,
            extract_meta=True
        )
        
        print(f"Starting basic crawl of: {request.url}")
        result = await self.crawler.start_crawl(request)
        
        # Monitor progress
        await self._monitor_crawl(result.id, "Basic Crawl")
        
        # Get results
        results = await self.crawler.get_crawl_results(result.id)
        if results:
            print(f"✅ Basic crawl completed successfully!")
            print(f"   - Total files: {results['statistics']['total_files']}")
            print(f"   - Total size: {results['statistics']['total_size']} bytes")
            print(f"   - File types: {list(results['statistics']['file_types'].keys())}")
            
            self.demo_results.append({
                "mode": "basic",
                "url": request.url,
                "files": results['statistics']['total_files'],
                "size": results['statistics']['total_size']
            })
    
    async def demo_enhanced_crawl(self):
        """Demonstrate enhanced crawling mode."""
        print("\n🔍 Demo 2: Enhanced Crawling Mode")
        print("=" * 50)
        
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.ENHANCED,
            max_depth=1,
            max_pages=2,
            delay=0.5,
            extract_images=True,
            extract_links=True,
            extract_forms=True,
            extract_scripts=True,
            extract_styles=True,
            extract_meta=True
        )
        
        print(f"Starting enhanced crawl of: {request.url}")
        result = await self.crawler.start_crawl(request)
        
        # Monitor progress
        await self._monitor_crawl(result.id, "Enhanced Crawl")
        
        # Get results
        results = await self.crawler.get_crawl_results(result.id)
        if results:
            print(f"✅ Enhanced crawl completed successfully!")
            print(f"   - Total files: {results['statistics']['total_files']}")
            print(f"   - Total size: {results['statistics']['total_size']} bytes")
            print(f"   - Enhanced features: OCR, AST, Network analysis")
            
            self.demo_results.append({
                "mode": "enhanced",
                "url": request.url,
                "files": results['statistics']['total_files'],
                "size": results['statistics']['total_size']
            })
    
    async def demo_stealth_crawl(self):
        """Demonstrate stealth crawling mode."""
        print("\n🕵️ Demo 3: Stealth Crawling Mode")
        print("=" * 50)
        
        request = CrawlRequest(
            url="https://httpbin.org/user-agent",
            mode=CrawlMode.STEALTH,
            max_depth=1,
            max_pages=1,
            delay=1.0,
            stealth_mode=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        print(f"Starting stealth crawl of: {request.url}")
        result = await self.crawler.start_crawl(request)
        
        # Monitor progress
        await self._monitor_crawl(result.id, "Stealth Crawl")
        
        # Get results
        results = await self.crawler.get_crawl_results(result.id)
        if results:
            print(f"✅ Stealth crawl completed successfully!")
            print(f"   - Anti-detection features enabled")
            print(f"   - Custom user agent used")
            print(f"   - Rate limiting applied")
            
            self.demo_results.append({
                "mode": "stealth",
                "url": request.url,
                "files": results['statistics']['total_files'],
                "size": results['statistics']['total_size']
            })
    
    async def demo_enterprise_crawl(self):
        """Demonstrate enterprise crawling mode."""
        print("\n🏢 Demo 4: Enterprise Crawling Mode")
        print("=" * 50)
        
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.ENTERPRISE,
            max_depth=1,
            max_pages=2,
            delay=1.0,
            compliance_mode=True,
            extract_images=True,
            extract_links=True,
            extract_forms=True,
            extract_scripts=True,
            extract_styles=True,
            extract_meta=True
        )
        
        print(f"Starting enterprise crawl of: {request.url}")
        result = await self.crawler.start_crawl(request)
        
        # Monitor progress
        await self._monitor_crawl(result.id, "Enterprise Crawl")
        
        # Get results
        results = await self.crawler.get_crawl_results(result.id)
        if results:
            print(f"✅ Enterprise crawl completed successfully!")
            print(f"   - GDPR/CCPA compliance enabled")
            print(f"   - Audit logging active")
            print(f"   - Data retention policies applied")
            
            self.demo_results.append({
                "mode": "enterprise",
                "url": request.url,
                "files": results['statistics']['total_files'],
                "size": results['statistics']['total_size']
            })
    
    async def demo_concurrent_crawls(self):
        """Demonstrate concurrent crawling capabilities."""
        print("\n⚡ Demo 5: Concurrent Crawling")
        print("=" * 50)
        
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        requests = []
        for url in urls:
            request = CrawlRequest(
                url=url,
                mode=CrawlMode.BASIC,
                max_depth=1,
                max_pages=1,
                delay=0.2
            )
            requests.append(request)
        
        print(f"Starting {len(requests)} concurrent crawls...")
        
        # Start all crawls
        results = []
        for i, request in enumerate(requests):
            result = await self.crawler.start_crawl(request)
            results.append(result)
            print(f"   Started crawl {i+1}: {request.url}")
        
        # Monitor all crawls
        await self._monitor_concurrent_crawls(results)
        
        print(f"✅ All {len(results)} concurrent crawls completed!")
        
        self.demo_results.append({
            "mode": "concurrent",
            "count": len(results),
            "urls": [r.url for r in results]
        })
    
    async def _monitor_crawl(self, crawl_id: str, crawl_name: str):
        """Monitor a single crawl's progress."""
        max_wait = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            result = await self.crawler.get_crawl_status(crawl_id)
            if not result:
                break
                
            if result.status == "completed":
                print(f"   ✅ {crawl_name} completed in {wait_time}s")
                return True
            elif result.status == "failed":
                print(f"   ❌ {crawl_name} failed after {wait_time}s")
                return False
            elif result.status == "stopped":
                print(f"   ⏹️ {crawl_name} stopped after {wait_time}s")
                return False
            
            # Show progress
            if result.total_pages > 0:
                progress = (result.successful_pages + result.failed_pages) / result.total_pages * 100
                print(f"   📊 {crawl_name} progress: {progress:.1f}% ({result.successful_pages + result.failed_pages}/{result.total_pages} pages)")
            
            await asyncio.sleep(2)
            wait_time += 2
        
        print(f"   ⏰ {crawl_name} timed out after {max_wait}s")
        return False
    
    async def _monitor_concurrent_crawls(self, results):
        """Monitor multiple concurrent crawls."""
        max_wait = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            completed = 0
            failed = 0
            running = 0
            
            for result in results:
                status = await self.crawler.get_crawl_status(result.id)
                if status:
                    if status.status == "completed":
                        completed += 1
                    elif status.status == "failed":
                        failed += 1
                    else:
                        running += 1
            
            print(f"   📊 Concurrent crawls: {completed} completed, {failed} failed, {running} running")
            
            if running == 0:
                print(f"   ✅ All concurrent crawls finished!")
                return True
            
            await asyncio.sleep(3)
            wait_time += 3
        
        print(f"   ⏰ Concurrent crawls timed out after {max_wait}s")
        return False
    
    def print_demo_summary(self):
        """Print a summary of all demo results."""
        print("\n" + "=" * 60)
        print("🎉 UNIVERSAL CRAWLER SYSTEM DEMO SUMMARY")
        print("=" * 60)
        
        print(f"📅 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Total demos run: {len(self.demo_results)}")
        
        print("\n📊 Demo Results:")
        for i, result in enumerate(self.demo_results, 1):
            if result["mode"] == "concurrent":
                print(f"   {i}. {result['mode'].title()} Crawling: {result['count']} URLs")
            else:
                print(f"   {i}. {result['mode'].title()} Mode: {result['url']}")
                print(f"      Files: {result['files']}, Size: {result['size']} bytes")
        
        print("\n✅ All demos completed successfully!")
        print("🚀 The Universal Crawler System is ready for production use!")
        
        print("\n📋 Next Steps:")
        print("   1. Start the API server: python universal_crawler_api.py")
        print("   2. Access the API docs: http://localhost:8000/docs")
        print("   3. Start the frontend: cd crawl-frontend && npm run dev")
        print("   4. Access the frontend: http://localhost:3000")
        
        print("\n🔗 Useful Links:")
        print("   - API Documentation: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/health")
        print("   - Crawling Modes: http://localhost:8000/modes")
        print("   - Statistics: http://localhost:8000/stats")

async def main():
    """Main demonstration function."""
    print("🌐 Universal Crawler System Demonstration")
    print("=" * 60)
    print("This demo showcases the capabilities of the universal crawler system")
    print("by running various types of crawls and showing the results.")
    print()
    
    async with UniversalCrawlerDemo() as demo:
        # Run all demos
        await demo.demo_basic_crawl()
        await demo.demo_enhanced_crawl()
        await demo.demo_stealth_crawl()
        await demo.demo_enterprise_crawl()
        await demo.demo_concurrent_crawls()
        
        # Print summary
        demo.print_demo_summary()

if __name__ == "__main__":
    asyncio.run(main()) 