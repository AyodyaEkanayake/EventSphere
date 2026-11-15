
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Get database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./eventsphere.db"
)

# Convert Render PostgreSQL URLs to the psycopg driver format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
class Base(DeclarativeBase):
    pass

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()