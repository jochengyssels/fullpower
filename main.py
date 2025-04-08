from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
import os
from pydantic import BaseModel

# Import services
from services.geocoding import geocode_location
from services.weather import WeatherService
from services.kitewindow import calculate_golden_kitewindow

# Add these imports for database functionality
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import get_db
import models
import schemas
import crud

from models import KiteSchool, KiteSpot
from sqlalchemy import select


from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API key for Tomorrow.io
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("kitespot-api")

# Initialize FastAPI app
app = FastAPI(
    title="Full Power API",
    description="API for kitesurfing forecasts and golden window predictions",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
weather_service = WeatherService()

# API key for Tomorrow.io
TOMORROW_API_KEY = "zbtDpBoMzGlylEh5tblXugBsjkTyfw2S"

@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Full Power API",
        "version": "1.0.0",
        "description": "API for kitesurfing forecasts and golden window predictions"
    }

@app.get("/api/weather", response_model=Dict[str, Any])
async def get_weather(location: str = Query(..., title="Kitespot Location", min_length=2)):
    """
    Fetches weather forecast for a kitespot based on location string (e.g. 'Tarifa, Spain').
    Returns data optimized for golden kite window calculation and chart display.
    """
    if not TOMORROW_API_KEY:
        raise HTTPException(status_code=500, detail="Missing Tomorrow.io API key")

    try:
        cleaned_location = location.split("-")[0].strip()
        lat, lon = await geocode_location(cleaned_location)
        logger.info(f"📍 Geocoded {cleaned_location} → lat: {lat}, lon: {lon}")

        # Get 48-hour forecast with hourly timesteps
        forecast_url = f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&timesteps=1h&units=metric&apikey={TOMORROW_API_KEY}"
        realtime_url = f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lon}&units=metric&apikey={TOMORROW_API_KEY}"
        
        async with aiohttp.ClientSession() as session:
            realtime_task = session.get(realtime_url)
            forecast_task = session.get(forecast_url)
            realtime_response, forecast_response = await asyncio.gather(realtime_task, forecast_task)

            realtime_data = await realtime_response.json()
            forecast_data = await forecast_response.json()

        if "data" not in realtime_data or "values" not in realtime_data["data"]:
            raise HTTPException(status_code=500, detail="Invalid realtime weather response")

        realtime = realtime_data["data"]["values"]
        hourly_forecast = forecast_data.get("timelines", {}).get("hourly", [])
        
        # Process hourly forecast data
        processed_forecast = []
        for hour in hourly_forecast:
            time_str = hour.get("time")
            values = hour.get("values", {})
            
            # Convert wind speed from m/s to knots (1 m/s = 1.94384 knots)
            wind_speed_ms = values.get("windSpeed", 0)
            wind_gust_ms = values.get("windGust", 0)
            wind_speed_knots = round(wind_speed_ms * 1.94384, 1)
            wind_gust_knots = round(wind_gust_ms * 1.94384, 1)
            
            # Determine if it's day or night based on solar data
            hour_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            is_day = 1 if 6 <= hour_dt.hour <= 18 else 0  # Simple day/night check
            
            # Map weather code to a standard format
            weather_code = weather_service.map_weather_code(values.get("weatherCode", 0))
            
            processed_hour = {
                "timestamp": time_str,
                "wind_speed": wind_speed_knots,
                "wind_gust": wind_gust_knots,
                "wind_dir": values.get("windDirection", 0),
                "temp": values.get("temperature", 0),
                "humidity": values.get("humidity", 0),
                "precipitation": values.get("precipitationProbability", 0),
                "weather_code": weather_code,
                "is_day": is_day,
                # Calculate if this hour is in the golden window (15-25 knots is ideal)
                "is_golden_window": 15 <= wind_speed_knots <= 25
            }
            processed_forecast.append(processed_hour)
        
        # Get current conditions from realtime data
        current_wind_speed_knots = round(realtime.get("windSpeed", 0) * 1.94384, 1)
        current_conditions = {
            "wind_speed": current_wind_speed_knots,
            "wind_gust": round(realtime.get("windGust", 0) * 1.94384, 1),
            "wind_dir": realtime.get("windDirection", 0),
            "temp": realtime.get("temperature", 0),
            "humidity": realtime.get("humidity", 0),
            "precipitation": realtime.get("precipitationProbability", 0),
            "weather_code": weather_service.map_weather_code(realtime.get("weatherCode", 0)),
            "is_day": 1 if 6 <= datetime.now().hour <= 18 else 0,
            "is_golden_window": 15 <= current_wind_speed_knots <= 25
        }
        
        # Calculate golden kite window
        golden_window = calculate_golden_kitewindow(processed_forecast)
        
        # Get enhanced forecast with additional data if available
        enhanced_forecast = await weather_service.enhance_forecast(lat, lon)
        
        return {
            "location": {
                "name": cleaned_location,
                "latitude": lat,
                "longitude": lon
            },
            "current_conditions": current_conditions,
            "forecast": processed_forecast,
            "golden_kitewindow": golden_window,
            "enhanced": enhanced_forecast,
            "model_used": enhanced_forecast.get("source", "tomorrow.io")
        }

    except Exception as e:
        logger.error(f"Forecast API request failed: {str(e)}")
        return {
            "error": str(e),
            "location": {
                "name": location,
                "latitude": 0,
                "longitude": 0
            },
            "current_conditions": {},
            "forecast": [],
            "golden_kitewindow": {},
            "enhanced": {},
            "model_used": "error"
        }

@app.get("/api/kitespots/", response_model=List[Dict[str, Any]])
async def read_kitespots_from_db(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.KiteSpot).offset(skip).limit(limit))
    kitespots = result.scalars().all()
    
    return [
        {
            "id": spot.id,
            "name": spot.name,
            "location": spot.region,
            "country": spot.country,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "difficulty": spot.difficulty,
            "water_type": spot.water_type
        }
        for spot in kitespots
    ]

@app.get("/api/kitespots/{kitespot_id}/weather", response_model=List[Dict[str, Any]])
async def get_kitespot_weather(
    kitespot_id: int, 
    hours: int = Query(24, description="Number of hours to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns weather data for a specific kitespot.
    """
    # Check if kitespot exists
    result = await db.execute(select(KiteSpot).filter(KiteSpot.id == kitespot_id))
    kitespot = result.scalars().first()
    
    if not kitespot:
        raise HTTPException(status_code=404, detail="Kitespot not found")
    
    # Get weather data
    result = await db.execute(text("""
    SELECT 
        timestamp, temperature, humidity, precipitation, rain,
        wind_speed_10m, wind_speed_80m, wind_speed_120m,
        wind_direction_10m, wind_direction_80m, wind_direction_120m,
        wind_gusts_10m
    FROM kitespot_weather
    WHERE kitespot_id = :kitespot_id
    ORDER BY timestamp DESC
    LIMIT :hours
    """), {
        "kitespot_id": kitespot_id,
        "hours": hours
    })
    
    rows = result.fetchall()
    
    # Convert to list of dictionaries
    weather_data = []
    for row in rows:
        weather_data.append({
            "timestamp": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "precipitation": row[3],
            "rain": row[4],
            "wind_speed_10m": row[5],
            "wind_speed_80m": row[6],
            "wind_speed_120m": row[7],
            "wind_direction_10m": row[8],
            "wind_direction_80m": row[9],
            "wind_direction_120m": row[10],
            "wind_gusts_10m": row[11]
        })
    
    return weather_data

# User routes
@app.post("/api/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user)

@app.get("/api/users/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# KiteSpot routes
@app.post("/api/kitespots/", response_model=schemas.KiteSpot)
async def create_kitespot(kitespot: schemas.KiteSpotCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_kitespot(db=db, kitespot=kitespot)

@app.get("/api/kitespots/db", response_model=List[schemas.KiteSpot])
async def read_kitespots_from_db(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    kitespots = await crud.get_kitespots(db, skip=skip, limit=limit)
    return kitespots

# FavoriteSpot routes
@app.post("/api/users/{user_id}/favorites/", response_model=schemas.FavoriteSpot)
async def create_favorite_for_user(
    user_id: int, favorite: schemas.FavoriteSpotCreate, db: AsyncSession = Depends(get_db)
):
    return await crud.create_favorite_spot(db=db, favorite=favorite, user_id=user_id)

@app.get("/api/users/{user_id}/favorites/", response_model=List[schemas.FavoriteSpot])
async def read_user_favorites(user_id: int, db: AsyncSession = Depends(get_db)):
    favorites = await crud.get_user_favorites(db, user_id=user_id)
    return favorites

# KiteSession routes
@app.post("/api/users/{user_id}/sessions/", response_model=schemas.KiteSession)
async def create_session_for_user(
    user_id: int, session: schemas.KiteSessionCreate, db: AsyncSession = Depends(get_db)
):
    return await crud.create_kite_session(db=db, session=session, user_id=user_id)

@app.get("/api/users/{user_id}/sessions/", response_model=List[schemas.KiteSession])
async def read_user_sessions(user_id: int, db: AsyncSession = Depends(get_db)):
    sessions = await crud.get_user_sessions(db, user_id=user_id)
    return sessions



# Add this route to your main.py
@app.get("/api/kiteschools", response_model=List[Dict[str, Any]])
async def get_kiteschools(
    country: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a list of kiteschools, optionally filtered by country.
    """
    query = select(KiteSchool)
    
    if country:
        query = query.filter(KiteSchool.country == country)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    schools = result.scalars().all()
    
    return [
        {
            "id": school.id,
            "company_name": school.company_name,
            "location": school.location,
            "country": school.country,
            "google_review_score": school.google_review_score,
            "owner_name": school.owner_name,
            "website_url": school.website_url,
            "course_pricing": school.course_pricing
        }
        for school in schools
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

