import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from models import Base

# Load environment variables
load_dotenv()

# Get PostgreSQL connection string
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")

# Convert async URL to sync URL
sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
engine = create_engine(sync_url)

def update_schema():
    """Update the database schema."""
    # Drop the kitespot_weather table if it exists
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS kitespot_weather CASCADE"))
        conn.commit()

    # Create all tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    update_schema()
    print("Schema updated successfully")

