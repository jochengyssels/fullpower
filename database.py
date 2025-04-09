import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

logger = logging.getLogger("railway-app.database")

# Create Base class for models
Base = declarative_base()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL environment variable is not set! Using default connection string.")
    DATABASE_URL = "postgresql+asyncpg://kiteuser:fullpower@localhost/kitesurf"
else:
    # If using Railway's PostgreSQL, the URL might need to be modified
    # Railway provides a postgres:// URL, but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info(f"Using database URL: {DATABASE_URL.split('@')[0]}@...")

# Create async engine with simplified parameters
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}", exc_info=True)
    raise

# Create async session factory
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_db():
    """
    Dependency that provides a database session
    """
    session = async_session_factory()
    try:
        logger.debug("Database session created")
        yield session
    finally:
        logger.debug("Database session closed")
        await session.close()
