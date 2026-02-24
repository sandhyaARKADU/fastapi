# main.py
from fastapi import FastAPI
from routers.aggregate import router as aggregate_router

app = FastAPI(title="Async API Aggregator")

# Register the aggregate router
app.include_router(aggregate_router)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI! Async API Aggregator is ready."}

@app.get("/api/status")
def status():
    return {
        "status": "running",
        "framework": "FastAPI",
        "features": ["Async Aggregation", "TTL Caching"],
        "docs": "/docs"
    }