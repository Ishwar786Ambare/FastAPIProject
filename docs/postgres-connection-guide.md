# FastAPI + PostgreSQL Connection Guide

A comprehensive step-by-step guide to connect PostgreSQL database with your FastAPI application.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Database Setup](#database-setup)
5. [Configuration](#configuration)
6. [Implementation](#implementation)
7. [Testing](#testing)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

### System Architecture

![FastAPI PostgreSQL Architecture](./fastapi_postgres_architecture.png)

The connection flow follows this pattern:

1. **Client Request** → HTTP request from frontend/client
2. **FastAPI Route** → Endpoint handler processes the request
3. **Database Session** → `get_db()` dependency provides database connection
4. **CRUD Functions** → Business logic layer for database operations
5. **SQLAlchemy ORM** → Object-Relational Mapping layer
6. **PostgreSQL Database** → Persistent data storage

### Data Flow

![Setup Workflow](./setup_workflow.png)

---

## 🔧 Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed
- **PostgreSQL** installed locally OR access to a cloud PostgreSQL instance
- **Virtual environment** (recommended)
- **Basic understanding** of:
  - FastAPI fundamentals
  - Database concepts (tables, relationships)
  - Python type hints

---

## 📦 Installation

### Step 1: Install Required Packages

Activate your virtual environment and install dependencies:

```bash
# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install sqlalchemy psycopg2-binary python-dotenv
```

**Package Breakdown:**

| Package | Purpose |
|---------|---------|
| `sqlalchemy` | ORM (Object-Relational Mapping) framework |
| `psycopg2-binary` | PostgreSQL adapter for Python |
| `python-dotenv` | Load environment variables from `.env` file |

### Step 2: Update Requirements

```bash
pip freeze > requirements.txt
```

---

## 🗄️ Database Setup

### Option A: Local PostgreSQL

1. **Download and Install** PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

2. **Create Database:**

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create new database
CREATE DATABASE fastapi_db;

-- Create user (optional)
CREATE USER fastapi_user WITH PASSWORD 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
```

### Option B: Cloud PostgreSQL (Recommended for Beginners)

Choose a free tier from:

- **[Neon](https://neon.tech)** - Serverless PostgreSQL
- **[Supabase](https://supabase.com)** - PostgreSQL with extras
- **[ElephantSQL](https://www.elephantsql.com)** - PostgreSQL as a service

They provide a connection string like:
```
postgresql://username:password@host:port/database_name
```

---

## ⚙️ Configuration

### Step 1: Update `.env` File

Create or update your `.env` file in the project root:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_db

# For cloud databases, use the provided connection string:
# DATABASE_URL=postgresql://user:pass@host.region.provider.com:5432/dbname
```

> **⚠️ Security Warning:** Never commit `.env` files to version control. Add it to `.gitignore`.

### Step 2: Create `.gitignore`

Ensure your `.gitignore` includes:

```
.env
__pycache__/
*.pyc
venv/
```

---

## 💻 Implementation

### Step 1: Create `database.py`

This file manages database connections and sessions.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
# echo=True enables SQL query logging (disable in production)
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
# Each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

# Dependency function to get database session
def get_db():
    """
    Provides a database session for each request.
    
    Usage:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            # db is automatically provided and cleaned up
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Key Concepts Explained:**

- **Engine**: Manages connections to the database
- **SessionLocal**: Factory for creating database sessions
- **Base**: Base class that all ORM models inherit from
- **get_db()**: Dependency injection function for FastAPI routes

### Step 2: Create `db_models.py`

SQLAlchemy models define your database schema.

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class DBUser(Base):
    """
    User table in the database
    
    Attributes:
        id: Primary key
        name: User's name
        age: User's age (optional)
        signup_ts: Timestamp of user registration
        stocks: Relationship to user's stocks
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    signup_ts = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # One-to-Many relationship: One user can have many stocks
    stocks = relationship("DBStock", back_populates="owner", cascade="all, delete-orphan")


class DBStock(Base):
    """
    Stock table in the database
    
    Attributes:
        id: Primary key
        name: Stock symbol (e.g., AAPL, GOOG)
        price: Current stock price
        quantity: Number of shares
        is_active: Whether the stock is actively tracked
        user_id: Foreign key to users table
        owner: Relationship to user who owns this stock
    """
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-One relationship: Each stock belongs to one user
    owner = relationship("DBUser", back_populates="stocks")
```

### Step 3: Update `model.py` (Pydantic Schemas)

![Pydantic vs SQLAlchemy](./pydantic_vs_sqlalchemy.png)

**Understanding the Difference:**

| Aspect | Pydantic Models | SQLAlchemy Models |
|--------|----------------|-------------------|
| **Purpose** | Data validation & serialization | Database ORM mapping |
| **Used For** | API request/response | Database tables |
| **Location** | `model.py` | `db_models.py` |
| **Validation** | ✅ Automatic | ❌ None |

Add these schemas to your `model.py`:

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List

# ========== USER SCHEMAS ==========

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    name: str = Field(min_length=3, description="User's full name")
    age: Optional[int] = Field(None, ge=0, le=150, description="User's age")
    
    @field_validator('name')
    @classmethod
    def name_must_start_with_capital(cls, value):
        if not value[0].isupper():
            raise ValueError('Name must start with a capital letter')
        return value


class UserResponse(BaseModel):
    """Schema for user responses from database"""
    id: int
    name: str
    age: Optional[int]
    signup_ts: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy compatibility


class UserWithStocks(UserResponse):
    """Schema for user with their stocks"""
    stocks: List['StockResponse'] = []


# ========== STOCK SCHEMAS ==========

class StockCreate(BaseModel):
    """Schema for creating a new stock"""
    name: str = Field(min_length=1, max_length=10, description="Stock symbol")
    price: float = Field(gt=0, description="Stock price (must be positive)")
    quantity: int = Field(gt=0, description="Number of shares")
    is_active: bool = True


class StockResponse(BaseModel):
    """Schema for stock responses from database"""
    id: int
    name: str
    price: float
    quantity: int
    is_active: bool
    user_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 4: Create `crud.py`

CRUD operations encapsulate all database interactions.

```python
from sqlalchemy.orm import Session
from db_models import DBUser, DBStock
from model import UserCreate, StockCreate
from typing import List, Optional

# ==================== USER CRUD ====================

def create_user(db: Session, user: UserCreate) -> DBUser:
    """
    Create a new user in the database
    
    Args:
        db: Database session
        user: UserCreate schema with validated data
    
    Returns:
        Created user object with database-generated ID
    """
    db_user = DBUser(name=user.name, age=user.age)
    db.add(db_user)  # Add to session
    db.commit()  # Commit transaction
    db.refresh(db_user)  # Refresh to get auto-generated fields
    return db_user


def get_user(db: Session, user_id: int) -> Optional[DBUser]:
    """Get a single user by ID"""
    return db.query(DBUser).filter(DBUser.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[DBUser]:
    """
    Get all users with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    """
    return db.query(DBUser).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user: UserCreate) -> Optional[DBUser]:
    """Update an existing user"""
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user:
        db_user.name = user.name
        db_user.age = user.age
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user and all their stocks (cascade)"""
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# ==================== STOCK CRUD ====================

def create_stock(db: Session, stock: StockCreate, user_id: int) -> DBStock:
    """
    Create a new stock for a specific user
    
    Args:
        db: Database session
        stock: StockCreate schema with validated data
        user_id: ID of the user who owns this stock
    """
    db_stock = DBStock(
        name=stock.name,
        price=stock.price,
        quantity=stock.quantity,
        is_active=stock.is_active,
        user_id=user_id
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def get_stocks(db: Session, skip: int = 0, limit: int = 100) -> List[DBStock]:
    """Get all stocks with pagination"""
    return db.query(DBStock).offset(skip).limit(limit).all()


def get_user_stocks(db: Session, user_id: int) -> List[DBStock]:
    """Get all stocks owned by a specific user"""
    return db.query(DBStock).filter(DBStock.user_id == user_id).all()


def update_stock(db: Session, stock_id: int, stock: StockCreate) -> Optional[DBStock]:
    """Update an existing stock"""
    db_stock = db.query(DBStock).filter(DBStock.id == stock_id).first()
    if db_stock:
        db_stock.name = stock.name
        db_stock.price = stock.price
        db_stock.quantity = stock.quantity
        db_stock.is_active = stock.is_active
        db.commit()
        db.refresh(db_stock)
    return db_stock


def delete_stock(db: Session, stock_id: int) -> bool:
    """Delete a specific stock"""
    db_stock = db.query(DBStock).filter(DBStock.id == stock_id).first()
    if db_stock:
        db.delete(db_stock)
        db.commit()
        return True
    return False
```

### Step 5: Update `main.py`

Integrate everything into your FastAPI application:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import db_models
import crud
from model import UserCreate, UserResponse, StockCreate, StockResponse, UserWithStocks
from typing import List

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI + PostgreSQL API",
    description="A complete API with PostgreSQL integration",
    version="1.0.0"
)

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== USER ENDPOINTS ====================

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user
    
    - **name**: User's name (required, min 3 chars, must start with capital)
    - **age**: User's age (optional, 0-150)
    """
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=UserWithStocks)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID with their stocks"""
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return db_user


@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100)
    """
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return users


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """Update an existing user"""
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Delete a user and all their stocks"""
    success = crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )


# ==================== STOCK ENDPOINTS ====================

@app.post("/users/{user_id}/stocks/", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
def create_stock_for_user(
    user_id: int,
    stock: StockCreate,
    db: Session = Depends(get_db)
):
    """
    Create a stock for a specific user
    
    - **name**: Stock symbol (e.g., AAPL, GOOG)
    - **price**: Stock price (must be positive)
    - **quantity**: Number of shares (must be positive)
    - **is_active**: Whether to actively track this stock
    """
    # Verify user exists
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return crud.create_stock(db=db, stock=stock, user_id=user_id)


@app.get("/stocks/", response_model=List[StockResponse])
def read_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stocks from all users"""
    stocks = crud.get_stocks(db=db, skip=skip, limit=limit)
    return stocks


@app.get("/users/{user_id}/stocks/", response_model=List[StockResponse])
def read_user_stocks(user_id: int, db: Session = Depends(get_db)):
    """Get all stocks for a specific user"""
    return crud.get_user_stocks(db=db, user_id=user_id)


@app.put("/stocks/{stock_id}", response_model=StockResponse)
def update_stock_endpoint(stock_id: int, stock: StockCreate, db: Session = Depends(get_db)):
    """Update an existing stock"""
    db_stock = crud.update_stock(db=db, stock_id=stock_id, stock=stock)
    if db_stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with ID {stock_id} not found"
        )
    return db_stock


@app.delete("/stocks/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock_endpoint(stock_id: int, db: Session = Depends(get_db)):
    """Delete a specific stock"""
    success = crud.delete_stock(db=db, stock_id=stock_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with ID {stock_id} not found"
        )


# ==================== ROOT ENDPOINT ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "FastAPI with PostgreSQL is running!",
        "status": "healthy",
        "database": "connected"
    }
```

---

## 🧪 Testing

### Step 1: Start the Server

```bash
# Make sure you're in the project directory
cd c:\Users\ishwa\PycharmProjects\FastAPIProject

# Activate virtual environment
.\venv\Scripts\activate

# Start FastAPI server
uvicorn main:app --reload
```

### Step 2: Access Interactive Docs

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Step 3: Test API Endpoints

#### Create a User

**POST** `/users/`

```json
{
  "name": "John Doe",
  "age": 30
}
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30,
  "signup_ts": "2026-01-31T13:00:00.000Z"
}
```

#### Create a Stock for User

**POST** `/users/1/stocks/`

```json
{
  "name": "AAPL",
  "price": 175.50,
  "quantity": 10,
  "is_active": true
}
```

#### Get User with Stocks

**GET** `/users/1`

```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30,
  "signup_ts": "2026-01-31T13:00:00.000Z",
  "stocks": [
    {
      "id": 1,
      "name": "AAPL",
      "price": 175.50,
      "quantity": 10,
      "is_active": true,
      "user_id": 1,
      "created_at": "2026-01-31T13:05:00.000Z"
    }
  ]
}
```

---

## ✅ Best Practices

### 1. **Dependency Injection**

Always use `Depends(get_db)` for database sessions:

```python
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    # db is automatically created and cleaned up
    return crud.get_users(db)
```

### 2. **Separate Concerns**

Keep models separate:
- **Pydantic** (`model.py`) - API validation
- **SQLAlchemy** (`db_models.py`) - Database schema

### 3. **Error Handling**

Always handle missing records:

```python
db_user = crud.get_user(db, user_id)
if not db_user:
    raise HTTPException(status_code=404, detail="User not found")
```

### 4. **Environment Variables**

Never hardcode credentials:

```python
# ❌ Bad
DATABASE_URL = "postgresql://user:pass@localhost/db"

# ✅ Good
DATABASE_URL = os.getenv("DATABASE_URL")
```

### 5. **Use Transactions**

SQLAlchemy handles this automatically with `commit()` and `rollback()`:

```python
try:
    db.add(new_user)
    db.commit()
except Exception:
    db.rollback()
    raise
```

### 6. **Add Indexes**

Use indexes on frequently queried columns:

```python
name = Column(String, index=True)  # Creates database index
```

---

## 🐛 Troubleshooting

### Issue 1: Connection Refused

**Error:** `could not connect to server`

**Solutions:**
- ✅ Check if PostgreSQL is running
- ✅ Verify DATABASE_URL in `.env`
- ✅ Test connection with `psql` or pgAdmin

```bash
# Test PostgreSQL connection
psql -U postgres -h localhost -p 5432
```

### Issue 2: Table Doesn't Exist

**Error:** `relation "users" does not exist`

**Solutions:**
- ✅ Ensure `Base.metadata.create_all(bind=engine)` is called
- ✅ Check that models inherit from `Base`
- ✅ Restart the server

### Issue 3: Import Errors

**Error:** `No module named 'database'`

**Solutions:**
- ✅ Check file is named `database.py`
- ✅ Ensure you're in the project directory
- ✅ Verify virtual environment is activated

### Issue 4: Authentication Failed

**Error:** `password authentication failed`

**Solutions:**
- ✅ Check username and password in DATABASE_URL
- ✅ Reset PostgreSQL password if needed
- ✅ Use correct database name

### Issue 5: Port Already in Use

**Error:** `Address already in use`

**Solutions:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <pid> /F
```

---

## 📚 Project Structure

After implementation, your project should look like this:

```
FastAPIProject/
├── docs/
│   ├── postgres-connection-guide.md
│   ├── fastapi_postgres_architecture.png
│   ├── pydantic_vs_sqlalchemy.png
│   └── setup_workflow.png
├── venv/
├── .env                    # Environment variables
├── .gitignore
├── database.py             # Database configuration
├── db_models.py            # SQLAlchemy ORM models
├── model.py                # Pydantic schemas
├── crud.py                 # CRUD operations
├── main.py                 # FastAPI application
└── requirements.txt
```

---

## 🚀 Next Steps

### Database Migrations with Alembic

For production apps, use Alembic to manage schema changes:

```bash
pip install alembic
alembic init alembic
```

### Add Authentication

Implement JWT authentication for secure APIs:

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### Add Testing

Write tests for your API:

```bash
pip install pytest httpx
```

### Deploy to Production

Consider deployment platforms:
- **Render** (render.com)
- **Railway** (railway.app)
- **Heroku** (heroku.com)

---

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🤝 Need Help?

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
3. Explore [SQLAlchemy Tutorials](https://docs.sqlalchemy.org/en/20/tutorial/)

---

**Created:** January 31, 2026  
**Version:** 1.0.0  
**Author:** FastAPI PostgreSQL Integration Guide
