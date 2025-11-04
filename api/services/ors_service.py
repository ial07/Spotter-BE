from django.conf import settings 
import openrouteservice
from ..utils.helpers import parse_location_string # Import the helper

def get_route_data(location_strings):
    """Fetches driving route data (distance and duration) from ORS by parsing coordinate strings."""
    try:
        # 1. Initialize client
        client = openrouteservice.Client(
            key=settings.ORS_API_KEY, 
            requests_kwargs={'verify': False}
        )
        
        # 2. Parse coordinate strings into the required list of lists
        coordinates_list = [
            parse_location_string(loc) for loc in location_strings
        ]
            
        # 3. Request directions with numeric coordinates
        route_result = client.directions(
            coordinates=coordinates_list, 
            profile='driving-hgv', 
            preference='shortest',
        )

        if not route_result.get('routes'):
            raise Exception("ORS returned no routes. Check coordinates or road access.")
        
        route_info = route_result['routes'][0]
        distance_m = route_info['summary']['distance']
        duration_s = route_info['summary']['duration']

        return {
            "distance_miles": distance_m * 0.000621371, 
            "duration_hours": duration_s / 3600,       
            "route_geometry": route_info.get('geometry'),
            "status": "success"
        }
        
    except Exception as e:
        # Ensure errors from coordinate parsing are returned to the user
        print(f"ORS API Error: {e}") 
        return {"status": "error", "message": str(e)}