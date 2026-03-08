"""
Universal Crawler Package
========================

A comprehensive web crawling system designed to handle any website.
"""

from .crawler import UniversalCrawler, CrawlRequest, CrawlMode, CrawlResult
from .config import Config, get_config

__version__ = "1.0.0"
__author__ = "Universal Crawler Team"

__all__ = [
    "UniversalCrawler",
    "CrawlRequest", 
    "CrawlMode",
    "CrawlResult",
    "Config",
    "get_config"
]
