import asyncio
import csv
import logging
from sqlalchemy import select
from database import async_session
from models import KiteSpot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def import_kitespots(csv_path="data/kitespots.csv"):
    """Import kitespots from CSV file"""
    spots_added = 0
    
    async with async_session() as db:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Clean and convert data
                name = row.get('name', '').strip()
                country = row.get('country', '').strip()
                location = row.get('location', '').strip()
                difficulty = row.get('difficulty', '').strip()
                water_type = row.get('water_type', '').strip()
                
                # Convert latitude and longitude to float
                try:
                    latitude = float(row.get('latitude', '0').strip() or 0)
                    longitude = float(row.get('longitude', '0').strip() or 0)
                except ValueError:
                    latitude = 0
                    longitude = 0
                
                # Create new kitespot
                spot = KiteSpot(
                    name=name,
                    country=country,
                    latitude=latitude,
                    longitude=longitude,
                    region=location,  # Store location in region field
                    difficulty=difficulty,
                    water_type=water_type,
                    description=f"A {difficulty.lower() if difficulty else 'unknown'} kitespot with {water_type.lower() if water_type else 'unknown'} water conditions."
                )
                
                db.add(spot)
                spots_added += 1
                
                # Commit in batches of 100 to avoid memory issues
                if spots_added % 100 == 0:
                    await db.commit()
                    logger.info(f"Imported {spots_added} spots so far...")
        
        # Final commit for remaining records
        await db.commit()
        logger.info(f"Successfully imported {spots_added} kitespots into the database.")

if __name__ == "__main__":
    asyncio.run(import_kitespots())