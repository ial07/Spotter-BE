# Trip Planner API (Django + DRF)

## Overview

This backend calculates trip routes and generates HOS (Hours of Service) logs based on given trip details.
It returns route data, stops, and daily log events.

---

## Setup

1. Clone the repo:

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # mac/linux
   .venv\Scripts\activate      # windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your API key in env file:

   ```bash
   DJANGO_SECRET_KEY="your_openrouteservice_key"
   ```

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the server:

   ```bash
   python manage.py runserver
   ```

---

## API Usage

**Endpoint:**
`POST http://localhost:8000/api/calculate-trip/`

**Request Body:**

```json
{
  "currentLocation": "-74.1724, 40.7357",
  "pickupLocation": "-73.9250, 40.8500",
  "dropoffLocation": "-71.0589, 42.3601",
  "currentCycleUsed": 45.5
}
```

**Example (cURL):**

```bash
curl -X POST "http://localhost:8000/api/calculate-trip/" \
 -H "Content-Type: application/json" \
 -d '{"currentLocation":"-74.1724, 40.7357","pickupLocation":"-73.9250, 40.8500","dropoffLocation":"-71.0589, 42.3601","currentCycleUsed":45.5}'
```

---

## Notes

* Use **localhost** instead of 127.0.0.1 to keep cookies consistent.
* Enable `CORS_ALLOW_CREDENTIALS = True` in Django settings for React integration.
* Make sure `withCredentials: true` is set in Axios.

---

## Response

Returns:

* Route info (miles, hours, required days)
* Stops (pickup, rest, fuel, dropoff)
* Daily HOS logs

---

## Deployment Tips

* Use HTTPS and production-ready settings:

  ```ini
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SESSION_COOKIE_SAMESITE = "None"
  ```
* Use PostgreSQL for production.
