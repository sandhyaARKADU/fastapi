# JWT Authentication API - Project Analysis

## Overview
Secure task management system with JWT authentication, user registration/login, and per-user task isolation.

## Architecture

### Components

#### 1. **Main Application** (`main.py`)
- FastAPI initialization
- Database setup on startup
- Auth and task router registration
- Health check endpoints
- Documentation: `/docs`

#### 2. **Authentication Module** (`auth.py`)
- JWT token generation and verification
- Password hashing with bcrypt
- Token expiration management
- Functions:
  - `hash_password()` - Bcrypt hashing
  - `verify_password()` - Compare plain vs hashed
  - `create_access_token()` - Generate 30-min token
  - `create_refresh_token()` - Generate 7-day token
  - `decode_token()` - Verify and extract claims

#### 3. **Database Layer** (`database.py`)
- Async SQLAlchemy (MySQL)
- Two models:
  - `User` - User accounts with credentials
  - `Task` - User-owned tasks
- Session management

#### 4. **Dependency Injection** (`dependencies.py`)
- `get_current_user()` - Extract user from JWT
- OAuth2 bearer scheme
- Token validation
- User database lookup

#### 5. **Schemas** (`schemas.py`)
- User schemas: `UserCreate`, `UserResponse`
- Task schemas: `TaskCreate`, `TaskResponse`
- Token schema: `TokenResponse`

#### 6. **Routes** (`routes/`)
- `auth.py` - Registration, login, profile
- `tasks.py` - User-specific task CRUD

## Authentication Flow

### Registration
```
User Request
  ├─ POST /auth/register
  │   ├─ { username, email, password }
  │
  ├─ Validate email uniqueness
  ├─ Validate username uniqueness
  ├─ Hash password with bcrypt
  ├─ Store User in database
  └─ Return UserResponse (201)
```

### Login
```
User Request
  ├─ POST /auth/login
  │   ├─ OAuth2 form: { username, password }
  │
  ├─ Query user by email
  ├─ Verify password (bcrypt.verify)
  ├─ Generate access token (30 min)
  ├─ Generate refresh token (7 days)
  └─ Return TokenResponse
```

### Protected Request
```
Client Request
  ├─ GET /tasks
  ├─ Header: Authorization: Bearer <access_token>
  │
  ├─ Extract token from header
  ├─ Decode JWT (verify signature)
  ├─ Extract user_id from payload
  ├─ Query user from database
  ├─ Dependency returns current_user
  └─ Return user's tasks
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_username (username)
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  description VARCHAR(500),
  priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
  completed BOOLEAN DEFAULT FALSE,
  owner_id INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_owner (owner_id),
  INDEX idx_priority (priority)
);
```

### Field Details

**Users:**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | INT | PRIMARY KEY | User identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| email | VARCHAR(100) | UNIQUE, NOT NULL | Email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hash |
| created_at | DATETIME | DEFAULT NOW | Registration time |

**Tasks:**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| id | INT | PRIMARY KEY | Task identifier |
| title | VARCHAR(100) | NOT NULL | Task name |
| description | VARCHAR(500) | | Task details |
| priority | ENUM | DEFAULT 'medium' | Priority level |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |
| owner_id | INT | FOREIGN KEY (users.id) | Task owner (isolation) |
| created_at | DATETIME | DEFAULT NOW | Creation time |
| updated_at | DATETIME | ON UPDATE | Last modification |

## JWT Token Structure

### Access Token (30 minutes)
```json
{
  "sub": "1",                      // User ID (string)
  "type": "access",                // Token type
  "exp": 1708950600,               // Expiration timestamp
  "iat": 1708948800                // Issued at timestamp
}
```

### Refresh Token (7 days)
```json
{
  "sub": "1",
  "type": "refresh",
  "exp": 1709553600,               // 7 days later
  "iat": 1708948800
}
```

### Token Details
| Claim | Value | Purpose |
|-------|-------|---------|
| sub | user_id | Subject (user identifier) |
| type | access/refresh | Distinguish token types |
| exp | timestamp | Expiration time |
| iat | timestamp | Issued at time |
| alg | HS256 | Signing algorithm |

## API Endpoints

### Authentication Endpoints
```
POST /auth/register                201  Create new user
  Body: { username, email, password }
  
  Response:
  {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "created_at": "2024-02-26T10:30:00"
  }

POST /auth/login                   200  Authenticate user
  Body (OAuth2): { username, password }
  
  Response:
  {
    "access_token": "eyJ0eXA...",
    "refresh_token": "eyJ0eXA...",
    "token_type": "bearer"
  }

GET /auth/me                       200  Get current user profile
  Header: Authorization: Bearer <token>
  
  Response: { id, username, email, created_at }
```

### Task Endpoints (Authenticated)
```
GET /tasks                         200  List user's tasks
  Header: Authorization: Bearer <token>
  Query: page=1, per_page=10
  
  Response:
  {
    "tasks": [...],
    "total": 10,
    "page": 1,
    "per_page": 10
  }

POST /tasks                        201  Create task for user
  Header: Authorization: Bearer <token>
  Body: { title, description?, priority? }
  
  Response: { id, title, description, priority, completed, owner_id, ... }
```

## Security Implementation

### Password Security
```python
# Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash_password("secret123")
# bcrypt with cost factor 12, 2^12 = 4096 iterations

# Verification
verify_password("secret123", stored_hash)
# Constant-time comparison prevents timing attacks
```

### JWT Security
```python
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

# Token generation
jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Token verification
jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# Validates signature and expiration
```

### Authentication Dependency
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Decode token (verify signature & expiration)
    payload = decode_token(token)
    
    # Extract user_id
    user_id = payload.get("sub")
    
    # Fetch user from database
    user = await db.execute(select(User).where(User.id == user_id))
    
    # Return user or raise 401
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return user
```

## User Isolation (Security)

### Task Ownership
Each task is owned by a user via `owner_id` foreign key.

```python
# When creating task
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user)  # Authenticated user
):
    task = Task(
        **task_data.model_dump(),
        owner_id=current_user.id  # Auto-bind to current user
    )
    db.add(task)
    await db.commit()
    return task
```

### Task Listing
Tasks are filtered by current user:

```python
@router.get("/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user)
):
    # Only return current user's tasks
    query = select(Task).where(Task.owner_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()
```

## Dependencies

```
fastapi              >= 0.100
uvicorn             >= 0.23
sqlalchemy          >= 2.0
aiomysql            >= 0.2
pydantic            >= 2.0
pydantic[email]     >= 2.0        # EmailStr validation
python-jose[cryptography]         # JWT handling
passlib[bcrypt]     >= 1.7.4      # Password hashing
python-multipart    >= 0.0.5      # OAuth2 forms
```

## Configuration

### Environment Variables
```env
# Database
DB_USER=root
DB_PASSWORD=Test1234
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tasks_db

# Security (CRITICAL - change in production!)
SECRET_KEY=your-secret-key-change-in-production

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Hardcoded Configuration
```python
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)
```

## Error Handling

| Status | Endpoint | Condition | Message |
|--------|----------|-----------|---------|
| 201 | POST /auth/register | Success | User object |
| 409 | POST /auth/register | Email exists | "Email already registered" |
| 409 | POST /auth/register | Username exists | "Username already taken" |
| 200 | POST /auth/login | Success | Tokens |
| 401 | POST /auth/login | Invalid creds | "Invalid credentials" |
| 401 | GET /tasks | Invalid token | "Could not validate credentials" |
| 401 | GET /tasks | Expired token | "Could not validate credentials" |
| 200 | GET /auth/me | Success | User object |
| 401 | GET /auth/me | Invalid token | "Could not validate credentials" |

## Testing Strategy

```python
# Unit Tests
async def test_hash_password():
    # Verify bcrypt works correctly

async def test_create_access_token():
    # Verify token generation

async def test_decode_token():
    # Verify token verification

async def test_token_expiration():
    # Verify expired token rejected

# Integration Tests
async def test_register_new_user():
    # Register → Verify in DB

async def test_login_user():
    # Login → Get tokens

async def test_protected_endpoint():
    # Request with token → Success
    # Request without token → 401

async def test_user_isolation():
    # User A can't see User B's tasks

async def test_invalid_credentials():
    # Invalid password → 401
    # Non-existent email → 401

async def test_token_expiration():
    # Expired token → 401
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Register | 50-100ms | Bcrypt hashing (cost=12) |
| Login | 50-100ms | Bcrypt verify |
| Protected request | 5-20ms | Token decode + DB lookup |
| Get user tasks | 10-50ms | DB query + filter |

## Scaling Considerations

### Current Architecture
```
Client
  ├─ POST /auth/register (bcrypt heavy)
  ├─ POST /auth/login (bcrypt heavy)
  └─ GET /tasks (with JWT verification)
       ↓
   Single FastAPI Instance
       ↓
   Single MySQL Database
```

### Scaling Strategy

1. **Bcrypt Performance:**
   - Bcrypt is CPU-intensive (intentional)
   - Use multiple workers (Gunicorn)
   - Consider JWT without database lookup (stateless)

2. **Horizontal Scaling:**
   - Load balancer (nginx)
   - Multiple FastAPI instances with shared DB
   - Sticky sessions not needed (stateless)

3. **Database:**
   - MySQL replication for read scaling
   - User queries on read replicas

4. **Caching:**
   - Cache user lookups after login
   - Redis session store (optional)

## Known Issues & TODOs

- [ ] Add refresh token endpoint
- [ ] Implement token refresh flow
- [ ] Add email verification
- [ ] Password reset workflow
- [ ] Role-based access control (admin, user)
- [ ] Session management / logout endpoint
- [ ] 2FA (two-factor authentication)
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Rate limiting on auth endpoints
- [ ] Audit logging (login attempts, etc.)
- [ ] IP whitelist/blacklist

## Security Checklist

- [x] Bcrypt password hashing
- [x] JWT token validation
- [x] User isolation per request
- [x] SQL injection prevention (SQLAlchemy)
- [x] CORS not overly permissive
- [ ] HTTPS/TLS required (deployment)
- [ ] Strong SECRET_KEY (change default)
- [ ] Rate limiting on auth
- [ ] Audit logging
- [ ] Password complexity requirements
- [ ] Account lockout after failures

## Related Projects
- **CRUD_API** - Basic task management
- **task_caching** - Background tasks with auth
- **Async_API_aggregator** - Async patterns
