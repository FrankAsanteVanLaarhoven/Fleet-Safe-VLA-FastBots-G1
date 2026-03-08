from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base

class LessonType(enum.Enum):
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    PROJECT = "project"

class LessonStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Lesson content in markdown
    video_url = Column(String(500), nullable=True)
    video_duration = Column(Integer, default=0)  # Duration in seconds
    thumbnail_url = Column(String(500), nullable=True)
    order_index = Column(Integer, default=0)  # Order within course
    is_free = Column(Boolean, default=False)
    is_preview = Column(Boolean, default=False)
    type = Column(Enum(LessonType), default=LessonType.VIDEO)
    status = Column(Enum(LessonStatus), default=LessonStatus.DRAFT)
    difficulty = Column(Integer, default=1)  # 1-5 scale
    estimated_time = Column(Integer, default=0)  # Estimated time in minutes
    resources = Column(Text, nullable=True)  # JSON string for additional resources
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    progress = relationship("Progress", back_populates="lesson")
    quizzes = relationship("Quiz", back_populates="lesson")
    exercises = relationship("Exercise", back_populates="lesson")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(Text, nullable=False)  # JSON string for quiz questions
    passing_score = Column(Integer, default=70)  # Percentage required to pass
    time_limit = Column(Integer, default=0)  # Time limit in minutes (0 = no limit)
    max_attempts = Column(Integer, default=3)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)
    hints = Column(Text, nullable=True)  # JSON string for hints
    difficulty = Column(Integer, default=1)  # 1-5 scale
    estimated_time = Column(Integer, default=0)  # Estimated time in minutes
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="exercises")
    submissions = relationship("ExerciseSubmission", back_populates="exercise") 