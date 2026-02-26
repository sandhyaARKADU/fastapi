# Task Caching API - Deployment Guide

This guide provides comprehensive instructions for deploying the Task Caching API with background task management to various environments.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for source code management)
- Redis (optional, for advanced caching)

## 🚀 Local Development Deployment

### 1. Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd task_caching
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
python-dotenv==1.0.0
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
- Health Check: `http://localhost:8000/health`
- Root Endpoint: `http://localhost:8000/`

## 🐳 Docker Deployment

### 1. Create Dockerfile

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

### 3. Create Docker Compose (with Redis)

```yaml
version: '3.8'
services:
  task-caching-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - CACHE_TYPE=redis
      - REDIS_URL=redis://redis:6379/0
    restart: unless-stopped
    depends_on:
      - redis
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis_data:
```

### 4. Build and Run

```bash
# Build and run
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Verify Redis connection
docker exec -it task_caching_redis_1 redis-cli ping
```

## 🚀 Production Deployment Options

### Option 1: Docker Compose (Recommended for Small Deployments)

Use the `docker-compose.yml` from the Docker section.

### Option 2: Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-caching-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: task-caching-api
  template:
    metadata:
      labels:
        app: task-caching-api
    spec:
      containers:
        - name: task-caching-api
          image: task-caching-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: CACHE_TYPE
              value: "redis"
            - name: REDIS_URL
              value: "redis://redis-service:6379/0"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: task-caching-api
spec:
  selector:
    app: task-caching-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7.2-alpine
          ports:
            - containerPort: 6379
          volumeMounts:
            - mountPath: /data
              name: redis-data
          command: ["redis-server", "--appendonly", "yes"]
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: redis-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
    - protocol: TCP
      port: 6379
      targetPort: 6379
  type: ClusterIP
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
heroku create task-caching-api

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set CACHE_TYPE=redis
heroku addons:create heroku-redis:hobby-dev

# Deploy
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

# Cache configuration
CACHE_TYPE=redis  # or "memory" for in-memory cache
REDIS_URL=redis://localhost:6379/0

# API settings
API_TITLE="Task Caching API"
API_VERSION="1.0.0"

# Logging
LOG_LEVEL=INFO

# Task configuration
TASK_DEFAULT_TTL=300  # Task Time To Live in seconds
MAX_ACTIVE_TASKS=100
```

### Caching Configuration

The application supports two caching strategies:

1. **In-Memory Cache (Default)**: Simple and fast, but not suitable for distributed systems
2. **Redis Cache**: Recommended for production and distributed environments

To use Redis, install:

```bash
pip install redis
```

And add to `main.py`:

```python
import redis
import json
from datetime import timedelta
from typing import Any

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(url)
    
    def get(self, key: str) -> Any:
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        self.redis.setex(key, timedelta(seconds=ttl), json.dumps(value))
    
    def delete(self, key: str):
        self.redis.delete(key)
    
    def keys(self, pattern: str = "*"):
        return self.redis.keys(pattern)
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
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-26T10:34:05.654Z",
  "active_tasks": 5
}
```

### Task Monitoring

View active tasks:

```
GET /api/admin/dashboard
```

## 🔒 Security Considerations

### Production Best Practices

1. **HTTPS**: Always use HTTPS in production
2. **CORS**: Configure CORS properly
3. **Rate Limiting**: Add rate limiting middleware
4. **Security Headers**: Use security headers (e.g., CSP, HSTS)
5. **Environment Variables**: Don't hardcode sensitive information
6. **Redis Security**: Secure your Redis instance with passwords and access controls

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

3. **Redis Connection Issues**:
   - Check if Redis server is running
   - Verify the connection string
   - Ensure Redis is accessible from the application

4. **Task Management Issues**:
   - Check task store implementation
   - Verify background task processing
   - Review task status transitions

5. **Docker Container Issues**:
   ```bash
   docker-compose logs -f
   docker exec -it task_caching_task-caching-api_1 bash  # Debug into API container
   docker exec -it task_caching_redis_1 redis-cli ping  # Debug into Redis container
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

3. **Redis Optimization**:
   - Use connection pooling
   - Enable Redis persistence
   - Monitor Redis performance

4. **Task Processing**:
   - Implement task queue (Celery/RQ) for heavy tasks
   - Optimize task TTL configuration
   - Add task retry logic

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
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v
    
    - name: Build Docker image
      run: |
        docker build -t task-caching-api:latest .
    
    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker tag task-caching-api:latest ${{ secrets.DOCKER_USERNAME }}/task-caching-api:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/task-caching-api:latest
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f deployment.yaml
```

## 📞 Support

For issues and questions:

1. Check the application logs
2. Verify all dependencies are installed correctly
3. Review the API documentation at `/docs`
4. Check the health check endpoint at `/health`
5. Verify the Redis connection (if used)
6. Monitor task processing and cache performance

---

**Last Updated**: February 2026  
**Version**: 1.0.0
