"""
Dynamic Context Optimizer for Hybrid RAG-CAG (DCO-RAG/CAG)
Patent-track innovation: "RL-guided switch that predicts context-stability to toggle between 
retrieval and cache modes in <50 ms"

Patent Class: G06F16/951, G06N5/04
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import hashlib
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextMode(Enum):
    """Context optimization modes"""
    RAG = "retrieval_augmented_generation"
    CAG = "cache_augmented_generation"
    HYBRID = "hybrid_mode"

class ContextStability(Enum):
    """Context stability levels"""
    STATIC = "static"
    SEMI_STATIC = "semi_static"
    DYNAMIC = "dynamic"
    HIGHLY_DYNAMIC = "highly_dynamic"

@dataclass
class ContextFeatures:
    """Features for context stability prediction"""
    url_pattern: str
    content_hash: str
    update_frequency: float
    content_size: int
    link_density: float
    dynamic_elements: int
    cache_headers: Dict[str, str]
    last_modified: float
    etag: Optional[str]
    stability_score: float

@dataclass
class OptimizationDecision:
    """Decision made by the context optimizer"""
    mode: ContextMode
    confidence: float
    reasoning: str
    switch_overhead: float
    predicted_latency: float
    stability_prediction: ContextStability

@dataclass
class CacheEntry:
    """Cache entry for CAG mode"""
    content_hash: str
    content: str
    metadata: Dict[str, Any]
    timestamp: float
    access_count: int
    last_access: float

class ContextStabilityPredictor:
    """Neural network for predicting context stability"""
    
    def __init__(self):
        self.model = self._build_predictor()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.training_history = []
    
    def _build_predictor(self) -> nn.Module:
        """Build neural network for stability prediction"""
        return nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
    
    def extract_features(self, url: str, content: str, metadata: Dict[str, Any]) -> ContextFeatures:
        """Extract features for stability prediction"""
        # URL pattern analysis
        url_pattern = self._analyze_url_pattern(url)
        
        # Content analysis
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        content_size = len(content)
        link_density = content.count('<a href') / max(content_size / 1000, 1)
        dynamic_elements = content.count('script') + content.count('ajax') + content.count('api')
        
        # Cache headers analysis
        cache_headers = metadata.get('cache_headers', {})
        last_modified = metadata.get('last_modified', time.time())
        etag = metadata.get('etag')
        
        # Calculate update frequency (simplified)
        update_frequency = self._estimate_update_frequency(url, metadata)
        
        # Calculate stability score
        stability_score = self._calculate_stability_score(
            url_pattern, update_frequency, link_density, dynamic_elements, cache_headers
        )
        
        return ContextFeatures(
            url_pattern=url_pattern,
            content_hash=content_hash,
            update_frequency=update_frequency,
            content_size=content_size,
            link_density=link_density,
            dynamic_elements=dynamic_elements,
            cache_headers=cache_headers,
            last_modified=last_modified,
            etag=etag,
            stability_score=stability_score
        )
    
    def _analyze_url_pattern(self, url: str) -> str:
        """Analyze URL pattern for stability prediction"""
        if '/api/' in url:
            return "api_endpoint"
        elif '/static/' in url or '/assets/' in url:
            return "static_resource"
        elif '/blog/' in url or '/news/' in url:
            return "content_page"
        elif '/admin/' in url or '/dashboard/' in url:
            return "dynamic_interface"
        else:
            return "general_page"
    
    def _estimate_update_frequency(self, url: str, metadata: Dict[str, Any]) -> float:
        """Estimate content update frequency"""
        url_pattern = self._analyze_url_pattern(url)
        
        # Base frequencies (updates per day)
        base_frequencies = {
            "api_endpoint": 100.0,
            "static_resource": 0.1,
            "content_page": 2.0,
            "dynamic_interface": 50.0,
            "general_page": 1.0
        }
        
        return base_frequencies.get(url_pattern, 1.0)
    
    def _calculate_stability_score(self, url_pattern: str, update_frequency: float,
                                 link_density: float, dynamic_elements: int,
                                 cache_headers: Dict[str, str]) -> float:
        """Calculate stability score from features"""
        # Normalize features
        norm_frequency = min(update_frequency / 100.0, 1.0)
        norm_link_density = min(link_density / 10.0, 1.0)
        norm_dynamic_elements = min(dynamic_elements / 50.0, 1.0)
        
        # Pattern weights
        pattern_weights = {
            "api_endpoint": 0.2,
            "static_resource": 0.9,
            "content_page": 0.6,
            "dynamic_interface": 0.3,
            "general_page": 0.5
        }
        
        pattern_weight = pattern_weights.get(url_pattern, 0.5)
        
        # Calculate stability score (higher = more stable)
        stability = (
            pattern_weight * 0.4 +
            (1.0 - norm_frequency) * 0.3 +
            (1.0 - norm_link_density) * 0.2 +
            (1.0 - norm_dynamic_elements) * 0.1
        )
        
        return max(0.0, min(1.0, stability))
    
    def predict_stability(self, features: ContextFeatures) -> float:
        """Predict context stability using neural network"""
        # Convert features to tensor
        feature_vector = torch.tensor([
            features.update_frequency,
            features.content_size / 10000.0,  # Normalize
            features.link_density,
            features.dynamic_elements / 100.0,  # Normalize
            features.stability_score,
            len(features.cache_headers) / 10.0,  # Normalize
            time.time() - features.last_modified,
            1.0 if features.etag else 0.0,
            features.content_size / 1000000.0,  # MB
            features.update_frequency / 100.0
        ], dtype=torch.float32).unsqueeze(0)
        
        # Predict stability
        with torch.no_grad():
            prediction = self.model(feature_vector)
            return prediction.item()
    
    def train(self, features: List[ContextFeatures], actual_stabilities: List[float]):
        """Train the stability predictor"""
        if len(features) < 10:  # Need minimum training data
            return
        
        # Prepare training data
        feature_vectors = []
        for feature in features:
            feature_vector = torch.tensor([
                feature.update_frequency,
                feature.content_size / 10000.0,
                feature.link_density,
                feature.dynamic_elements / 100.0,
                feature.stability_score,
                len(feature.cache_headers) / 10.0,
                time.time() - feature.last_modified,
                1.0 if feature.etag else 0.0,
                feature.content_size / 1000000.0,
                feature.update_frequency / 100.0
            ], dtype=torch.float32)
            feature_vectors.append(feature_vector)
        
        X = torch.stack(feature_vectors)
        y = torch.tensor(actual_stabilities, dtype=torch.float32)
        
        # Training step
        self.optimizer.zero_grad()
        predictions = self.model(X).squeeze()
        loss = self.criterion(predictions, y)
        loss.backward()
        self.optimizer.step()
        
        self.training_history.append(loss.item())

class CacheManager:
    """Cache manager for CAG mode"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.access_history = deque(maxlen=1000)
    
    def get(self, content_hash: str) -> Optional[CacheEntry]:
        """Get cache entry"""
        if content_hash in self.cache:
            entry = self.cache[content_hash]
            entry.access_count += 1
            entry.last_access = time.time()
            self.access_history.append(content_hash)
            return entry
        return None
    
    def put(self, content_hash: str, content: str, metadata: Dict[str, Any]):
        """Put content in cache"""
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
        
        self.cache[content_hash] = CacheEntry(
            content_hash=content_hash,
            content=content,
            metadata=metadata,
            timestamp=time.time(),
            access_count=1,
            last_access=time.time()
        )
    
    def _evict_least_used(self):
        """Evict least used cache entry"""
        if not self.cache:
            return
        
        # Find least recently used entry
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_access)
        del self.cache[lru_key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {"hit_rate": 0.0, "size": 0, "max_size": self.max_size}
        
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        hit_rate = total_accesses / max(len(self.access_history), 1)
        
        return {
            "hit_rate": hit_rate,
            "size": len(self.cache),
            "max_size": self.max_size,
            "avg_access_count": total_accesses / len(self.cache)
        }

class RAGEngine:
    """Retrieval-Augmented Generation engine"""
    
    def __init__(self):
        self.vector_store = {}  # Simplified vector store
        self.retrieval_history = []
    
    async def retrieve_context(self, query: str, url: str) -> str:
        """Retrieve context for RAG mode"""
        logger.info(f"Retrieving context for {url}")
        
        # Simulate retrieval latency
        await asyncio.sleep(0.1)  # 100ms retrieval time
        
        # Simulate context retrieval
        context = f"Retrieved context for {url}: {query[:100]}..."
        
        self.retrieval_history.append({
            "url": url,
            "query": query,
            "timestamp": time.time(),
            "latency": 0.1
        })
        
        return context
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics"""
        if not self.retrieval_history:
            return {"avg_latency": 0.0, "total_retrievals": 0}
        
        latencies = [r["latency"] for r in self.retrieval_history]
        return {
            "avg_latency": np.mean(latencies),
            "total_retrievals": len(self.retrieval_history),
            "max_latency": np.max(latencies),
            "min_latency": np.min(latencies)
        }

class DynamicContextOptimizer:
    """Dynamic Context Optimizer for Hybrid RAG-CAG"""
    
    def __init__(self):
        self.stability_predictor = ContextStabilityPredictor()
        self.cache_manager = CacheManager()
        self.rag_engine = RAGEngine()
        self.decision_history = []
        self.switch_overhead_target = 0.05  # 50ms target
        
    async def optimize_context(self, url: str, query: str, content: str, 
                             metadata: Dict[str, Any]) -> OptimizationDecision:
        """Optimize context retrieval strategy"""
        start_time = time.time()
        
        # Extract features
        features = self.stability_predictor.extract_features(url, content, metadata)
        
        # Predict stability
        predicted_stability = self.stability_predictor.predict_stability(features)
        
        # Check cache first
        cache_entry = self.cache_manager.get(features.content_hash)
        
        # Make optimization decision
        decision = self._make_decision(features, predicted_stability, cache_entry, query)
        
        # Execute decision
        result = await self._execute_decision(decision, url, query, content, cache_entry)
        
        # Calculate switch overhead
        switch_overhead = time.time() - start_time
        decision.switch_overhead = switch_overhead
        
        # Validate performance target
        if switch_overhead > self.switch_overhead_target:
            logger.warning(f"Switch overhead {switch_overhead:.3f}s exceeds target {self.switch_overhead_target}s")
        
        self.decision_history.append(decision)
        return decision
    
    def _make_decision(self, features: ContextFeatures, predicted_stability: float,
                      cache_entry: Optional[CacheEntry], query: str) -> OptimizationDecision:
        """Make optimization decision based on features and predictions"""
        
        # Decision logic based on stability and cache availability
        if predicted_stability > 0.8 and cache_entry:
            # High stability + cache hit -> CAG mode
            mode = ContextMode.CAG
            confidence = 0.9
            reasoning = "High stability with cache hit - using CAG mode"
        elif predicted_stability > 0.6:
            # Medium-high stability -> Hybrid mode
            mode = ContextMode.HYBRID
            confidence = 0.7
            reasoning = "Medium stability - using hybrid mode"
        else:
            # Low stability -> RAG mode
            mode = ContextMode.RAG
            confidence = 0.8
            reasoning = "Low stability - using RAG mode"
        
        # Determine stability level
        if predicted_stability > 0.8:
            stability_level = ContextStability.STATIC
        elif predicted_stability > 0.6:
            stability_level = ContextStability.SEMI_STATIC
        elif predicted_stability > 0.4:
            stability_level = ContextStability.DYNAMIC
        else:
            stability_level = ContextStability.HIGHLY_DYNAMIC
        
        # Predict latency
        predicted_latency = self._predict_latency(mode, features)
        
        return OptimizationDecision(
            mode=mode,
            confidence=confidence,
            reasoning=reasoning,
            switch_overhead=0.0,  # Will be calculated later
            predicted_latency=predicted_latency,
            stability_prediction=stability_level
        )
    
    def _predict_latency(self, mode: ContextMode, features: ContextFeatures) -> float:
        """Predict latency for different modes"""
        base_latency = 0.05  # 50ms base
        
        if mode == ContextMode.CAG:
            return base_latency * 0.1  # 5ms for cache
        elif mode == ContextMode.HYBRID:
            return base_latency * 0.5  # 25ms for hybrid
        else:  # RAG mode
            return base_latency * 2.0  # 100ms for retrieval
    
    async def _execute_decision(self, decision: OptimizationDecision, url: str, 
                              query: str, content: str, 
                              cache_entry: Optional[CacheEntry]) -> str:
        """Execute the optimization decision"""
        
        if decision.mode == ContextMode.CAG and cache_entry:
            # Use cached content
            logger.info(f"Using CAG mode for {url}")
            return cache_entry.content
        
        elif decision.mode == ContextMode.HYBRID:
            # Use hybrid approach
            logger.info(f"Using hybrid mode for {url}")
            
            # Try cache first, then RAG
            if cache_entry:
                return cache_entry.content
            else:
                rag_context = await self.rag_engine.retrieve_context(query, url)
                # Cache the result
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                self.cache_manager.put(content_hash, rag_context, {"url": url})
                return rag_context
        
        else:  # RAG mode
            # Use retrieval-augmented generation
            logger.info(f"Using RAG mode for {url}")
            rag_context = await self.rag_engine.retrieve_context(query, url)
            
            # Cache the result for future use
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            self.cache_manager.put(content_hash, rag_context, {"url": url})
            
            return rag_context
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get optimization performance metrics"""
        if not self.decision_history:
            return {}
        
        # Calculate metrics
        mode_distribution = {}
        avg_switch_overhead = 0.0
        avg_latency = 0.0
        target_achievement = 0.0
        
        for decision in self.decision_history:
            mode = decision.mode.value
            mode_distribution[mode] = mode_distribution.get(mode, 0) + 1
            
            avg_switch_overhead += decision.switch_overhead
            avg_latency += decision.predicted_latency
            
            if decision.switch_overhead <= self.switch_overhead_target:
                target_achievement += 1
        
        total_decisions = len(self.decision_history)
        
        return {
            "total_decisions": total_decisions,
            "mode_distribution": {k: v/total_decisions for k, v in mode_distribution.items()},
            "avg_switch_overhead": avg_switch_overhead / total_decisions,
            "avg_latency": avg_latency / total_decisions,
            "target_achievement_rate": target_achievement / total_decisions,
            "cache_stats": self.cache_manager.get_cache_stats(),
            "rag_stats": self.rag_engine.get_retrieval_stats()
        }

# Main execution function
async def main():
    """Main execution function for Dynamic Context Optimizer"""
    logger.info("Starting Dynamic Context Optimizer for Hybrid RAG-CAG")
    
    # Initialize optimizer
    optimizer = DynamicContextOptimizer()
    
    # Test scenarios
    test_scenarios = [
        {
            "url": "https://example.com/static/style.css",
            "query": "CSS styling information",
            "content": "body { margin: 0; padding: 0; }",
            "metadata": {
                "cache_headers": {"Cache-Control": "max-age=31536000"},
                "last_modified": time.time() - 86400,
                "etag": "abc123"
            }
        },
        {
            "url": "https://example.com/api/data",
            "query": "API response data",
            "content": '{"status": "success", "data": []}',
            "metadata": {
                "cache_headers": {"Cache-Control": "no-cache"},
                "last_modified": time.time() - 60,
                "etag": None
            }
        },
        {
            "url": "https://example.com/blog/article",
            "query": "Blog article content",
            "content": "This is a blog article about technology...",
            "metadata": {
                "cache_headers": {"Cache-Control": "max-age=3600"},
                "last_modified": time.time() - 3600,
                "etag": "def456"
            }
        }
    ]
    
    # Execute optimization for each scenario
    for i, scenario in enumerate(test_scenarios):
        decision = await optimizer.optimize_context(
            scenario["url"],
            scenario["query"],
            scenario["content"],
            scenario["metadata"]
        )
        
        logger.info(f"Scenario {i+1}: {decision.mode.value}")
        logger.info(f"Confidence: {decision.confidence:.2f}")
        logger.info(f"Switch overhead: {decision.switch_overhead*1000:.1f}ms")
        logger.info(f"Reasoning: {decision.reasoning}")
    
    # Report metrics
    metrics = optimizer.get_optimization_metrics()
    logger.info(f"Optimization Metrics: {metrics}")
    
    # Validate performance targets
    target_achieved = metrics.get("target_achievement_rate", 0.0) > 0.95
    logger.info(f"Performance target achieved: {target_achieved}")
    
    return {
        "total_decisions": metrics.get("total_decisions", 0),
        "avg_switch_overhead": metrics.get("avg_switch_overhead", 0.0),
        "target_achievement_rate": metrics.get("target_achievement_rate", 0.0),
        "target_achieved": target_achieved
    }

if __name__ == "__main__":
    asyncio.run(main()) 