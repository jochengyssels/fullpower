import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import async_session
from models import KiteSpot

async def seed_database():
    async with async_session() as db:
        # Check if we already have kitespots
        result = await db.execute(text("SELECT COUNT(*) FROM kitespots"))
        count = result.scalar()
        
        if count > 0:
            print(f"Database already has {count} kitespots. Skipping seed.")
            return
        
        # Add popular kitespots
        kitespots = [
            {"name": "Punta Trettu", "country": "Italy", "latitude": 39.1833, "longitude": 8.3167, 
             "description": "Shallow lagoon with consistent wind, perfect for beginners and freestyle."},
            {"name": "Tarifa", "country": "Spain", "latitude": 36.0143, "longitude": -5.6044,
             "description": "Europe's wind capital with strong Levante and Poniente winds."},
            {"name": "Maui", "country": "Hawaii", "latitude": 20.7984, "longitude": -156.3319,
             "description": "World-famous for its consistent trade winds and beautiful scenery."},
            {"name": "Cape Town", "country": "South Africa", "latitude": -33.9249, "longitude": 18.4241,
             "description": "Strong summer winds and multiple spots for all levels."},
            {"name": "Cabarete", "country": "Dominican Republic", "latitude": 19.758, "longitude": -70.4193,
             "description": "Thermal winds that pick up in the afternoon, with a vibrant beach scene."},
            {"name": "Dakhla", "country": "Morocco", "latitude": 23.7136, "longitude": -15.9355,
             "description": "Flat water lagoon and wave spots with reliable wind."},
            {"name": "Jericoacoara", "country": "Brazil", "latitude": -2.7975, "longitude": -40.5137,
             "description": "Consistent trade winds and a mix of flat water and wave conditions."},
            {"name": "Essaouira", "country": "Morocco", "latitude": 31.5085, "longitude": -9.7595,
             "description": "Windy city with a mix of beach and point breaks."},
        ]
        
        for spot_data in kitespots:
            spot = KiteSpot(**spot_data)
            db.add(spot)
        
        await db.commit()
        print(f"Added {len(kitespots)} kitespots to the database.")

if __name__ == "__main__":
    asyncio.run(seed_database())