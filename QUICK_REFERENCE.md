# FastAPI Projects - Quick Reference Guide

## Project Summary

This workspace contains 5 independent FastAPI projects demonstrating different API patterns and best practices.

## Projects Overview

### 1. 🚀 Async_API_aggregator
**Purpose:** Multi-API aggregation with concurrent execution and caching

**Key Features:**
- Concurrent API calls with `asyncio.gather()`
- TTL-based caching (5-minute expiry)
- Weather and News data aggregation
- Cache hit/miss tracking
- Graceful error handling with fallbacks

**Tech Stack:** FastAPI, httpx, cachetools
**Difficulty:** Intermediate

**When to use:** Learn async patterns, concurrent request handling

---

### 2. 📝 CRUD_API
**Purpose:** Complete task management with full CRUD operations

**Key Features:**
- Create, Read, Update, Delete tasks
- MySQL/SQLite database support
- Async SQLAlchemy ORM
- Pagination and filtering
- Priority levels and completion status

**Tech Stack:** FastAPI, SQLAlchemy, aiomysql
**Difficulty:** Intermediate

**When to use:** Learn database operations, Pydantic validation, ORM patterns

---

### 3. 🔐 JWT Authentication
**Purpose:** Secure API with JWT tokens and user management

**Key Features:**
- User registration and login
- JWT access tokens (30 min) + refresh tokens (7 days)
- Bcrypt password hashing
- Per-user task isolation
- OAuth2 bearer authentication
- Role-based task ownership

**Tech Stack:** FastAPI, SQLAlchemy, python-jose, passlib
**Difficulty:** Advanced

**When to use:** Learn authentication, authorization, token-based security

---

### 4. ⚡ task_caching
**Purpose:** Asynchronous background task processing with status tracking

**Key Features:**
- UUID-based task tracking
- Background task execution
- Task status monitoring (PENDING → RUNNING → COMPLETED/FAILED)
- Admin dashboard with statistics
- Real-time status polling
- In-memory task store

**Tech Stack:** FastAPI, asyncio
**Difficulty:** Intermediate

**When to use:** Learn background tasks, async job processing, admin dashboards

---

### 5. 🎯 quickstart
**Purpose:** Minimal introduction to FastAPI

**Key Features:**
- Simple GET endpoints
- Path and query parameters
- Basic routing

**Tech Stack:** FastAPI
**Difficulty:** Beginner

**When to use:** FastAPI basics, quick start template

---

## Quick Start Guide

### Setup Environment
```bash
cd /Users/sandhya.arkadu/Desktop/FastAPI_Projects
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Individual Projects
```bash
# Async API Aggregator
cd Async_API_aggregator && uvicorn main:app --reload --port 8000

# CRUD API
cd CRUD_API && uvicorn main:app --reload --port 8001

# JWT Authentication
cd JWT && uvicorn main:app --reload --port 8002

# Task Caching
cd task_caching && uvicorn main:app --reload --port 8003

# Quickstart
cd quickstart/backend && uvicorn main:app --reload --port 8004
```

### Access Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## Architecture Comparison

| Feature | Async_API | CRUD_API | JWT | task_caching | quickstart |
|---------|-----------|----------|-----|--------------|-----------|
| Database | ❌ | ✅ | ✅ | ❌ | ❌ |
| Authentication | ❌ | ❌ | ✅ | ❌ | ❌ |
| Caching | ✅ | ❌ | ❌ | ❌ | ❌ |
| Background Tasks | ❌ | ❌ | ❌ | ✅ | ❌ |
| Async/Await | ✅ | ✅ | ✅ | ✅ | ❌ |
| External APIs | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pagination | ❌ | ✅ | ✅ | ❌ | ❌ |
| Filtering | ❌ | ✅ | ✅ | ❌ | ❌ |

---

## Learning Path

### Beginner → Intermediate → Advanced

**Phase 1: Foundations (quickstart)**
1. Start with quickstart
2. Learn FastAPI basics
3. Understand routing and parameters

**Phase 2: Data Handling (CRUD_API)**
1. Learn database operations
2. Understand ORM patterns
3. Learn Pydantic validation
4. Implement pagination and filtering

**Phase 3: Async Patterns (Async_API_aggregator)**
1. Learn async/await
2. Understand concurrent operations
3. Learn caching strategies
4. Handle external APIs

**Phase 4: Security (JWT)**
1. Learn authentication
2. Understand JWT tokens
3. Implement password hashing
4. Learn authorization patterns

**Phase 5: Advanced Patterns (task_caching)**
1. Learn background tasks
2. Understand async job processing
3. Build admin dashboards
4. Learn status tracking

---

## Core Concepts Map

### Async/Await
- **Async_API_aggregator:** `asyncio.gather()` for concurrent calls
- **CRUD_API:** Async database sessions
- **JWT:** Async user lookups
- **task_caching:** Background task execution

### Database Operations
- **CRUD_API:** Full CRUD with pagination
- **JWT:** User + task storage
- Uses: SQLAlchemy ORM, async drivers

### Authentication
- **JWT:** Complete auth flow (register, login, protected endpoints)
- OAuth2 bearer tokens
- Password hashing with bcrypt

### Caching
- **Async_API_aggregator:** TTL-based in-memory caching
- Cache hit/miss tracking
- Expiration management

### Background Tasks
- **task_caching:** Async task execution
- Status tracking
- Result storage

### API Design
- RESTful endpoints
- Pydantic validation
- Error handling
- Documentation

---

## Database Configuration

### MySQL Setup
```sql
CREATE DATABASE tasks_db;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'Test1234';
GRANT ALL PRIVILEGES ON tasks_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Environment Variables
```env
DB_USER=root
DB_PASSWORD=Test1234
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tasks_db
```

### Connection String
```
mysql+aiomysql://root:Test1234@localhost:3306/tasks_db
```

---

## API Testing Examples

### Test Async_API_aggregator
```bash
# Get aggregated data
curl http://localhost:8000/aggregate/london

# Force cache refresh
curl http://localhost:8000/aggregate/london?no_cache=true

# Clear cache
curl -X DELETE http://localhost:8000/aggregate/cache
```

### Test CRUD_API
```bash
# Create task
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","priority":"high"}'

# List tasks
curl http://localhost:8001/tasks?page=1&per_page=10

# Get task
curl http://localhost:8001/tasks/1

# Update task
curl -X PUT http://localhost:8001/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Delete task
curl -X DELETE http://localhost:8001/tasks/1
```

### Test JWT
```bash
# Register
curl -X POST http://localhost:8002/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=pass123"

# Get profile (use token from login)
curl http://localhost:8002/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get user tasks
curl http://localhost:8002/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test task_caching
```bash
# Create task
curl -X POST http://localhost:8003/api/tasks/report \
  -H "Content-Type: application/json" \
  -d '{"params":{}}'

# Get task status (use task_id from response)
curl http://localhost:8003/api/tasks/TASK_ID_HERE

# List all tasks
curl http://localhost:8003/api/tasks

# Admin dashboard
curl http://localhost:8003/api/admin/dashboard

# Health check
curl http://localhost:8003/health
```

---

## Deployment Checklist

### Development
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Start local MySQL
- [ ] Run projects locally
- [ ] Test with curl/Postman

### Production
- [ ] Change SECRET_KEY (JWT)
- [ ] Update CORS settings
- [ ] Enable HTTPS/TLS
- [ ] Use environment variables for sensitive data
- [ ] Set up database replication
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure CI/CD pipeline
- [ ] Use Gunicorn with multiple workers
- [ ] Set up load balancer (nginx)
- [ ] Implement backup strategy

---

## File Structure Summary

```
FastAPI_Projects/
├── PRD.md                          # Main documentation
│
├── Async_API_aggregator/
│   ├── main.py
│   ├── clients.py
│   ├── cache.py
│   ├── routers/aggregate.py
│   └── ANALYSIS.md                 # Project-specific analysis
│
├── CRUD_API/
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   ├── routes/tasks.py
│   └── ANALYSIS.md
│
├── JWT/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── routes/auth.py
│   ├── routes/tasks.py
│   └── ANALYSIS.md
│
├── task_caching/
│   ├── main.py
│   ├── tasks.py
│   ├── routes/admin.py
│   └── ANALYSIS.md
│
├── quickstart/
│   └── backend/main.py
│
├── venv/                           # Virtual environment
└── README.md
```

---

## Common Tasks

### Add New Endpoint
1. Create route function with async
2. Add Pydantic schema for input/output
3. Use dependency injection for dependencies
4. Register in main.py with include_router()

### Add Database Model
1. Define class in database.py extending Base
2. Add columns with Column()
3. Create Pydantic schema in schemas.py
4. Add CRUD operations in routes

### Add Authentication
1. Reference JWT project structure
2. Import get_current_user from dependencies
3. Add current_user: User = Depends(get_current_user) to endpoint
4. Endpoint will reject requests without valid JWT

### Add Caching
1. Check Async_API_aggregator for TTL cache pattern
2. Or upgrade to Redis for distributed caching

### Add Background Tasks
1. Reference task_caching project
2. Inject BackgroundTasks in endpoint
3. Use background_tasks.add_task()
4. Return immediately with task ID

---

## Performance Tips

1. **Database:** Use indexes on frequently filtered columns
2. **Caching:** Implement Redis for distributed cache
3. **Async:** Always use async/await, never block
4. **Pagination:** Don't fetch all records at once
5. **Connection Pool:** Configure proper pool size
6. **Bcrypt:** Cost factor 12 is slow but secure
7. **Logging:** Use structured logging
8. **Monitoring:** Track key metrics

---

## Security Best Practices

✅ **Implemented:**
- Bcrypt password hashing
- JWT token validation
- Pydantic input validation
- SQL injection prevention (SQLAlchemy)
- CORS configuration

⚠️ **To Add:**
- HTTPS/TLS
- Rate limiting
- Request logging
- Audit trails
- 2FA
- Email verification

❌ **Do NOT:**
- Hardcode secrets in code
- Use `allow_origins=["*"]` in production
- Log sensitive data
- Trust user input
- Disable SSL verification

---

## Troubleshooting

### Database Connection Error
```
Solution: Verify MySQL is running
mysql -u root -p
```

### Port Already in Use
```
Solution: Use different port
uvicorn main:app --port 8005
```

### Module Not Found
```
Solution: Activate virtual environment
source venv/bin/activate
```

### JWT Token Invalid
```
Solution: Check token expiration and SECRET_KEY
```

### CORS Error
```
Solution: Check CORS configuration in main.py
```

---

## Additional Resources

### Official Documentation
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Uvicorn: https://www.uvicorn.org/

### Learning Resources
- FastAPI Full Course (YouTube)
- Real Python FastAPI Tutorials
- FastAPI by Sebastian Ramirez (creator)

### Community
- FastAPI Discord
- Stack Overflow (fastapi tag)
- GitHub Discussions

---

## Next Steps

1. **Explore each project** - Run locally, understand code
2. **Modify and experiment** - Change endpoints, add features
3. **Combine patterns** - Add auth to CRUD API
4. **Deploy** - Move to production environment
5. **Scale** - Add caching, load balancing
6. **Monitor** - Implement logging and metrics

---

**Document Version:** 1.0  
**Last Updated:** February 26, 2026  
**Status:** Complete  
**Maintenance:** Active

