from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Import services and utilities
from .services.ors_service import get_route_data
from .services.hos_service import generate_hos_logbook
from .utils.helpers import parse_location_string, Stop
from .constants import MAX_DRIVING_BEFORE_BREAK, MIN_MANDATORY_BREAK 
from .models import DriverLogbook


class CalculateTripAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        current_location_raw = data.get('currentLocation', '').strip()
        pickup_location_raw = data.get('pickupLocation', '').strip()
        dropoff_location_raw = data.get('dropoffLocation', '').strip()
        current_cycle_used = float(data.get('currentCycleUsed', 0))

        # Validation
        for name, value in {
            "currentLocation": current_location_raw,
            "pickupLocation": pickup_location_raw,
            "dropoffLocation": dropoff_location_raw
        }.items():
            if not value:
                return Response(
                    {"message": f"Missing or invalid location input: '{name}' must be a coordinate string (Lon,Lat)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Route calculation
        deadhead_route = get_route_data([current_location_raw, pickup_location_raw])
        if deadhead_route['status'] == 'error':
            return Response({"message": f"Error calculating Deadhead route: {deadhead_route['message']}"}, status=500)

        transport_route = get_route_data([pickup_location_raw, dropoff_location_raw])
        if transport_route['status'] == 'error':
            return Response({"message": f"Error calculating Transport route: {transport_route['message']}"}, status=500)

        # Coordinates
        try:
            pickup_coords = parse_location_string(pickup_location_raw)
            dropoff_coords = parse_location_string(dropoff_location_raw)
        except ValueError as e:
            return Response({"message": f"Coordinate parsing error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        total_driving_hours = deadhead_route['duration_hours'] + transport_route['duration_hours']
        total_trip_miles = deadhead_route['distance_miles'] + transport_route['distance_miles']
        total_on_duty_non_driving = 2.0

        intermediate_stops = []
        if total_driving_hours > MAX_DRIVING_BEFORE_BREAK:
            intermediate_stops.append({
                "lat": pickup_coords[1],
                "lon": pickup_coords[0],
                "type": "REST",
                "description": "Mandatory 30-Min Rest Break (Approximate Location at Pickup)",
                "duration_hours": MIN_MANDATORY_BREAK,
            })

        mid_lat = (pickup_coords[1] + dropoff_coords[1]) / 2
        mid_lon = (pickup_coords[0] + dropoff_coords[0]) / 2
        fuel_stop = {
            "lat": mid_lat,
            "lon": mid_lon,
            "type": "FUEL",
            "description": "Mid-Route Refueling Stop (Approximate Location)",
            "duration_hours": 0.5,
        }
        intermediate_stops.append(fuel_stop)
        total_on_duty_non_driving += 0.5

        if not request.session.session_key:
            request.session.create()

        

        # === Retrieve previous logs ===
        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None

        if user:
            driver_logbook, _ = DriverLogbook.objects.get_or_create(user=user)
            old_logs = driver_logbook.logs if driver_logbook.logs else []
        else:
            # read from session safely
            old_logs = request.session.get("logbook_events", [])
        

        last_day_number = old_logs[-1]["day"] if old_logs else 0

        # === Generate new logs ===
        new_logs = generate_hos_logbook(
            total_driving_hours,
            current_cycle_used,
            total_on_duty_non_driving,
            pickup_location_raw
        )

        # Adjust day numbers to continue incrementing
        for log in new_logs:
            log["day"] += last_day_number

        combined_logs = old_logs + new_logs

        # === Save updated logs ===
        if user:
            driver_logbook.logs = combined_logs
            driver_logbook.save()
        else:
            request.session["logbook_events"] = combined_logs
            request.session.modified = True
            request.session.save()  

        # === Final response ===
        response_data = {
            "routeData": {
                "deadhead_miles": round(deadhead_route['distance_miles'], 1),
                "transport_miles": round(transport_route['distance_miles'], 1),
                "total_miles": round(total_trip_miles, 1),
                "total_driving_hours": round(total_driving_hours, 1),
                "required_days": len(new_logs),
                "route_geometry": [
                    deadhead_route.get('route_geometry'),
                    transport_route.get('route_geometry')
                ],
                "stops": intermediate_stops,
            },
            "logbookEvents": combined_logs
        }

        return Response(response_data, status=status.HTTP_200_OK)
