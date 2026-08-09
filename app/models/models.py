from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    github_username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-Many Relationship: One user can have many projects
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    tech_stack = Column(String, nullable=False)  # Comma-separated or string (e.g. "Python, FastAPI, PostgreSQL")
    github_url = Column(String, nullable=True)
    live_url = Column(String, nullable=True)
    status = Column(String, default="in_progress")  # in_progress, completed, planned
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key link to User
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")