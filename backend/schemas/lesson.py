from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class LessonType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    PROJECT = "project"

class LessonStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[HttpUrl] = None
    video_duration: int = Field(0, ge=0)
    thumbnail_url: Optional[HttpUrl] = None
    order_index: int = Field(0, ge=0)
    is_free: bool = False
    is_preview: bool = False
    type: LessonType = LessonType.VIDEO
    status: LessonStatus = LessonStatus.DRAFT
    difficulty: int = Field(1, ge=1, le=5)
    estimated_time: int = Field(0, ge=0)
    resources: Optional[List[Dict[str, Any]]] = None
    course_id: int

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[HttpUrl] = None
    video_duration: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[HttpUrl] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_free: Optional[bool] = None
    is_preview: Optional[bool] = None
    type: Optional[LessonType] = None
    status: Optional[LessonStatus] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    estimated_time: Optional[int] = Field(None, ge=0)
    resources: Optional[List[Dict[str, Any]]] = None

class LessonResponse(LessonBase):
    id: int
    course_title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LessonDetail(LessonResponse):
    next_lesson: Optional[Dict[str, Any]] = None
    previous_lesson: Optional[Dict[str, Any]] = None
    user_progress: Optional[Dict[str, Any]] = None
    quiz: Optional[Dict[str, Any]] = None
    exercise: Optional[Dict[str, Any]] = None

class LessonSearch(BaseModel):
    course_id: Optional[int] = None
    type: Optional[LessonType] = None
    status: Optional[LessonStatus] = None
    is_free: Optional[bool] = None
    is_preview: Optional[bool] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    sort_by: str = "order_index"
    sort_order: str = "asc"
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class QuizBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    questions: List[Dict[str, Any]] = Field(..., min_items=1)
    passing_score: int = Field(70, ge=0, le=100)
    time_limit: int = Field(0, ge=0)  # 0 = no limit
    max_attempts: int = Field(3, ge=1)
    lesson_id: int

class QuizCreate(QuizBase):
    pass

class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    time_limit: Optional[int] = Field(None, ge=0)
    max_attempts: Optional[int] = Field(None, ge=1)

class QuizResponse(QuizBase):
    id: int
    lesson_title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class QuizAttempt(BaseModel):
    quiz_id: int
    answers: List[Dict[str, Any]]
    time_taken: Optional[int] = None  # in seconds

class QuizResult(BaseModel):
    attempt_id: int
    score: float
    max_score: float
    percentage: float
    passed: bool
    answers: List[Dict[str, Any]]
    correct_answers: List[Dict[str, Any]]
    time_taken: int
    completed_at: datetime

class ExerciseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: str
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    hints: Optional[List[str]] = None
    difficulty: int = Field(1, ge=1, le=5)
    estimated_time: int = Field(0, ge=0)
    lesson_id: int

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    hints: Optional[List[str]] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    estimated_time: Optional[int] = Field(None, ge=0)

class ExerciseResponse(ExerciseBase):
    id: int
    lesson_title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ExerciseSubmission(BaseModel):
    exercise_id: int
    submission_code: str
    submission_file: Optional[str] = None  # File URL if submitted as file

class ExerciseResult(BaseModel):
    submission_id: int
    status: str  # submitted, graded, passed, failed
    score: float
    feedback: Optional[str] = None
    graded_by: Optional[str] = None
    graded_at: Optional[datetime] = None
    submitted_at: datetime 