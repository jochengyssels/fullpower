import asyncio
import csv
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import async_session
from models import KiteSchool

async def fetch_csv(url):
    """Fetch CSV data from URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch CSV: {response.status}")
            return await response.text()

async def import_kiteschools(csv_url=None, csv_path=None):
    """Import kiteschools from CSV file or URL"""
    # Get CSV content either from URL or local file
    if csv_url:
        print(f"Fetching CSV from URL: {csv_url}")
        csv_content = await fetch_csv(csv_url)
        csv_data = csv_content.splitlines()
    elif csv_path:
        print(f"Reading CSV from file: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
            csv_data = csv_content.splitlines()
    else:
        raise ValueError("Either csv_url or csv_path must be provided")

    # Parse CSV
    reader = csv.DictReader(csv_data)
    
    # Connect to database
    async with async_session() as db:
        # Check if table exists and has data
        result = await db.execute(text("SELECT COUNT(*) FROM kiteschools"))
        count = result.scalar()
        
        if count > 0:
            print(f"Table already has {count} records.")
            user_input = input("Do you want to continue and potentially add duplicate records? (y/n): ")
            if user_input.lower() != 'y':
                print("Import cancelled.")
                return
        
        # Import data
        schools_added = 0
        for row in reader:
            # Clean up data
            school = KiteSchool(
                company_name=row.get('Company Name', '').strip(),
                location=row.get('Location (City/Town)', '').strip(),
                country=row.get('Country', '').strip(),
                google_review_score=row.get('Google Review Score', '').strip() or None,
                owner_name=row.get('Owner\'s Name', '').strip() or None,
                website_url=row.get('Website URL', '').strip() or None,
                course_pricing=row.get('Course Pricing', '').strip() or None
            )
            
            db.add(school)
            schools_added += 1
            
            # Commit in batches of 100 to avoid memory issues
            if schools_added % 100 == 0:
                await db.commit()
                print(f"Imported {schools_added} schools so far...")
        
        # Final commit for remaining records
        await db.commit()
        print(f"Successfully imported {schools_added} kiteschools into the database.")

if __name__ == "__main__":
    # URL of the CSV file
    CSV_URL = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/kiteschools-c4d1pLceGCht2jWPJBbnvEi0xl8I8G.csv"
    
    # Alternatively, use local file path
    # CSV_PATH = "data/kiteschools.csv"
    
    asyncio.run(import_kiteschools(csv_url=CSV_URL))
    # If you prefer to use the local file:
    # asyncio.run(import_kiteschools(csv_path=CSV_PATH))