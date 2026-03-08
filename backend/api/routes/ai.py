"""
AI API routes for Aura Design Tool
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import verify_token
from ..models.ai import AISuggestion, AIGenerationRequest
from ..services.ai_service import AIService

router = APIRouter()

@router.post("/suggestions", response_model=List[AISuggestion])
async def get_ai_suggestions(
    request: AIGenerationRequest,
    current_user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get AI-powered design suggestions"""
    ai_service = AIService(db)
    return ai_service.generate_suggestions(request)

@router.post("/generate-image")
async def generate_image(
    prompt: str,
    current_user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Generate an image using AI"""
    ai_service = AIService(db)
    return ai_service.generate_image(prompt)

@router.post("/optimize-design")
async def optimize_design(
    design_data: dict,
    current_user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Optimize a design using AI"""
    ai_service = AIService(db)
    return ai_service.optimize_design(design_data) 