from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    duration_minutes: int = Field(0, ge=0)
    lesson_count: int = Field(0, ge=0)
    price: float = Field(0.0, ge=0.0)
    original_price: float = Field(0.0, ge=0.0)
    is_free: bool = False
    is_featured: bool = False
    is_popular: bool = False
    level: CourseLevel = CourseLevel.BEGINNER
    status: CourseStatus = CourseStatus.DRAFT
    tags: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    category_id: Optional[int] = None

class CourseCreate(CourseBase):
    instructor_id: int

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    lesson_count: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0.0)
    original_price: Optional[float] = Field(None, ge=0.0)
    is_free: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_popular: Optional[bool] = None
    level: Optional[CourseLevel] = None
    status: Optional[CourseStatus] = None
    tags: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    category_id: Optional[int] = None

class CourseResponse(CourseBase):
    id: int
    student_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    instructor_id: int
    instructor_name: str
    instructor_avatar: Optional[str] = None
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CourseDetail(CourseResponse):
    lessons: List[Dict[str, Any]] = []
    reviews: List[Dict[str, Any]] = []
    enrollment_count: int = 0
    completion_rate: float = 0.0
    average_completion_time: Optional[int] = None  # in days

class CourseSearch(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    level: Optional[CourseLevel] = None
    is_free: Optional[bool] = None
    is_featured: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    max_price: Optional[float] = Field(None, ge=0.0)
    instructor_id: Optional[int] = None
    status: Optional[CourseStatus] = None
    sort_by: str = "created_at"  # created_at, rating, price, popularity
    sort_order: str = "desc"  # asc, desc
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class CourseStats(BaseModel):
    course_id: int
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    average_rating: float
    total_reviews: int
    average_completion_time: Optional[int] = None
    completion_rate: float
    revenue: float
    refund_rate: float

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    course_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CourseEnrollment(BaseModel):
    course_id: int
    user_id: int
    payment_status: str = "pending"
    payment_amount: float = 0.0
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None

class CourseReview(BaseModel):
    course_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None 