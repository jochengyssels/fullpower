import asyncio
import logging
from sqlalchemy import text
from database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_kitespots():
    """Reset only the kitespots table"""
    logger.info("Starting kitespots table reset...")
    
    async with engine.begin() as conn:
        # Drop the kitespots table
        logger.info("Dropping kitespots table...")
        await conn.execute(text("DROP TABLE IF EXISTS kitespots CASCADE"))
        
        # Create the kitespots table
        logger.info("Creating kitespots table...")
        await conn.execute(text("""
            CREATE TABLE kitespots (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                description TEXT,
                latitude FLOAT,
                longitude FLOAT,
                country VARCHAR,
                region VARCHAR,
                city VARCHAR,
                difficulty VARCHAR,
                water_type VARCHAR,
                best_wind_direction VARCHAR,
                best_season VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        logger.info("Kitespots table reset successfully!")

if __name__ == "__main__":
    asyncio.run(reset_kitespots()) 