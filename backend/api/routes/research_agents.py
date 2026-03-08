#!/usr/bin/env python3
"""
Research Agents API Routes
=========================

FastAPI routes for research agents that can:
- Process natural language prompts
- Search the web for relevant information
- Analyze and extract relevant content
- Generate specialized AI prompts based on research
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import asyncio
import json
import re
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

from core.security import verify_token
from microservices_orchestrator import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency for authentication
async def get_current_user(token: str = Depends(verify_token)):
    return token

class WebSearchAgent:
    """Agent for searching the web and finding relevant websites."""
    
    def __init__(self):
        self.search_engines = {
            'google': 'https://www.google.com/search',
            'bing': 'https://www.bing.com/search',
            'duckduckgo': 'https://duckduckgo.com/'
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for relevant websites based on natural language query."""
        try:
            # Use DuckDuckGo for search (no API key required)
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return await self._parse_search_results(html, max_results)
                else:
                    logger.error(f"Search failed with status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []
    
    async def _parse_search_results(self, html: str, max_results: int) -> List[Dict[str, Any]]:
        """Parse search results from HTML."""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find search result links
            result_links = soup.find_all('a', class_='result__a')[:max_results]
            
            for link in result_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if href and title:
                    # Extract URL from DuckDuckGo redirect
                    if 'uddg=' in href:
                        url = href.split('uddg=')[1].split('&')[0]
                    else:
                        url = href
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'snippet': self._extract_snippet(link),
                        'relevance_score': self._calculate_relevance(title, href)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            return []
    
    def _extract_snippet(self, link_element) -> str:
        """Extract snippet text from search result."""
        try:
            snippet_element = link_element.find_next_sibling('a', class_='result__snippet')
            if snippet_element:
                return snippet_element.get_text(strip=True)
            return ""
        except:
            return ""
    
    def _calculate_relevance(self, title: str, url: str) -> float:
        """Calculate relevance score for search result."""
        score = 0.0
        
        # Domain relevance
        domain = urlparse(url).netloc.lower()
        if any(keyword in domain for keyword in ['wordpress', 'framer', 'webflow', 'shopify', 'woocommerce']):
            score += 0.3
        
        # Title relevance
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in ['template', 'theme', 'design', 'website', 'site']):
            score += 0.2
        
        return min(score, 1.0)

class ContentAnalyzerAgent:
    """Agent for analyzing website content and determining platform type."""
    
    def __init__(self):
        self.platform_indicators = {
            'wordpress': [
                'wp-content', 'wp-includes', 'wp-admin',
                'wordpress', 'wp-json', 'wp_head', 'wp_footer'
            ],
            'framer': [
                'framer', 'framer.app', 'framer.cloud',
                'framer-motion', 'framer-js'
            ],
            'webflow': [
                'webflow', 'webflow.io', 'webflow.com',
                'w-', 'w-form', 'w-nav'
            ],
            'shopify': [
                'shopify', 'myshopify.com',
                'shopify-section', 'shopify-product'
            ],
            'woocommerce': [
                'woocommerce', 'wc-', 'woocommerce-',
                'add_to_cart', 'product_cat'
            ],
            'square': [
                'square', 'squareup.com',
                'square-commerce', 'square-payment'
            ],
            'figma': [
                'figma', 'figma.com',
                'figma-embed', 'figma-design'
            ]
        }
    
    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze website to determine platform and extract relevant information."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._analyze_content(html, url)
                    else:
                        return {
                            'platform': 'unknown',
                            'confidence': 0.0,
                            'features': [],
                            'error': f'HTTP {response.status}'
                        }
                        
        except Exception as e:
            logger.error(f"Error analyzing website {url}: {e}")
            return {
                'platform': 'unknown',
                'confidence': 0.0,
                'features': [],
                'error': str(e)
            }
    
    async def _analyze_content(self, html: str, url: str) -> Dict[str, Any]:
        """Analyze HTML content to determine platform and features."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for platform indicators
        platform_scores = {}
        for platform, indicators in self.platform_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator.lower() in html.lower():
                    score += 1
            platform_scores[platform] = score
        
        # Determine most likely platform
        best_platform = max(platform_scores.items(), key=lambda x: x[1])
        platform = best_platform[0] if best_platform[1] > 0 else 'dynamic'
        confidence = min(best_platform[1] / len(self.platform_indicators[platform]), 1.0) if platform != 'dynamic' else 0.5
        
        # Extract features
        features = await self._extract_features(soup, platform)
        
        return {
            'platform': platform,
            'confidence': confidence,
            'features': features,
            'url': url,
            'title': soup.title.string if soup.title else '',
            'meta_description': self._extract_meta_description(soup)
        }
    
    async def _extract_features(self, soup: BeautifulSoup, platform: str) -> List[str]:
        """Extract platform-specific features from HTML."""
        features = []
        
        if platform == 'wordpress':
            if soup.find('meta', {'name': 'generator', 'content': re.compile(r'WordPress', re.I)}):
                features.append('WordPress CMS')
            if soup.find('link', {'href': re.compile(r'wp-content/themes', re.I)}):
                features.append('Custom Theme')
            if soup.find('script', {'src': re.compile(r'wp-content/plugins', re.I)}):
                features.append('WordPress Plugins')
        
        elif platform == 'framer':
            if soup.find('script', {'src': re.compile(r'framer', re.I)}):
                features.append('Framer Components')
            if soup.find('div', {'class': re.compile(r'framer', re.I)}):
                features.append('Framer Layout')
        
        elif platform == 'webflow':
            if soup.find('div', {'class': re.compile(r'w-', re.I)}):
                features.append('Webflow Elements')
            if soup.find('script', {'src': re.compile(r'webflow', re.I)}):
                features.append('Webflow CMS')
        
        elif platform == 'shopify':
            if soup.find('meta', {'name': 'shopify-checkout-api-token'}):
                features.append('Shopify Store')
            if soup.find('script', {'src': re.compile(r'shopify', re.I)}):
                features.append('Shopify Theme')
        
        elif platform == 'woocommerce':
            if soup.find('meta', {'name': 'generator', 'content': re.compile(r'WooCommerce', re.I)}):
                features.append('WooCommerce Store')
            if soup.find('div', {'class': re.compile(r'woocommerce', re.I)}):
                features.append('WooCommerce Elements')
        
        return features
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from HTML."""
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        return ""

class ResearchOrchestrator:
    """Orchestrates the research process from natural language to specialized prompts."""
    
    def __init__(self):
        self.web_search_agent = WebSearchAgent()
        self.content_analyzer = ContentAnalyzerAgent()
    
    async def process_natural_language_request(self, prompt: str, agent_type: str = 'auto', prompt_type: str = 'cursor') -> Dict[str, Any]:
        """Process natural language request and generate specialized prompt."""
        try:
            # Step 1: Analyze the natural language prompt
            analysis = await self._analyze_prompt(prompt)
            
            # Step 2: Search for relevant websites
            search_results = await self.web_search_agent.search_web(analysis['search_query'])
            
            # Step 3: Analyze the most relevant website
            if search_results:
                best_result = max(search_results, key=lambda x: x['relevance_score'])
                website_analysis = await self.content_analyzer.analyze_website(best_result['url'])
                
                # Step 4: Generate specialized prompt
                specialized_prompt = await self._generate_specialized_prompt(
                    prompt, analysis, website_analysis, agent_type, prompt_type
                )
                
                return {
                    'success': True,
                    'original_prompt': prompt,
                    'analysis': analysis,
                    'search_results': search_results,
                    'website_analysis': website_analysis,
                    'specialized_prompt': specialized_prompt,
                    'recommended_agent': website_analysis['platform'],
                    'recommended_prompt_type': prompt_type,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback: generate prompt without specific website
                specialized_prompt = await self._generate_generic_prompt(prompt, agent_type, prompt_type)
                
                return {
                    'success': True,
                    'original_prompt': prompt,
                    'analysis': analysis,
                    'search_results': [],
                    'website_analysis': None,
                    'specialized_prompt': specialized_prompt,
                    'recommended_agent': agent_type,
                    'recommended_prompt_type': prompt_type,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing natural language request: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze natural language prompt to extract intent and requirements."""
        prompt_lower = prompt.lower()
        
        # Extract platform keywords
        platforms = {
            'wordpress': ['wordpress', 'wp', 'blog', 'cms'],
            'framer': ['framer', 'prototype', 'design tool'],
            'webflow': ['webflow', 'no-code', 'visual editor'],
            'shopify': ['shopify', 'ecommerce', 'online store'],
            'woocommerce': ['woocommerce', 'woo', 'wordpress store'],
            'square': ['square', 'square commerce', 'payment'],
            'figma': ['figma', 'design', 'ui/ux', 'prototype'],
            'dynamic': ['dynamic', 'spa', 'react', 'vue', 'angular']
        }
        
        detected_platform = 'dynamic'
        for platform, keywords in platforms.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_platform = platform
                break
        
        # Extract intent
        intent = 'clone'
        if any(word in prompt_lower for word in ['create', 'build', 'make']):
            intent = 'create'
        elif any(word in prompt_lower for word in ['improve', 'enhance', 'update']):
            intent = 'improve'
        
        # Generate search query
        search_query = prompt.replace('create', '').replace('build', '').replace('make', '').strip()
        
        return {
            'detected_platform': detected_platform,
            'intent': intent,
            'search_query': search_query,
            'keywords': self._extract_keywords(prompt)
        }
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract relevant keywords from prompt."""
        # Simple keyword extraction - could be enhanced with NLP
        words = prompt.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]  # Limit to 10 keywords
    
    async def _generate_specialized_prompt(self, original_prompt: str, analysis: Dict, website_analysis: Dict, agent_type: str, prompt_type: str) -> str:
        """Generate specialized prompt based on analysis and website."""
        platform = website_analysis['platform']
        url = website_analysis['url']
        
        # Import the specialized agent manager
        from .specialized_agents import agent_manager
        
        try:
            # Use the specialized agent to generate prompt
            prompt = await agent_manager.generate_prompt(url, platform, prompt_type)
            
            # Enhance with context from original prompt
            enhanced_prompt = f"""Based on the request: "{original_prompt}"

{prompt}

Additional Context:
- Original Request: {original_prompt}
- Detected Platform: {platform}
- Website Features: {', '.join(website_analysis['features'])}
- Intent: {analysis['intent']}

Please ensure the generated solution addresses the specific requirements mentioned in the original request."""
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error generating specialized prompt: {e}")
            return await self._generate_generic_prompt(original_prompt, agent_type, prompt_type)
    
    async def _generate_generic_prompt(self, prompt: str, agent_type: str, prompt_type: str) -> str:
        """Generate generic prompt when no specific website is found."""
        if prompt_type == 'cursor':
            return f"""Create a website based on this description: {prompt}

Requirements:
- Use Next.js 14 with TypeScript
- Implement Tailwind CSS for styling
- Use Framer Motion for animations
- Include all interactive elements
- Implement responsive design
- Include all functionality and features
- Use modern React patterns and hooks
- Ensure accessibility compliance
- Optimize for performance

Additional Context:
- Agent Type: {agent_type}
- Original Request: {prompt}

Please create a comprehensive solution that addresses all aspects of the request."""
        
        elif prompt_type == 'bolt':
            return f"""Create a Bolt AI prompt for: {prompt}

Development Requirements:
- Full-stack web application
- Modern tech stack implementation
- Database design and structure
- API endpoints and functionality
- User authentication system
- Responsive design implementation
- Performance optimization
- Security best practices
- Deployment configuration
- Complete documentation

Additional Context:
- Agent Type: {agent_type}
- Original Request: {prompt}"""
        
        else:
            return f"Generate {prompt_type} prompt for: {prompt}"

# Initialize research orchestrator
research_orchestrator = ResearchOrchestrator()

@router.post("/process-natural-language")
async def process_natural_language_request(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process natural language request and generate specialized prompt."""
    try:
        prompt = request_data.get("prompt")
        agent_type = request_data.get("agent_type", "auto")
        prompt_type = request_data.get("prompt_type", "cursor")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Process the natural language request
        result = await research_orchestrator.process_natural_language_request(
            prompt, agent_type, prompt_type
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing natural language request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search-web")
async def search_web(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Search the web for relevant websites."""
    try:
        query = request_data.get("query")
        max_results = request_data.get("max_results", 5)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        async with WebSearchAgent() as search_agent:
            results = await search_agent.search_web(query, max_results)
        
        return JSONResponse(content={
            "success": True,
            "query": query,
            "results": results,
            "total_count": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error searching web: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/analyze-website")
async def analyze_website(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze a website to determine platform and features."""
    try:
        url = request_data.get("url")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Analyze website
        analyzer = ContentAnalyzerAgent()
        analysis = await analyzer.analyze_website(url)
        
        return JSONResponse(content={
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing website: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/capabilities")
async def get_research_capabilities():
    """Get research agent capabilities."""
    capabilities = {
        "natural_language_processing": {
            "description": "Process natural language requests without URLs",
            "features": [
                "Intent detection",
                "Platform identification",
                "Keyword extraction",
                "Context analysis"
            ]
        },
        "web_search": {
            "description": "Search the web for relevant websites",
            "features": [
                "Multi-engine search",
                "Relevance scoring",
                "Result filtering",
                "Content extraction"
            ]
        },
        "website_analysis": {
            "description": "Analyze websites to determine platform and features",
            "features": [
                "Platform detection",
                "Feature extraction",
                "Content analysis",
                "Technology identification"
            ]
        },
        "prompt_generation": {
            "description": "Generate specialized AI prompts based on research",
            "features": [
                "Context-aware prompts",
                "Platform-specific requirements",
                "Multiple AI platform support",
                "Customization options"
            ]
        }
    }
    
    return JSONResponse(content={
        "capabilities": capabilities,
        "timestamp": datetime.now().isoformat()
    }) 