from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    email: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")

class EmailVerification(BaseModel):
    token: str = Field(..., description="Email verification token")

class RefreshToken(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class Logout(BaseModel):
    refresh_token: str = Field(..., description="Refresh token to invalidate")

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True 