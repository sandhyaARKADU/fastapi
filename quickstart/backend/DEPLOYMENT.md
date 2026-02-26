# Quickstart API - Deployment Guide

This guide provides simple and straightforward instructions for deploying the Quickstart API to various environments.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for source code management)

## 🚀 Local Development Deployment

### 1. Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd quickstart/backend
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Verify Deployment

Open your browser and navigate to:
- API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`
- Status Check: `http://localhost:8000/api/status`
- Root Endpoint: `http://localhost:8000/`

## 🐳 Docker Deployment

### 1. Create Dockerfile

Create `Dockerfile` in the `backend` directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Create .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv
.env
*.env
```

### 3. Build and Run Docker Container

```bash
cd quickstart/backend

# Build the image
docker build -t quickstart-api .

# Run the container
docker run -d -p 8000:8000 --name quickstart-container quickstart-api

# Check container status
docker ps

# View logs
docker logs quickstart-container
```

### 4. Verify Deployment

Same as local development:
- API Documentation: `http://localhost:8000/docs`
- Status Check: `http://localhost:8000/api/status`

## 🚀 Production Deployment Options

### Option 1: Docker Compose (Recommended for Small Deployments)

Create `docker-compose.yml` in the `quickstart` directory:

```yaml
version: '3.8'
services:
  quickstart-api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run:

```bash
cd quickstart
docker-compose up -d --build
```

### Option 2: Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quickstart-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quickstart-api
  template:
    metadata:
      labels:
        app: quickstart-api
    spec:
      containers:
        - name: quickstart-api
          image: quickstart-api:latest
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /api/status
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/status
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: quickstart-api
spec:
  selector:
    app: quickstart-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

Apply:

```bash
kubectl apply -f deployment.yaml
```

### Option 3: Heroku Deployment

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create quickstart-api

# Set environment variables
heroku config:set ENVIRONMENT=production

# Deploy
cd quickstart/backend
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open app
heroku open
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Environment configuration
ENVIRONMENT=development
DEBUG=True

# API settings
API_TITLE="My First API"
API_VERSION="1.0.0"

# Logging
LOG_LEVEL=INFO
```

### Application Configuration

Add configuration to `main.py`:

```python
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("API_TITLE", "My First API"),
    version=os.getenv("API_VERSION", "1.0.0")
)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

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
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": app.version,
        "docs": "/docs"
    }
```

## 📊 Monitoring and Logging

### Logging Configuration

Add to `main.py`:

```python
import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "standard",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
```

### Health Checks

The application provides a health check endpoint:

```
GET /api/status
```

Response:
```json
{
  "status": "running",
  "framework": "FastAPI",
  "environment": "development",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## 🔒 Security Considerations

### Production Best Practices

1. **HTTPS**: Always use HTTPS in production
2. **CORS**: Configure CORS properly
3. **Rate Limiting**: Add rate limiting middleware
4. **Security Headers**: Use security headers (e.g., CSP, HSTS)
5. **Environment Variables**: Don't hardcode sensitive information

### Adding CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Adding Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to all endpoints
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    return await limiter(request=request, call_next=call_next)
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   lsof -ti :8000 | xargs kill -9  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

2. **Dependency Issues**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **Docker Container Issues**:
   ```bash
   docker logs quickstart-container
   docker exec -it quickstart-container bash  # Debug into container
   ```

### Log Analysis

```bash
# View logs
tail -f app.log

# Search for errors
grep -i "error" app.log

# Check log levels
grep -i "warning\|error" app.log
```

## 📈 Performance Optimization

1. **Enable Gzip Compression**:
   ```bash
   pip install fastapi-compression
   ```

2. **Use a Reverse Proxy**:
   - Nginx
   - Apache

3. **Caching**: Add caching for static content

## 🔄 CI/CD Pipeline

Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd quickstart/backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd quickstart/backend
        pytest tests/ -v
    
    - name: Build Docker image
      run: |
        cd quickstart/backend
        docker build -t quickstart-api:latest .
    
    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker tag quickstart-api:latest ${{ secrets.DOCKER_USERNAME }}/quickstart-api:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/quickstart-api:latest
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f deployment.yaml
```

## 📞 Support

For issues and questions:

1. Check the application logs
2. Verify all dependencies are installed correctly
3. Review the API documentation at `/docs`
4. Check the health check endpoint at `/api/status`

---

**Last Updated**: February 2026  
**Version**: 1.0.0
