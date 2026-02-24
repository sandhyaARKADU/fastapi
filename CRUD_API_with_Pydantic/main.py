# main.py
from fastapi import FastAPI
from database import init_db
from routes.tasks import router as tasks_router

app = FastAPI(title="CRUD API with Pydantic & SQLAlchemy")

@app.on_event("startup")
async def startup_event():
    """Initialize the database when the application starts"""
    await init_db()

# Include the tasks router
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Hello teja! The CRUD API is running and connected to the database."}

@app.get("/api/status")
def status():
    return {
        "status": "running",
        "framework": "FastAPI",
        "database": "SQLite (Async)",
        "docs": "/docs"
    }