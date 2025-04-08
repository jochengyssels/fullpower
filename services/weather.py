import aiohttp
import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger("kitespot-api.weather")

class WeatherService:
    """
    Service for fetching and processing weather data from various sources.
    """
    
    def __init__(self):
        """Initialize the weather service."""
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 30 * 60  # 30 minutes
    
    def map_weather_code(self, code: int) -> int:
        """
        Maps Tomorrow.io weather codes to standardized codes for the frontend.
        Returns codes compatible with the frontend weather icon system.
        
        Args:
            code: Tomorrow.io weather code
            
        Returns:
            Standardized weather code
        """
        # Tomorrow.io weather codes mapping
        # 1000: Clear
        # 1100: Mostly Clear
        # 1101: Partly Cloudy
        # 1102: Mostly Cloudy
        # 1001: Cloudy
        # 2000: Fog
        # 2100: Light Fog
        # 4000: Drizzle
        # 4001: Rain
        # 4200: Light Rain
        # 4201: Heavy Rain
        # 5000: Snow
        # 5001: Flurries
        # 5100: Light Snow
        # 5101: Heavy Snow
        # 6000: Freezing Drizzle
        # 6001: Freezing Rain
        # 6200: Light Freezing Rain
        # 6201: Heavy Freezing Rain
        # 7000: Ice Pellets
        # 7101: Heavy Ice Pellets
        # 7102: Light Ice Pellets
        # 8000: Thunderstorm
        
        if code == 1000:  # Clear
            return 800
        elif code in [1100, 1101]:  # Partly Cloudy
            return 801
        elif code == 1102:  # Mostly Cloudy
            return 802
        elif code == 1001:  # Cloudy
            return 804
        elif code in [2000, 2100]:  # Fog
            return 741
        elif code == 4000:  # Drizzle
            return 300
        elif code in [4001, 4200]:  # Light Rain
            return 500
        elif code == 4201:  # Heavy Rain
            return 502
        elif code in [5000, 5100]:  # Light Snow
            return 600
        elif code == 5101:  # Heavy Snow
            return 602
        elif code in [6000, 6001, 6200, 6201]:  # Freezing Rain
            return 511
        elif code in [7000, 7101, 7102]:  # Ice Pellets
            return 611
        elif code == 8000:  # Thunderstorm
            return 200
        else:
            return 800  # Default to clear
    
    async def enhance_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Enhances the forecast with additional data from other sources.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Enhanced forecast data
        """
        # Check cache
        cache_key = f"{lat},{lon}"
        if cache_key in self.cache and datetime.now().timestamp() < self.cache_expiry.get(cache_key, 0):
            logger.info(f"Using cached enhanced forecast for {cache_key}")
            return self.cache[cache_key]
        
        try:
            # In a real implementation, you might fetch data from additional sources
            # For now, we'll just return some mock enhanced data
            
            # Calculate a "kitesurf probability" based on the time of year and location
            # This is just a simple example - in reality, you'd use more sophisticated models
            month = datetime.now().month
            
            # Northern hemisphere summer (May-Sep) is good for northern spots
            # Southern hemisphere summer (Nov-Mar) is good for southern spots
            is_northern_summer = 5 <= month <= 9
            is_southern_summer = month >= 11 or month <= 3
            
            is_northern = lat > 0
            is_southern = lat < 0
            
            seasonal_factor = 1.0
            if (is_northern and is_northern_summer) or (is_southern and is_southern_summer):
                seasonal_factor = 1.2  # Boost for in-season locations
            elif (is_northern and not is_northern_summer) or (is_southern and not is_southern_summer):
                seasonal_factor = 0.8  # Reduction for off-season locations
            
            # Some locations are known to be more reliable
            reliability_factor = 1.0
            if abs(lat) > 30 and abs(lat) < 40:  # Many good spots are in this range
                reliability_factor = 1.1
            
            # Create enhanced data
            enhanced_data = {
                "source": "enhanced_model",
                "seasonal_factor": seasonal_factor,
                "reliability_factor": reliability_factor,
                "kitesurf_confidence": round(min(100, seasonal_factor * reliability_factor * 85), 1),
                "best_months": self._get_best_months(lat),
                "local_tips": self._get_local_tips(lat, lon),
                "updated_at": datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = enhanced_data
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return enhanced_data
        
        except Exception as e:
            logger.error(f"Error enhancing forecast: {str(e)}")
            return {
                "source": "fallback",
                "error": str(e),
                "kitesurf_confidence": 70,  # Default confidence
                "updated_at": datetime.now().isoformat()
            }
    
    def _get_best_months(self, lat: float) -> List[str]:
        """
        Returns the best months for kitesurfing based on latitude.
        
        Args:
            lat: Latitude
            
        Returns:
            List of month names
        """
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        
        if lat > 0:  # Northern hemisphere
            return months[4:9]  # May to September
        else:  # Southern hemisphere
            return months[10:] + months[:3]  # November to March
    
    def _get_local_tips(self, lat: float, lon: float) -> str:
        """
        Returns local tips for the location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            String with local tips
        """
        # Tarifa
        if abs(lat - 36.0143) < 0.1 and abs(lon - (-5.6044)) < 0.1:
            return "Tarifa is known for strong Levante (easterly) and Poniente (westerly) winds. The Levante can be gusty, while the Poniente is steadier and better for beginners."
        
        # Maui
        elif abs(lat - 20.7984) < 0.1 and abs(lon - (-156.3319)) < 0.1:
            return "Kite Beach in Maui has reliable trade winds that typically pick up in the afternoon. Morning sessions are usually calmer and better for beginners."
        
        # Cape Town
        elif abs(lat - (-33.9249)) < 0.1 and abs(lon - 18.4241) < 0.1:
            return "Cape Town's Table Bay offers strong south-easterly winds in summer. Be aware of the strong currents that can develop during outgoing tides."
        
        # Cabarete
        elif abs(lat - 19.758) < 0.1 and abs(lon - (-70.4193)) < 0.1:
            return "Cabarete has thermal winds that typically pick up around noon and peak in the afternoon. Morning sessions are usually calmer."
        
        # Dakhla
        elif abs(lat - 23.7136) < 0.1 and abs(lon - (-15.9355)) < 0.1:
            return "Dakhla's lagoon offers flat water and steady winds, perfect for beginners and freestyle riders. The ocean side has waves for more advanced riders."
        
        # Generic tips
        else:
            return "Always check local regulations and safety guidelines. Kite with a buddy and inform yourself about local conditions and hazards."

