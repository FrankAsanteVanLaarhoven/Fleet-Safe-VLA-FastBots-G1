"""
Changelog API routes for Aura Design Tool
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from ..models.changelog import ChangelogEntry, ChangelogResponse
from ..services.changelog_service import ChangelogService
from ..core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/", response_model=List[ChangelogResponse])
async def get_changelog(
    version: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get changelog entries"""
    service = ChangelogService(db)
    return await service.get_changelog(version=version, limit=limit)

@router.get("/latest", response_model=ChangelogResponse)
async def get_latest_release(db: Session = Depends(get_db)):
    """Get the latest release"""
    service = ChangelogService(db)
    return await service.get_latest_release()

@router.get("/version/{version}", response_model=ChangelogResponse)
async def get_version(version: str, db: Session = Depends(get_db)):
    """Get a specific version"""
    service = ChangelogService(db)
    entry = await service.get_version(version)
    if not entry:
        raise HTTPException(status_code=404, detail="Version not found")
    return entry

@router.post("/", response_model=ChangelogResponse)
async def create_changelog_entry(
    entry: ChangelogEntry,
    db: Session = Depends(get_db)
):
    """Create a new changelog entry"""
    service = ChangelogService(db)
    return await service.create_entry(entry) 