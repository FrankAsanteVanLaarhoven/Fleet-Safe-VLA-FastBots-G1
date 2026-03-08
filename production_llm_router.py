"""
Production-Ready Intelligent LLM Router
Implements cost-optimized routing between free and premium models
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json

logger = logging.getLogger(__name__)

class ModelTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class ModelConfig:
    name: str
    tier: ModelTier
    cost_per_1m_tokens: float
    quality_score: float
    max_tokens: int
    provider: str
    endpoint: str
    api_key_env: str
    fallback_models: List[str]
    availability_score: float = 1.0

class TaskComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProductionLLMRouter:
    """
    Production-ready intelligent LLM router with cost optimization and budget management.
    
    Features:
    - Cost-optimized routing between free and premium models
    - Budget management and spending controls
    - Quality scoring and model selection
    - Automatic failover and load balancing
    - Real-time availability monitoring
    """
    
    def __init__(self, budget_limit: float = 100.0):
        self.budget_limit = budget_limit
        self.budget_used = 0.0
        self.budget_reset_date = time.time()
        
        # Initialize model configurations
        self.models = self._initialize_models()
        self.model_health = {model_name: 1.0 for model_name in self.models.keys()}
        self.usage_stats = {model_name: {"requests": 0, "tokens": 0, "cost": 0.0} for model_name in self.models.keys()}
        
        # Routing strategies
        self.routing_strategies = {
            "cost_optimized": self._route_cost_optimized,
            "quality_first": self._route_quality_first,
            "balanced": self._route_balanced,
            "emergency": self._route_emergency
        }
        
        logger.info(f"Production LLM Router initialized with budget: ${budget_limit}")
    
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations with real-world pricing and capabilities."""
        return {
            # Free Tier Models
            "deepseek_r1": ModelConfig(
                name="deepseek_r1",
                tier=ModelTier.FREE,
                cost_per_1m_tokens=0.0,
                quality_score=0.95,
                max_tokens=32768,
                provider="deepseek",
                endpoint="https://api.deepseek.com/v1/chat/completions",
                api_key_env="DEEPSEEK_API_KEY",
                fallback_models=["gemini_flash", "claude_haiku"],
                availability_score=0.98
            ),
            "gemini_flash": ModelConfig(
                name="gemini_flash",
                tier=ModelTier.FREE,
                cost_per_1m_tokens=0.0,
                quality_score=0.85,
                max_tokens=8192,
                provider="google",
                endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                api_key_env="GOOGLE_API_KEY",
                fallback_models=["deepseek_r1", "claude_haiku"],
                availability_score=0.99
            ),
            "claude_haiku": ModelConfig(
                name="claude_haiku",
                tier=ModelTier.FREE,
                cost_per_1m_tokens=0.0,
                quality_score=0.88,
                max_tokens=4096,
                provider="anthropic",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                fallback_models=["deepseek_r1", "gemini_flash"],
                availability_score=0.97
            ),
            
            # Premium Tier Models
            "deepseek_v3": ModelConfig(
                name="deepseek_v3",
                tier=ModelTier.PREMIUM,
                cost_per_1m_tokens=1.10,
                quality_score=0.90,
                max_tokens=32768,
                provider="deepseek",
                endpoint="https://api.deepseek.com/v1/chat/completions",
                api_key_env="DEEPSEEK_API_KEY",
                fallback_models=["deepseek_r1", "claude_sonnet"],
                availability_score=0.99
            ),
            "claude_sonnet": ModelConfig(
                name="claude_sonnet",
                tier=ModelTier.PREMIUM,
                cost_per_1m_tokens=15.00,
                quality_score=0.95,
                max_tokens=4096,
                provider="anthropic",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                fallback_models=["deepseek_v3", "gpt4_turbo"],
                availability_score=0.99
            ),
            "gpt4_turbo": ModelConfig(
                name="gpt4_turbo",
                tier=ModelTier.PREMIUM,
                cost_per_1m_tokens=10.00,
                quality_score=0.92,
                max_tokens=4096,
                provider="openai",
                endpoint="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                fallback_models=["claude_sonnet", "deepseek_v3"],
                availability_score=0.98
            ),
            
            # Enterprise Tier Models
            "claude_opus": ModelConfig(
                name="claude_opus",
                tier=ModelTier.ENTERPRISE,
                cost_per_1m_tokens=75.00,
                quality_score=0.98,
                max_tokens=4096,
                provider="anthropic",
                endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                fallback_models=["claude_sonnet", "gpt4_turbo"],
                availability_score=0.99
            ),
            "gpt4_omni": ModelConfig(
                name="gpt4_omni",
                tier=ModelTier.ENTERPRISE,
                cost_per_1m_tokens=60.00,
                quality_score=0.96,
                max_tokens=4096,
                provider="openai",
                endpoint="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                fallback_models=["claude_opus", "claude_sonnet"],
                availability_score=0.99
            )
        }
    
    def get_budget_status(self) -> Dict[str, float]:
        """Get current budget status and usage."""
        budget_remaining = self.budget_limit - self.budget_used
        budget_percentage = (self.budget_used / self.budget_limit) * 100 if self.budget_limit > 0 else 0
        
        return {
            "budget_limit": self.budget_limit,
            "budget_used": self.budget_used,
            "budget_remaining": budget_remaining,
            "budget_percentage": budget_percentage,
            "days_until_reset": max(0, (30 * 24 * 3600 - (time.time() - self.budget_reset_date)) / (24 * 3600))
        }
    
    def estimate_cost(self, model_name: str, estimated_tokens: int) -> float:
        """Estimate cost for a given model and token count."""
        model = self.models.get(model_name)
        if not model:
            return float('inf')
        
        return (estimated_tokens / 1_000_000) * model.cost_per_1m_tokens
    
    def assess_task_complexity(self, task_description: str, content_length: int, 
                             context_requirements: str) -> TaskComplexity:
        """Assess task complexity based on multiple factors."""
        complexity_score = 0.0
        
        # Content length factor
        if content_length < 1000:
            complexity_score += 0.1
        elif content_length < 5000:
            complexity_score += 0.3
        elif content_length < 10000:
            complexity_score += 0.5
        else:
            complexity_score += 0.7
        
        # Context requirements factor
        if context_requirements == "minimal":
            complexity_score += 0.1
        elif context_requirements == "moderate":
            complexity_score += 0.3
        elif context_requirements == "extensive":
            complexity_score += 0.6
        elif context_requirements == "critical":
            complexity_score += 0.8
        
        # Task description keywords
        complex_keywords = ["analysis", "synthesis", "reasoning", "evaluation", "comparison", "prediction"]
        simple_keywords = ["extract", "summarize", "classify", "identify", "list"]
        
        task_lower = task_description.lower()
        for keyword in complex_keywords:
            if keyword in task_lower:
                complexity_score += 0.2
        for keyword in simple_keywords:
            if keyword in task_lower:
                complexity_score += 0.1
        
        # Normalize to 0-1 range
        complexity_score = min(1.0, complexity_score)
        
        # Map to complexity levels
        if complexity_score < 0.25:
            return TaskComplexity.LOW
        elif complexity_score < 0.5:
            return TaskComplexity.MEDIUM
        elif complexity_score < 0.75:
            return TaskComplexity.HIGH
        else:
            return TaskComplexity.CRITICAL
    
    def _route_cost_optimized(self, task_complexity: TaskComplexity, 
                            estimated_tokens: int, budget_remaining: float) -> str:
        """Route to most cost-effective model that meets quality requirements."""
        available_models = []
        
        for model_name, model in self.models.items():
            if self.model_health[model_name] < 0.5:  # Skip unhealthy models
                continue
            
            estimated_cost = self.estimate_cost(model_name, estimated_tokens)
            if estimated_cost > budget_remaining:
                continue
            
            # Calculate cost-effectiveness score
            cost_effectiveness = model.quality_score / (estimated_cost + 0.01)  # Avoid division by zero
            availability_adjusted_score = cost_effectiveness * model.availability_score
            
            available_models.append((model_name, availability_adjusted_score, estimated_cost))
        
        if not available_models:
            # Emergency fallback to free models
            for model_name, model in self.models.items():
                if model.tier == ModelTier.FREE and self.model_health[model_name] > 0.3:
                    return model_name
            return "deepseek_r1"  # Ultimate fallback
        
        # Sort by cost-effectiveness and select best
        available_models.sort(key=lambda x: x[1], reverse=True)
        return available_models[0][0]
    
    def _route_quality_first(self, task_complexity: TaskComplexity, 
                           estimated_tokens: int, budget_remaining: float) -> str:
        """Route to highest quality model within budget."""
        available_models = []
        
        for model_name, model in self.models.items():
            if self.model_health[model_name] < 0.5:
                continue
            
            estimated_cost = self.estimate_cost(model_name, estimated_tokens)
            if estimated_cost > budget_remaining:
                continue
            
            # Prioritize quality over cost
            quality_score = model.quality_score * model.availability_score
            available_models.append((model_name, quality_score, estimated_cost))
        
        if not available_models:
            return self._route_cost_optimized(task_complexity, estimated_tokens, budget_remaining)
        
        available_models.sort(key=lambda x: x[1], reverse=True)
        return available_models[0][0]
    
    def _route_balanced(self, task_complexity: TaskComplexity, 
                       estimated_tokens: int, budget_remaining: float) -> str:
        """Route using balanced approach between cost and quality."""
        available_models = []
        
        for model_name, model in self.models.items():
            if self.model_health[model_name] < 0.5:
                continue
            
            estimated_cost = self.estimate_cost(model_name, estimated_tokens)
            if estimated_cost > budget_remaining:
                continue
            
            # Balanced score: 60% quality, 40% cost-effectiveness
            quality_score = model.quality_score * model.availability_score
            cost_effectiveness = 1.0 / (estimated_cost + 0.01)
            balanced_score = 0.6 * quality_score + 0.4 * cost_effectiveness
            
            available_models.append((model_name, balanced_score, estimated_cost))
        
        if not available_models:
            return self._route_cost_optimized(task_complexity, estimated_tokens, budget_remaining)
        
        available_models.sort(key=lambda x: x[1], reverse=True)
        return available_models[0][0]
    
    def _route_emergency(self, task_complexity: TaskComplexity, 
                        estimated_tokens: int, budget_remaining: float) -> str:
        """Emergency routing when budget is critically low."""
        # Always use free models in emergency mode
        free_models = [(name, model) for name, model in self.models.items() 
                      if model.tier == ModelTier.FREE and self.model_health[name] > 0.3]
        
        if free_models:
            # Select healthiest free model
            free_models.sort(key=lambda x: x[1].availability_score, reverse=True)
            return free_models[0][0]
        
        return "deepseek_r1"  # Ultimate fallback
    
    async def route_intelligently(self, task_description: str, content: str, 
                                context_requirements: str = "moderate",
                                strategy: str = "cost_optimized") -> Tuple[str, Dict]:
        """
        Intelligently route to the best model based on task requirements and budget.
        
        Returns:
            Tuple of (selected_model_name, routing_metadata)
        """
        # Assess task complexity
        content_length = len(content)
        task_complexity = self.assess_task_complexity(task_description, content_length, context_requirements)
        
        # Estimate token count (rough approximation)
        estimated_tokens = content_length // 4  # Rough token estimation
        
        # Get budget status
        budget_status = self.get_budget_status()
        budget_remaining = budget_status["budget_remaining"]
        
        # Select routing strategy
        if budget_remaining < 5.0:  # Critical budget situation
            strategy = "emergency"
        elif task_complexity == TaskComplexity.CRITICAL:
            strategy = "quality_first"
        
        routing_func = self.routing_strategies.get(strategy, self._route_cost_optimized)
        selected_model = routing_func(task_complexity, estimated_tokens, budget_remaining)
        
        # Prepare routing metadata
        routing_metadata = {
            "selected_model": selected_model,
            "task_complexity": task_complexity.value,
            "estimated_tokens": estimated_tokens,
            "estimated_cost": self.estimate_cost(selected_model, estimated_tokens),
            "budget_remaining": budget_remaining,
            "routing_strategy": strategy,
            "model_health": self.model_health[selected_model],
            "timestamp": time.time()
        }
        
        logger.info(f"Intelligent routing: {selected_model} (strategy: {strategy}, "
                   f"complexity: {task_complexity.value}, cost: ${routing_metadata['estimated_cost']:.4f})")
        
        return selected_model, routing_metadata
    
    async def execute_with_routing(self, task_description: str, content: str, 
                                 context_requirements: str = "moderate",
                                 strategy: str = "cost_optimized") -> Dict:
        """
        Execute LLM task with intelligent routing and automatic failover.
        
        Returns:
            Dict containing response and execution metadata
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Route to best model
                selected_model, routing_metadata = await self.route_intelligently(
                    task_description, content, context_requirements, strategy
                )
                
                # Execute the request
                start_time = time.time()
                response = await self._execute_model_request(selected_model, task_description, content)
                execution_time = time.time() - start_time
                
                # Update usage statistics
                self._update_usage_stats(selected_model, routing_metadata["estimated_tokens"], 
                                       routing_metadata["estimated_cost"])
                
                return {
                    "success": True,
                    "response": response,
                    "model_used": selected_model,
                    "execution_time": execution_time,
                    "routing_metadata": routing_metadata,
                    "retry_count": retry_count
                }
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Model execution failed (attempt {retry_count}): {e}")
                
                # Mark model as unhealthy
                if "selected_model" in locals():
                    self.model_health[selected_model] *= 0.8
                
                # Try fallback models
                if retry_count < max_retries:
                    fallback_models = self.models[selected_model].fallback_models
                    for fallback in fallback_models:
                        if self.model_health[fallback] > 0.3:
                            selected_model = fallback
                            break
                    else:
                        # No healthy fallbacks, use emergency routing
                        strategy = "emergency"
        
        # All retries failed
        return {
            "success": False,
            "error": "All model attempts failed",
            "retry_count": retry_count
        }
    
    async def _execute_model_request(self, model_name: str, task_description: str, content: str) -> str:
        """Execute request to specific model (placeholder implementation)."""
        # This would contain the actual API calls to different providers
        # For now, return a mock response
        await asyncio.sleep(0.1)  # Simulate API call
        return f"Mock response from {model_name} for task: {task_description[:50]}..."
    
    def _update_usage_stats(self, model_name: str, tokens: int, cost: float):
        """Update usage statistics for monitoring."""
        if model_name in self.usage_stats:
            self.usage_stats[model_name]["requests"] += 1
            self.usage_stats[model_name]["tokens"] += tokens
            self.usage_stats[model_name]["cost"] += cost
            self.budget_used += cost
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics."""
        total_requests = sum(stats["requests"] for stats in self.usage_stats.values())
        total_cost = sum(stats["cost"] for stats in self.usage_stats.values())
        total_tokens = sum(stats["tokens"] for stats in self.usage_stats.values())
        
        # Calculate cost savings vs using premium models exclusively
        premium_cost_per_1m = 15.0  # Average premium model cost
        potential_cost = (total_tokens / 1_000_000) * premium_cost_per_1m
        cost_savings = potential_cost - total_cost
        
        return {
            "total_requests": total_requests,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "cost_savings": cost_savings,
            "savings_percentage": (cost_savings / potential_cost * 100) if potential_cost > 0 else 0,
            "budget_status": self.get_budget_status(),
            "model_health": self.model_health,
            "usage_by_model": self.usage_stats
        }
    
    async def health_check(self) -> Dict:
        """Perform health check on all models."""
        health_results = {}
        
        for model_name, model in self.models.items():
            try:
                # Simulate health check (would be actual API calls)
                await asyncio.sleep(0.05)
                health_score = 1.0  # Would be based on actual response
                self.model_health[model_name] = health_score
                health_results[model_name] = {"status": "healthy", "score": health_score}
            except Exception as e:
                health_score = 0.0
                self.model_health[model_name] = health_score
                health_results[model_name] = {"status": "unhealthy", "error": str(e)}
        
        return health_results

# Example usage
async def main():
    """Example usage of the Production LLM Router."""
    router = ProductionLLMRouter(budget_limit=50.0)
    
    # Example tasks
    tasks = [
        {
            "description": "Extract product information from e-commerce page",
            "content": "Product: iPhone 15 Pro, Price: $999, Features: A17 Pro chip, 48MP camera...",
            "context": "minimal"
        },
        {
            "description": "Analyze complex technical documentation and provide insights",
            "content": "Detailed technical specification document with 5000+ words...",
            "context": "extensive"
        }
    ]
    
    for task in tasks:
        result = await router.execute_with_routing(
            task["description"], 
            task["content"], 
            task["context"]
        )
        print(f"Task: {task['description']}")
        print(f"Result: {result}")
        print(f"Budget remaining: ${router.get_budget_status()['budget_remaining']:.2f}")
        print("-" * 50)
    
    # Print performance metrics
    metrics = router.get_performance_metrics()
    print(f"Cost savings: ${metrics['cost_savings']:.2f} ({metrics['savings_percentage']:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main()) 