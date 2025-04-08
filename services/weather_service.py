import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests_cache
import aiohttp
import json
from sqlalchemy import select, text, cast, TIMESTAMP, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions
from openmeteo_requests import Client
from retry_requests import retry
from typing import List, Dict

# Add the parent directory to the path so we can import modules from there
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import async_session
from models import KiteSpot, KiteSpotWeather

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class OpenMeteoWeatherService:
    def __init__(self):
        """Initialize the weather service."""
        # Get logger
        self.logger = logging.getLogger("kitespot-weather-service")

        # Setup the Open-Meteo API client with cache and retry logic
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = Client(session=retry_session)
        
    async def fetch_weather_data_batch(self, kitespots: List[KiteSpot]) -> Dict[int, pd.DataFrame]:
        """Fetch weather data for multiple kitespots using the batch API."""
        try:
            # Prepare locations as arrays of coordinates
            latitudes = []
            longitudes = []
            for spot in kitespots:
                latitudes.append(float(spot.latitude))
                longitudes.append(float(spot.longitude))

            # Define hourly parameters
            hourly_params = [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "visibility"
            ]

            # Calculate dates
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            # Prepare the request payload
            params = {
                "latitude": ",".join(map(str, latitudes)),
                "longitude": ",".join(map(str, longitudes)),
                "hourly": ",".join(hourly_params),
                "start_date": today.isoformat(),
                "end_date": tomorrow.isoformat(),
                "timezone": "auto"
            }

            self.logger.info(f"Fetching weather data for {len(kitespots)} spots with coordinates: " + 
                           ", ".join([f"({lat}, {lon})" for lat, lon in zip(latitudes, longitudes)]))

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Batch API error: {response.status} - {error_text}")
                        return {}

                    data = await response.json()
                    if not data or not isinstance(data, list):
                        self.logger.error("Invalid response format from batch API")
                        self.logger.error(f"Response data: {data}")
                        return {}

                    # Process the response into DataFrames for each kitespot
                    results = {}
                    for i, (spot, location_data) in enumerate(zip(kitespots, data)):
                        try:
                            if "hourly" not in location_data:
                                self.logger.error(f"No hourly data for spot {spot.name}")
                                continue

                            spot_data = {}
                            timestamps = pd.to_datetime(location_data["hourly"]["time"])

                            for param in hourly_params:
                                if param in location_data["hourly"]:
                                    spot_data[param] = location_data["hourly"][param]

                            if spot_data:
                                spot_data["timestamp"] = timestamps
                                df = pd.DataFrame(spot_data)
                                results[spot.id] = df
                                self.logger.info(f"Successfully processed weather data for {spot.name}")
                        except Exception as e:
                            self.logger.error(f"Error processing data for kitespot {spot.name}: {str(e)}")
                            continue

                    return results

        except Exception as e:
            self.logger.error(f"Error fetching batch weather data: {str(e)}")
            return {}
    
    async def store_weather_data(self, kitespot_id: int, weather_df: pd.DataFrame):
        """Store weather data in the database."""
        try:
            # Ensure timestamps are timezone-aware
            if weather_df["timestamp"].dt.tz is None:
                weather_df["timestamp"] = weather_df["timestamp"].dt.tz_localize("UTC")

            async with async_session() as session:
                # Delete existing weather data for this kitespot and time range
                await session.execute(
                    text("""
                        DELETE FROM kitespot_weather 
                        WHERE kitespot_id = :kitespot_id 
                        AND timestamp >= :start_time 
                        AND timestamp < :end_time
                    """),
                    {
                        "kitespot_id": kitespot_id,
                        "start_time": weather_df["timestamp"].min().to_pydatetime(),
                        "end_time": (weather_df["timestamp"].max() + pd.Timedelta(hours=1)).to_pydatetime()
                    }
                )

                # Insert new weather data
                for _, row in weather_df.iterrows():
                    weather = KiteSpotWeather(
                        kitespot_id=kitespot_id,
                        timestamp=row["timestamp"].to_pydatetime(),
                        temperature=row.get("temperature_2m"),
                        humidity=row.get("relative_humidity_2m"),
                        precipitation=row.get("precipitation"),
                        wind_speed_10m=row.get("wind_speed_10m"),
                        wind_direction_10m=row.get("wind_direction_10m"),
                        cloud_cover=row.get("cloud_cover"),
                        visibility=row.get("visibility")
                    )
                    session.add(weather)

                await session.commit()

        except Exception as e:
            self.logger.error(f"Error storing weather data for kitespot {kitespot_id}: {str(e)}")
    
    async def fetch_and_store_weather_data(self):
        """Fetch and store weather data for all kitespots."""
        try:
            # Get all kitespots
            async with async_session() as session:
                result = await session.execute(text("SELECT * FROM kitespots"))
                kitespots = result.fetchall()

            self.logger.info(f"Fetching weather data for {len(kitespots)} kitespots")

            # Process kitespots in batches of 10 to avoid rate limits
            batch_size = 10
            for i in range(0, len(kitespots), batch_size):
                batch = kitespots[i:i + batch_size]
                self.logger.info(f"Processing batch {i//batch_size + 1} of {(len(kitespots) + batch_size - 1)//batch_size}")

                # Fetch weather data for the batch
                weather_data = await self.fetch_weather_data_batch(batch)

                # Store the weather data
                for kitespot_id, df in weather_data.items():
                    await self.store_weather_data(kitespot_id, df)

                # Wait for 1 minute between batches to respect rate limits
                if i + batch_size < len(kitespots):
                    self.logger.info("Waiting for 1 minute to respect API rate limits...")
                    await asyncio.sleep(60)

        except Exception as e:
            self.logger.error(f"Error in fetch_and_store_weather_data: {str(e)}")

# For testing
async def main():
    service = OpenMeteoWeatherService()
    await service.fetch_and_store_weather_data()

if __name__ == "__main__":
    asyncio.run(main())

