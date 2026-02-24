# main.py
from fastapi import FastAPI

app = FastAPI(title="My First API")

@app.get("/")
def root():
    return {"message": "Hello teja u can done to run that successfully!"}

@app.get("/greet/{name}")
def greet(name: str, excited: bool = False):
    greeting = f"greeted, {name}"
    if excited:
        greeting += "!!!"
    return {"greeting": greeting}

@app.get("/api/status")
def status():
    return {
        "status": "running",
        "framework": "FastAPI",
        "docs": "/docs"
    }