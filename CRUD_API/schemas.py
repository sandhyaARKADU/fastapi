# schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, 
                       description="Task title")
    description: Optional[str] = Field(None, max_length=500)
    priority: Priority = Priority.medium
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    """Schema for task responses"""
    id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode

class TaskList(BaseModel):
    """Schema for paginated task list"""
    tasks: list[TaskResponse]
    total: int
    page: int
    per_page: int