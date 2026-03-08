from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ProgressBase(BaseModel):
    user_id: int
    course_id: int
    lesson_id: Optional[int] = None
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0)
    time_spent: int = Field(0, ge=0)  # Time spent in seconds
    notes: Optional[str] = None

class ProgressCreate(ProgressBase):
    pass

class ProgressUpdate(BaseModel):
    status: Optional[ProgressStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class ProgressResponse(ProgressBase):
    id: int
    last_accessed: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProgressDetail(ProgressResponse):
    course_title: str
    lesson_title: Optional[str] = None
    course_progress: float = 0.0
    total_lessons: int = 0
    completed_lessons: int = 0

class UserProgress(BaseModel):
    user_id: int
    total_courses_enrolled: int = 0
    total_courses_completed: int = 0
    total_lessons_completed: int = 0
    total_time_spent: int = 0  # in seconds
    average_progress: float = 0.0
    recent_activity: List[Dict[str, Any]] = []

class CourseProgress(BaseModel):
    course_id: int
    course_title: str
    total_lessons: int = 0
    completed_lessons: int = 0
    progress_percentage: float = 0.0
    time_spent: int = 0  # in seconds
    last_accessed: Optional[datetime] = None
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    lessons_progress: List[Dict[str, Any]] = []

class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int
    payment_status: str = "pending"
    payment_amount: float = Field(0.0, ge=0.0)
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    payment_status: Optional[str] = None
    payment_amount: Optional[float] = Field(None, ge=0.0)
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    certificate_issued: Optional[bool] = None

class EnrollmentResponse(EnrollmentBase):
    id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    certificate_issued: bool = False
    certificate_issued_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EnrollmentDetail(EnrollmentResponse):
    course_title: str
    course_thumbnail: Optional[str] = None
    instructor_name: str
    progress_percentage: float = 0.0
    total_lessons: int = 0
    completed_lessons: int = 0

class ReviewBase(BaseModel):
    user_id: int
    course_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: int
    is_verified: bool = False
    is_helpful: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ReviewDetail(ReviewResponse):
    user_name: str
    user_avatar: Optional[str] = None
    course_title: str
    course_thumbnail: Optional[str] = None

class CertificateBase(BaseModel):
    user_id: int
    course_id: int
    certificate_number: str
    expires_at: Optional[datetime] = None
    certificate_url: Optional[str] = None

class CertificateCreate(CertificateBase):
    pass

class CertificateUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    certificate_url: Optional[str] = None
    is_valid: Optional[bool] = None

class CertificateResponse(CertificateBase):
    id: int
    issued_at: datetime
    is_valid: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CertificateDetail(CertificateResponse):
    user_name: str
    course_title: str
    instructor_name: str
    completion_date: datetime
    course_duration: int = 0  # in minutes

class LearningStats(BaseModel):
    user_id: int
    total_courses: int = 0
    completed_courses: int = 0
    in_progress_courses: int = 0
    total_lessons: int = 0
    completed_lessons: int = 0
    total_time_spent: int = 0  # in seconds
    certificates_earned: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    streak_days: int = 0
    weekly_goal_progress: float = 0.0

class ActivityLog(BaseModel):
    id: int
    user_id: int
    activity_type: str  # lesson_started, lesson_completed, course_enrolled, etc.
    entity_type: str  # course, lesson, quiz, exercise
    entity_id: int
    description: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 