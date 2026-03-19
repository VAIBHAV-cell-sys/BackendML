"""
Weather service to fetch weather data from OpenWeather API
"""
import requests
from typing import Dict, Optional
from config import Config


class WeatherService:
    """
    Service class to interact with OpenWeather API
    """
    
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.OPENWEATHER_BASE_URL
    
    def get_weather(self, location: str) -> Dict:
        """
        Fetch current weather data for a given location
        
        Args:
            location (str): City name or location string
        
        Returns:
            dict: Weather data containing temperature, humidity, rainfall, and condition
        
        Raises:
            Exception: If API call fails or location is invalid
        """
        try:
            # Prepare API request parameters
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"  # Use Celsius for temperature
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            
            # Check if request was successful
            if response.status_code == 404:
                raise ValueError(f"Location '{location}' not found")
            
            response.raise_for_status()
            
            # Parse response data
            data = response.json()
            
            # Extract relevant weather information
            weather_data = {
                "temp": round(data["main"]["temp"], 1),
                "humidity": data["main"]["humidity"],
                "rain": self._extract_rainfall(data),
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "feels_like": round(data["main"]["feels_like"], 1),
                "pressure": data["main"]["pressure"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "clouds": data.get("clouds", {}).get("all", 0)
            }
            
            return weather_data
        
        except requests.exceptions.Timeout:
            raise Exception("Weather API request timed out. Please try again.")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {str(e)}")
        
        except KeyError as e:
            raise Exception(f"Unexpected weather data format: {str(e)}")
    
    def _extract_rainfall(self, data: Dict) -> float:
        """
        Safely extract rainfall data from API response
        
        Args:
            data (dict): Raw API response data
        
        Returns:
            float: Rainfall amount in mm (0.0 if no rain data available)
        """
        # Check for rain in last 1 hour
        if "rain" in data:
            if "1h" in data["rain"]:
                return round(data["rain"]["1h"], 2)
            elif "3h" in data["rain"]:
                # Convert 3h rain to approximate 1h value
                return round(data["rain"]["3h"] / 3, 2)
        
        # No rain data available
        return 0.0
    
    def get_weather_summary(self, location: str) -> str:
        """
        Get a human-readable weather summary
        
        Args:
            location (str): City name or location string
        
        Returns:
            str: Weather summary text
        """
        weather = self.get_weather(location)
        
        summary = (
            f"{weather['condition']} ({weather['description']}), "
            f"{weather['temp']}°C (feels like {weather['feels_like']}°C), "
            f"Humidity: {weather['humidity']}%"
        )
        
        if weather['rain'] > 0:
            summary += f", Rainfall: {weather['rain']}mm"
        
        return summary


# Create a singleton instance
weather_service = WeatherService()


# Convenience function for direct import
def get_weather(location: str) -> Dict:
    """
    Convenience function to fetch weather data
    
    Args:
        location (str): City name or location string
    
    Returns:
        dict: Weather data
    """
    return weather_service.get_weather(location)
