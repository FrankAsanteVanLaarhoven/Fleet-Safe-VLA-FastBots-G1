from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base

class CourseLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CourseStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # Full course content in markdown
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, default=0)
    lesson_count = Column(Integer, default=0)
    student_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    original_price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_popular = Column(Boolean, default=False)
    level = Column(Enum(CourseLevel), default=CourseLevel.BEGINNER)
    status = Column(Enum(CourseStatus), default=CourseStatus.DRAFT)
    tags = Column(Text, nullable=True)  # JSON string for tags
    prerequisites = Column(Text, nullable=True)  # JSON string for prerequisites
    learning_objectives = Column(Text, nullable=True)  # JSON string for objectives
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    instructor = relationship("User", backref="courses_created")
    category = relationship("Category", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")
    reviews = relationship("Review", back_populates="course")
    progress = relationship("Progress", back_populates="course")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    courses = relationship("Course", back_populates="category") 