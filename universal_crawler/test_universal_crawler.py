#!/usr/bin/env python3
"""
Universal Crawler Test Suite
============================

Comprehensive tests for the universal crawler system.
Tests all major components and functionality.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

# Import the modules to test
from universal_crawler_system import (
    UniversalCrawler, 
    CrawlRequest, 
    CrawlMode, 
    CrawlResult
)
from config import Config, get_config, create_default_config

class TestCrawlRequest:
    """Test CrawlRequest dataclass."""
    
    def test_crawl_request_creation(self):
        """Test creating a CrawlRequest."""
        request = CrawlRequest(
            url="https://example.com",
            mode=CrawlMode.ENHANCED,
            max_depth=3,
            max_pages=100
        )
        
        assert request.url == "https://example.com"
        assert request.mode == CrawlMode.ENHANCED
        assert request.max_depth == 3
        assert request.max_pages == 100
        assert request.delay == 1.0  # Default value
        assert request.timeout == 30  # Default value
    
    def test_crawl_request_defaults(self):
        """Test CrawlRequest default values."""
        request = CrawlRequest(url="https://example.com")
        
        assert request.mode == CrawlMode.ENHANCED
        assert request.max_depth == 3
        assert request.max_pages == 100
        assert request.extract_images is True
        assert request.extract_links is True
        assert request.compliance_mode is True

class TestCrawlResult:
    """Test CrawlResult dataclass."""
    
    def test_crawl_result_creation(self):
        """Test creating a CrawlResult."""
        result = CrawlResult(
            id="test-id",
            url="https://example.com",
            status="running",
            start_time="2024-01-01T00:00:00Z"
        )
        
        assert result.id == "test-id"
        assert result.url == "https://example.com"
        assert result.status == "running"
        assert result.start_time == "2024-01-01T00:00:00Z"
        assert result.total_pages == 0  # Default value
        assert result.successful_pages == 0  # Default value
        assert result.failed_pages == 0  # Default value

class TestConfig:
    """Test configuration system."""
    
    def test_config_creation(self):
        """Test creating a Config instance."""
        config = Config()
        
        assert config.environment.value == "development"
        assert config.database.url == "sqlite:///crawler.db"
        assert config.api.port == 8000
        assert config.storage.base_path == "crawl_data"
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        errors = config.validate()
        
        # Should not have errors with default config
        assert len(errors) == 0
    
    def test_config_environment_variables(self):
        """Test loading configuration from environment variables."""
        with patch.dict(os.environ, {
            'API_PORT': '9000',
            'STORAGE_PATH': 'test_data',
            'LOG_LEVEL': 'DEBUG'
        }):
            config = Config()
            config.load_environment_variables()
            
            assert config.api.port == 9000
            assert config.storage.base_path == "test_data"
            assert config.logging.level == "DEBUG"
    
    def test_create_default_config(self, tmp_path):
        """Test creating default configuration file."""
        config_path = tmp_path / "test_config.json"
        create_default_config(str(config_path))
        
        assert config_path.exists()
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        assert "database" in config_data
        assert "storage" in config_data
        assert "api" in config_data
        assert "crawler" in config_data

class TestUniversalCrawler:
    """Test UniversalCrawler class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def crawler(self, temp_dir):
        """Create a crawler instance for testing."""
        async with UniversalCrawler({"storage_dir": temp_dir}) as crawler:
            yield crawler
    
    def test_crawler_initialization(self, temp_dir):
        """Test crawler initialization."""
        crawler = UniversalCrawler({"storage_dir": temp_dir})
        
        assert crawler.storage_dir == Path(temp_dir)
        assert crawler.session is None
        assert len(crawler.crawl_results) == 0
        assert len(crawler.active_crawls) == 0
    
    @pytest.mark.asyncio
    async def test_crawler_context_manager(self, temp_dir):
        """Test crawler as async context manager."""
        async with UniversalCrawler({"storage_dir": temp_dir}) as crawler:
            assert crawler.session is not None
            assert not crawler.session.closed
        
        # Session should be closed after context exit
        assert crawler.session.closed
    
    @pytest.mark.asyncio
    async def test_start_crawl(self, crawler):
        """Test starting a crawl."""
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.BASIC,
            max_depth=1,
            max_pages=1
        )
        
        result = await crawler.start_crawl(request)
        
        assert result.id is not None
        assert result.url == "https://httpbin.org"
        assert result.status == "running"
        assert result.start_time is not None
        
        # Check that crawl is tracked
        assert result.id in crawler.crawl_results
        assert result.id in crawler.active_crawls
        assert crawler.active_crawls[result.id] is True
    
    @pytest.mark.asyncio
    async def test_stop_crawl(self, crawler):
        """Test stopping a crawl."""
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.BASIC,
            max_depth=1,
            max_pages=1
        )
        
        result = await crawler.start_crawl(request)
        
        # Stop the crawl
        success = await crawler.stop_crawl(result.id)
        assert success is True
        
        # Check that crawl is marked as stopped
        assert crawler.active_crawls[result.id] is False
    
    @pytest.mark.asyncio
    async def test_get_crawl_status(self, crawler):
        """Test getting crawl status."""
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.BASIC,
            max_depth=1,
            max_pages=1
        )
        
        result = await crawler.start_crawl(request)
        
        # Get status
        status = await crawler.get_crawl_status(result.id)
        assert status is not None
        assert status.id == result.id
        assert status.url == result.url
        assert status.status == "running"
    
    @pytest.mark.asyncio
    async def test_get_crawl_status_not_found(self, crawler):
        """Test getting status of non-existent crawl."""
        status = await crawler.get_crawl_status("non-existent-id")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_delete_crawl(self, crawler):
        """Test deleting a crawl."""
        request = CrawlRequest(
            url="https://httpbin.org",
            mode=CrawlMode.BASIC,
            max_depth=1,
            max_pages=1
        )
        
        result = await crawler.start_crawl(request)
        
        # Delete the crawl
        success = await crawler.delete_crawl(result.id)
        assert success is True
        
        # Check that crawl is removed
        assert result.id not in crawler.crawl_results
        assert result.id not in crawler.active_crawls
    
    @pytest.mark.asyncio
    async def test_delete_crawl_not_found(self, crawler):
        """Test deleting non-existent crawl."""
        success = await crawler.delete_crawl("non-existent-id")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_all_crawls(self, crawler):
        """Test getting all crawls."""
        # Start multiple crawls
        request1 = CrawlRequest(url="https://httpbin.org", mode=CrawlMode.BASIC)
        request2 = CrawlRequest(url="https://example.com", mode=CrawlMode.BASIC)
        
        result1 = await crawler.start_crawl(request1)
        result2 = await crawler.start_crawl(request2)
        
        # Get all crawls
        all_crawls = await crawler.get_all_crawls()
        
        assert len(all_crawls) == 2
        crawl_ids = [crawl.id for crawl in all_crawls]
        assert result1.id in crawl_ids
        assert result2.id in crawl_ids

class TestCrawlModes:
    """Test different crawling modes."""
    
    def test_crawl_mode_enum(self):
        """Test CrawlMode enum values."""
        assert CrawlMode.BASIC.value == "basic"
        assert CrawlMode.ENHANCED.value == "enhanced"
        assert CrawlMode.FULL_SITE.value == "full_site"
        assert CrawlMode.DEEP.value == "deep"
        assert CrawlMode.STEALTH.value == "stealth"
        assert CrawlMode.ENTERPRISE.value == "enterprise"
    
    def test_crawl_mode_creation(self):
        """Test creating requests with different modes."""
        for mode in CrawlMode:
            request = CrawlRequest(url="https://example.com", mode=mode)
            assert request.mode == mode

class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_crawl_workflow(self, temp_dir):
        """Test a complete crawl workflow."""
        async with UniversalCrawler({"storage_dir": temp_dir}) as crawler:
            # Create a crawl request
            request = CrawlRequest(
                url="https://httpbin.org",
                mode=CrawlMode.BASIC,
                max_depth=1,
                max_pages=1,
                delay=0.1  # Fast for testing
            )
            
            # Start the crawl
            result = await crawler.start_crawl(request)
            assert result.status == "running"
            
            # Wait for completion (with timeout)
            max_wait = 30  # seconds
            wait_time = 0
            while result.status == "running" and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
                result = await crawler.get_crawl_status(result.id)
                if not result:
                    break
            
            # Check final status
            assert result.status in ["completed", "failed", "stopped"]
            
            # Get results
            if result.status == "completed":
                results = await crawler.get_crawl_results(result.id)
                assert results is not None
                assert "summary" in results
                assert "files" in results
                assert "statistics" in results

class TestErrorHandling:
    """Test error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_url_handling(self, temp_dir):
        """Test handling of invalid URLs."""
        async with UniversalCrawler({"storage_dir": temp_dir}) as crawler:
            request = CrawlRequest(
                url="https://invalid-domain-that-does-not-exist-12345.com",
                mode=CrawlMode.BASIC,
                max_depth=1,
                max_pages=1
            )
            
            result = await crawler.start_crawl(request)
            
            # Wait for completion
            max_wait = 10
            wait_time = 0
            while result.status == "running" and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
                result = await crawler.get_crawl_status(result.id)
                if not result:
                    break
            
            # Should fail gracefully
            assert result.status in ["failed", "stopped"]
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, temp_dir):
        """Test handling of network timeouts."""
        async with UniversalCrawler({"storage_dir": temp_dir}) as crawler:
            request = CrawlRequest(
                url="https://httpbin.org/delay/10",  # 10 second delay
                mode=CrawlMode.BASIC,
                max_depth=1,
                max_pages=1,
                timeout=5  # 5 second timeout
            )
            
            result = await crawler.start_crawl(request)
            
            # Wait for completion
            max_wait = 15
            wait_time = 0
            while result.status == "running" and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
                result = await crawler.get_crawl_status(result.id)
                if not result:
                    break
            
            # Should handle timeout gracefully
            assert result.status in ["failed", "stopped", "completed"]

class TestPerformance:
    """Performance tests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_crawls(self, temp_dir):
        """Test handling multiple concurrent crawls."""
        async with UniversalCrawler({"storage_dir": temp_dir}) as crawler:
            # Start multiple crawls concurrently
            requests = [
                CrawlRequest(
                    url="https://httpbin.org",
                    mode=CrawlMode.BASIC,
                    max_depth=1,
                    max_pages=1,
                    delay=0.1
                ) for _ in range(3)
            ]
            
            # Start all crawls
            results = []
            for request in requests:
                result = await crawler.start_crawl(request)
                results.append(result)
            
            # Wait for all to complete
            max_wait = 30
            wait_time = 0
            while any(r.status == "running" for r in results) and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
                for i, result in enumerate(results):
                    updated = await crawler.get_crawl_status(result.id)
                    if updated:
                        results[i] = updated
            
            # Check that all completed
            completed = sum(1 for r in results if r.status == "completed")
            assert completed >= 1  # At least one should complete

def run_tests():
    """Run all tests."""
    import sys
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Run pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])

if __name__ == "__main__":
    run_tests() 