#!/usr/bin/env python3
"""
Pricing & Licensing API Routes
==============================

Comprehensive pricing system for the Iron Cloud platform:
- Freemium API model with tiered pricing
- Enterprise licensing and billing
- Data marketplace functionality
- White-label partner program
- Professional services integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
import json
from enum import Enum
from dataclasses import dataclass, asdict

from core.security import verify_token
from microservices_orchestrator import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency for authentication
async def get_current_user(token: str = Depends(verify_token)):
    return token

class PricingTier(Enum):
    """Pricing tiers for the Iron Cloud platform"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    WHITE_LABEL = "white_label"

class BillingCycle(Enum):
    """Billing cycles for subscriptions"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"

@dataclass
class PricingPlan:
    """Pricing plan configuration"""
    tier: PricingTier
    name: str
    description: str
    monthly_price: float
    annual_price: float
    api_calls_per_month: int
    features: List[str]
    limits: Dict[str, Any]
    sla_guarantee: float
    support_level: str

@dataclass
class EnterpriseLicense:
    """Enterprise licensing configuration"""
    license_id: str
    company_name: str
    tier: PricingTier
    seats: int
    start_date: datetime
    end_date: datetime
    features: List[str]
    custom_limits: Dict[str, Any]
    billing_contact: Dict[str, str]
    technical_contact: Dict[str, str]

@dataclass
class MarketplaceItem:
    """Data marketplace item"""
    item_id: str
    name: str
    description: str
    category: str
    price: float
    currency: str
    data_type: str
    size_mb: int
    quality_score: float
    seller: str
    created_at: datetime
    tags: List[str]

class PricingManager:
    """Manages pricing, licensing, and marketplace operations"""
    
    def __init__(self):
        self.pricing_plans = self._initialize_pricing_plans()
        self.enterprise_licenses = {}
        self.marketplace_items = {}
        self.white_label_partners = {}
    
    def _initialize_pricing_plans(self) -> Dict[str, PricingPlan]:
        """Initialize pricing plans for all tiers"""
        return {
            "free": PricingPlan(
                tier=PricingTier.FREE,
                name="Open Source Community Edition",
                description="Free tier for developers and small projects",
                monthly_price=0.0,
                annual_price=0.0,
                api_calls_per_month=25000,
                features=[
                    "Basic frameworks (Selenium, Playwright)",
                    "Community support",
                    "Self-hosted deployment",
                    "Basic crawling capabilities",
                    "Standard security"
                ],
                limits={
                    "concurrent_requests": 5,
                    "data_retention_days": 30,
                    "export_formats": ["JSON", "CSV"],
                    "support_response_hours": 48
                },
                sla_guarantee=99.5,
                support_level="community"
            ),
            "pro": PricingPlan(
                tier=PricingTier.PRO,
                name="Pro Developer",
                description="Professional tier for developers and small teams",
                monthly_price=49.0,
                annual_price=490.0,
                api_calls_per_month=250000,
                features=[
                    "All frameworks + AI routing",
                    "Email support",
                    "Cloud deployment",
                    "Advanced crawling",
                    "Cost optimization",
                    "Priority processing"
                ],
                limits={
                    "concurrent_requests": 25,
                    "data_retention_days": 90,
                    "export_formats": ["JSON", "CSV", "Excel", "PDF"],
                    "support_response_hours": 24
                },
                sla_guarantee=99.8,
                support_level="email"
            ),
            "enterprise": PricingPlan(
                tier=PricingTier.ENTERPRISE,
                name="Enterprise Professional",
                description="Enterprise-grade solution for large organizations",
                monthly_price=2999.0,
                annual_price=29990.0,
                api_calls_per_month=2500000,
                features=[
                    "Unlimited API calls",
                    "Full AI orchestration suite",
                    "24/7 support + SLA",
                    "On-premise deployment",
                    "Custom integrations",
                    "Professional services",
                    "Advanced security",
                    "Compliance modules"
                ],
                limits={
                    "concurrent_requests": 100,
                    "data_retention_days": 365,
                    "export_formats": ["JSON", "CSV", "Excel", "PDF", "Markdown", "ZIP"],
                    "support_response_hours": 4
                },
                sla_guarantee=99.99,
                support_level="dedicated"
            ),
            "government": PricingPlan(
                tier=PricingTier.GOVERNMENT,
                name="Government & Defense",
                description="Military-grade security for government and defense",
                monthly_price=9999.0,
                annual_price=99990.0,
                api_calls_per_month=10000000,
                features=[
                    "Military-grade security",
                    "Air-gapped deployment",
                    "FIPS 140-2 Level 4 compliance",
                    "Dedicated support team",
                    "Custom development",
                    "Quantum-safe cryptography",
                    "Zero-trust architecture",
                    "Advanced threat protection"
                ],
                limits={
                    "concurrent_requests": 500,
                    "data_retention_days": 2555,
                    "export_formats": ["JSON", "CSV", "Excel", "PDF", "Markdown", "ZIP", "Custom"],
                    "support_response_hours": 1
                },
                sla_guarantee=99.999,
                support_level="dedicated_team"
            ),
            "white_label": PricingPlan(
                tier=PricingTier.WHITE_LABEL,
                name="White Label Partner",
                description="White-label solution for partners and resellers",
                monthly_price=4999.0,
                annual_price=49990.0,
                api_calls_per_month=5000000,
                features=[
                    "White-label branding",
                    "Custom domain support",
                    "Partner dashboard",
                    "Revenue sharing",
                    "Custom integrations",
                    "Dedicated support",
                    "Marketing materials",
                    "Training resources"
                ],
                limits={
                    "concurrent_requests": 200,
                    "data_retention_days": 365,
                    "export_formats": ["JSON", "CSV", "Excel", "PDF", "Markdown", "ZIP"],
                    "support_response_hours": 8
                },
                sla_guarantee=99.95,
                support_level="partner"
            )
        }
    
    async def get_pricing_plans(self) -> Dict[str, Any]:
        """Get all available pricing plans"""
        return {
            "plans": {tier: asdict(plan) for tier, plan in self.pricing_plans.items()},
            "currency": "USD",
            "billing_cycles": [cycle.value for cycle in BillingCycle],
            "features_comparison": self._get_features_comparison(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_features_comparison(self) -> Dict[str, List[str]]:
        """Get feature comparison matrix"""
        return {
            "api_calls": ["25K", "250K", "2.5M", "10M", "5M"],
            "concurrent_requests": ["5", "25", "100", "500", "200"],
            "support_response": ["48h", "24h", "4h", "1h", "8h"],
            "sla_guarantee": ["99.5%", "99.8%", "99.99%", "99.999%", "99.95%"],
            "deployment": ["Self-hosted", "Cloud", "On-premise", "Air-gapped", "White-label"],
            "security": ["Basic", "Advanced", "Enterprise", "Military", "Partner"]
        }
    
    async def calculate_cost(self, tier: str, billing_cycle: str, custom_usage: Optional[Dict] = None) -> Dict[str, Any]:
        """Calculate cost for a specific tier and billing cycle"""
        if tier not in self.pricing_plans:
            raise ValueError(f"Invalid tier: {tier}")
        
        plan = self.pricing_plans[tier]
        
        # Calculate base price
        if billing_cycle == "monthly":
            base_price = plan.monthly_price
        elif billing_cycle == "annually":
            base_price = plan.annual_price
        else:
            base_price = plan.monthly_price
        
        # Calculate custom usage costs
        usage_costs = 0.0
        if custom_usage:
            if custom_usage.get("additional_api_calls", 0) > 0:
                usage_costs += self._calculate_api_usage_cost(tier, custom_usage["additional_api_calls"])
            if custom_usage.get("additional_storage_gb", 0) > 0:
                usage_costs += self._calculate_storage_cost(tier, custom_usage["additional_storage_gb"])
        
        total_cost = base_price + usage_costs
        
        return {
            "tier": tier,
            "billing_cycle": billing_cycle,
            "base_price": base_price,
            "usage_costs": usage_costs,
            "total_cost": total_cost,
            "currency": "USD",
            "savings_vs_competitors": self._calculate_competitor_savings(tier, total_cost),
            "roi_estimate": self._calculate_roi_estimate(tier, total_cost)
        }
    
    def _calculate_api_usage_cost(self, tier: str, additional_calls: int) -> float:
        """Calculate cost for additional API calls"""
        rates = {
            "free": 0.001,  # $0.001 per call
            "pro": 0.0005,  # $0.0005 per call
            "enterprise": 0.0001,  # $0.0001 per call
            "government": 0.00005,  # $0.00005 per call
            "white_label": 0.0002   # $0.0002 per call
        }
        return additional_calls * rates.get(tier, 0.001)
    
    def _calculate_storage_cost(self, tier: str, additional_gb: int) -> float:
        """Calculate cost for additional storage"""
        rates = {
            "free": 0.10,  # $0.10 per GB
            "pro": 0.05,   # $0.05 per GB
            "enterprise": 0.02,  # $0.02 per GB
            "government": 0.01,  # $0.01 per GB
            "white_label": 0.03   # $0.03 per GB
        }
        return additional_gb * rates.get(tier, 0.10)
    
    def _calculate_competitor_savings(self, tier: str, total_cost: float) -> Dict[str, float]:
        """Calculate savings compared to competitors"""
        competitor_costs = {
            "firecrawl": {
                "free": 0,
                "pro": 83,
                "enterprise": 5000,
                "government": 15000,
                "white_label": 8000
            },
            "brightdata": {
                "free": 0,
                "pro": 500,
                "enterprise": 8000,
                "government": 20000,
                "white_label": 12000
            },
            "scrapingbee": {
                "free": 0,
                "pro": 200,
                "enterprise": 3000,
                "government": 10000,
                "white_label": 6000
            }
        }
        
        savings = {}
        for competitor, costs in competitor_costs.items():
            competitor_cost = costs.get(tier, total_cost)
            if competitor_cost > 0:
                savings[competitor] = ((competitor_cost - total_cost) / competitor_cost) * 100
        
        return savings
    
    def _calculate_roi_estimate(self, tier: str, total_cost: float) -> Dict[str, Any]:
        """Calculate ROI estimate for the investment"""
        # Estimated time savings and efficiency gains
        efficiency_gains = {
            "free": {"time_savings_hours": 20, "efficiency_gain": 0.3},
            "pro": {"time_savings_hours": 80, "efficiency_gain": 0.6},
            "enterprise": {"time_savings_hours": 200, "efficiency_gain": 0.8},
            "government": {"time_savings_hours": 500, "efficiency_gain": 0.95},
            "white_label": {"time_savings_hours": 150, "efficiency_gain": 0.7}
        }
        
        gains = efficiency_gains.get(tier, {"time_savings_hours": 0, "efficiency_gain": 0})
        
        # Calculate ROI based on average developer hourly rate
        developer_hourly_rate = 100  # Average developer rate
        time_savings_value = gains["time_savings_hours"] * developer_hourly_rate
        efficiency_value = total_cost * gains["efficiency_gain"]
        
        total_value = time_savings_value + efficiency_value
        roi_percentage = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            "time_savings_hours": gains["time_savings_hours"],
            "time_savings_value": time_savings_value,
            "efficiency_gain": gains["efficiency_gain"],
            "efficiency_value": efficiency_value,
            "total_value": total_value,
            "roi_percentage": roi_percentage,
            "payback_period_months": total_cost / (time_savings_value / 12) if time_savings_value > 0 else 0
        }

class MarketplaceManager:
    """Manages data marketplace operations"""
    
    def __init__(self):
        self.items = {}
        self.categories = [
            "business_intelligence",
            "financial_data",
            "ecommerce_data",
            "social_media_data",
            "news_data",
            "research_data",
            "compliance_data",
            "custom_datasets"
        ]
    
    async def add_marketplace_item(self, item_data: Dict[str, Any]) -> str:
        """Add a new item to the marketplace"""
        item_id = f"item_{len(self.items) + 1}_{int(datetime.now().timestamp())}"
        
        item = MarketplaceItem(
            item_id=item_id,
            name=item_data["name"],
            description=item_data["description"],
            category=item_data["category"],
            price=item_data["price"],
            currency=item_data.get("currency", "USD"),
            data_type=item_data["data_type"],
            size_mb=item_data["size_mb"],
            quality_score=item_data.get("quality_score", 0.8),
            seller=item_data["seller"],
            created_at=datetime.now(),
            tags=item_data.get("tags", [])
        )
        
        self.items[item_id] = item
        return item_id
    
    async def get_marketplace_items(self, category: Optional[str] = None, 
                                  min_quality: Optional[float] = None,
                                  max_price: Optional[float] = None) -> Dict[str, Any]:
        """Get marketplace items with optional filtering"""
        items = list(self.items.values())
        
        if category:
            items = [item for item in items if item.category == category]
        
        if min_quality:
            items = [item for item in items if item.quality_score >= min_quality]
        
        if max_price:
            items = [item for item in items if item.price <= max_price]
        
        return {
            "items": [asdict(item) for item in items],
            "total_count": len(items),
            "categories": self.categories,
            "timestamp": datetime.now().isoformat()
        }

class WhiteLabelManager:
    """Manages white-label partner program"""
    
    def __init__(self):
        self.partners = {}
        self.revenue_sharing_rates = {
            "silver": 0.15,  # 15% revenue share
            "gold": 0.20,    # 20% revenue share
            "platinum": 0.25  # 25% revenue share
        }
    
    async def register_partner(self, partner_data: Dict[str, Any]) -> str:
        """Register a new white-label partner"""
        partner_id = f"partner_{len(self.partners) + 1}_{int(datetime.now().timestamp())}"
        
        partner = {
            "partner_id": partner_id,
            "company_name": partner_data["company_name"],
            "contact_email": partner_data["contact_email"],
            "tier": partner_data.get("tier", "silver"),
            "custom_domain": partner_data.get("custom_domain"),
            "branding": partner_data.get("branding", {}),
            "revenue_share": self.revenue_sharing_rates.get(partner_data.get("tier", "silver"), 0.15),
            "registered_at": datetime.now(),
            "status": "active"
        }
        
        self.partners[partner_id] = partner
        return partner_id
    
    async def get_partner_info(self, partner_id: str) -> Dict[str, Any]:
        """Get partner information and statistics"""
        if partner_id not in self.partners:
            raise ValueError(f"Partner not found: {partner_id}")
        
        partner = self.partners[partner_id]
        
        # Mock statistics for demonstration
        stats = {
            "total_revenue": 15000.0,
            "revenue_share_earned": partner["revenue_share"] * 15000.0,
            "active_customers": 25,
            "total_api_calls": 1500000,
            "customer_satisfaction": 4.8
        }
        
        return {
            "partner": partner,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

# Initialize managers
pricing_manager = PricingManager()
marketplace_manager = MarketplaceManager()
white_label_manager = WhiteLabelManager()

@router.get("/pricing-plans")
async def get_pricing_plans():
    """Get all available pricing plans"""
    return await pricing_manager.get_pricing_plans()

@router.post("/calculate-cost")
async def calculate_cost(request_data: Dict[str, Any]):
    """Calculate cost for a specific tier and billing cycle"""
    return await pricing_manager.calculate_cost(
        tier=request_data["tier"],
        billing_cycle=request_data["billing_cycle"],
        custom_usage=request_data.get("custom_usage")
    )

@router.get("/marketplace")
async def get_marketplace_items(
    category: Optional[str] = None,
    min_quality: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get marketplace items with optional filtering"""
    return await marketplace_manager.get_marketplace_items(
        category=category,
        min_quality=min_quality,
        max_price=max_price
    )

@router.post("/marketplace/add")
async def add_marketplace_item(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Add a new item to the marketplace"""
    item_id = await marketplace_manager.add_marketplace_item(request_data)
    return {"item_id": item_id, "status": "success"}

@router.post("/white-label/register")
async def register_white_label_partner(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Register a new white-label partner"""
    partner_id = await white_label_manager.register_partner(request_data)
    return {"partner_id": partner_id, "status": "success"}

@router.get("/white-label/{partner_id}")
async def get_partner_info(
    partner_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get partner information and statistics"""
    return await white_label_manager.get_partner_info(partner_id)

@router.get("/competitor-analysis")
async def get_competitor_analysis():
    """Get competitive analysis and pricing comparison"""
    return {
        "competitors": {
            "firecrawl": {
                "pro_tier_price": 83,
                "enterprise_tier_price": 5000,
                "features": ["Basic crawling", "API access", "Cloud deployment"],
                "limitations": ["No AI optimization", "Limited security", "No white-label"]
            },
            "brightdata": {
                "pro_tier_price": 500,
                "enterprise_tier_price": 8000,
                "features": ["Proxy network", "Data center", "Residential IPs"],
                "limitations": ["No AI integration", "Complex pricing", "Limited automation"]
            },
            "scrapingbee": {
                "pro_tier_price": 200,
                "enterprise_tier_price": 3000,
                "features": ["Simple API", "JavaScript rendering", "Geolocation"],
                "limitations": ["No AI features", "Basic security", "Limited scalability"]
            }
        },
        "our_advantages": [
            "100% cost optimization through AI routing",
            "Military-grade security with quantum-safe cryptography",
            "Autonomous operation with self-healing capabilities",
            "White-label solutions for partners",
            "Professional services and consulting",
            "Advanced compliance and audit features"
        ],
        "cost_savings": {
            "vs_firecrawl": "40-60%",
            "vs_brightdata": "50-70%",
            "vs_scrapingbee": "30-50%"
        },
        "timestamp": datetime.now().isoformat()
    } 