# JWT Authentication API - Deployment Guide

This guide provides comprehensive instructions for deploying the JWT Authentication API with MySQL integration to various environments.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for source code management)
- MySQL Server 5.7 or higher (for production)

## 🚀 Local Development Deployment

### 1. Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd JWT
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
aiomysql==0.2.0  # For MySQL
python-multipart==0.0.6
pydantic[email]==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure the Database

1. **Install and start MySQL server**
2. **Create a database and user**:

```sql
CREATE DATABASE fastapi_jwt;
CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON fastapi_jwt.* TO 'fastapi_user'@'localhost';
FLUSH PRIVILEGES;
```

3. **Create a `.env` file**:

```env
# Environment configuration
ENVIRONMENT=development
DEBUG=True

# Database configuration
DATABASE_URL=mysql+aiomysql://fastapi_user:your_strong_password@localhost/fastapi_jwt

# JWT configuration
SECRET_KEY=your-super-secret-key-here-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API settings
API_TITLE="JWT Authentication API"
API_VERSION="1.0.0"

# Logging
LOG_LEVEL=INFO
```

### 5. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Deployment

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
```

### 3. Create Docker Compose (with MySQL)

```yaml
version: '3.8'
services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_DATABASE: fastapi_jwt
      MYSQL_USER: fastapi_user
      MYSQL_PASSWORD: your_strong_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -u root -p$MYSQL_ROOT_PASSWORD"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=mysql+aiomysql://fastapi_user:your_strong_password@db/fastapi_jwt
      - SECRET_KEY=your-super-secret-key-here
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mysql_data:
```

### 4. Build and Run

```bash
# Build and run
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Verify database connection
docker exec -it jwt_db_1 mysql -u fastapi_user -pyour_strong_password fastapi_jwt -e "SHOW TABLES;"
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
  name: jwt-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: jwt-api
  template:
    metadata:
      labels:
        app: jwt-api
    spec:
      containers:
        - name: jwt-api
          image: jwt-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              value: "mysql+aiomysql://fastapi_user:your_strong_password@mysql-service/fastapi_jwt"
            - name: SECRET_KEY
              value: "your-super-secret-key-here"
            - name: ALGORITHM
              value: "HS256"
            - name: ACCESS_TOKEN_EXPIRE_MINUTES
              value: "30"
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
  name: jwt-api
spec:
  selector:
    app: jwt-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          env:
            - name: MYSQL_DATABASE
              value: "fastapi_jwt"
            - name: MYSQL_USER
              value: "fastapi_user"
            - name: MYSQL_PASSWORD
              value: "your_strong_password"
            - name: MYSQL_ROOT_PASSWORD
              value: "root_password"
          ports:
            - containerPort: 3306
          volumeMounts:
            - mountPath: /var/lib/mysql
              name: mysql-data
      volumes:
        - name: mysql-data
          persistentVolumeClaim:
            claimName: mysql-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
spec:
  selector:
    app: mysql
  ports:
    - protocol: TCP
      port: 3306
      targetPort: 3306
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
heroku create jwt-api-fastapi

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set DATABASE_URL=mysql+aiomysql://user:pass@host/dbname
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set ALGORITHM=HS256
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open app
heroku open
```

## 🔧 Configuration

### Environment Variables

The `.env` file should contain:

```env
# Environment configuration
ENVIRONMENT=development
DEBUG=True

# Database configuration
DATABASE_URL=mysql+aiomysql://username:password@localhost/dbname

# JWT configuration
SECRET_KEY=your-super-secret-key-here-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API settings
API_TITLE="JWT Authentication API"
API_VERSION="1.0.0"

# Logging
LOG_LEVEL=INFO
```

### Generating a Strong SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
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
  "database": "MySQL (Async)",
  "auth": "JWT",
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
6. **Database Security**: Use strong passwords and limited permissions
7. **JWT Security**: Use short token expiration times and strong secrets

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
   - Check if MySQL server is running
   - Verify the connection string
   - Ensure the database exists and the user has permissions

4. **JWT Token Issues**:
   - Check SECRET_KEY is consistent
   - Verify token expiration time
   - Check algorithm configuration

5. **Docker Container Issues**:
   ```bash
   docker-compose logs -f
   docker exec -it jwt_api_1 bash  # Debug into API container
   docker exec -it jwt_db_1 mysql -u fastapi_user -p  # Debug into MySQL container
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
   - Consider read replicas for high traffic

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
        docker build -t jwt-api:latest .
    
    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker tag jwt-api:latest ${{ secrets.DOCKER_USERNAME }}/jwt-api:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/jwt-api:latest
    
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
6. Check JWT token configuration and validation

---

**Last Updated**: February 2026  
**Version**: 1.0.0
