from fastapi import APIRouter
from tasks import task_store, TaskStatus

# Create router
router = APIRouter()


@router.get("/admin/dashboard")
async def admin_dashboard():
    """Get admin dashboard with task and cache statistics"""
    tasks = list(task_store.values())
    task_stats = {
        "total": len(tasks),
        "pending": sum(1 for t in tasks if t["status"] == TaskStatus.PENDING),
        "running": sum(1 for t in tasks if t["status"] == TaskStatus.RUNNING),
        "completed": sum(1 for t in tasks if t["status"] == TaskStatus.COMPLETED),
        "failed": sum(1 for t in tasks if t["status"] == TaskStatus.FAILED),
    }
    
    return {
        "tasks": task_stats,
        "recent_tasks": sorted(tasks, key=lambda t: t.get("created_at", ""), reverse=True)[:10]
    }


@router.get("/admin/tasks/summary")
async def tasks_summary():
    """Get a summary of all tasks"""
    tasks = list(task_store.values())
    return {
        "total_tasks": len(tasks),
        "status_breakdown": {
            "pending": sum(1 for t in tasks if t["status"] == TaskStatus.PENDING),
            "running": sum(1 for t in tasks if t["status"] == TaskStatus.RUNNING),
            "completed": sum(1 for t in tasks if t["status"] == TaskStatus.COMPLETED),
            "failed": sum(1 for t in tasks if t["status"] == TaskStatus.FAILED),
        },
        "tasks": tasks
    }
