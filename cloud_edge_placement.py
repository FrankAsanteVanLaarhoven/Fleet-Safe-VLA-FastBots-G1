"""
Cloud-Edge Data Placement Engine
Intelligent data placement optimization with predictive analytics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import aiohttp
import redis.asyncio as redis

from advanced_data_locator import SectorType, DataStructureType

logger = logging.getLogger(__name__)

class StorageLocation(Enum):
    """Storage location types"""
    CLOUD_PRIMARY = "cloud_primary"
    CLOUD_SECONDARY = "cloud_secondary"
    EDGE_LOCAL = "edge_local"
    EDGE_REGIONAL = "edge_regional"
    HYBRID = "hybrid"

class AccessPattern(Enum):
    """Data access patterns"""
    FREQUENT_READ = "frequent_read"
    FREQUENT_WRITE = "frequent_write"
    RARE_ACCESS = "rare_access"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME = "real_time"

@dataclass
class AccessPrediction:
    """Access pattern prediction"""
    access_frequency: float  # Accesses per hour
    access_pattern: AccessPattern
    peak_hours: List[int]
    seasonal_variation: float
    confidence_score: float

@dataclass
class RegulatoryConstraints:
    """Regulatory compliance constraints"""
    data_residency: List[str]
    encryption_required: bool
    audit_trail_required: bool
    retention_period: str
    compliance_frameworks: List[str]

@dataclass
class PerformanceRequirements:
    """Performance requirements"""
    latency_sla: float  # milliseconds
    throughput_sla: float  # MB/s
    availability_sla: float  # percentage
    consistency_level: str  # strong, eventual, etc.

@dataclass
class DataPlacementDecision:
    """Data placement decision"""
    primary_location: StorageLocation
    backup_locations: List[StorageLocation]
    caching_strategy: str
    compression_level: str
    encryption_required: bool
    replication_factor: int
    cost_estimate: float
    performance_prediction: Dict[str, float]
    compliance_validated: bool

class AccessPatternMLPredictor:
    """ML-based access pattern prediction"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.access_history = {}
        
    async def predict_access_frequency(
        self, 
        data_characteristics: Dict[str, Any],
        historical_patterns: Dict[str, Any],
        business_context: SectorType
    ) -> AccessPrediction:
        """Predict future access patterns for data"""
        
        # Extract features for prediction
        features = self._extract_prediction_features(
            data_characteristics, historical_patterns, business_context
        )
        
        # Make prediction
        if self.is_trained:
            prediction = await self._make_ml_prediction(features)
        else:
            prediction = await self._make_heuristic_prediction(features)
        
        # Determine access pattern
        access_pattern = self._determine_access_pattern(prediction['access_frequency'])
        
        # Calculate peak hours
        peak_hours = self._calculate_peak_hours(business_context, data_characteristics)
        
        # Calculate seasonal variation
        seasonal_variation = self._calculate_seasonal_variation(business_context)
        
        return AccessPrediction(
            access_frequency=prediction['access_frequency'],
            access_pattern=access_pattern,
            peak_hours=peak_hours,
            seasonal_variation=seasonal_variation,
            confidence_score=prediction['confidence']
        )
    
    def _extract_prediction_features(
        self, 
        data_characteristics: Dict[str, Any],
        historical_patterns: Dict[str, Any],
        business_context: SectorType
    ) -> Dict[str, float]:
        """Extract features for access pattern prediction"""
        
        features = {
            'data_size': data_characteristics.get('data_volume', 0),
            'data_complexity': data_characteristics.get('complexity_score', 0.5),
            'business_criticality': self._get_business_criticality(business_context),
            'update_frequency': self._get_update_frequency_score(data_characteristics),
            'historical_access_rate': historical_patterns.get('avg_access_rate', 0.1),
            'peak_access_multiplier': historical_patterns.get('peak_multiplier', 2.0),
            'seasonal_factor': historical_patterns.get('seasonal_factor', 1.0)
        }
        
        return features
    
    async def _make_ml_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """Make ML-based prediction"""
        
        # Prepare feature vector
        feature_vector = np.array([[
            features['data_size'],
            features['data_complexity'],
            features['business_criticality'],
            features['update_frequency'],
            features['historical_access_rate'],
            features['peak_access_multiplier'],
            features['seasonal_factor']
        ]])
        
        # Scale features
        scaled_features = self.scaler.transform(feature_vector)
        
        # Make prediction
        predicted_frequency = self.model.predict(scaled_features)[0]
        
        return {
            'access_frequency': max(0.0, predicted_frequency),
            'confidence': 0.85  # ML confidence
        }
    
    async def _make_heuristic_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """Make heuristic-based prediction"""
        
        # Simple heuristic based on business context and data characteristics
        base_frequency = features['historical_access_rate']
        
        # Adjust based on business criticality
        criticality_multiplier = 1.0 + (features['business_criticality'] * 0.5)
        
        # Adjust based on update frequency
        update_multiplier = 1.0 + (features['update_frequency'] * 0.3)
        
        # Calculate predicted frequency
        predicted_frequency = base_frequency * criticality_multiplier * update_multiplier
        
        return {
            'access_frequency': predicted_frequency,
            'confidence': 0.6  # Heuristic confidence
        }
    
    def _determine_access_pattern(self, access_frequency: float) -> AccessPattern:
        """Determine access pattern based on frequency"""
        
        if access_frequency > 100:  # More than 100 accesses per hour
            return AccessPattern.REAL_TIME
        elif access_frequency > 10:  # 10-100 accesses per hour
            return AccessPattern.FREQUENT_READ
        elif access_frequency > 1:  # 1-10 accesses per hour
            return AccessPattern.FREQUENT_WRITE
        elif access_frequency > 0.1:  # Less than 1 access per hour
            return AccessPattern.BATCH_PROCESSING
        else:
            return AccessPattern.RARE_ACCESS
    
    def _calculate_peak_hours(self, business_context: SectorType, data_characteristics: Dict[str, Any]) -> List[int]:
        """Calculate peak access hours"""
        
        # Business hours based on sector
        sector_peak_hours = {
            SectorType.FINANCIAL_SERVICES: [9, 10, 11, 14, 15, 16],  # Market hours
            SectorType.HEALTHCARE: [8, 9, 10, 11, 14, 15, 16, 17],  # Clinic hours
            SectorType.ECOMMERCE: [12, 13, 14, 19, 20, 21, 22],  # Shopping hours
            SectorType.GOVERNMENT: [9, 10, 11, 14, 15, 16],  # Office hours
            SectorType.SPORTS: [19, 20, 21, 22],  # Evening hours
        }
        
        return sector_peak_hours.get(business_context, [9, 10, 11, 14, 15, 16])
    
    def _calculate_seasonal_variation(self, business_context: SectorType) -> float:
        """Calculate seasonal variation factor"""
        
        # Seasonal factors by sector
        seasonal_factors = {
            SectorType.FINANCIAL_SERVICES: 1.2,  # Higher during fiscal year end
            SectorType.HEALTHCARE: 1.1,  # Slight increase during flu season
            SectorType.ECOMMERCE: 1.5,  # Much higher during holidays
            SectorType.GOVERNMENT: 1.0,  # Relatively stable
            SectorType.SPORTS: 1.3,  # Higher during seasons
        }
        
        return seasonal_factors.get(business_context, 1.0)
    
    def _get_business_criticality(self, business_context: SectorType) -> float:
        """Get business criticality score"""
        
        criticality_scores = {
            SectorType.FINANCIAL_SERVICES: 0.9,  # Very critical
            SectorType.HEALTHCARE: 0.95,  # Extremely critical
            SectorType.GOVERNMENT: 0.8,  # High criticality
            SectorType.ECOMMERCE: 0.7,  # Medium criticality
            SectorType.SPORTS: 0.5,  # Lower criticality
        }
        
        return criticality_scores.get(business_context, 0.6)
    
    def _get_update_frequency_score(self, data_characteristics: Dict[str, Any]) -> float:
        """Get update frequency score"""
        
        update_frequency = data_characteristics.get('update_frequency', 'unknown')
        
        frequency_scores = {
            'real_time': 1.0,
            'hourly': 0.8,
            'daily': 0.6,
            'weekly': 0.4,
            'monthly': 0.2,
            'unknown': 0.5
        }
        
        return frequency_scores.get(update_frequency, 0.5)

class RegulatoryComplianceAnalyzer:
    """Regulatory compliance analysis engine"""
    
    def __init__(self):
        self.compliance_rules = self._initialize_compliance_rules()
        
    def _initialize_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance rules by sector and region"""
        
        return {
            'financial_services': {
                'data_residency': ['EU', 'UK', 'US'],
                'encryption_required': True,
                'audit_trail_required': True,
                'retention_period': '7_years',
                'compliance_frameworks': ['MiFID_II', 'SEC', 'FCA', 'GDPR']
            },
            'healthcare': {
                'data_residency': ['EU', 'UK', 'US'],
                'encryption_required': True,
                'audit_trail_required': True,
                'retention_period': 'lifetime',
                'compliance_frameworks': ['GDPR', 'HIPAA', 'NHS_data_governance']
            },
            'ecommerce': {
                'data_residency': ['EU', 'UK', 'US'],
                'encryption_required': True,
                'audit_trail_required': False,
                'retention_period': '2_years',
                'compliance_frameworks': ['GDPR', 'CCPA', 'PCI_DSS']
            },
            'government': {
                'data_residency': ['UK'],  # UK government data
                'encryption_required': True,
                'audit_trail_required': True,
                'retention_period': '10_years',
                'compliance_frameworks': ['FOIA', 'data_transparency', 'public_records']
            },
            'climate': {
                'data_residency': ['global'],
                'encryption_required': False,
                'audit_trail_required': True,
                'retention_period': 'permanent',
                'compliance_frameworks': ['IPCC_standards', 'environmental_regulations']
            }
        }
    
    async def analyze_requirements(
        self, 
        data_type: str,
        sector: SectorType,
        geographical_scope: Optional[str]
    ) -> RegulatoryConstraints:
        """Analyze regulatory requirements"""
        
        # Get sector-specific rules
        sector_key = sector.value
        sector_rules = self.compliance_rules.get(sector_key, {})
        
        # Determine geographical scope
        if geographical_scope:
            data_residency = [geographical_scope]
        else:
            data_residency = sector_rules.get('data_residency', ['global'])
        
        # Check for additional requirements based on data type
        additional_frameworks = self._get_additional_frameworks(data_type, sector)
        
        return RegulatoryConstraints(
            data_residency=data_residency,
            encryption_required=sector_rules.get('encryption_required', True),
            audit_trail_required=sector_rules.get('audit_trail_required', False),
            retention_period=sector_rules.get('retention_period', '1_year'),
            compliance_frameworks=sector_rules.get('compliance_frameworks', []) + additional_frameworks
        )
    
    def _get_additional_frameworks(self, data_type: str, sector: SectorType) -> List[str]:
        """Get additional compliance frameworks based on data type"""
        
        additional_frameworks = []
        
        # Add frameworks based on data type
        if 'personal' in data_type.lower():
            additional_frameworks.extend(['GDPR', 'CCPA'])
        
        if 'financial' in data_type.lower():
            additional_frameworks.extend(['PCI_DSS', 'SOX'])
        
        if 'health' in data_type.lower():
            additional_frameworks.extend(['HIPAA', 'NHS_data_governance'])
        
        return additional_frameworks

class EdgePerformanceOptimizer:
    """Edge performance optimization engine"""
    
    def __init__(self):
        self.performance_models = self._initialize_performance_models()
        self.cost_models = self._initialize_cost_models()
        
    def _initialize_performance_models(self) -> Dict[str, Any]:
        """Initialize performance prediction models"""
        # In production, these would be trained ML models
        return {
            'latency_model': None,
            'throughput_model': None,
            'availability_model': None
        }
    
    def _initialize_cost_models(self) -> Dict[str, Dict[str, float]]:
        """Initialize cost models for different storage locations"""
        
        return {
            'cloud_primary': {
                'storage_cost_per_gb_month': 0.023,  # AWS S3 Standard
                'transfer_cost_per_gb': 0.09,
                'request_cost_per_1000': 0.0004
            },
            'cloud_secondary': {
                'storage_cost_per_gb_month': 0.0125,  # AWS S3 IA
                'transfer_cost_per_gb': 0.09,
                'request_cost_per_1000': 0.0004
            },
            'edge_local': {
                'storage_cost_per_gb_month': 0.05,  # Local storage
                'transfer_cost_per_gb': 0.0,
                'request_cost_per_1000': 0.0
            },
            'edge_regional': {
                'storage_cost_per_gb_month': 0.03,  # Regional edge
                'transfer_cost_per_gb': 0.02,
                'request_cost_per_1000': 0.0001
            }
        }
    
    async def calculate_optimal_placement(
        self, 
        access_prediction: AccessPrediction,
        regulatory_constraints: RegulatoryConstraints,
        cost_optimization: bool = True,
        performance_requirements: Optional[PerformanceRequirements] = None
    ) -> Dict[str, Any]:
        """Calculate optimal data placement strategy"""
        
        # Evaluate placement options
        placement_options = await self._evaluate_placement_options(
            access_prediction, regulatory_constraints, performance_requirements
        )
        
        # Select optimal placement
        optimal_placement = await self._select_optimal_placement(
            placement_options, cost_optimization
        )
        
        # Calculate costs
        cost_estimate = await self._calculate_cost_estimate(optimal_placement, access_prediction)
        
        # Predict performance
        performance_prediction = await self._predict_performance(optimal_placement, access_prediction)
        
        return {
            'optimal_location': optimal_placement['primary_location'],
            'redundancy_strategy': optimal_placement['backup_locations'],
            'edge_caching': optimal_placement['caching_strategy'],
            'compression_level': optimal_placement['compression_level'],
            'encryption_required': optimal_placement['encryption_required'],
            'replication_factor': optimal_placement['replication_factor'],
            'cost_estimate': cost_estimate,
            'performance_prediction': performance_prediction,
            'compliance_validated': optimal_placement['compliance_validated']
        }
    
    async def _evaluate_placement_options(
        self, 
        access_prediction: AccessPrediction,
        regulatory_constraints: RegulatoryConstraints,
        performance_requirements: Optional[PerformanceRequirements]
    ) -> List[Dict[str, Any]]:
        """Evaluate different placement options"""
        
        options = []
        
        # Option 1: Cloud Primary
        cloud_primary = {
            'primary_location': StorageLocation.CLOUD_PRIMARY,
            'backup_locations': [StorageLocation.CLOUD_SECONDARY],
            'caching_strategy': 'cloud_cdn',
            'compression_level': 'medium',
            'encryption_required': regulatory_constraints.encryption_required,
            'replication_factor': 2,
            'compliance_validated': self._validate_compliance(StorageLocation.CLOUD_PRIMARY, regulatory_constraints),
            'performance_score': self._calculate_performance_score(StorageLocation.CLOUD_PRIMARY, access_prediction),
            'cost_score': self._calculate_cost_score(StorageLocation.CLOUD_PRIMARY, access_prediction)
        }
        options.append(cloud_primary)
        
        # Option 2: Edge Local
        edge_local = {
            'primary_location': StorageLocation.EDGE_LOCAL,
            'backup_locations': [StorageLocation.CLOUD_PRIMARY],
            'caching_strategy': 'local_cache',
            'compression_level': 'high',
            'encryption_required': regulatory_constraints.encryption_required,
            'replication_factor': 1,
            'compliance_validated': self._validate_compliance(StorageLocation.EDGE_LOCAL, regulatory_constraints),
            'performance_score': self._calculate_performance_score(StorageLocation.EDGE_LOCAL, access_prediction),
            'cost_score': self._calculate_cost_score(StorageLocation.EDGE_LOCAL, access_prediction)
        }
        options.append(edge_local)
        
        # Option 3: Hybrid
        hybrid = {
            'primary_location': StorageLocation.HYBRID,
            'backup_locations': [StorageLocation.CLOUD_PRIMARY, StorageLocation.EDGE_REGIONAL],
            'caching_strategy': 'adaptive_caching',
            'compression_level': 'adaptive',
            'encryption_required': regulatory_constraints.encryption_required,
            'replication_factor': 3,
            'compliance_validated': self._validate_compliance(StorageLocation.HYBRID, regulatory_constraints),
            'performance_score': self._calculate_performance_score(StorageLocation.HYBRID, access_prediction),
            'cost_score': self._calculate_cost_score(StorageLocation.HYBRID, access_prediction)
        }
        options.append(hybrid)
        
        return options
    
    async def _select_optimal_placement(
        self, 
        placement_options: List[Dict[str, Any]],
        cost_optimization: bool
    ) -> Dict[str, Any]:
        """Select optimal placement based on criteria"""
        
        if cost_optimization:
            # Select based on cost score
            optimal = max(placement_options, key=lambda x: x['cost_score'])
        else:
            # Select based on performance score
            optimal = max(placement_options, key=lambda x: x['performance_score'])
        
        return optimal
    
    async def _calculate_cost_estimate(
        self, 
        placement: Dict[str, Any],
        access_prediction: AccessPrediction
    ) -> float:
        """Calculate cost estimate for placement"""
        
        location = placement['primary_location'].value
        cost_model = self.cost_models.get(location, self.cost_models['cloud_primary'])
        
        # Estimate data size (simplified)
        estimated_size_gb = 1.0  # GB
        
        # Calculate monthly costs
        storage_cost = cost_model['storage_cost_per_gb_month'] * estimated_size_gb
        transfer_cost = cost_model['transfer_cost_per_gb'] * access_prediction.access_frequency * 24 * 30  # Monthly
        request_cost = cost_model['request_cost_per_1000'] * access_prediction.access_frequency * 24 * 30 / 1000  # Monthly
        
        total_cost = storage_cost + transfer_cost + request_cost
        
        return total_cost
    
    async def _predict_performance(
        self, 
        placement: Dict[str, Any],
        access_prediction: AccessPrediction
    ) -> Dict[str, float]:
        """Predict performance for placement"""
        
        location = placement['primary_location']
        
        # Simplified performance prediction
        if location == StorageLocation.EDGE_LOCAL:
            latency = 5.0  # ms
            throughput = 100.0  # MB/s
            availability = 0.99  # 99%
        elif location == StorageLocation.CLOUD_PRIMARY:
            latency = 50.0  # ms
            throughput = 50.0  # MB/s
            availability = 0.999  # 99.9%
        else:  # Hybrid
            latency = 20.0  # ms
            throughput = 75.0  # MB/s
            availability = 0.995  # 99.5%
        
        return {
            'latency_ms': latency,
            'throughput_mbps': throughput,
            'availability': availability,
            'consistency_level': 'strong'
        }
    
    def _validate_compliance(
        self, 
        location: StorageLocation,
        regulatory_constraints: RegulatoryConstraints
    ) -> bool:
        """Validate compliance for storage location"""
        
        # Simplified compliance validation
        if regulatory_constraints.encryption_required:
            # All locations support encryption
            pass
        
        if regulatory_constraints.audit_trail_required:
            # Cloud locations have better audit trail support
            if location in [StorageLocation.EDGE_LOCAL]:
                return False
        
        return True
    
    def _calculate_performance_score(
        self, 
        location: StorageLocation,
        access_prediction: AccessPrediction
    ) -> float:
        """Calculate performance score for location"""
        
        # Base performance scores
        base_scores = {
            StorageLocation.EDGE_LOCAL: 0.9,
            StorageLocation.EDGE_REGIONAL: 0.8,
            StorageLocation.CLOUD_PRIMARY: 0.7,
            StorageLocation.CLOUD_SECONDARY: 0.6,
            StorageLocation.HYBRID: 0.85
        }
        
        base_score = base_scores.get(location, 0.5)
        
        # Adjust based on access pattern
        if access_prediction.access_pattern == AccessPattern.REAL_TIME:
            if location in [StorageLocation.EDGE_LOCAL, StorageLocation.EDGE_REGIONAL]:
                base_score *= 1.2  # Edge is better for real-time
            else:
                base_score *= 0.8
        
        return min(base_score, 1.0)
    
    def _calculate_cost_score(
        self, 
        location: StorageLocation,
        access_prediction: AccessPrediction
    ) -> float:
        """Calculate cost score for location (higher is better)"""
        
        # Base cost scores (inverse of cost)
        base_scores = {
            StorageLocation.EDGE_LOCAL: 0.8,  # Lower cost
            StorageLocation.EDGE_REGIONAL: 0.7,
            StorageLocation.CLOUD_PRIMARY: 0.5,
            StorageLocation.CLOUD_SECONDARY: 0.6,
            StorageLocation.HYBRID: 0.4  # Higher cost
        }
        
        base_score = base_scores.get(location, 0.5)
        
        # Adjust based on access frequency
        if access_prediction.access_frequency > 100:
            # High frequency access benefits from edge
            if location in [StorageLocation.EDGE_LOCAL, StorageLocation.EDGE_REGIONAL]:
                base_score *= 1.1
        
        return min(base_score, 1.0)

class CloudEdgeDataPlacementEngine:
    """Main cloud-edge data placement engine"""
    
    def __init__(self):
        self.access_pattern_predictor = AccessPatternMLPredictor()
        self.regulatory_compliance_engine = RegulatoryComplianceAnalyzer()
        self.performance_optimizer = EdgePerformanceOptimizer()
        self.redis_client = None
        
    async def initialize(self):
        """Initialize the placement engine"""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            await self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        logger.info("Cloud-Edge Data Placement Engine initialized")
    
    async def optimize_data_placement(self, classified_data: Dict[str, Any]) -> DataPlacementDecision:
        """Optimize data placement for classified data"""
        
        # Predict future access patterns
        access_prediction = await self.access_pattern_predictor.predict_access_frequency(
            data_characteristics=classified_data.get('metadata', {}),
            historical_patterns=await self._get_historical_access_patterns(),
            business_context=classified_data.get('sector_classification', SectorType.GOVERNMENT)
        )
        
        # Analyze regulatory requirements
        regulatory_constraints = await self.regulatory_compliance_engine.analyze_requirements(
            data_type=classified_data.get('data_type', 'unknown'),
            sector=classified_data.get('sector_classification', SectorType.GOVERNMENT),
            geographical_scope=classified_data.get('geographical_metadata', {}).get('region')
        )
        
        # Calculate optimal placement strategy
        placement_strategy = await self.performance_optimizer.calculate_optimal_placement(
            access_prediction=access_prediction,
            regulatory_constraints=regulatory_constraints,
            cost_optimization=True,
            performance_requirements=classified_data.get('performance_sla')
        )
        
        return DataPlacementDecision(
            primary_location=placement_strategy['optimal_location'],
            backup_locations=placement_strategy['redundancy_strategy'],
            caching_strategy=placement_strategy['edge_caching'],
            compression_level=placement_strategy['compression_level'],
            encryption_required=placement_strategy['encryption_required'],
            replication_factor=placement_strategy['replication_factor'],
            cost_estimate=placement_strategy['cost_estimate'],
            performance_prediction=placement_strategy['performance_prediction'],
            compliance_validated=placement_strategy['compliance_validated']
        )
    
    async def _get_historical_access_patterns(self) -> Dict[str, Any]:
        """Get historical access patterns"""
        # In production, would fetch from database
        return {
            'avg_access_rate': 0.5,  # accesses per hour
            'peak_multiplier': 3.0,
            'seasonal_factor': 1.1
        }

# Example usage
async def main():
    """Example usage of cloud-edge placement engine"""
    
    # Initialize engine
    placement_engine = CloudEdgeDataPlacementEngine()
    await placement_engine.initialize()
    
    # Example classified data
    classified_data = {
        'metadata': {
            'data_volume': 1000000,
            'complexity_score': 0.7,
            'update_frequency': 'real_time'
        },
        'sector_classification': SectorType.FINANCIAL_SERVICES,
        'data_type': 'market_data',
        'geographical_metadata': {
            'region': 'UK',
            'country': 'United Kingdom'
        },
        'performance_sla': PerformanceRequirements(
            latency_sla=10.0,
            throughput_sla=100.0,
            availability_sla=99.9,
            consistency_level='strong'
        )
    }
    
    # Optimize placement
    placement_decision = await placement_engine.optimize_data_placement(classified_data)
    
    print(f"Primary Location: {placement_decision.primary_location.value}")
    print(f"Backup Locations: {[loc.value for loc in placement_decision.backup_locations]}")
    print(f"Caching Strategy: {placement_decision.caching_strategy}")
    print(f"Cost Estimate: ${placement_decision.cost_estimate:.2f}/month")
    print(f"Performance Prediction: {placement_decision.performance_prediction}")
    print(f"Compliance Validated: {placement_decision.compliance_validated}")

if __name__ == "__main__":
    asyncio.run(main()) 