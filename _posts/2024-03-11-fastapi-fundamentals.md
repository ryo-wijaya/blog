---
layout: post
title: "FastAPI Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for FastAPI fundamentals. Covers routing, Pydantic v2, dependency injection, middleware, error handling, database integration, JWT auth, and testing.
author: ryo
date: 2024-03-11 00:26:09 +0800
categories: [Software Engineering]
tags: [python, fastapi, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Project Setup

Install FastAPI with Uvicorn. Swagger UI is auto-served at `/docs` and ReDoc at `/redoc`.

```bash
pip install fastapi "uvicorn[standard]" pydantic
```

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "hello"}
```

```bash
uvicorn main:app --reload              # dev server, hot reload
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 1.1. Recommended Project Layout

```
app/
├── main.py
├── routers/
│   ├── users.py
│   └── items.py
├── schemas/           # Pydantic request/response models
│   └── user.py
├── db/
│   ├── database.py    # engine, session factory
│   └── models.py      # SQLAlchemy ORM models
├── dependencies.py    # shared Depends functions
└── config.py          # settings via pydantic-settings
```

---

## 2. Path & Query Parameters

FastAPI infers parameter source from the function signature: path params must match the route template; everything else becomes a query param.

```python
from fastapi import FastAPI, Query, Path

app = FastAPI()

# Path parameter - type is validated automatically
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}

# Query parameters - any non-path param becomes a query param
@app.get("/users")
def list_users(
    page: int = 1,
    size: int = Query(default=10, ge=1, le=100),   # with validation
    name: str | None = None,                        # optional
):
    return {"page": page, "size": size, "name": name}

# GET /users?page=2&size=20&name=ryo

# Path with validation
@app.get("/items/{item_id}")
def get_item(item_id: int = Path(ge=1)):
    return {"item_id": item_id}
```

---

## 3. Request Body & Pydantic v2

Declare a Pydantic `BaseModel` as the body parameter type. FastAPI parses, validates, and deserializes the JSON body automatically.

```python
from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip()

    @model_validator(mode="after")
    def cross_field_check(self) -> "CreateUserRequest":
        if self.age < 18 and not self.email.endswith(".edu"):
            raise ValueError("under 18 must use .edu email")
        return self

@app.post("/users", status_code=201)
def create_user(body: CreateUserRequest):
    # body is already parsed and validated
    return {"name": body.name}
```

### 3.1. Pydantic v2 Key Patterns

Key methods for serializing models and constructing them from ORM objects or raw JSON strings.

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}   # allow constructing from ORM objects

user = UserResponse(id=1, name="Ryo", email="ryo@example.com")
user.model_dump()                      # dict
user.model_dump(exclude={"email"})     # exclude fields
user.model_dump_json()                 # JSON string
UserResponse.model_validate(orm_obj)   # from ORM object (requires from_attributes=True)
UserResponse.model_validate_json('{"id":1,"name":"Ryo","email":"x"}')
```

---

## 4. Response Models & Status Codes

Use `response_model` to filter and serialize output. Set `status_code` on the route decorator or return a `JSONResponse` directly for full control.

```python
from fastapi import status
from fastapi.responses import JSONResponse, Response

# response_model filters and serialises output
@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: int): ...

# Explicit status code
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(body: CreateUserRequest): ...

# 204 No Content
@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int):
    return Response(status_code=204)

# Manual response with custom headers
return JSONResponse(
    status_code=200,
    content={"msg": "ok"},
    headers={"X-Custom": "value"}
)

# ResponseEntity-style
from fastapi.responses import Response
from fastapi import Response as FastAPIResponse
```

---

## 5. Dependency Injection

`Depends` is FastAPI's DI system. Dependencies can be functions, classes, or generators (for cleanup).

```python
from fastapi import Depends, Header

# Simple function dependency
def get_current_user(authorization: str = Header(...)):
    return decode_token(authorization)

@app.get("/profile")
def profile(user = Depends(get_current_user)):
    return user

# Class-based dependency
class PaginationParams:
    def __init__(self, page: int = 1, size: int = 10):
        self.page = page
        self.size = size

@app.get("/items")
def list_items(p: PaginationParams = Depends()):
    return {"page": p.page, "size": p.size}

# Generator dependency - yield for cleanup
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sub-dependencies - FastAPI resolves the full chain
def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.removeprefix("Bearer ")
    return db.query(User).filter_by(username=decode_subject(token)).first()

@app.get("/me")
def me(user = Depends(get_current_user)):
    return user
```

---

## 6. Routers

Split routes into `APIRouter` modules and include them in the main app with `include_router()`. Set a `prefix` and `tags` on the router to group related endpoints.

```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def list_users(): ...

@router.get("/{id}")
def get_user(id: int): ...

@router.post("/", status_code=201)
def create_user(body: CreateUserRequest): ...

# main.py
from routers import users, items

app.include_router(users.router)
app.include_router(items.router, prefix="/api/v1")   # override prefix
```

---

## 7. Middleware & CORS

Add middleware with `app.add_middleware()`. Middleware is applied in reverse registration order (last registered runs first).

```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time() - start)
        return response

app.add_middleware(TimingMiddleware)
```

---

## 8. Error Handling

Raise `HTTPException` inline for standard HTTP errors. Register `exception_handler` for domain-specific exceptions to return consistent error shapes.

```python
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Raise HTTP errors inline
@app.get("/users/{id}")
def get_user(id: int):
    user = db.get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Custom exception class + handler
class NotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"{exc.resource} {exc.id} not found"},
    )

# Override default validation error response
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
```

---

## 9. Background Tasks

Inject `BackgroundTasks` to queue work that runs after the response is sent to the client.

```python
from fastapi import BackgroundTasks

def send_welcome_email(to: str):
    # runs after response is sent to client
    print(f"Sending to {to}")

@app.post("/register", status_code=201)
def register(user: CreateUserRequest, background_tasks: BackgroundTasks):
    created = save_user(user)
    background_tasks.add_task(send_welcome_email, user.email)
    return created   # response returns immediately
```

For heavier background work (retries, persistence, scheduling), use Celery or ARQ.

---

## 10. Database with SQLAlchemy

Define engine and session factory in `database.py`, ORM models in `models.py`. Inject a session via `Depends(get_db)` in route handlers.

```python
# db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://user:pass@localhost/mydb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# db/models.py
from sqlalchemy import Column, Integer, String
from db.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String, unique=True)

# Dependency
from db.database import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Router
@router.post("/", status_code=201, response_model=UserResponse)
def create_user(body: CreateUserRequest, db: Session = Depends(get_db)):
    user = UserModel(name=body.name, email=body.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## 11. Authentication - JWT

Install `python-jose` for JWT signing and `passlib` for password hashing.

```bash
pip install "python-jose[cryptography]" "passlib[bcrypt]"
```

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key"    # use env var in production
ALGORITHM = "HS256"
EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(UserModel).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(username=form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}

@app.get("/me")
def me(current_user = Depends(get_current_user)):
    return current_user
```

---

## 12. Testing

Install `pytest` and `httpx`. `TestClient` wraps the ASGI app for synchronous test calls. Override dependencies with `app.dependency_overrides`.

```bash
pip install pytest httpx
```

```python
from fastapi.testclient import TestClient
import pytest
from main import app, get_db

client = TestClient(app)

def test_get_user_returns_200():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_user_invalid_body_returns_422():
    response = client.post("/users", json={"name": "", "email": "not-an-email"})
    assert response.status_code == 422

# Override a dependency in tests
def override_get_db():
    yield test_db

app.dependency_overrides[get_db] = override_get_db

# Fixture-based setup
@pytest.fixture
def client_with_db():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_user(client_with_db):
    res = client_with_db.post("/users", json={"name": "Ryo", "email": "ryo@example.com", "age": 25})
    assert res.status_code == 201
    assert res.json()["name"] == "Ryo"
```

---

## 13. Async vs Sync Routes

FastAPI supports both sync and async route handlers. Use `async def` only with async-compatible libraries; use `def` when calling synchronous code.

```python
import time
import asyncio

# Sync - FastAPI runs in a thread pool automatically (blocking I/O is fine here)
@app.get("/sync")
def sync_endpoint():
    time.sleep(1)     # blocks the thread, not the event loop
    return {"ok": True}

# Async - runs on the event loop (must NOT block)
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)    # non-blocking
    return {"ok": True}
```

- Use `async def` with async-compatible libraries (`asyncpg`, `httpx`, `aioredis`).
- Use `def` (sync) when using synchronous libraries - FastAPI runs them in a thread pool.
- Never call blocking code (`time.sleep`, synchronous DB calls) inside `async def`.

---

## 14. Lifespan Events

Use the `lifespan` context manager for startup and shutdown logic. Yield once to separate the two phases.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - runs before app starts accepting requests
    print("starting up")
    await init_db_pool()
    yield
    # Shutdown - runs on graceful shutdown
    print("shutting down")
    await close_db_pool()

app = FastAPI(lifespan=lifespan)
```

`@app.on_event("startup")` / `@app.on_event("shutdown")` are deprecated - use `lifespan` instead.

---

## 15. Settings with `pydantic-settings`

Load settings from environment variables or a `.env` file. Use `@lru_cache` to avoid re-reading the file on every request.

```bash
pip install pydantic-settings
```

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    allowed_origins: list[str] = []

    model_config = {"env_file": ".env"}   # reads from .env automatically

settings = Settings()

# .env
# DATABASE_URL=postgresql://user:pass@localhost/mydb
# SECRET_KEY=supersecret
```

Inject via dependency:

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

@app.get("/info")
def info(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```
