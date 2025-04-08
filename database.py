from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import TIMESTAMP

# Load environment variables
load_dotenv()

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://kiteuser:fullpower@localhost/kitesurf")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "server_settings": {
            "timezone": "UTC"
        }
    }postgresql+asyncpg://kiteuser:fullpower@localhost/kitesurf
)

# SessionLocal class
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()