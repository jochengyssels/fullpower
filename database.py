import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set!")
    # Instead of falling back to SQLite, we'll use a dummy URL that will fail gracefully
    DATABASE_URL = "postgresql+asyncpg://kiteuser:fullpower@localhost/kitesurf"
    
# Convert postgres:// to postgresql:// (Railway uses postgres://)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Convert to async URL if needed
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

logger.info(f"Using database URL: {DATABASE_URL.split('@')[0]}@...")

# Create async engine with better error handling
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        # Configure connection pool for Railway
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections after 30 minutes
        # Increase connect_timeout for Railway
        connect_args={
            "command_timeout": 30,
            "timeout": 30
        } if DATABASE_URL.startswith("postgresql") else {}
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    # Create a dummy engine that will fail gracefully
    # This allows the app to start even without a working database
    engine = create_async_engine(
        "postgresql+asyncpg://kiteuser:fullpower@localhost/kitesurf",
        echo=False,
        future=True,
    )
    logger.warning("Created dummy engine - database operations will fail until connection is fixed")

# Create async session
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for all models
Base = declarative_base()

# Async context manager for database sessions
async def get_db():
    """Async context manager for database sessions"""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        await session.close()

# Function to initialize database (create tables)
async def init_db():
    """Initialize database tables"""
    try:
        # Import all models here to ensure they're registered with Base
        # from models import KiteSpot, WeatherData  # Adjust import based on your models
        
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Drop all tables if needed (be careful with this in production!)
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.exception("Full exception details:")
        return False

# Function to check database connection
async def check_db_connection():
    """Check if database connection is working"""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

# Dependency for FastAPI
async def get_db_session():
    """Dependency for FastAPI to get a database session"""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            # Re-raise the exception to be handled by FastAPI
            raise
        finally:
            await session.close()