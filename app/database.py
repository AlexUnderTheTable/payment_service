"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import get_settings


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# Create engine once on module load
settings = get_settings()
engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
