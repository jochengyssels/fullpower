import asyncio
from models import KiteSpot
from database import async_session
from sqlalchemy import text

async def get_spots():
    async with async_session() as session:
        spots = await session.execute(
            text('SELECT id, name, latitude, longitude FROM kitespots LIMIT 5')
        )
        return spots.fetchall()

async def main():
    spots = await get_spots()
    for spot in spots:
        print(f'{spot[0]}: {spot[1]} ({spot[2]}, {spot[3]})')

if __name__ == '__main__':
    asyncio.run(main()) 