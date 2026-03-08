# DesignCode API Documentation

## Overview

The DesignCode API is a RESTful API built with FastAPI that provides endpoints for managing courses, lessons, user progress, and analytics for the DesignCode learning platform.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.designcode.io`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Users

#### GET /api/users/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/users/me
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "bio": "Designer and developer"
}
```

### Courses

#### GET /api/courses
Get all courses with pagination.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "title": "React for Designers",
    "description": "Learn React fundamentals and build beautiful user interfaces",
    "instructor": "Sarah Chen",
    "duration": 720,
    "level": "beginner",
    "category": "frontend",
    "price": 89.99,
    "rating": 4.9,
    "students_count": 15420,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/courses/{course_id}
Get a specific course by ID.

**Response:**
```json
{
  "id": 1,
  "title": "React for Designers",
  "description": "Learn React fundamentals and build beautiful user interfaces",
  "instructor": "Sarah Chen",
  "duration": 720,
  "level": "beginner",
  "category": "frontend",
  "price": 89.99,
  "rating": 4.9,
  "students_count": 15420,
  "lessons": [
    {
      "id": 1,
      "title": "Introduction to React",
      "duration": 15,
      "order": 1
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/courses
Create a new course (admin only).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Advanced CSS Techniques",
  "description": "Master advanced CSS concepts",
  "instructor": "David Kim",
  "duration": 600,
  "level": "advanced",
  "category": "frontend",
  "price": 79.99
}
```

### Lessons

#### GET /api/lessons
Get all lessons, optionally filtered by course.

**Query Parameters:**
- `course_id` (int): Filter by course ID
- `skip` (int): Number of records to skip
- `limit` (int): Number of records to return

**Response:**
```json
[
  {
    "id": 1,
    "title": "Introduction to React",
    "description": "Learn the basics of React",
    "course_id": 1,
    "duration": 900,
    "order": 1,
    "video_url": "https://example.com/video1.mp4",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/lessons/{lesson_id}
Get a specific lesson by ID.

**Response:**
```json
{
  "id": 1,
  "title": "Introduction to React",
  "description": "Learn the basics of React",
  "course_id": 1,
  "duration": 900,
  "order": 1,
  "video_url": "https://example.com/video1.mp4",
  "materials": [
    {
      "type": "pdf",
      "url": "https://example.com/notes.pdf",
      "title": "Lesson Notes"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Progress

#### GET /api/progress
Get progress for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "lesson_id": 1,
    "course_id": 1,
    "completed": true,
    "watched_duration": 900,
    "last_position": 900,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z"
  }
]
```

#### GET /api/progress/course/{course_id}
Get progress for a specific course.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "course_id": 1,
  "completed_lessons": 5,
  "total_lessons": 10,
  "completion_percentage": 50.0,
  "total_watched_time": 4500,
  "last_activity": "2024-01-01T01:00:00Z"
}
```

#### POST /api/progress
Create or update progress for a lesson.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "lesson_id": 1,
  "course_id": 1,
  "completed": true,
  "watched_duration": 900,
  "last_position": 900
}
```

### Analytics

#### GET /api/analytics/dashboard
Get dashboard analytics for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_lessons": 100,
  "completed_lessons": 45,
  "completion_rate": 45.0,
  "course_progress": [
    {
      "course_title": "React for Designers",
      "completed_lessons": 8,
      "total_lessons": 10,
      "progress_percentage": 80.0
    }
  ],
  "recent_activity": [
    {
      "lesson_id": 1,
      "completed": true,
      "updated_at": "2024-01-01T01:00:00Z"
    }
  ]
}
```

#### GET /api/analytics/course/{course_id}
Get analytics for a specific course.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "course_title": "React for Designers",
  "total_lessons": 10,
  "completed_lessons": 8,
  "completion_rate": 80.0,
  "total_duration": 9000,
  "watched_duration": 7200,
  "watch_percentage": 80.0,
  "lesson_details": [
    {
      "title": "Introduction to React",
      "duration": 900,
      "completed": true,
      "watched_duration": 900,
      "updated_at": "2024-01-01T01:00:00Z"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

## Pagination

For endpoints that return lists, pagination is supported with the following query parameters:

- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 100, max: 1000)

## WebSocket Support

The API also supports WebSocket connections for real-time features:

- **WebSocket URL**: `ws://localhost:8000/ws`
- **Authentication**: Include JWT token in the connection query parameter

## SDKs

Official SDKs are available for:

- **JavaScript/TypeScript**: `npm install @designcode/sdk`
- **Python**: `pip install designcode-sdk`
- **React Hook**: `npm install @designcode/react-hook`

## Support

For API support and questions:

- **Documentation**: [docs.designcode.io/api](https://docs.designcode.io/api)
- **Email**: api-support@designcode.io
- **GitHub Issues**: [github.com/designcode/api-issues](https://github.com/designcode/api-issues) 