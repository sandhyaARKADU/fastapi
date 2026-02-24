# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Token Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Priority = Priority.medium

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class TaskList(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
