import aiohttp
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger("kitespot-api.geocoding")

# LocationIQ API key - you should replace this with your own
LOCATIONIQ_API_KEY = "pk.7d195946b1d5836bbef50b02dc8a4a41"

# Cache for geocoding results to reduce API calls
geocoding_cache = {}

async def geocode_location(location: str) -> Tuple[float, float]:
    """
    Geocodes a location string to latitude and longitude coordinates.
    Uses LocationIQ API for geocoding.
    
    Args:
        location: A string representing a location (e.g., "Tarifa, Spain")
        
    Returns:
        A tuple of (latitude, longitude)
        
    Raises:
        Exception: If geocoding fails
    """
    # Check cache first
    if location in geocoding_cache:
        logger.info(f"Using cached geocoding for {location}")
        return geocoding_cache[location]
    
    # Known kitespot locations - hardcoded for reliability
    known_spots = {
        "punta trettu": (39.1833, 8.3167),
        "tarifa": (36.0143, -5.6044),
        "maui": (20.7984, -156.3319),
        "cape town": (33.9249, 18.4241),
        "cabarete": (19.758, -70.4193),
        "dakhla": (23.7136, -15.9355),
        "jericoacoara": (-2.7975, -40.5137),
        "essaouira": (31.5085, -9.7595),
    }
    
    # Check if it's a known location
    location_lower = location.lower()
    for key, coords in known_spots.items():
        if key in location_lower:
            logger.info(f"Using known coordinates for {location}")
            geocoding_cache[location] = coords
            return coords
    
    try:
        # Use LocationIQ API for geocoding
        url = f"https://us1.locationiq.com/v1/search.php?key={LOCATIONIQ_API_KEY}&q={location}&format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Geocoding API error: {response.status}")
                    raise Exception(f"Geocoding failed with status {response.status}")
                
                data = await response.json()
                
                if not data or len(data) == 0:
                    logger.error(f"No geocoding results for {location}")
                    raise Exception(f"No geocoding results found for {location}")
                
                # Get the first result
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                
                # Cache the result
                geocoding_cache[location] = (lat, lon)
                
                return (lat, lon)
    
    except Exception as e:
        logger.error(f"Geocoding error for {location}: {str(e)}")
        raise Exception(f"Failed to geocode location: {str(e)}")

async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
    Performs reverse geocoding to get location details from coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        A dictionary with location details
    """
    try:
        url = f"https://us1.locationiq.com/v1/reverse.php?key={LOCATIONIQ_API_KEY}&lat={lat}&lon={lon}&format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Reverse geocoding API error: {response.status}")
                    return {"name": "Unknown Location"}
                
                data = await response.json()
                
                if not data or "address" not in data:
                    return {"name": "Unknown Location"}
                
                address = data["address"]
                
                # Extract relevant location information
                city = address.get("city", "")
                town = address.get("town", "")
                village = address.get("village", "")
                county = address.get("county", "")
                state = address.get("state", "")
                country = address.get("country", "")
                
                # Build location name
                location_name = city or town or village or "Unknown Location"
                location_region = county or state or country
                
                if location_region:
                    full_name = f"{location_name}, {location_region}"
                else:
                    full_name = location_name
                
                return {
                    "name": full_name,
                    "city": city or town or village,
                    "region": county or state,
                    "country": country
                }
    
    except Exception as e:
        logger.error(f"Reverse geocoding error: {str(e)}")
        return {"name": "Unknown Location"}

