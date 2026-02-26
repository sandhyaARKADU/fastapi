# CRUD API - Project Analysis

## Overview
Complete task management system with full CRUD operations, database persistence, and async SQLAlchemy ORM.

## Architecture

### Components

#### 1. **Main Application** (`main.py`)
- FastAPI app initialization
- Database initialization on startup
- Task router registration
- Status endpoints
- Documentation: `/docs`

#### 2. **Database Layer** (`database.py`)
- Async SQLAlchemy engine (MySQL + aiomysql)
- AsyncSession factory with transaction management
- SQLAlchemy ORM models
- Models:
  - `Task` - Task data model
  - `PriorityEnum` - Priority enumeration

#### 3. **Schemas** (`schemas.py`)
- Pydantic data validation models
- Request schemas: `TaskCreate`, `TaskUpdate`
- Response schemas: `TaskResponse`, `TaskList`
- Field validation with custom validators
- ORM mode for automatic conversion

#### 4. **Task Routes** (`routes/tasks.py`)
- GET /tasks - List with pagination/filtering
- POST /tasks - Create new task
- GET /tasks/{task_id} - Fetch single
- PUT /tasks/{task_id} - Update (partial)
- DELETE /tasks/{task_id} - Delete

## Database Schema

### Task Table
```sql
CREATE TABLE tasks (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  description VARCHAR(500),
  priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
  completed BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_priority (priority),
  INDEX idx_completed (completed)
);
```

### Field Specifications
| Column | Type | Validation | Notes |
|--------|------|-----------|-------|
| id | INT | Auto-increment | Primary key |
| title | VARCHAR(100) | min=1, max=100, required | Cannot be whitespace |
| description | VARCHAR(500) | max=500, optional | Can be NULL |
| priority | ENUM | low/medium/high | Default: medium |
| completed | BOOLEAN | true/false | Default: false |
| created_at | DATETIME | Auto | Set on insert |
| updated_at | DATETIME | Auto | Updated on modify |

## Key Features

### Pagination
```python
# Query parameters
page: int = 1              # Page number (1-indexed)
per_page: int = 10         # Items per page (max 100)

# Response includes total count
{
  "tasks": [...],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

### Filtering
```python
# Optional filters
completed: Optional[bool] = None    # Filter by status
priority: Optional[Priority] = None # Filter by priority

# Examples
GET /tasks?completed=true              # Only completed
GET /tasks?priority=high                # Only high priority
GET /tasks?page=2&per_page=20          # Pagination
```

### Validation

**Title Validation:**
```python
@validator('title')
def title_must_not_be_empty(cls, v):
    if not v.strip():
        raise ValueError('Title cannot be empty or whitespace')
    return v.strip()
```

**Updates:**
- All fields optional in update
- Partial updates supported
- Only set fields are updated

### ORM Mapping
```python
class Config:
    from_attributes = True  # Enable ORM mode
```

Allows automatic conversion from SQLAlchemy models to Pydantic schemas.

## API Endpoints

```
GET /                                  200  Root endpoint
GET /api/status                        200  Service status

GET /tasks                             200  List all tasks
  Query: page=1, per_page=10
  Query: completed=true/false
  Query: priority=low|medium|high

POST /tasks                            201  Create task
  Body: { title, description?, priority? }

GET /tasks/{task_id}                   200  Get single task
PUT /tasks/{task_id}                   200  Update task
  Body: { title?, description?, priority?, completed? }

DELETE /tasks/{task_id}                204  Delete task
```

## Response Models

### Task Response
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Complete FastAPI course",
  "priority": "high",
  "completed": false,
  "created_at": "2024-02-26T10:30:00",
  "updated_at": "2024-02-26T10:30:00"
}
```

### List Response
```json
{
  "tasks": [
    { "id": 1, "title": "Task 1", ... },
    { "id": 2, "title": "Task 2", ... }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

### Error Response
```json
{
  "detail": "Task not found"
}
```

## Dependencies

```
fastapi              >= 0.100
uvicorn             >= 0.23
sqlalchemy          >= 2.0
aiomysql            >= 0.2        # MySQL async driver
aiosqlite           >= 0.17        # SQLite async driver (alternative)
pydantic            >= 2.0
python-multipart    >= 0.0.5
```

## Configuration

### Database URLs
```python
# MySQL (Production)
DATABASE_URL = "mysql+aiomysql://root:Test1234@localhost:3306/tasks_db"

# SQLite (Development)
DATABASE_URL = "sqlite+aiosqlite:///./tasks.db"
```

### Environment Variables
```env
DB_USER=root
DB_PASSWORD=Test1234
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tasks_db
```

## Database Operations

### Session Management
```python
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Query Examples

**List with filtering:**
```python
query = select(Task)

if completed is not None:
    query = query.where(Task.completed == completed)
if priority:
    query = query.where(Task.priority == priority)

result = await db.execute(query)
tasks = result.scalars().all()
```

**Count:**
```python
count_query = select(func.count()).select_from(query.subquery())
total = (await db.execute(count_query)).scalar()
```

**Pagination:**
```python
query = query.offset((page - 1) * per_page).limit(per_page)
```

## Error Handling

| Status | Condition | Message |
|--------|-----------|---------|
| 404 | Task not found | "Task not found" |
| 422 | Invalid input | Pydantic validation error |
| 500 | Database error | Database exception |

## Scaling Considerations

### Current Architecture
```
Single FastAPI Instance
    ↓
SQLAlchemy AsyncSession
    ↓
Connection Pool (10-20 connections)
    ↓
MySQL Database (single instance)
```

### Scaling Strategy
1. **Horizontal Scaling:**
   - Load balancer (nginx)
   - Multiple FastAPI instances

2. **Database:**
   - MySQL replication (master-slave)
   - Read replicas for GET requests
   - Write to master

3. **Caching:**
   - Add Redis for frequently accessed tasks
   - Cache popular filters/pages

4. **Indexing:**
   - Index on `priority` and `completed`
   - Composite index for filtering

## Performance Optimization

### Current Performance
| Operation | Time | Notes |
|-----------|------|-------|
| GET /tasks (10 items) | 10-50ms | With DB query |
| POST /tasks | 5-20ms | Insert + auto_increment |
| PUT /tasks/{id} | 5-20ms | Update + timestamp |
| DELETE /tasks/{id} | 5-20ms | Delete operation |

### Optimization Opportunities
- Database indexing
- Query result caching
- Batch operations
- Connection pooling tuning
- Lazy loading vs eager loading

## Testing Strategy

```python
# Unit Tests
def test_create_task():
    # Test task creation with valid data

def test_create_task_invalid():
    # Test validation (empty title, etc.)

def test_list_tasks_pagination():
    # Test page and per_page parameters

def test_filter_tasks():
    # Test completed and priority filters

def test_update_partial():
    # Test partial updates

def test_delete_task():
    # Test deletion

# Integration Tests
async def test_crud_workflow():
    # Create → Read → Update → Delete flow

async def test_concurrent_operations():
    # Multiple concurrent requests
```

## Known Issues & TODOs

- [ ] Add soft delete (archive instead of permanent delete)
- [ ] Implement search/full-text search
- [ ] Add activity logging (audit trail)
- [ ] Support bulk operations
- [ ] Add attachment support
- [ ] Implement webhooks for changes
- [ ] Add caching layer (Redis)
- [ ] Database migration tool (Alembic)

## Startup/Shutdown Process

```
Startup:
  ├─ Connect to MySQL
  ├─ Create table if not exists
  ├─ Initialize connection pool
  └─ Ready to serve

Shutdown:
  ├─ Close active connections
  ├─ Commit pending transactions
  └─ Dispose engine
```

## Monitoring

### Key Metrics
- Query execution time
- Connection pool utilization
- Error rates
- Task creation/deletion rates
- Pagination usage patterns

### Health Checks
- Database connectivity
- Table existence
- Connection pool status

## Security Considerations

### Current Implementation
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy parameterized queries)
- No authentication (public API)

### Recommendations
- Add authentication (see JWT project)
- Implement row-level security
- Add rate limiting
- Input sanitization
- Request logging

## Related Projects
- **JWT** - Add authentication to this API
- **Async_API_aggregator** - Async patterns
- **task_caching** - Background tasks
