# api/utils/helpers.py
import re

# Define the structure for a Stop (for map display)
Stop = dict[str, str | float]

def format_time_24hr(time_float):
    """
    Converts a floating-point time value (e.g., 7.5) into a 24-hour HH:MM string (e.g., '07:30').
    The modulo 24 ensures time wraps correctly if calculated time exceeds 24.
    """
    # Calculate hours and ensure it stays within 0-23
    hours = int(time_float) % 24
    # Calculate minutes from the fractional part of the time
    minutes = int((time_float % 1) * 60)
    return f"{hours:02}:{minutes:02}"

def parse_location_string(location_string):
    """Converts a 'lon,lat' string into a list of two floats: [lon, lat]"""
    location_string = str(location_string).strip()
    try:
        # Use regex to find two numbers separated by a comma (with optional whitespace)
        match = re.match(r"\s*([+-]?\d+\.?\d*)\s*,\s*([+-]?\d+\.?\d*)\s*", location_string)
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            # OpenRouteService expects [Longitude, Latitude]
            return [lon, lat] 
        else:
            raise ValueError(f"Input is not a valid coordinate pair: {location_string}")
    except Exception as e:
        raise ValueError(f"Invalid coordinate format or values: {location_string}") from e