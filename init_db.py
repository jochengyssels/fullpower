import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base, DATABASE_URL
from models import User, KiteSpot, FavoriteSpot, KiteSession

async def init_db():
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    # Create all tables
    async with engine.begin() as conn:
        # Comment out the drop_all line in production to avoid data loss
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Close engine
    await engine.dispose()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())