from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=255)
    bio: Optional[str] = None
    website: Optional[HttpUrl] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    bio: Optional[str] = None
    website: Optional[HttpUrl] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_admin: bool
    role: UserRole
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    total_courses_enrolled: int = 0
    total_courses_completed: int = 0
    total_certificates: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    learning_time_hours: float = 0.0

class UserStats(BaseModel):
    user_id: int
    total_courses: int
    completed_courses: int
    in_progress_courses: int
    total_lessons: int
    completed_lessons: int
    total_time_spent: int  # in seconds
    certificates_earned: int
    average_rating: float
    total_reviews: int

class UserPreferences(BaseModel):
    theme: str = "system"  # light, dark, system
    language: str = "en"
    email_notifications: bool = True
    push_notifications: bool = True
    marketing_emails: bool = False
    course_recommendations: bool = True
    accessibility_features: Dict[str, bool] = {}

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

class UserSearch(BaseModel):
    query: str = Field(..., min_length=1)
    role: Optional[UserRole] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    limit: int = 20
    offset: int = 0 