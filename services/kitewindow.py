from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("kitespot-api.kitewindow")

def calculate_golden_kitewindow(forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates the golden kite window based on forecast data.
    Returns the best time period for kitesurfing.
    
    Args:
        forecast: List of hourly forecast data
        
    Returns:
        Dictionary with golden window information
    """
    if not forecast:
        return {
            "start_time": None,
            "end_time": None,
            "score": 0,
            "duration": 0,
            "message": "No forecast data available"
        }
    
    try:
        # Find all hours with good wind conditions
        scored_hours = []
        for i, hour in enumerate(forecast):
            # Base score on wind speed (15-20 knots is ideal)
            wind_score = 0
            wind_speed = hour.get("wind_speed", 0)
            
            if 15 <= wind_speed <= 20:
                wind_score = 100  # Perfect wind
            elif 20 < wind_speed <= 25:
                wind_score = 80   # Strong but good
            elif 12 <= wind_speed < 15:
                wind_score = 60   # A bit light but workable
            elif 25 < wind_speed <= 30:
                wind_score = 40   # Very strong, for experienced only
            elif wind_speed < 12 or wind_speed > 30:
                wind_score = 0    # Too light or too strong
            
            # Adjust score based on other factors
            # Prefer consistent wind (smaller difference between speed and gust)
            gust_diff = hour.get("wind_gust", wind_speed + 5) - wind_speed
            consistency_factor = max(0, 1 - (gust_diff / 10))  # Lower difference is better
            
            # Prefer daytime
            is_day = hour.get("is_day", 1)
            time_factor = 1.0 if is_day == 1 else 0.7
            
            # Prefer no precipitation
            precip = hour.get("precipitation", 0)
            precip_factor = max(0, 1 - (precip / 100))
            
            # Calculate final score
            final_score = wind_score * consistency_factor * time_factor * precip_factor
            
            scored_hours.append({
                "index": i,
                "timestamp": hour.get("timestamp", ""),
                "score": final_score,
                "wind_speed": wind_speed,
                "is_golden": hour.get("is_golden_window", False)
            })
        
        # Sort by score
        scored_hours.sort(key=lambda x: x["score"], reverse=True)
        
        # Find the best consecutive window (at least 2 hours)
        best_window = {
            "start_time": None,
            "end_time": None,
            "score": 0,
            "duration": 0,
            "message": "No suitable conditions found"
        }
        
        if scored_hours and scored_hours[0]["score"] > 0:
            best_hour = scored_hours[0]
            best_index = best_hour["index"]
            
            # Look for consecutive hours with good scores
            start_index = best_index
            end_index = best_index
            
            # Check backward
            i = best_index - 1
            while i >= 0 and forecast[i].get("is_golden_window", False):
                start_index = i
                i -= 1
            
            # Check forward
            i = best_index + 1
            while i < len(forecast) and forecast[i].get("is_golden_window", False):
                end_index = i
                i += 1
            
            # Calculate average score for the window
            window_hours = forecast[start_index:end_index+1]
            if window_hours:
                avg_wind = sum(h.get("wind_speed", 0) for h in window_hours) / len(window_hours)
                avg_score = sum(h.get("wind_speed", 0) for h in window_hours) / len(window_hours)
                
                # Format times for display
                try:
                    start_time = window_hours[0].get("timestamp", "")
                    end_time = window_hours[-1].get("timestamp", "")
                    
                    # Parse timestamps
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    
                    # Format for display
                    start_display = start_dt.strftime("%a %H:%M")
                    end_display = end_dt.strftime("%a %H:%M")
                    
                    duration_hours = end_index - start_index + 1
                    
                    # Create message based on conditions
                    if avg_wind >= 15 and avg_wind <= 20:
                        message = f"Perfect conditions for {duration_hours} hours!"
                    elif avg_wind > 20 and avg_wind <= 25:
                        message = f"Strong winds for {duration_hours} hours - good for experienced riders"
                    elif avg_wind >= 12 and avg_wind < 15:
                        message = f"Light but workable winds for {duration_hours} hours"
                    else:
                        message = f"Marginal conditions for {duration_hours} hours"
                    
                    best_window = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "start_display": start_display,
                        "end_display": end_display,
                        "score": round(avg_score, 1),
                        "duration": duration_hours,
                        "message": message
                    }
                except Exception as e:
                    logger.error(f"Error formatting golden window times: {str(e)}")
                    best_window["message"] = "Error calculating window times"
        
        return best_window
    
    except Exception as e:
        logger.error(f"Error calculating golden window: {str(e)}")
        return {
            "start_time": None,
            "end_time": None,
            "score": 0,
            "duration": 0,
            "message": f"Error: {str(e)}"
        }

def get_kite_size_recommendation(wind_speed: float, rider_weight: float = 75.0) -> Dict[str, Any]:
    """
    Recommends kite sizes based on wind speed and rider weight.
    
    Args:
        wind_speed: Wind speed in knots
        rider_weight: Rider weight in kg (default: 75kg)
        
    Returns:
        Dictionary with kite size recommendations
    """
    # Base calculation for a 75kg rider
    if wind_speed < 8:
        base_size = 14
        range_low = 12
        range_high = 17
        confidence = "low"
        message = "Very light wind - largest kite recommended"
    elif wind_speed < 12:
        base_size = 12
        range_low = 10
        range_high = 14
        confidence = "medium"
        message = "Light wind - larger kite recommended"
    elif wind_speed < 16:
        base_size = 10
        range_low = 9
        range_high = 12
        confidence = "high"
        message = "Medium wind - ideal conditions"
    elif wind_speed < 20:
        base_size = 9
        range_low = 7
        range_high = 10
        confidence = "high"
        message = "Medium-strong wind - good conditions"
    elif wind_speed < 25:
        base_size = 7
        range_low = 5
        range_high = 9
        confidence = "medium"
        message = "Strong wind - smaller kite recommended"
    elif wind_speed < 30:
        base_size = 5
        range_low = 4
        range_high = 7
        confidence = "medium"
        message = "Very strong wind - small kite required"
    else:
        base_size = 4
        range_low = 3
        range_high = 5
        confidence = "low"
        message = "Extreme wind - for experts only"
    
    # Adjust for rider weight
    weight_factor = rider_weight / 75.0
    adjusted_size = base_size * weight_factor
    adjusted_range_low = range_low * weight_factor
    adjusted_range_high = range_high * weight_factor
    
    return {
        "recommended_size": round(adjusted_size, 1),
        "size_range": f"{round(adjusted_range_low, 1)}-{round(adjusted_range_high, 1)}m",
        "confidence": confidence,
        "message": message
    }

