from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from core.database import get_db
from core.security import verify_token
from models.user import User
from models.course import Course
from models.lesson import Lesson
from models.progress import Progress

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get dashboard analytics for the current user"""
    user_id = current_user.get("sub")
    
    # Get user's total progress
    total_lessons = db.query(Lesson).count()
    completed_lessons = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.completed == True
    ).count()
    
    # Get course progress
    course_progress = db.query(
        Course.title,
        func.count(Progress.id).label('completed_lessons'),
        func.count(Lesson.id).label('total_lessons')
    ).join(Lesson, Course.id == Lesson.course_id)\
     .outerjoin(Progress, (Progress.lesson_id == Lesson.id) & (Progress.user_id == user_id) & (Progress.completed == True))\
     .group_by(Course.id, Course.title)\
     .all()
    
    # Get recent activity
    recent_progress = db.query(Progress)\
        .filter(Progress.user_id == user_id)\
        .order_by(desc(Progress.updated_at))\
        .limit(5)\
        .all()
    
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_rate": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
        "course_progress": [
            {
                "course_title": cp.title,
                "completed_lessons": cp.completed_lessons,
                "total_lessons": cp.total_lessons,
                "progress_percentage": (cp.completed_lessons / cp.total_lessons * 100) if cp.total_lessons > 0 else 0
            }
            for cp in course_progress
        ],
        "recent_activity": [
            {
                "lesson_id": rp.lesson_id,
                "completed": rp.completed,
                "updated_at": rp.updated_at.isoformat()
            }
            for rp in recent_progress
        ]
    }

@router.get("/course/{course_id}")
async def get_course_analytics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get analytics for a specific course"""
    user_id = current_user.get("sub")
    
    # Get course details
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get lesson progress for this course
    lesson_progress = db.query(
        Lesson.title,
        Lesson.duration,
        Progress.completed,
        Progress.watched_duration,
        Progress.updated_at
    ).join(Progress, (Progress.lesson_id == Lesson.id) & (Progress.user_id == user_id))\
     .filter(Lesson.course_id == course_id)\
     .all()
    
    total_duration = sum(lp.duration for lp in lesson_progress)
    watched_duration = sum(lp.watched_duration for lp in lesson_progress if lp.watched_duration)
    completed_lessons = sum(1 for lp in lesson_progress if lp.completed)
    
    return {
        "course_title": course.title,
        "total_lessons": len(lesson_progress),
        "completed_lessons": completed_lessons,
        "completion_rate": (completed_lessons / len(lesson_progress) * 100) if lesson_progress else 0,
        "total_duration": total_duration,
        "watched_duration": watched_duration,
        "watch_percentage": (watched_duration / total_duration * 100) if total_duration > 0 else 0,
        "lesson_details": [
            {
                "title": lp.title,
                "duration": lp.duration,
                "completed": lp.completed,
                "watched_duration": lp.watched_duration,
                "updated_at": lp.updated_at.isoformat() if lp.updated_at else None
            }
            for lp in lesson_progress
        ]
    }

@router.get("/global")
async def get_global_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get global analytics (admin only)"""
    # Check if user is admin (you can implement your own admin check)
    user_id = current_user.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get total users
    total_users = db.query(User).count()
    
    # Get total courses
    total_courses = db.query(Course).count()
    
    # Get total lessons
    total_lessons = db.query(Lesson).count()
    
    # Get total progress entries
    total_progress = db.query(Progress).count()
    
    # Get completion statistics
    completed_lessons = db.query(Progress).filter(Progress.completed == True).count()
    
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "total_progress_entries": total_progress,
        "completed_lessons": completed_lessons,
        "global_completion_rate": (completed_lessons / total_progress * 100) if total_progress > 0 else 0
    } 