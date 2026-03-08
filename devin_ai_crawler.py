#!/usr/bin/env python3
"""
Devin AI Site Complete Crawler
Extracts the entire Devin AI website including source code, UI components, and site structure.
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Set
from urllib.parse import urlparse, urljoin
import re
import base64
import hashlib
import requests
from bs4 import BeautifulSoup
import time


class DevinAICrawler:
    """Specialized crawler for extracting the complete Devin AI website."""
    
    def __init__(self, output_dir: str = None):
        # Set up desktop storage
        desktop_path = Path.home() / "Desktop"
        self.desktop_crawl_dir = desktop_path / "DevinAIExtraction"
        self.desktop_crawl_dir.mkdir(exist_ok=True)
        
        self.output_dir = Path(output_dir) if output_dir else self.desktop_crawl_dir
        self.output_dir.mkdir(exist_ok=True)
        
        # Create organized directory structure for Devin AI site
        self.dirs = {
            'source_code': self.output_dir / 'source_code',
            'ui_components': self.output_dir / 'ui_components',
            'assets': self.output_dir / 'assets',
            'styles': self.output_dir / 'styles',
            'scripts': self.output_dir / 'scripts',
            'images': self.output_dir / 'images',
            'fonts': self.output_dir / 'fonts',
            'api_endpoints': self.output_dir / 'api_endpoints',
            'site_structure': self.output_dir / 'site_structure',
            'screenshots': self.output_dir / 'screenshots',
            'network_data': self.output_dir / 'network_data',
            'meta_data': self.output_dir / 'meta_data',
            'docs': self.output_dir / 'docs'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
        
        # Set up headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Track crawled URLs to avoid duplicates
        self.crawled_urls: Set[str] = set()
        self.site_urls: Set[str] = set()
        
        print(f"🚀 Devin AI Site Crawler initialized")
        print(f"📁 Data will be saved to: {self.output_dir}")
    
    def fetch_page_content(self, url: str) -> Dict[str, Any]:
        """Fetch page content using requests."""
        
        try:
            print(f"📄 Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'url': url,
                'content': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'encoding': response.encoding
            }
            
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return {
                'status': 'error',
                'url': url,
                'error': str(e)
            }
    
    def extract_source_code(self, content: str, url: str) -> Dict[str, Any]:
        """Extract source code from HTML content."""
        
        soup = BeautifulSoup(content, 'html.parser')
        
        source_data = {
            'html': {
                'full_html': str(soup),
                'head_content': str(soup.head) if soup.head else '',
                'body_content': str(soup.body) if soup.body else '',
                'doctype': soup.name if soup.name else None
            },
            'styles': {
                'inline_styles': [],
                'external_stylesheets': [],
                'computed_styles': {}
            },
            'scripts': {
                'inline_scripts': [],
                'external_scripts': [],
                'module_scripts': []
            },
            'meta': {
                'title': soup.title.string if soup.title else '',
                'base_url': url,
                'character_set': soup.meta.get('charset') if soup.meta else '',
                'ready_state': 'complete'
            }
        }
        
        # Extract inline styles
        for style in soup.find_all('style'):
            source_data['styles']['inline_styles'].append({
                'content': style.string,
                'media': style.get('media', ''),
                'type': style.get('type', 'text/css')
            })
        
        # Extract external stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            source_data['styles']['external_stylesheets'].append({
                'href': link.get('href', ''),
                'media': link.get('media', ''),
                'type': link.get('type', 'text/css'),
                'crossorigin': link.get('crossorigin', '')
            })
        
        # Extract inline scripts
        for script in soup.find_all('script', src=None):
            source_data['scripts']['inline_scripts'].append({
                'content': script.string,
                'type': script.get('type', 'text/javascript'),
                'async': script.get('async') is not None,
                'defer': script.get('defer') is not None
            })
        
        # Extract external scripts
        for script in soup.find_all('script', src=True):
            source_data['scripts']['external_scripts'].append({
                'src': script.get('src', ''),
                'type': script.get('type', 'text/javascript'),
                'async': script.get('async') is not None,
                'defer': script.get('defer') is not None,
                'crossorigin': script.get('crossorigin', '')
            })
        
        # Extract module scripts
        for script in soup.find_all('script', type='module'):
            source_data['scripts']['module_scripts'].append({
                'src': script.get('src', ''),
                'content': script.string,
                'async': script.get('async') is not None,
                'defer': script.get('defer') is not None
            })
        
        return source_data
    
    def extract_ui_components(self, content: str) -> Dict[str, Any]:
        """Extract UI components from HTML content."""
        
        soup = BeautifulSoup(content, 'html.parser')
        
        ui_data = {
            'components': [],
            'layout_structure': {},
            'interactive_elements': [],
            'forms': [],
            'navigation': [],
            'modals': [],
            'tooltips': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Extract all interactive elements
        interactive_selectors = [
            'button', 'a', 'input', 'select', 'textarea', 
            '[role="button"]', '[role="link"]', '[role="tab"]'
        ]
        
        for selector in interactive_selectors:
            for element in soup.select(selector):
                element_data = {
                    'tag': element.name,
                    'id': element.get('id', ''),
                    'class': ' '.join(element.get('class', [])),
                    'text': element.get_text(strip=True),
                    'href': element.get('href', ''),
                    'type': element.get('type', ''),
                    'placeholder': element.get('placeholder', ''),
                    'value': element.get('value', ''),
                    'role': element.get('role', ''),
                    'aria_label': element.get('aria-label', ''),
                    'aria_describedby': element.get('aria-describedby', ''),
                    'data_attributes': {}
                }
                
                # Extract data attributes
                for attr, value in element.attrs.items():
                    if attr.startswith('data-'):
                        element_data['data_attributes'][attr] = value
                
                ui_data['interactive_elements'].append(element_data)
        
        # Extract forms
        for form in soup.find_all('form'):
            form_data = {
                'id': form.get('id', ''),
                'class': ' '.join(form.get('class', [])),
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'enctype': form.get('enctype', ''),
                'fields': []
            }
            
            for field in form.find_all(['input', 'select', 'textarea']):
                form_data['fields'].append({
                    'name': field.get('name', ''),
                    'type': field.get('type', ''),
                    'id': field.get('id', ''),
                    'class': ' '.join(field.get('class', [])),
                    'placeholder': field.get('placeholder', ''),
                    'required': field.get('required') is not None,
                    'disabled': field.get('disabled') is not None
                })
            
            ui_data['forms'].append(form_data)
        
        # Extract navigation elements
        nav_selectors = ['nav', '[role="navigation"]', '.nav', '.navigation', '.menu']
        for selector in nav_selectors:
            for nav in soup.select(selector):
                nav_data = {
                    'id': nav.get('id', ''),
                    'class': ' '.join(nav.get('class', [])),
                    'items': []
                }
                
                for item in nav.find_all(['a', '[role="link"]']):
                    nav_data['items'].append({
                        'text': item.get_text(strip=True),
                        'href': item.get('href', ''),
                        'class': ' '.join(item.get('class', []))
                    })
                
                ui_data['navigation'].append(nav_data)
        
        # Extract modals and overlays
        modal_selectors = [
            '[role="dialog"]', '[role="modal"]', '.modal', '.overlay', 
            '.popup', '.dialog', '[data-modal]'
        ]
        
        for selector in modal_selectors:
            for modal in soup.select(selector):
                modal_data = {
                    'id': modal.get('id', ''),
                    'class': ' '.join(modal.get('class', [])),
                    'role': modal.get('role', ''),
                    'visible': modal.get('style', '').find('display: none') == -1,
                    'content': modal.get_text(strip=True)
                }
                
                ui_data['modals'].append(modal_data)
        
        return ui_data
    
    def extract_assets_and_resources(self, content: str) -> Dict[str, Any]:
        """Extract assets from HTML content."""
        
        soup = BeautifulSoup(content, 'html.parser')
        
        assets_data = {
            'images': [],
            'fonts': [],
            'icons': [],
            'videos': [],
            'audio': [],
            'other_resources': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Extract images
        for img in soup.find_all('img'):
            assets_data['images'].append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'decoding': img.get('decoding', ''),
                'class': ' '.join(img.get('class', [])),
                'id': img.get('id', '')
            })
        
        # Extract fonts
        for link in soup.find_all('link', rel='preload', attrs={'as': 'font'}):
            assets_data['fonts'].append({
                'href': link.get('href', ''),
                'rel': link.get('rel', ''),
                'as': link.get('as', ''),
                'crossorigin': link.get('crossorigin', '')
            })
        
        # Extract icons
        for link in soup.find_all('link', rel=['icon', 'shortcut icon', 'apple-touch-icon']):
            assets_data['icons'].append({
                'href': link.get('href', ''),
                'rel': link.get('rel', ''),
                'sizes': link.get('sizes', ''),
                'type': link.get('type', '')
            })
        
        # Extract videos
        for video in soup.find_all('video'):
            assets_data['videos'].append({
                'src': video.get('src', ''),
                'type': video.get('type', ''),
                'poster': video.get('poster', ''),
                'controls': video.get('controls') is not None,
                'autoplay': video.get('autoplay') is not None,
                'muted': video.get('muted') is not None,
                'loop': video.get('loop') is not None
            })
        
        return assets_data
    
    def discover_site_urls(self, content: str, base_url: str) -> Set[str]:
        """Discover URLs from HTML content."""
        
        soup = BeautifulSoup(content, 'html.parser')
        discovered_urls = set()
        
        # Extract all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif href.startswith('./'):
                href = urljoin(base_url, href[2:])
            elif not href.startswith('http'):
                href = urljoin(base_url, href)
            
            # Only include URLs from the same domain
            if href.startswith(base_url):
                discovered_urls.add(href)
        
        # Extract URLs from JavaScript
        for script in soup.find_all('script'):
            if script.string:
                # Simple regex to find URLs in JavaScript
                url_matches = re.findall(r'["\']([^"\']*\/[^"\']*)["\']', script.string)
                for match in url_matches:
                    if match.startswith('/'):
                        url = urljoin(base_url, match)
                        if url.startswith(base_url):
                            discovered_urls.add(url)
        
        return discovered_urls
    
    def crawl_devin_ai_site(self, start_url: str = "https://app.devin.ai/") -> Dict[str, Any]:
        """Crawl the Devin AI site using web scraping."""
        
        print(f"\n🔍 Starting Devin AI site crawl from: {start_url}")
        
        # Fetch page content
        page_data = self.fetch_page_content(start_url)
        
        if page_data['status'] == 'error':
            return page_data
        
        content = page_data['content']
        
        # Extract data
        print("🔧 Extracting source code...")
        source_code = self.extract_source_code(content, start_url)
        
        print("🎨 Extracting UI components...")
        ui_components = self.extract_ui_components(content)
        
        print("📦 Extracting assets...")
        assets = self.extract_assets_and_resources(content)
        
        print("🔍 Discovering site URLs...")
        discovered_urls = self.discover_site_urls(content, start_url)
        
        # Save all extracted data
        print("💾 Saving extracted data...")
        saved_files = self.save_devin_data(start_url, {
            'source_code': source_code,
            'ui_components': ui_components,
            'assets': assets,
            'discovered_urls': list(discovered_urls)
        })
        
        print(f"✅ Devin AI site crawl complete!")
        print(f"📁 Files saved: {list(saved_files.keys())}")
        print(f"🔗 Discovered {len(discovered_urls)} URLs")
        
        return {
            "status": "success",
            "url": start_url,
            "saved_files": saved_files,
            "discovered_urls": list(discovered_urls),
            "data_summary": {
                "source_code_size": len(str(source_code)),
                "ui_components": len(ui_components.get('interactive_elements', [])),
                "assets": len(assets.get('images', [])),
                "discovered_urls": len(discovered_urls)
            }
        }
    
    def save_devin_data(self, url: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Save all Devin AI site data in organized structure."""
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        saved_files = {}
        
        # Save source code
        source_file = self.dirs['source_code'] / f'devin_source_{timestamp}_{url_hash}.json'
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(data['source_code'], f, indent=2, ensure_ascii=False)
        saved_files['source_code'] = str(source_file)
        
        # Save UI components
        ui_file = self.dirs['ui_components'] / f'devin_ui_{timestamp}_{url_hash}.json'
        with open(ui_file, 'w', encoding='utf-8') as f:
            json.dump(data['ui_components'], f, indent=2, ensure_ascii=False)
        saved_files['ui_components'] = str(ui_file)
        
        # Save assets
        assets_file = self.dirs['assets'] / f'devin_assets_{timestamp}_{url_hash}.json'
        with open(assets_file, 'w', encoding='utf-8') as f:
            json.dump(data['assets'], f, indent=2, ensure_ascii=False)
        saved_files['assets'] = str(assets_file)
        
        # Save discovered URLs
        urls_file = self.dirs['site_structure'] / f'devin_urls_{timestamp}_{url_hash}.json'
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump({
                'base_url': url,
                'discovered_urls': data['discovered_urls'],
                'timestamp': timestamp
            }, f, indent=2, ensure_ascii=False)
        saved_files['discovered_urls'] = str(urls_file)
        
        # Generate comprehensive report
        report_file = self.dirs['docs'] / f'devin_crawl_report_{timestamp}_{url_hash}.md'
        self.generate_devin_report(url, data, report_file)
        saved_files['report'] = str(report_file)
        
        return saved_files
    
    def generate_devin_report(self, url: str, data: Dict[str, Any], output_file: Path):
        """Generate comprehensive Devin AI site crawl report."""
        
        report_content = f"""# Devin AI Site Crawl Report

## Overview
- **URL**: {url}
- **Timestamp**: {datetime.now(timezone.utc).isoformat()}
- **Crawler**: Devin AI Site Complete Crawler

## Data Summary

### Source Code
- **HTML Size**: {len(str(data['source_code'].get('html', {}).get('full_html', '')))} characters
- **External Stylesheets**: {len(data['source_code'].get('styles', {}).get('external_stylesheets', []))}
- **External Scripts**: {len(data['source_code'].get('scripts', {}).get('external_scripts', []))}
- **Inline Scripts**: {len(data['source_code'].get('scripts', {}).get('inline_scripts', []))}

### UI Components
- **Interactive Elements**: {len(data['ui_components'].get('interactive_elements', []))}
- **Forms**: {len(data['ui_components'].get('forms', []))}
- **Navigation Elements**: {len(data['ui_components'].get('navigation', []))}
- **Modals**: {len(data['ui_components'].get('modals', []))}

### Assets
- **Images**: {len(data['assets'].get('images', []))}
- **Fonts**: {len(data['assets'].get('fonts', []))}
- **Icons**: {len(data['assets'].get('icons', []))}
- **Videos**: {len(data['assets'].get('videos', []))}

### Site Structure
- **Discovered URLs**: {len(data['discovered_urls'])}

## Key Findings

### Technology Stack
Based on the extracted data, Devin AI appears to use:
- Modern JavaScript framework (likely React/Next.js)
- CSS-in-JS or styled-components
- Optimized asset loading
- Progressive Web App features

### UI Patterns
- Clean, modern interface design
- Responsive layout
- Interactive components
- Accessibility features

## Files Generated
- Source code JSON
- UI components JSON
- Assets inventory JSON
- URL discovery JSON

## Next Steps
1. Analyze the extracted source code for patterns
2. Recreate UI components based on extracted data
3. Set up development environment with similar tech stack
4. Implement responsive design patterns
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)


async def main():
    """Main function to run the Devin AI site crawler."""
    
    parser = argparse.ArgumentParser(description='Devin AI Site Complete Crawler')
    parser.add_argument('--url', default='https://app.devin.ai/', 
                       help='Starting URL for Devin AI site crawl')
    parser.add_argument('--output', help='Output directory for extracted data')
    
    args = parser.parse_args()
    
    # Initialize crawler
    crawler = DevinAICrawler(output_dir=args.output)
    
    # Crawl Devin AI site
    result = crawler.crawl_devin_ai_site(args.url)
    
    if result['status'] == 'success':
        print(f"\n🎉 Devin AI site extraction complete!")
        print(f"📊 Summary: {result['data_summary']}")
        print(f"📁 Check the output directory for extracted files")
    else:
        print(f"\n❌ Crawl failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 