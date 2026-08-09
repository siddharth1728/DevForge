from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.config.config import DATABASE_URL

# Create the SQLAlchemy database engine
# connect_args={"check_same_thread": False} is required only for SQLite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

# SessionLocal class will be instantiated to create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for our SQLAlchemy ORM models
Base = declarative_base()

# Dependency to get DB session per HTTP request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()