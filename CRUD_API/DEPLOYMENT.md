# CRUD API - Deployment Guide

This guide provides comprehensive instructions for deploying the CRUD API with Pydantic & SQLAlchemy to various environments.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for source code management)
- SQLite (included with Python for development)

## 🚀 Local Development Deployment

### 1. Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd CRUD_API
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
sqlalchemy==2.0.23
asyncpg==0.29.0  # For PostgreSQL
aiomysql==0.2.0  # For MySQL
python-multipart==0.0.6
pydantic[email]==2.5.2
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
*.db
```

### 3. Build and Run Docker Container

```bash
# Build the image
docker build -t crud-api .

# Run the container
docker run -d -p 8000:8000 --name crud-api-container crud-api

# Check container status
docker ps

# View logs
docker logs crud-api-container
```

### 4. Verify Deployment

Same as local development:
- API Documentation: `http://localhost:8000/docs`
- Status Check: `http://localhost:8000/api/status`

## 🚀 Production Deployment Options

### Option 1: Docker Compose (Recommended for Small Deployments)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  crud-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite:///./tasks.db
    restart: unless-stopped
    volumes:
      - ./tasks.db:/app/tasks.db
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run:

```bash
docker-compose up -d
```

### Option 2: Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crud-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crud-api
  template:
    metadata:
      labels:
        app: crud-api
    spec:
      containers:
        - name: crud-api
          image: crud-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              value: "sqlite:///./tasks.db"
          volumeMounts:
            - mountPath: /app/tasks.db
              name: tasks-db
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
      volumes:
        - name: tasks-db
          persistentVolumeClaim:
            claimName: tasks-db-claim
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: tasks-db-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: crud-api
spec:
  selector:
    app: crud-api
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
heroku create crud-api-fastapi

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set DATABASE_URL=sqlite:///./tasks.db

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

# Database configuration
DATABASE_URL=sqlite:///./tasks.db

# API settings
API_TITLE="CRUD API with Pydantic & SQLAlchemy"
API_VERSION="1.0.0"

# Logging
LOG_LEVEL=INFO
```

### Database Configuration

The application supports multiple databases. To use PostgreSQL or MySQL instead of SQLite:

#### PostgreSQL

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/dbname
```

```bash
pip install asyncpg
```

#### MySQL

```env
DATABASE_URL=mysql+aiomysql://username:password@localhost/dbname
```

```bash
pip install aiomysql
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
  "database": "SQLite (Async)",
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

3. **Database Connection Issues**:
   - Check if the database server is running
   - Verify the connection string
   - Ensure the database exists and the user has permissions

4. **Docker Container Issues**:
   ```bash
   docker logs crud-api-container
   docker exec -it crud-api-container bash  # Debug into container
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

3. **Database Optimization**:
   - Use connection pooling
   - Add indexes to frequently queried fields
   - Consider using a database server (PostgreSQL/MySQL) instead of SQLite for high traffic

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
        docker build -t crud-api:latest .
    
    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker tag crud-api:latest ${{ secrets.DOCKER_USERNAME }}/crud-api:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/crud-api:latest
    
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
5. Verify the database connection and operations

---

**Last Updated**: February 2026  
**Version**: 1.0.0
