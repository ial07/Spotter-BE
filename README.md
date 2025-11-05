PROJECT: Backend — Trip Planner & HOS Log (Django + DRF)

OVERVIEW
This backend provides one primary endpoint to calculate truck trips and generate HOS logbooks.
It returns route data, intermediate stops (pickup, rest, fuel, dropoff), and daily log events.

REQUIREMENTS

Python 3.10+

pip

Virtual environment (recommended)

OpenRouteService API key (set as ORS_API_KEY in environment)

PostgreSQL or default SQLite (for local dev)

INSTALLATION (local)

Clone repo to your main directory:
git clone <repo-url>

Change directory:
cd <repo-folder>

Create and activate virtualenv:
python -m venv .venv
source .venv/bin/activate (mac/linux)
.venv\Scripts\activate (windows)

Install dependencies:
pip install -r requirements.txt

Set environment variables:
export ORS_API_KEY="your_openrouteservice_key" (mac/linux)
set ORS_API_KEY="your_openrouteservice_key" (windows)

Run migrations:
python manage.py migrate

(Optional) Create superuser:
python manage.py createsuperuser

Start development server:
python manage.py runserver localhost:8000

CORS & SESSIONS (local dev)

If you use a separate React dev server (e.g., http://localhost:5173
), set:
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_SAMESITE = "Lax" and SESSION_COOKIE_SECURE = False for local HTTP testing.

USING THE API (POSTMAN / CURL / FRONTEND)
Endpoint:
[POST] http://localhost:8000/api/calculate-trip/

Request body (JSON):
{
"currentLocation": "-74.1724, 40.7357",
"pickupLocation": "-73.9250, 40.8500",
"dropoffLocation": "-71.0589, 42.3601",
"currentCycleUsed": 45.5
}

cURL example:
curl -X POST "http://localhost:8000/api/calculate-trip/
"
-H "Content-Type: application/json"
-d '{"currentLocation":"-74.1724, 40.7357","pickupLocation":"-73.9250, 40.8500","dropoffLocation":"-71.0589, 42.3601","currentCycleUsed":45.5}'
--cookie-jar cookies.txt --cookie cookies.txt

Axios example (React):
const api = axios.create({
baseURL: "http://localhost:8000/api
",
withCredentials: true,
headers: { "Content-Type": "application/json" },
});
const response = await api.post("/calculate-trip/", payload);

Notes for frontend:

Use baseURL with "http://localhost:8000
" (use localhost, not 127.0.0.1) to keep cookie behavior consistent.

If you rely on sessions for guest users, keep withCredentials: true in axios and enable CORS_ALLOW_CREDENTIALS on backend.

SUCCESSFUL RESPONSE (overview)
Response JSON contains:

routeData:

deadhead_miles, transport_miles, total_miles

total_driving_hours

required_days

route_geometry: [deadhead_geometry, transport_geometry] (polylines)

stops: array of objects {lat, lon, type, description, duration_hours}

logbookEvents: array of daily logs

each day has { day: int, events: [ {status, start_time, duration_hours, notes} ] }

COMMON ISSUES & TROUBLESHOOTING

Empty or invalid coordinates:

Ensure coordinates are "lon,lat" and numeric.

The API validates via regex and returns 400 if invalid.

ORS errors:

Check ORS_API_KEY, network, and route accessibility.

Session not persisting with React:

Use localhost consistently.

Enable CORS_ALLOW_CREDENTIALS = True.

Set withCredentials: true in axios.

Ensure browser allows cookies for localhost.

Session key still None:

Confirm SessionMiddleware is in MIDDLEWARE and corsheaders.middleware.CorsMiddleware appears before SessionMiddleware.

You can force session creation in view: request.session.create()

EXTENSIONS & DEPLOYMENT NOTES

For production, use a proper WSGI/ASGI host (Railway/Render) and HTTPS. Then set:
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"

Replace OpenRouteService free key with a production account as needed.

Use Postgres for production; update DATABASES in settings.

CODE STRUCTURE (quick)

api/views.py: CalculateTripAPIView

services/ors_service.py: wrapper for OpenRouteService

services/hos_service.py: generate_hos_logbook

utils/helpers.py: parse_location_string, format_time_24hr, Stop type

models.py: DriverLogbook model (JSONField logs)

settings.py: CORS, session, ORS_API_KEY config

NEXT STEPS (suggested)

Add automated tests for HOS logic.

Add serialization for DriverLogbook.

Add endpoint to retrieve saved logbook by user/session id.

Add frontend example usage folder or Postman collection.

CONTACT
If you need help running this locally or want me to prepare a small frontend demo for quick testing, reply with your preferred dev environment and I will provide steps.
