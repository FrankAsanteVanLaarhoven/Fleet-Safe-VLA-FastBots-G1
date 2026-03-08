"""
Designs API routes for Aura Design Tool
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import verify_token
from ..models.design import Design, DesignCreate, DesignUpdate
from ..services.design_service import DesignService

router = APIRouter()

@router.get("/", response_model=List[Design])
async def get_designs(
    current_user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user's designs"""
    design_service = DesignService(db)
    return design_service.get_user_designs(current_user_id)

@router.post("/", response_model=Design)
async def create_design(
    design: DesignCreate,
    current_user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new design"""
    design_service = DesignService(db)
    return design_service.create_design(current_user_id, design)

@router.get("/{design_id}", response_model=Design)
async def get_design(
    design_id: str,
    current_user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific design"""
    design_service = DesignService(db)
    design = design_service.get_design(design_id, current_user_id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design 