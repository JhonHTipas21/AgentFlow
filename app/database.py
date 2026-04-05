"""
AgentFlow Database Connection
Engine creation, session factory, and dependency injection.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def _create_engine():
    """Create the appropriate engine based on DATABASE_URL."""
    url = settings.DATABASE_URL

    if "sqlite" in url:
        # SQLite for local development
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG,
        )
    else:
        # PostgreSQL for production
        return create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )


engine = _create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: yields a DB session and auto-closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (for development/testing)."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
