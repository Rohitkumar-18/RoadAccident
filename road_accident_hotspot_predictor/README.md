# Road Accident Hotspot Predictor
A full-stack MCA project starter using **Django REST Framework + React (Vite) + MySQL + DBSCAN**.

## What is included
- Django REST API for accident records, CSV upload, hotspot analysis and dashboard statistics.
- React dashboard with CSV upload, summary cards, accident table and interactive Leaflet map.
- MySQL database configuration and a SQL schema file.
- DBSCAN geographic clustering and an illustrative risk score based on frequency, severity and recency.
- Sample CSV for local testing.

> **Important:** This is a decision-support academic prototype. It identifies clusters in historical records; it does not guarantee or predict that an individual accident will occur. The supplied sample records are synthetic and must not be presented as real Bengaluru accident data.

## Requirements
- Python 3.10+
- Node.js 18+
- MySQL 8+
- VS Code (recommended)

## 1. Create the MySQL database
Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE road_safety_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

The full suggested schema is in `database/schema.sql`. Django migrations create the application tables automatically, so do not manually create those same tables if you use migrations.

## 2. Start the Django backend
Open a terminal in `backend/`:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update the MySQL username/password. If you prefer not to use a `.env` file, set the environment variables shown in `.env.example`.

Run migrations and start the API:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

API base URL: `http://127.0.0.1:8000/api/`

Useful endpoints:
- `GET /api/health/`
- `GET /api/accidents/`
- `POST /api/accidents/upload/` (multipart form field: `file`)
- `GET /api/hotspots/`
- `POST /api/analysis/run/`
- `GET /api/dashboard/`

## 3. Start the React frontend
Open a second terminal in `frontend/`:

```bash
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`).

The React app calls the Django API at `http://127.0.0.1:8000/api/`. You can override it by creating `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## 4. Load the sample data
Use the React **Upload CSV** control and select `sample_data/accidents_sample.csv`. Then click **Run hotspot analysis**.

CSV columns required:
- `accident_id`
- `date` (YYYY-MM-DD)
- `time` (HH:MM or HH:MM:SS)
- `latitude`
- `longitude`

Optional columns:
- `accident_type`, `severity`, `weather`, `road_type`, `vehicle_type`

Coordinates must be valid latitude/longitude values. For meaningful geographic hotspot detection, use real, properly licensed, location-level records. Many public datasets contain only aggregated counts and cannot be mapped to exact hotspots.

## 5. How the analysis works
1. The API validates and stores accident rows.
2. DBSCAN groups nearby coordinates using a haversine distance metric.
3. Each cluster gets a center point, accident count and a simple risk score.
4. The risk score combines normalized frequency, severity and recency. The weights are educational example values, not an official road-safety standard.
5. React displays cluster markers and summary information on the map.

## 6. Troubleshooting
- **MySQL access denied:** check `DB_NAME`, `DB_USER`, `DB_PASSWORD`, host and port in `backend/.env`.
- **Unknown database:** create `road_safety_db` first.
- **CORS error:** keep the React dev server on `localhost:5173`; the Django settings allow this origin.
- **No hotspots:** upload rows with valid coordinates and enough nearby points. DBSCAN's default `min_samples` is 3.
- **Map tiles blank:** internet access is required for OpenStreetMap tiles.
- **No data after upload:** check the Django terminal for CSV validation errors and ensure required column names are present.

## Project structure
```text
road_accident_hotspot_predictor/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── road_safety/
│   └── accidents/
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
├── database/schema.sql
└── sample_data/accidents_sample.csv
```
