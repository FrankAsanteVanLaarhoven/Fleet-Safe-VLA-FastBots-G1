#!/usr/bin/env python3
"""
Company Intelligence Engine - Real-time Research & Analysis
Comprehensive background checks with live API integrations
"""
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompanyProfile:
    """Comprehensive company profile with all research data"""
    name: str
    entity_type: str
    industry: str
    location: str
    
    # Company Information
    founded_year: Optional[int] = None
    company_size: Optional[str] = None
    revenue: Optional[str] = None
    funding_stage: Optional[str] = None
    total_funding: Optional[str] = None
    
    # Market Intelligence
    competitors: List[str] = None
    market_position: Optional[str] = None
    recent_news: List[Dict] = None
    stock_price: Optional[float] = None
    
    # Leadership
    executives: List[Dict] = None
    ceo: Optional[Dict] = None
    board_members: List[Dict] = None
    
    # Culture & Reviews
    glassdoor_rating: Optional[float] = None
    employee_reviews: List[Dict] = None
    company_values: List[str] = None
    
    # Social Media
    linkedin_followers: Optional[int] = None
    twitter_followers: Optional[int] = None
    social_sentiment: Optional[str] = None
    
    # Contact Information
    website: Optional[str] = None
    email_domains: List[str] = None
    phone_numbers: List[str] = None
    office_locations: List[Dict] = None
    
    # Technical Intelligence
    tech_stack: List[str] = None
    recent_hiring: List[Dict] = None
    job_openings: List[Dict] = None
    
    # Analysis Results
    risk_factors: List[str] = None
    growth_indicators: List[str] = None
    interview_insights: List[str] = None
    
    def __post_init__(self):
        if self.competitors is None:
            self.competitors = []
        if self.recent_news is None:
            self.recent_news = []
        if self.executives is None:
            self.executives = []
        if self.board_members is None:
            self.board_members = []
        if self.employee_reviews is None:
            self.employee_reviews = []
        if self.company_values is None:
            self.company_values = []
        if self.email_domains is None:
            self.email_domains = []
        if self.phone_numbers is None:
            self.phone_numbers = []
        if self.office_locations is None:
            self.office_locations = []
        if self.tech_stack is None:
            self.tech_stack = []
        if self.recent_hiring is None:
            self.recent_hiring = []
        if self.job_openings is None:
            self.job_openings = []
        if self.risk_factors is None:
            self.risk_factors = []
        if self.growth_indicators is None:
            self.growth_indicators = []
        if self.interview_insights is None:
            self.interview_insights = []

class CompanyIntelligenceEngine:
    """Real-time company intelligence engine with comprehensive research capabilities"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.session = None
        self.cache_dir = Path("data/company_database")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # API endpoints and configurations
        self.apis = {
            "linkedin": {
                "base_url": "https://api.linkedin.com/v2",
                "headers": {"Authorization": f"Bearer {self.api_keys.get('linkedin')}"}
            },
            "crunchbase": {
                "base_url": "https://api.crunchbase.com/v3.1",
                "headers": {"X-cb-user-key": self.api_keys.get('crunchbase')}
            },
            "glassdoor": {
                "base_url": "https://api.glassdoor.com/api/api.htm",
                "params": {
                    "v": "1",
                    "format": "json",
                    "t.p": self.api_keys.get('glassdoor_partner_id'),
                    "t.k": self.api_keys.get('glassdoor_key')
                }
            },
            "newsapi": {
                "base_url": "https://newsapi.org/v2",
                "headers": {"X-API-Key": self.api_keys.get('newsapi')}
            },
            "sec": {
                "base_url": "https://api.sec-api.io",
                "headers": {"Authorization": f"Bearer {self.api_keys.get('sec')}"}
            }
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def research_company(self, company_name: str, entity_type: str = "company") -> CompanyProfile:
        """Comprehensive company research with real-time data collection"""
        logger.info(f"🔍 Starting comprehensive research for: {company_name}")
        
        # Initialize company profile
        profile = CompanyProfile(
            name=company_name,
            entity_type=entity_type,
            industry="",
            location=""
        )
        
        # Run parallel research tasks
        tasks = [
            self._research_basic_info(company_name, profile),
            self._research_financial_data(company_name, profile),
            self._research_leadership(company_name, profile),
            self._research_market_position(company_name, profile),
            self._research_social_media(company_name, profile),
            self._research_news_sentiment(company_name, profile),
            self._research_employee_reviews(company_name, profile),
            self._research_technical_intelligence(company_name, profile),
            self._research_contact_information(company_name, profile)
        ]
        
        # Execute all research tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and update profile
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Research task failed: {result}")
            elif result:
                profile = self._merge_profile_data(profile, result)
        
        # Generate insights and analysis
        profile = await self._generate_intelligence_insights(profile)
        
        # Cache the results
        await self._cache_company_data(company_name, profile)
        
        logger.info(f"✅ Research completed for: {company_name}")
        return profile
    
    async def _research_basic_info(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research basic company information"""
        try:
            # Crunchbase basic info
            if self.api_keys.get('crunchbase'):
                crunchbase_data = await self._fetch_crunchbase_data(company_name)
                if crunchbase_data:
                    return {
                        'founded_year': crunchbase_data.get('founded_on_year'),
                        'company_size': crunchbase_data.get('num_employees_enum'),
                        'industry': crunchbase_data.get('category_groups', [{}])[0].get('name'),
                        'location': crunchbase_data.get('headquarters_location', {}).get('city'),
                        'website': crunchbase_data.get('homepage_url'),
                        'total_funding': crunchbase_data.get('total_funding_usd')
                    }
            
            # Fallback to web scraping if APIs unavailable
            return await self._scrape_basic_info(company_name)
            
        except Exception as e:
            logger.error(f"Basic info research failed: {e}")
            return {}
    
    async def _research_financial_data(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research financial information and funding"""
        try:
            financial_data = {}
            
            # SEC filings for public companies
            if self.api_keys.get('sec'):
                sec_data = await self._fetch_sec_data(company_name)
                if sec_data:
                    financial_data.update({
                        'revenue': sec_data.get('revenue'),
                        'stock_price': sec_data.get('stock_price'),
                        'market_cap': sec_data.get('market_cap')
                    })
            
            # Crunchbase funding data
            if self.api_keys.get('crunchbase'):
                funding_data = await self._fetch_crunchbase_funding(company_name)
                if funding_data:
                    financial_data.update({
                        'funding_stage': funding_data.get('funding_rounds', [{}])[-1].get('funding_type'),
                        'total_funding': funding_data.get('total_funding_usd'),
                        'investors': funding_data.get('investors', [])
                    })
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Financial research failed: {e}")
            return {}
    
    async def _research_leadership(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research company leadership and executives"""
        try:
            leadership_data = {}
            
            # LinkedIn company page
            if self.api_keys.get('linkedin'):
                linkedin_data = await self._fetch_linkedin_company(company_name)
                if linkedin_data:
                    leadership_data.update({
                        'executives': linkedin_data.get('employees', []),
                        'ceo': linkedin_data.get('ceo'),
                        'company_size': linkedin_data.get('company_size')
                    })
            
            # Crunchbase leadership data
            if self.api_keys.get('crunchbase'):
                crunchbase_leadership = await self._fetch_crunchbase_leadership(company_name)
                if crunchbase_leadership:
                    leadership_data.update({
                        'board_members': crunchbase_leadership.get('board_members', []),
                        'founders': crunchbase_leadership.get('founders', [])
                    })
            
            return leadership_data
            
        except Exception as e:
            logger.error(f"Leadership research failed: {e}")
            return {}
    
    async def _research_market_position(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research market position and competitors"""
        try:
            market_data = {}
            
            # Crunchbase competitors
            if self.api_keys.get('crunchbase'):
                competitors_data = await self._fetch_crunchbase_competitors(company_name)
                if competitors_data:
                    market_data.update({
                        'competitors': competitors_data.get('competitors', []),
                        'market_position': competitors_data.get('market_position')
                    })
            
            # News sentiment analysis
            if self.api_keys.get('newsapi'):
                news_data = await self._fetch_company_news(company_name)
                if news_data:
                    market_data.update({
                        'recent_news': news_data.get('articles', []),
                        'news_sentiment': self._analyze_news_sentiment(news_data.get('articles', []))
                    })
            
            return market_data
            
        except Exception as e:
            logger.error(f"Market research failed: {e}")
            return {}
    
    async def _research_social_media(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research social media presence and sentiment"""
        try:
            social_data = {}
            
            # LinkedIn company page
            if self.api_keys.get('linkedin'):
                linkedin_social = await self._fetch_linkedin_social(company_name)
                if linkedin_social:
                    social_data.update({
                        'linkedin_followers': linkedin_social.get('followers_count'),
                        'linkedin_posts': linkedin_social.get('recent_posts', [])
                    })
            
            # Twitter/X analysis (if API available)
            twitter_data = await self._fetch_twitter_data(company_name)
            if twitter_data:
                social_data.update({
                    'twitter_followers': twitter_data.get('followers_count'),
                    'twitter_sentiment': twitter_data.get('sentiment'),
                    'recent_tweets': twitter_data.get('recent_tweets', [])
                })
            
            return social_data
            
        except Exception as e:
            logger.error(f"Social media research failed: {e}")
            return {}
    
    async def _research_news_sentiment(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research recent news and sentiment analysis"""
        try:
            if not self.api_keys.get('newsapi'):
                return {}
            
            news_data = await self._fetch_company_news(company_name)
            if not news_data:
                return {}
            
            # Analyze sentiment of recent news
            sentiment_analysis = self._analyze_news_sentiment(news_data.get('articles', []))
            
            return {
                'recent_news': news_data.get('articles', []),
                'news_sentiment': sentiment_analysis,
                'key_topics': self._extract_key_topics(news_data.get('articles', []))
            }
            
        except Exception as e:
            logger.error(f"News research failed: {e}")
            return {}
    
    async def _research_employee_reviews(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research employee reviews and company culture"""
        try:
            if not self.api_keys.get('glassdoor'):
                return {}
            
            glassdoor_data = await self._fetch_glassdoor_data(company_name)
            if not glassdoor_data:
                return {}
            
            return {
                'glassdoor_rating': glassdoor_data.get('overallRating'),
                'employee_reviews': glassdoor_data.get('reviews', []),
                'company_values': glassdoor_data.get('values', []),
                'pros_cons': glassdoor_data.get('prosCons', {})
            }
            
        except Exception as e:
            logger.error(f"Employee reviews research failed: {e}")
            return {}
    
    async def _research_technical_intelligence(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research technical stack and hiring patterns"""
        try:
            tech_data = {}
            
            # Job postings analysis
            job_data = await self._fetch_job_postings(company_name)
            if job_data:
                tech_data.update({
                    'tech_stack': self._extract_tech_stack(job_data.get('jobs', [])),
                    'recent_hiring': job_data.get('recent_jobs', []),
                    'job_openings': job_data.get('active_jobs', [])
                })
            
            # GitHub organization analysis (if available)
            github_data = await self._fetch_github_data(company_name)
            if github_data:
                tech_data.update({
                    'github_repos': github_data.get('repositories', []),
                    'tech_trends': github_data.get('tech_trends', [])
                })
            
            return tech_data
            
        except Exception as e:
            logger.error(f"Technical intelligence research failed: {e}")
            return {}
    
    async def _research_contact_information(self, company_name: str, profile: CompanyProfile) -> Dict:
        """Research contact information and office locations"""
        try:
            contact_data = {}
            
            # Extract email domains from various sources
            email_domains = await self._extract_email_domains(company_name)
            if email_domains:
                contact_data['email_domains'] = email_domains
            
            # Office locations
            locations = await self._fetch_office_locations(company_name)
            if locations:
                contact_data['office_locations'] = locations
            
            # Phone numbers (if available)
            phone_numbers = await self._extract_phone_numbers(company_name)
            if phone_numbers:
                contact_data['phone_numbers'] = phone_numbers
            
            return contact_data
            
        except Exception as e:
            logger.error(f"Contact information research failed: {e}")
            return {}
    
    async def _generate_intelligence_insights(self, profile: CompanyProfile) -> CompanyProfile:
        """Generate intelligent insights and recommendations"""
        try:
            # Risk analysis
            profile.risk_factors = self._analyze_risk_factors(profile)
            
            # Growth indicators
            profile.growth_indicators = self._analyze_growth_indicators(profile)
            
            # Interview insights
            profile.interview_insights = self._generate_interview_insights(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return profile
    
    # API Integration Methods
    async def _fetch_crunchbase_data(self, company_name: str) -> Optional[Dict]:
        """Fetch company data from Crunchbase API"""
        try:
            url = f"{self.apis['crunchbase']['base_url']}/organizations/{company_name.lower().replace(' ', '-')}"
            headers = self.apis['crunchbase']['headers']
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Crunchbase API returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Crunchbase API error: {e}")
            return None
    
    async def _fetch_linkedin_company(self, company_name: str) -> Optional[Dict]:
        """Fetch company data from LinkedIn API"""
        try:
            # Note: LinkedIn API requires proper authentication
            # This is a simplified example
            url = f"{self.apis['linkedin']['base_url']}/organizations"
            headers = self.apis['linkedin']['headers']
            params = {"q": "vanityName", "vanityName": company_name.lower().replace(' ', '')}
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"LinkedIn API returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"LinkedIn API error: {e}")
            return None
    
    async def _fetch_company_news(self, company_name: str) -> Optional[Dict]:
        """Fetch recent news about the company"""
        try:
            url = f"{self.apis['newsapi']['base_url']}/everything"
            headers = self.apis['newsapi']['headers']
            params = {
                "q": company_name,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 20
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"News API returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"News API error: {e}")
            return None
    
    # Analysis Methods
    def _analyze_news_sentiment(self, articles: List[Dict]) -> str:
        """Analyze sentiment of news articles"""
        if not articles:
            return "neutral"
        
        # Simple sentiment analysis based on keywords
        positive_words = ["growth", "success", "profit", "expansion", "innovation", "positive"]
        negative_words = ["loss", "decline", "layoff", "struggle", "challenge", "negative"]
        
        positive_count = 0
        negative_count = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            for word in positive_words:
                if word in content:
                    positive_count += 1
            
            for word in negative_words:
                if word in content:
                    negative_count += 1
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_tech_stack(self, jobs: List[Dict]) -> List[str]:
        """Extract technology stack from job postings"""
        tech_keywords = [
            "python", "javascript", "react", "node.js", "java", "c++", "aws", "azure",
            "docker", "kubernetes", "machine learning", "ai", "data science",
            "sql", "mongodb", "redis", "elasticsearch", "kafka", "spark"
        ]
        
        found_tech = set()
        for job in jobs:
            description = job.get('description', '').lower()
            for tech in tech_keywords:
                if tech in description:
                    found_tech.add(tech)
        
        return list(found_tech)
    
    def _analyze_risk_factors(self, profile: CompanyProfile) -> List[str]:
        """Analyze potential risk factors"""
        risks = []
        
        # Financial risks
        if profile.revenue and "declining" in profile.revenue.lower():
            risks.append("Declining revenue trends")
        
        # Market risks
        if profile.competitors and len(profile.competitors) > 10:
            risks.append("Highly competitive market")
        
        # Leadership risks
        if profile.ceo and "recent" in str(profile.ceo).lower():
            risks.append("Recent leadership changes")
        
        # News sentiment risks
        if profile.recent_news:
            sentiment = self._analyze_news_sentiment(profile.recent_news)
            if sentiment == "negative":
                risks.append("Negative media coverage")
        
        return risks
    
    def _analyze_growth_indicators(self, profile: CompanyProfile) -> List[str]:
        """Analyze growth indicators"""
        indicators = []
        
        # Funding indicators
        if profile.total_funding and float(profile.total_funding.replace('$', '').replace(',', '')) > 10000000:
            indicators.append("Well-funded company")
        
        # Hiring indicators
        if profile.job_openings and len(profile.job_openings) > 20:
            indicators.append("Active hiring phase")
        
        # Market position
        if profile.market_position and "leader" in profile.market_position.lower():
            indicators.append("Market leader position")
        
        return indicators
    
    def _generate_interview_insights(self, profile: CompanyProfile) -> List[str]:
        """Generate interview-specific insights"""
        insights = []
        
        # Company culture insights
        if profile.glassdoor_rating and profile.glassdoor_rating > 4.0:
            insights.append("High employee satisfaction - emphasize work-life balance")
        
        # Technical focus
        if profile.tech_stack and len(profile.tech_stack) > 5:
            insights.append("Technology-focused company - prepare for technical questions")
        
        # Growth stage insights
        if profile.funding_stage:
            if "series" in profile.funding_stage.lower():
                insights.append("Growth-stage company - focus on scaling and growth")
            elif "ipo" in profile.funding_stage.lower():
                insights.append("Public company - emphasize stability and governance")
        
        return insights
    
    # Utility Methods
    def _merge_profile_data(self, profile: CompanyProfile, new_data: Dict) -> CompanyProfile:
        """Merge new research data into profile"""
        for key, value in new_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        return profile
    
    async def _cache_company_data(self, company_name: str, profile: CompanyProfile):
        """Cache company research data"""
        try:
            cache_file = self.cache_dir / f"{company_name.lower().replace(' ', '_')}.json"
            with open(cache_file, 'w') as f:
                json.dump(profile.__dict__, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to cache company data: {e}")
    
    async def _scrape_basic_info(self, company_name: str) -> Dict:
        """Fallback web scraping for basic company information"""
        # This would implement web scraping as fallback
        # For now, return basic structure
        return {
            'industry': 'Technology',
            'location': 'Unknown',
            'website': f'https://{company_name.lower().replace(" ", "")}.com'
        }
    
    # Placeholder methods for other API integrations
    async def _fetch_crunchbase_funding(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_crunchbase_leadership(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_crunchbase_competitors(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_linkedin_social(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_twitter_data(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_glassdoor_data(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_job_postings(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _fetch_github_data(self, company_name: str) -> Optional[Dict]:
        return None
    
    async def _extract_email_domains(self, company_name: str) -> List[str]:
        return []
    
    async def _fetch_office_locations(self, company_name: str) -> List[Dict]:
        return []
    
    async def _extract_phone_numbers(self, company_name: str) -> List[str]:
        return []
    
    def _extract_key_topics(self, articles: List[Dict]) -> List[str]:
        return []
    
    async def _fetch_sec_data(self, company_name: str) -> Optional[Dict]:
        return None

# Example usage
async def main():
    """Example usage of the Company Intelligence Engine"""
    api_keys = {
        'newsapi': 'your_news_api_key_here',
        'crunchbase': 'your_crunchbase_key_here',
        'linkedin': 'your_linkedin_token_here',
        'glassdoor': 'your_glassdoor_key_here',
        'sec': 'your_sec_api_key_here'
    }
    
    async with CompanyIntelligenceEngine(api_keys) as engine:
        # Research a company
        profile = await engine.research_company("Microsoft", "company")
        
        # Print results
        print(f"Company: {profile.name}")
        print(f"Industry: {profile.industry}")
        print(f"Founded: {profile.founded_year}")
        print(f"Size: {profile.company_size}")
        print(f"Rating: {profile.glassdoor_rating}")
        print(f"Risk Factors: {profile.risk_factors}")
        print(f"Growth Indicators: {profile.growth_indicators}")
        print(f"Interview Insights: {profile.interview_insights}")

if __name__ == "__main__":
    asyncio.run(main())
