import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base, DATABASE_URL
from models import KiteSchool  # Import the new model

async def update_db():
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    # Create the new table
    async with engine.begin() as conn:
        # This is the correct way to create tables with async SQLAlchemy
        await conn.run_sync(Base.metadata.create_all)
    
    # Close engine
    await engine.dispose()
    
    print("Database schema updated successfully with kiteschools table!")

if __name__ == "__main__":
    asyncio.run(update_db())