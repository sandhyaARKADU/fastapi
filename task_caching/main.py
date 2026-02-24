import uuid
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tasks import router as tasks_router, TaskStatus, task_store
from routes.admin import router as admin_router

# Initialize FastAPI app
app = FastAPI(
    title="Task Caching API",
    description="FastAPI application with background task management and caching",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Task Caching API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "tasks": "/api/tasks",
            "admin": "/api/admin/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_tasks": len(task_store)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
