import asyncio
import csv
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL, Base
from models import KiteSpot  # Import the updated model

async def reset_and_import_kitespots(csv_path):
    """Drop existing kitespots table, recreate it, and import data from CSV"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"Reading CSV from file: {csv_path}")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Drop and recreate the kitespots table
    print("Dropping and recreating kitespots table...")
    async with engine.begin() as conn:
        # Drop the table if it exists
        await conn.execute(text("DROP TABLE IF EXISTS kitespots CASCADE"))
        
        # Create the table with the new schema
        await conn.run_sync(lambda x: Base.metadata.create_all(
            x, tables=[KiteSpot.__table__]
        ))
    
    print("Table recreated successfully.")
    
    # Read CSV and import data
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Import data
        async with async_session() as db:
            spots_added = 0
            
            for row in reader:
                # Create new kitespot with all fields from CSV
                spot = KiteSpot(
                    name=row.get('name', '').strip(),
                    region=row.get('location', '').strip(),
                    country=row.get('country', '').strip(),
                    latitude=row.get('latitude', '').strip(),
                    longitude=row.get('longitude', '').strip(),
                    difficulty=row.get('difficulty', '').strip(),
                    water_type=row.get('water_type', '').strip()
                )
                
                db.add(spot)
                spots_added += 1
                
                # Commit in batches of 100 to avoid memory issues
                if spots_added % 100 == 0:
                    await db.commit()
                    print(f"Imported {spots_added} spots so far...")
            
            # Final commit for remaining records
            await db.commit()
            print(f"Successfully imported {spots_added} kitespots into the database.")
    
    # Close engine
    await engine.dispose()

if __name__ == "__main__":
    # Path to the CSV file
    CSV_PATH = "data/kitespots.csv"
    
    # Run the import
    asyncio.run(reset_and_import_kitespots(CSV_PATH))