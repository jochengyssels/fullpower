from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

from database import get_db_session, init_db, check_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global flag to track database status
db_connected = False

@app.on_event("startup")
async def startup_event():
    global db_connected
    logger.info("Application startup")
    try:
        # Check database connection first
        db_connected = await check_db_connection()
        
        if db_connected:
            # Only initialize database if connection is successful
            db_initialized = await init_db()
            if not db_initialized:
                logger.warning("Database connection successful but initialization failed")
        else:
            logger.warning("Application started but database connection failed")
            logger.warning("Check your DATABASE_URL environment variable")
            logger.warning(f"Current DATABASE_URL prefix: {os.getenv('DATABASE_URL', 'Not set').split('@')[0] if os.getenv('DATABASE_URL') else 'Not set'}")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        logger.exception("Full exception details:")
        # Allow app to start even with errors for debugging

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to check database connection for each request"""
    global db_connected
    
    # Skip database check for health endpoint
    if request.url.path == "/health":
        return await call_next(request)
    
    # Check if database is connected
    if not db_connected:
        # Try to reconnect
        db_connected = await check_db_connection()
        
        # If still not connected, return error for database-dependent endpoints
        if not db_connected and request.url.path.startswith(("/kitespots", "/api")):
            return JSONResponse(
                status_code=503,
                content={"detail": "Database connection unavailable. Please try again later."}
            )
    
    return await call_next(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global db_connected
    
    # Try to check connection if currently disconnected
    if not db_connected:
        db_connected = await check_db_connection()
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
        "database_url_set": os.getenv("DATABASE_URL") is not None
    }

# Example route using database
@app.get("/api/kitespots/")
async def get_kitespots(db: AsyncSession = Depends(get_db_session)):
    try:
        # Example query - adjust based on your actual models and schema
        result = await db.execute("SELECT * FROM kitespots LIMIT 10")
        spots = result.fetchall()
        return spots
    except Exception as e:
        logger.error(f"Error fetching kitespots: {str(e)}")
        # If database error, try the fallback
        return await get_kitespots_fallback()

# Fallback route for when database is unavailable
@app.get("/api/kitespots/fallback")
async def get_kitespots_fallback():
    """Fallback endpoint that doesn't require database access"""
    logger.info("Using fallback kite spots data")
    return [
        {"id": "1", "name": "Punta Trettu", "country": "Italy", "latitude": 39.1833, "longitude": 8.3167},
        {"id": "2", "name": "Dakhla", "country": "Morocco", "latitude": 23.7136, "longitude": -15.9355},
        {"id": "3", "name": "Tarifa", "country": "Spain", "latitude": 36.0143, "longitude": -5.6044},
        {"id": "4", "name": "Jericoacoara", "country": "Brazil", "latitude": -2.7975, "longitude": -40.5137},
        {"id": "5", "name": "Cabarete", "country": "Dominican Republic", "latitude": 19.758, "longitude": -70.4193},
        {"id": "6", "name": "Cape Town", "country": "South Africa", "latitude": -33.9249, "longitude": 18.4241},
    ]

# Nearest kite spot endpoint
@app.get("/api/kitespots/nearest")
async def get_nearest_kitespot(lat: float, lng: float, db: AsyncSession = Depends(get_db_session)):
    try:
        # In a real implementation, you would use a spatial query to find the nearest spot
        # For now, we'll just return a mock response
        return {
            "id": "3",
            "name": "Tarifa",
            "country": "Spain",
            "latitude": 36.0143,
            "longitude": -5.6044
        }
    except Exception as e:
        logger.error(f"Error finding nearest kitespot: {str(e)}")
        # Return a default spot
        return {
            "id": "3",
            "name": "Tarifa",
            "country": "Spain",
            "latitude": 36.0143,
            "longitude": -5.6044
        }

# Weather data endpoint
@app.get("/api/kitespots/{spot_id}/weather")
async def get_kitespot_weather(spot_id: str, db: AsyncSession = Depends(get_db_session)):
    try:
        # In a real implementation, you would fetch weather data from the database
        # For now, we'll just return mock data
        return {
            "spot_id": spot_id,
            "timestamp": "2023-05-01T12:00:00Z",
            "temperature": 22.5,
            "wind_speed_10m": 15.3,
            "wind_direction_10m": 90,
            "wind_gust": 18.7
        }
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        # Return mock data
        return {
            "spot_id": spot_id,
            "timestamp": "2023-05-01T12:00:00Z",
            "temperature": 22.5,
            "wind_speed_10m": 15.3,
            "wind_direction_10m": 90,
            "wind_gust": 18.7
        }