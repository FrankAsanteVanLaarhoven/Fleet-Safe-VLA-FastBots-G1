"""
Intelligent Template Selector
Advanced template selection with cloud-edge optimization
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import aiohttp
import redis.asyncio as redis

from advanced_data_locator import SectorType, DataStructureType, SemanticProfile
from sector_templates import SectorTemplate, TemplateType, TemplateField

logger = logging.getLogger(__name__)

class SelectionStrategy(Enum):
    """Template selection strategies"""
    SEMANTIC_MATCHING = "semantic_matching"
    RULE_BASED = "rule_based"
    ML_PREDICTION = "ml_prediction"
    HYBRID = "hybrid"

@dataclass
class TemplateMatch:
    """Template match result"""
    template: SectorTemplate
    confidence_score: float
    match_reasons: List[str]
    processing_recommendations: List[str]
    performance_metrics: Dict[str, float]

@dataclass
class TemplateSelectionResult:
    """Template selection result"""
    primary_template: SectorTemplate
    secondary_templates: List[SectorTemplate]
    confidence_score: float
    processing_recommendations: List[str]
    selection_strategy: SelectionStrategy
    performance_prediction: Dict[str, float]

class ContentSemanticAnalyzer:
    """Advanced content semantic analysis for template matching"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.semantic_cache = {}
        
    async def generate_content_profile(
        self, 
        content: str, 
        source_metadata: Dict[str, Any],
        domain_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive content profile for template matching"""
        
        # Extract semantic features
        semantic_features = await self._extract_semantic_features(content)
        
        # Analyze content structure
        structure_analysis = await self._analyze_content_structure(content)
        
        # Extract domain-specific patterns
        domain_patterns = await self._extract_domain_patterns(content, domain_context)
        
        # Calculate content metrics
        content_metrics = await self._calculate_content_metrics(content)
        
        # Generate content fingerprint
        content_fingerprint = await self._generate_content_fingerprint(
            semantic_features, structure_analysis, domain_patterns
        )
        
        return {
            'semantic_features': semantic_features,
            'structure_analysis': structure_analysis,
            'domain_patterns': domain_patterns,
            'content_metrics': content_metrics,
            'content_fingerprint': content_fingerprint,
            'source_metadata': source_metadata,
            'domain_context': domain_context,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def _extract_semantic_features(self, content: str) -> Dict[str, Any]:
        """Extract semantic features from content"""
        
        # TF-IDF vectorization
        try:
            tfidf_matrix = self.vectorizer.fit_transform([content])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top features
            top_indices = np.argsort(tfidf_scores)[-50:]  # Top 50 features
            top_features = {
                feature_names[i]: float(tfidf_scores[i])
                for i in top_indices if tfidf_scores[i] > 0.1
            }
        except Exception as e:
            logger.warning(f"TF-IDF extraction failed: {e}")
            top_features = {}
        
        # Extract named entities (simplified)
        named_entities = self._extract_named_entities(content)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(content)
        
        return {
            'tfidf_features': top_features,
            'named_entities': named_entities,
            'key_phrases': key_phrases,
            'content_length': len(content),
            'word_count': len(content.split()),
            'unique_words': len(set(content.lower().split()))
        }
    
    async def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure patterns"""
        
        structure_analysis = {
            'has_tables': '<table' in content.lower(),
            'has_lists': any(tag in content.lower() for tag in ['<ul>', '<ol>', '<li>']),
            'has_forms': '<form' in content.lower(),
            'has_json': content.strip().startswith('{') or content.strip().startswith('['),
            'has_xml': content.strip().startswith('<') and '<?xml' in content.lower(),
            'has_csv_patterns': self._detect_csv_patterns(content),
            'has_time_series': self._detect_time_series_patterns(content),
            'has_graphical_elements': any(tag in content.lower() for tag in ['<svg>', '<canvas>', '<img>'])
        }
        
        return structure_analysis
    
    async def _extract_domain_patterns(
        self, 
        content: str, 
        domain_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract domain-specific patterns"""
        
        domain_patterns = {
            'financial_indicators': self._extract_financial_indicators(content),
            'healthcare_indicators': self._extract_healthcare_indicators(content),
            'climate_indicators': self._extract_climate_indicators(content),
            'ecommerce_indicators': self._extract_ecommerce_indicators(content),
            'government_indicators': self._extract_government_indicators(content)
        }
        
        return domain_patterns
    
    async def _calculate_content_metrics(self, content: str) -> Dict[str, float]:
        """Calculate content quality and complexity metrics"""
        
        words = content.split()
        sentences = content.split('.')
        
        metrics = {
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'unique_word_ratio': len(set(words)) / len(words) if words else 0,
            'numeric_content_ratio': sum(1 for word in words if any(c.isdigit() for c in word)) / len(words) if words else 0,
            'special_char_ratio': sum(1 for c in content if not c.isalnum() and not c.isspace()) / len(content) if content else 0
        }
        
        return metrics
    
    async def _generate_content_fingerprint(
        self, 
        semantic_features: Dict[str, Any],
        structure_analysis: Dict[str, Any],
        domain_patterns: Dict[str, Any]
    ) -> str:
        """Generate content fingerprint for caching and deduplication"""
        
        import hashlib
        
        # Create fingerprint input
        fingerprint_data = {
            'semantic_features': semantic_features.get('tfidf_features', {}),
            'structure_analysis': structure_analysis,
            'domain_patterns': domain_patterns,
            'content_length': semantic_features.get('content_length', 0)
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    def _extract_named_entities(self, content: str) -> List[str]:
        """Extract named entities from content (simplified)"""
        # In production, would use NER models like spaCy
        entities = []
        
        # Simple pattern matching for common entities
        import re
        
        # Company names (simplified)
        company_patterns = [r'\b[A-Z][a-z]+ (Inc|Corp|LLC|Ltd)\b']
        for pattern in company_patterns:
            entities.extend(re.findall(pattern, content))
        
        # Currency amounts
        currency_patterns = [r'\$\d+(?:,\d{3})*(?:\.\d{2})?', r'£\d+(?:,\d{3})*(?:\.\d{2})?']
        for pattern in currency_patterns:
            entities.extend(re.findall(pattern, content))
        
        return list(set(entities))
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content"""
        # Simple key phrase extraction
        phrases = []
        
        # Look for common patterns
        import re
        
        # Noun phrases (simplified)
        noun_phrase_patterns = [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b']
        for pattern in noun_phrase_patterns:
            phrases.extend(re.findall(pattern, content))
        
        return list(set(phrases))
    
    def _detect_csv_patterns(self, content: str) -> bool:
        """Detect CSV-like patterns"""
        lines = content.split('\n')
        if len(lines) < 2:
            return False
        
        # Check if lines have consistent comma separation
        first_line_commas = lines[0].count(',')
        return all(line.count(',') == first_line_commas for line in lines[1:3])
    
    def _detect_time_series_patterns(self, content: str) -> bool:
        """Detect time series patterns"""
        import re
        
        # Look for date/time patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{1,2}:\d{2}:\d{2}'
        ]
        
        return any(re.search(pattern, content) for pattern in date_patterns)
    
    def _extract_financial_indicators(self, content: str) -> List[str]:
        """Extract financial indicators"""
        financial_terms = [
            'stock', 'bond', 'portfolio', 'trading', 'hedge fund', 'derivatives',
            'market cap', 'PE ratio', 'volatility', 'beta', 'alpha', 'Sharpe ratio',
            'SEC', 'FCA', 'ESMA', 'Basel', 'AML', 'KYC'
        ]
        
        content_lower = content.lower()
        return [term for term in financial_terms if term in content_lower]
    
    def _extract_healthcare_indicators(self, content: str) -> List[str]:
        """Extract healthcare indicators"""
        healthcare_terms = [
            'NHS', 'clinical trial', 'patient outcomes', 'treatment efficacy',
            'pharmaceutical', 'FDA', 'EMA', 'medical device', 'diagnosis'
        ]
        
        content_lower = content.lower()
        return [term for term in healthcare_terms if term in content_lower]
    
    def _extract_climate_indicators(self, content: str) -> List[str]:
        """Extract climate indicators"""
        climate_terms = [
            'IPCC', 'climate', 'temperature', 'emissions', 'sustainability',
            'environmental', 'carbon', 'renewable', 'greenhouse gas'
        ]
        
        content_lower = content.lower()
        return [term for term in climate_terms if term in content_lower]
    
    def _extract_ecommerce_indicators(self, content: str) -> List[str]:
        """Extract ecommerce indicators"""
        ecommerce_terms = [
            'product', 'pricing', 'Amazon', 'eBay', 'marketplace', 'seller',
            'inventory', 'shipping', 'reviews', 'conversion rate'
        ]
        
        content_lower = content.lower()
        return [term for term in ecommerce_terms if term in content_lower]
    
    def _extract_government_indicators(self, content: str) -> List[str]:
        """Extract government indicators"""
        government_terms = [
            'census', 'government', 'budget', 'election', 'regulatory',
            'compliance', 'audit', 'public sector', 'local authority'
        ]
        
        content_lower = content.lower()
        return [term for term in government_terms if term in content_lower]

class TemplateMatchingEngine:
    """Advanced template matching engine"""
    
    def __init__(self):
        self.template_library = self._initialize_template_library()
        self.matching_cache = {}
        
    def _initialize_template_library(self) -> Dict[str, SectorTemplate]:
        """Initialize comprehensive template library"""
        
        templates = {}
        
        # Financial Services Templates
        templates['financial_equities'] = SectorTemplate(
            sector=SectorType.FINANCIAL_SERVICES,
            template_name='equities_analysis',
            template_type=TemplateType.EXTRACTION,
            fields=[
                TemplateField('symbol', 'string', True, ['valid_symbol']),
                TemplateField('price', 'float', True, ['positive_value']),
                TemplateField('volume', 'integer', True, ['positive_value']),
                TemplateField('market_cap', 'float', False, ['positive_value']),
                TemplateField('pe_ratio', 'float', False, ['positive_value'])
            ],
            processing_rules={'time_series_frequency': 'real_time'},
            compliance_requirements=['MiFID_II', 'SEC_compliance'],
            update_frequency='real_time',
            priority=9
        )
        
        templates['financial_fixed_income'] = SectorTemplate(
            sector=SectorType.FINANCIAL_SERVICES,
            template_name='fixed_income_analysis',
            template_type=TemplateType.EXTRACTION,
            fields=[
                TemplateField('yield', 'float', True, ['positive_value']),
                TemplateField('duration', 'float', True, ['positive_value']),
                TemplateField('credit_rating', 'string', True, ['valid_rating']),
                TemplateField('maturity', 'date', True, ['future_date'])
            ],
            processing_rules={'valuation_models': ['discounted_cash_flow']},
            compliance_requirements=['MiFID_II', 'FCA_compliance'],
            update_frequency='daily',
            priority=8
        )
        
        # Healthcare Templates
        templates['healthcare_nhs_financial'] = SectorTemplate(
            sector=SectorType.HEALTHCARE,
            template_name='nhs_financial_analysis',
            template_type=TemplateType.EXTRACTION,
            fields=[
                TemplateField('trust_id', 'string', True, ['valid_trust_id']),
                TemplateField('revenue', 'float', True, ['positive_value']),
                TemplateField('expenditure', 'float', True, ['positive_value']),
                TemplateField('surplus_deficit', 'float', False, ['valid_amount'])
            ],
            processing_rules={'reporting_standards': ['IFRS', 'HM_Treasury_FReM']},
            compliance_requirements=['GDPR', 'NHS_data_governance'],
            update_frequency='monthly',
            priority=8
        )
        
        # Climate Templates
        templates['climate_ipcc'] = SectorTemplate(
            sector=SectorType.CLIMATE,
            template_name='ipcc_climate_analysis',
            template_type=TemplateType.EXTRACTION,
            fields=[
                TemplateField('scenario', 'string', True, ['valid_scenario']),
                TemplateField('variable', 'string', True, ['valid_variable']),
                TemplateField('value', 'float', True, ['valid_range']),
                TemplateField('uncertainty', 'float', False, ['positive_value'])
            ],
            processing_rules={'data_sources': ['IPCC_DDC', 'climate_observations']},
            compliance_requirements=['IPCC_standards'],
            update_frequency='quarterly',
            priority=7
        )
        
        return templates
    
    async def find_matching_templates(
        self, 
        content_profile: Dict[str, Any],
        confidence_threshold: float = 0.8,
        multi_template_support: bool = True
    ) -> Dict[str, Any]:
        """Find matching templates for content"""
        
        matches = []
        
        # Calculate similarity scores for each template
        for template_id, template in self.template_library.items():
            similarity_score = await self._calculate_template_similarity(
                content_profile, template
            )
            
            if similarity_score >= confidence_threshold:
                match = TemplateMatch(
                    template=template,
                    confidence_score=similarity_score,
                    match_reasons=self._generate_match_reasons(content_profile, template),
                    processing_recommendations=self._generate_processing_recommendations(template),
                    performance_metrics=self._estimate_performance_metrics(template)
                )
                matches.append(match)
        
        # Sort by confidence score
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return {
            'best_match': matches[0] if matches else None,
            'alternative_matches': matches[1:] if len(matches) > 1 else [],
            'total_matches': len(matches),
            'confidence_threshold': confidence_threshold
        }
    
    async def _calculate_template_similarity(
        self, 
        content_profile: Dict[str, Any], 
        template: SectorTemplate
    ) -> float:
        """Calculate similarity between content profile and template"""
        
        # Sector matching
        sector_match = self._calculate_sector_match(content_profile, template)
        
        # Structure matching
        structure_match = self._calculate_structure_match(content_profile, template)
        
        # Field matching
        field_match = self._calculate_field_match(content_profile, template)
        
        # Domain pattern matching
        domain_match = self._calculate_domain_match(content_profile, template)
        
        # Weighted combination
        similarity_score = (
            sector_match * 0.3 +
            structure_match * 0.2 +
            field_match * 0.3 +
            domain_match * 0.2
        )
        
        return min(similarity_score, 1.0)
    
    def _calculate_sector_match(
        self, 
        content_profile: Dict[str, Any], 
        template: SectorTemplate
    ) -> float:
        """Calculate sector matching score"""
        
        domain_patterns = content_profile.get('domain_patterns', {})
        
        # Map template sector to domain patterns
        sector_pattern_mapping = {
            SectorType.FINANCIAL_SERVICES: 'financial_indicators',
            SectorType.HEALTHCARE: 'healthcare_indicators',
            SectorType.CLIMATE: 'climate_indicators',
            SectorType.ECOMMERCE: 'ecommerce_indicators',
            SectorType.GOVERNMENT: 'government_indicators'
        }
        
        pattern_key = sector_pattern_mapping.get(template.sector)
        if pattern_key and domain_patterns.get(pattern_key):
            return min(len(domain_patterns[pattern_key]) / 5.0, 1.0)
        
        return 0.1  # Base score for no match
    
    def _calculate_structure_match(
        self, 
        content_profile: Dict[str, Any], 
        template: SectorTemplate
    ) -> float:
        """Calculate structure matching score"""
        
        structure_analysis = content_profile.get('structure_analysis', {})
        
        # Check if content structure matches template expectations
        if template.template_type == TemplateType.EXTRACTION:
            if structure_analysis.get('has_json') or structure_analysis.get('has_tables'):
                return 0.9
            elif structure_analysis.get('has_csv_patterns'):
                return 0.8
            else:
                return 0.5
        
        return 0.7  # Default score
    
    def _calculate_field_match(
        self, 
        content_profile: Dict[str, Any], 
        template: SectorTemplate
    ) -> float:
        """Calculate field matching score"""
        
        semantic_features = content_profile.get('semantic_features', {})
        tfidf_features = semantic_features.get('tfidf_features', {})
        
        # Check if template fields are present in content
        field_matches = 0
        total_fields = len(template.fields)
        
        for field in template.fields:
            if field.name.lower() in tfidf_features:
                field_matches += 1
        
        return field_matches / total_fields if total_fields > 0 else 0.0
    
    def _calculate_domain_match(
        self, 
        content_profile: Dict[str, Any], 
        template: SectorTemplate
    ) -> float:
        """Calculate domain pattern matching score"""
        
        domain_patterns = content_profile.get('domain_patterns', {})
        
        # Count matching domain indicators
        total_indicators = 0
        matching_indicators = 0
        
        for pattern_list in domain_patterns.values():
            total_indicators += len(pattern_list)
            if pattern_list:  # If any indicators found
                matching_indicators += 1
        
        return matching_indicators / len(domain_patterns) if domain_patterns else 0.0
    
    def _generate_match_reasons(
        self, 
        content_profile: Dict[str, Any], 
        template: SectorTemplate
    ) -> List[str]:
        """Generate reasons for template match"""
        
        reasons = []
        
        # Sector match reason
        reasons.append(f"Content matches {template.sector.value} sector")
        
        # Structure match reason
        structure_analysis = content_profile.get('structure_analysis', {})
        if structure_analysis.get('has_json'):
            reasons.append("Content contains structured JSON data")
        elif structure_analysis.get('has_tables'):
            reasons.append("Content contains tabular data")
        
        # Field match reason
        semantic_features = content_profile.get('semantic_features', {})
        tfidf_features = semantic_features.get('tfidf_features', {})
        matching_fields = [field.name for field in template.fields if field.name.lower() in tfidf_features]
        if matching_fields:
            reasons.append(f"Content contains template fields: {', '.join(matching_fields[:3])}")
        
        return reasons
    
    def _generate_processing_recommendations(self, template: SectorTemplate) -> List[str]:
        """Generate processing recommendations for template"""
        
        recommendations = []
        
        # Priority-based recommendations
        if template.priority >= 9:
            recommendations.append("High priority processing recommended")
        
        # Compliance recommendations
        if template.compliance_requirements:
            recommendations.append(f"Ensure compliance with: {', '.join(template.compliance_requirements)}")
        
        # Update frequency recommendations
        if template.update_frequency == 'real_time':
            recommendations.append("Real-time processing required")
        elif template.update_frequency == 'daily':
            recommendations.append("Daily batch processing recommended")
        
        return recommendations
    
    def _estimate_performance_metrics(self, template: SectorTemplate) -> Dict[str, float]:
        """Estimate performance metrics for template"""
        
        # Simplified performance estimation
        base_processing_time = 0.1  # seconds
        
        # Adjust based on template complexity
        complexity_multiplier = len(template.fields) / 5.0
        
        # Adjust based on priority
        priority_multiplier = 1.0 / template.priority
        
        estimated_processing_time = base_processing_time * complexity_multiplier * priority_multiplier
        
        return {
            'estimated_processing_time': estimated_processing_time,
            'memory_usage': len(template.fields) * 0.1,  # MB
            'cpu_usage': template.priority / 10.0,
            'success_rate': 0.95  # Estimated success rate
        }

class TemplateConfidenceAssessor:
    """Assess template selection confidence"""
    
    def __init__(self):
        self.confidence_models = self._initialize_confidence_models()
        
    def _initialize_confidence_models(self) -> Dict[str, Any]:
        """Initialize confidence assessment models"""
        # In production, these would be trained ML models
        return {
            'semantic_confidence': None,
            'structural_confidence': None,
            'historical_confidence': None
        }
    
    async def assess_template_match(
        self, 
        content_profile: Dict[str, Any],
        template_matches: Dict[str, Any],
        historical_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess confidence in template match"""
        
        if not template_matches.get('best_match'):
            return {
                'overall_confidence': 0.0,
                'confidence_breakdown': {},
                'optimization_suggestions': ['No suitable template found']
            }
        
        best_match = template_matches['best_match']
        
        # Calculate confidence breakdown
        confidence_breakdown = {
            'semantic_confidence': self._assess_semantic_confidence(content_profile, best_match),
            'structural_confidence': self._assess_structural_confidence(content_profile, best_match),
            'historical_confidence': self._assess_historical_confidence(best_match, historical_performance),
            'field_coverage_confidence': self._assess_field_coverage_confidence(content_profile, best_match)
        }
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_breakdown.values()) / len(confidence_breakdown)
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            confidence_breakdown, content_profile, best_match
        )
        
        return {
            'overall_confidence': overall_confidence,
            'confidence_breakdown': confidence_breakdown,
            'optimization_suggestions': optimization_suggestions
        }
    
    def _assess_semantic_confidence(
        self, 
        content_profile: Dict[str, Any], 
        template_match: TemplateMatch
    ) -> float:
        """Assess semantic confidence"""
        
        semantic_features = content_profile.get('semantic_features', {})
        tfidf_features = semantic_features.get('tfidf_features', {})
        
        # Calculate feature density
        feature_density = len(tfidf_features) / 100.0  # Normalize to 0-1
        
        # Calculate semantic relevance
        semantic_relevance = template_match.confidence_score
        
        return (feature_density + semantic_relevance) / 2.0
    
    def _assess_structural_confidence(
        self, 
        content_profile: Dict[str, Any], 
        template_match: TemplateMatch
    ) -> float:
        """Assess structural confidence"""
        
        structure_analysis = content_profile.get('structure_analysis', {})
        template = template_match.template
        
        # Check structure compatibility
        if template.template_type == TemplateType.EXTRACTION:
            if structure_analysis.get('has_json') or structure_analysis.get('has_tables'):
                return 0.9
            elif structure_analysis.get('has_csv_patterns'):
                return 0.8
            else:
                return 0.6
        
        return 0.7
    
    def _assess_historical_confidence(
        self, 
        template_match: TemplateMatch, 
        historical_performance: Dict[str, Any]
    ) -> float:
        """Assess historical confidence"""
        
        template_id = f"{template_match.template.sector.value}_{template_match.template.template_name}"
        
        if template_id in historical_performance:
            return historical_performance[template_id].get('success_rate', 0.8)
        
        return 0.8  # Default confidence
    
    def _assess_field_coverage_confidence(
        self, 
        content_profile: Dict[str, Any], 
        template_match: TemplateMatch
    ) -> float:
        """Assess field coverage confidence"""
        
        semantic_features = content_profile.get('semantic_features', {})
        tfidf_features = semantic_features.get('tfidf_features', {})
        template = template_match.template
        
        # Calculate field coverage
        matching_fields = sum(
            1 for field in template.fields 
            if field.name.lower() in tfidf_features
        )
        
        return matching_fields / len(template.fields) if template.fields else 0.0
    
    def _generate_optimization_suggestions(
        self, 
        confidence_breakdown: Dict[str, float],
        content_profile: Dict[str, Any],
        template_match: TemplateMatch
    ) -> List[str]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        # Low semantic confidence
        if confidence_breakdown['semantic_confidence'] < 0.6:
            suggestions.append("Consider enriching content with domain-specific terminology")
        
        # Low structural confidence
        if confidence_breakdown['structural_confidence'] < 0.6:
            suggestions.append("Consider preprocessing content to improve structure")
        
        # Low field coverage
        if confidence_breakdown['field_coverage_confidence'] < 0.5:
            suggestions.append("Content may be missing key template fields")
        
        # High confidence overall
        if sum(confidence_breakdown.values()) / len(confidence_breakdown) > 0.8:
            suggestions.append("Template match is highly confident - proceed with processing")
        
        return suggestions

class IntelligentTemplateSelector:
    """Main intelligent template selector"""
    
    def __init__(self):
        self.content_analyzer = ContentSemanticAnalyzer()
        self.template_matcher = TemplateMatchingEngine()
        self.confidence_assessor = TemplateConfidenceAssessor()
        self.redis_client = None
        
    async def initialize(self):
        """Initialize the template selector"""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            await self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        logger.info("Intelligent Template Selector initialized")
    
    async def select_optimal_template(
        self, 
        crawled_content: str,
        source_metadata: Optional[Dict[str, Any]] = None,
        domain_context: Optional[Dict[str, Any]] = None
    ) -> TemplateSelectionResult:
        """Select optimal template for content"""
        
        # Prepare metadata and context
        metadata = source_metadata or {}
        context = domain_context or {}
        
        # Analyze content characteristics
        content_profile = await self.content_analyzer.generate_content_profile(
            content=crawled_content,
            source_metadata=metadata,
            domain_context=context
        )
        
        # Match against template library
        template_matches = await self.template_matcher.find_matching_templates(
            content_profile=content_profile,
            confidence_threshold=0.8,
            multi_template_support=True
        )
        
        # Assess selection confidence
        historical_performance = await self._get_historical_performance()
        selection_confidence = await self.confidence_assessor.assess_template_match(
            content_profile=content_profile,
            template_matches=template_matches,
            historical_performance=historical_performance
        )
        
        # Determine selection strategy
        selection_strategy = self._determine_selection_strategy(
            template_matches, selection_confidence
        )
        
        # Create result
        if template_matches.get('best_match'):
            primary_template = template_matches['best_match'].template
            secondary_templates = [match.template for match in template_matches.get('alternative_matches', [])]
        else:
            primary_template = None
            secondary_templates = []
        
        return TemplateSelectionResult(
            primary_template=primary_template,
            secondary_templates=secondary_templates,
            confidence_score=selection_confidence['overall_confidence'],
            processing_recommendations=selection_confidence['optimization_suggestions'],
            selection_strategy=selection_strategy,
            performance_prediction=self._predict_performance(template_matches)
        )
    
    async def _get_historical_performance(self) -> Dict[str, Any]:
        """Get historical template performance data"""
        # In production, would fetch from database
        return {
            'financial_equities_analysis': {'success_rate': 0.95, 'avg_processing_time': 0.2},
            'nhs_financial_analysis': {'success_rate': 0.92, 'avg_processing_time': 0.3},
            'ipcc_climate_analysis': {'success_rate': 0.88, 'avg_processing_time': 0.4}
        }
    
    def _determine_selection_strategy(
        self, 
        template_matches: Dict[str, Any],
        selection_confidence: Dict[str, Any]
    ) -> SelectionStrategy:
        """Determine template selection strategy"""
        
        if selection_confidence['overall_confidence'] > 0.9:
            return SelectionStrategy.SEMANTIC_MATCHING
        elif selection_confidence['overall_confidence'] > 0.7:
            return SelectionStrategy.HYBRID
        else:
            return SelectionStrategy.RULE_BASED
    
    def _predict_performance(self, template_matches: Dict[str, Any]) -> Dict[str, float]:
        """Predict performance for selected template"""
        
        if not template_matches.get('best_match'):
            return {'processing_time': 0.0, 'success_rate': 0.0, 'resource_usage': 0.0}
        
        best_match = template_matches['best_match']
        performance_metrics = best_match.performance_metrics
        
        return {
            'processing_time': performance_metrics.get('estimated_processing_time', 0.1),
            'success_rate': performance_metrics.get('success_rate', 0.9),
            'resource_usage': performance_metrics.get('cpu_usage', 0.5)
        }

# Example usage
async def main():
    """Example usage of intelligent template selector"""
    
    # Initialize selector
    selector = IntelligentTemplateSelector()
    await selector.initialize()
    
    # Example content
    sample_content = """
    {
        "symbol": "AAPL",
        "price": 150.25,
        "volume": 5000000,
        "market_cap": 2500000000000,
        "pe_ratio": 25.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    
    # Select template
    result = await selector.select_optimal_template(
        crawled_content=sample_content,
        source_metadata={'source': 'financial_api'},
        domain_context={'domain': 'financial_services'}
    )
    
    print(f"Primary Template: {result.primary_template.template_name if result.primary_template else 'None'}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Selection Strategy: {result.selection_strategy.value}")
    print(f"Processing Recommendations: {result.processing_recommendations}")
    print(f"Performance Prediction: {result.performance_prediction}")

if __name__ == "__main__":
    asyncio.run(main()) 