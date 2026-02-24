# main.py
from fastapi import FastAPI
from database import init_db
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router

app = FastAPI(title="JWT Authentication API")

@app.on_event("startup")
async def startup_event():
    """Initialize the database and create tables"""
    await init_db()

# Register Routers
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Hello teja! The JWT Authentication API is running."}

@app.get("/api/status")
def status():
    return {
        "status": "running",
        "framework": "FastAPI",
        "database": "MySQL (Async)",
        "auth": "JWT",
        "docs": "/docs"
    }