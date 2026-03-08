from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.security import verify_token
from models.progress import Progress
from schemas.progress import ProgressCreate, ProgressResponse, ProgressUpdate

router = APIRouter()

@router.get("/", response_model=List[ProgressResponse])
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get progress for the current user"""
    user_id = current_user.get("sub")
    progress = db.query(Progress).filter(Progress.user_id == user_id).all()
    return [ProgressResponse.from_orm(p) for p in progress]

@router.get("/course/{course_id}", response_model=ProgressResponse)
async def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get progress for a specific course"""
    user_id = current_user.get("sub")
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.course_id == course_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this course"
        )
    
    return ProgressResponse.from_orm(progress)

@router.post("/", response_model=ProgressResponse)
async def create_progress(
    progress_data: ProgressCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create or update progress for a lesson"""
    user_id = current_user.get("sub")
    
    # Check if progress already exists
    existing_progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.lesson_id == progress_data.lesson_id
    ).first()
    
    if existing_progress:
        # Update existing progress
        for field, value in progress_data.dict(exclude_unset=True).items():
            setattr(existing_progress, field, value)
        db.commit()
        db.refresh(existing_progress)
        return ProgressResponse.from_orm(existing_progress)
    else:
        # Create new progress
        progress = Progress(
            user_id=user_id,
            **progress_data.dict()
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return ProgressResponse.from_orm(progress)

@router.put("/{progress_id}", response_model=ProgressResponse)
async def update_progress(
    progress_id: int,
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Update progress"""
    user_id = current_user.get("sub")
    progress = db.query(Progress).filter(
        Progress.id == progress_id,
        Progress.user_id == user_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found"
        )
    
    for field, value in progress_data.dict(exclude_unset=True).items():
        setattr(progress, field, value)
    
    db.commit()
    db.refresh(progress)
    return ProgressResponse.from_orm(progress)

@router.delete("/{progress_id}")
async def delete_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Delete progress"""
    user_id = current_user.get("sub")
    progress = db.query(Progress).filter(
        Progress.id == progress_id,
        Progress.user_id == user_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found"
        )
    
    db.delete(progress)
    db.commit()
    return {"message": "Progress deleted successfully"} 