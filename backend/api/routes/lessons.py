from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.security import verify_token
from models.lesson import Lesson
from schemas.lesson import LessonCreate, LessonResponse, LessonUpdate

router = APIRouter()

@router.get("/", response_model=List[LessonResponse])
async def get_lessons(
    course_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all lessons, optionally filtered by course"""
    query = db.query(Lesson)
    if course_id:
        query = query.filter(Lesson.course_id == course_id)
    
    lessons = query.offset(skip).limit(limit).all()
    return [LessonResponse.from_orm(lesson) for lesson in lessons]

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lesson by ID"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    return LessonResponse.from_orm(lesson)

@router.post("/", response_model=LessonResponse)
async def create_lesson(
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create a new lesson"""
    lesson = Lesson(**lesson_data.dict())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return LessonResponse.from_orm(lesson)

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Update a lesson"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    for field, value in lesson_data.dict(exclude_unset=True).items():
        setattr(lesson, field, value)
    
    db.commit()
    db.refresh(lesson)
    return LessonResponse.from_orm(lesson)

@router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Delete a lesson"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"} 