"""
SQLAlchemy models + DB initialisation for the auth system.
PostgreSQL is run via Docker
"""

from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

load_dotenv()

# ── Database URL (override via .env) ──────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "AUTH_DATABASE_URL",
    "postgresql://chatops_user:chatops_password@localhost:5432/chatops_auth",
)

# ── Engine + Session ─────────────────────────────────────────────────────────
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ── Base class ───────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ── Enums ────────────────────────────────────────────────────────────────────
import enum as _enum

class UserRole(_enum.Enum):
    root_admin = "root_admin"
    admin = "admin"
    user = "user"


# ── ORM Models ───────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
 
    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(String(64),  unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role          = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    is_active     = Column(Boolean, default=True, nullable=False)
    created_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login    = Column(DateTime, nullable=True)
 
    sessions      = relationship("Session", back_populates="user",
                                 cascade="all, delete-orphan")
    audit_logs    = relationship("AuditLog", back_populates="user",
                                 cascade="all, delete-orphan")
 
    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role.value}>"


class Session(Base):
    __tablename__ = "sessions"
 
    id            = Column(Integer, primary_key=True, autoincrement=True)
    session_id    = Column(String(128), unique=True, nullable=False, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at    = Column(DateTime, nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    request_count = Column(Integer, default=0, nullable=False)
 
    user          = relationship("User", back_populates="sessions")
 
    def __repr__(self) -> str:
        return f"<Session {self.session_id!r} user_id={self.user_id}>"
 
 
class AuditLog(Base):
    __tablename__ = "audit_logs"
 
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(128), nullable=True)
    action     = Column(String(256), nullable=False)
    details    = Column(String(1024), nullable=True)
    timestamp  = Column(DateTime, default=datetime.utcnow, nullable=False)
 
    user       = relationship("User", back_populates="audit_logs")
 
    def __repr__(self) -> str:
        return f"<AuditLog user_id={self.user_id} action={self.action!r}>"


# ── Helpers ───────────────────────────────────────────────────────────────────
 
def init_db() -> None:
    """Create all tables (idempotent)."""
    Base.metadata.create_all(bind=engine)
 
 
def get_db():
    """Yield a DB session — use as a context manager or in a with-block."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()