import asyncio
import schedule
import time
import logging
from weather_service import OpenMeteoWeatherService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("weather-scheduler")

async def update_weather():
    """Update weather data for all kitespots"""
    logger.info("Starting scheduled weather update")
    service = OpenMeteoWeatherService()
    await service.fetch_and_store_weather_data()
    logger.info("Completed scheduled weather update")

def run_weather_update():
    """Run the weather update asynchronously"""
    asyncio.run(update_weather())

def main():
    """Main function to run the scheduler"""
    logger.info("Starting weather scheduler")
    
    # Run immediately on startup
    run_weather_update()
    
    # Schedule to run every hour
    schedule.every().hour.do(run_weather_update)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

