import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException

# Create router
router = APIRouter()

# In-memory task store
task_store: dict = {}

class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


async def generate_report(task_id: str, params: dict):
    """Simulate a long-running report generation."""
    task_store[task_id]["status"] = TaskStatus.RUNNING
    task_store[task_id]["started_at"] = datetime.utcnow().isoformat()
    
    try:
        await asyncio.sleep(3)  # Simulate processing (reduced for demo)
        
        task_store[task_id]["status"] = TaskStatus.COMPLETED
        task_store[task_id]["result"] = {
            "report_url": f"/reports/{task_id}.pdf",
            "rows_processed": 15000
        }
    except Exception as e:
        task_store[task_id]["status"] = TaskStatus.FAILED
        task_store[task_id]["error"] = str(e)
    
    task_store[task_id]["finished_at"] = datetime.utcnow().isoformat()


@router.post("/tasks/report")
async def create_report(params: dict, background_tasks: BackgroundTasks):
    """Create a new report generation task"""
    task_id = str(uuid.uuid4())
    task_store[task_id] = {
        "id": task_id,
        "type": "report",
        "status": TaskStatus.PENDING,
        "created_at": datetime.utcnow().isoformat()
    }
    background_tasks.add_task(generate_report, task_id, params)
    return {"task_id": task_id, "status": "pending"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a specific task"""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_store[task_id]


@router.get("/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "total": len(task_store),
        "tasks": list(task_store.values())
    }