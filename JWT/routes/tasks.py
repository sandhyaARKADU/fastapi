# routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from database import get_db, Task, User
from schemas import TaskCreate, TaskResponse, TaskList, Priority
from dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=TaskList)
async def list_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks for the current user"""
    query = select(Task).where(Task.owner_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return TaskList(tasks=tasks, total=total, page=page, per_page=per_page)

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a task for the current user"""
    task = Task(
        **task_data.model_dump(),
        owner_id=current_user.id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
