# gluestick-line

Glue stick manufacturing line simulator for an Advanced Programming project.

## What It Includes

- Python backend with `FastAPI`
- 4 glue-stick assembly stations
- Start / Stop / Reset HMI
- Defect detection and fault display
- InfluxDB for time-series storage
- Grafana with a preprovisioned dashboard

## Production Stations

1. Glue core insertion
2. Twist mechanism assembly
3. Outer body mounting
4. Cap placement

## Run With Docker

From the project root:

```bash
docker compose -f frontend/dockercompose.yml --env-file frontend/.env up --build
```

Open:

- HMI: `http://127.0.0.1:8000`
- Backend health: `http://127.0.0.1:8000/health`
- Grafana: `http://127.0.0.1:3000`
- InfluxDB: `http://127.0.0.1:8086`

Default Grafana login:

- Username: `admin`
- Password: value from `frontend/.env` (`admin` by default)

## Run Backend Locally

Install dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
```

Start the backend from the project root:

```bash
python3 -m uvicorn backend.main:app --reload
```

If port `8000` is already in use:

```bash
python3 -m uvicorn backend.main:app --reload --port 8001
```

## Main Files

- `backend/main.py`: API routes and app wiring
- `backend/simulation.py`: production line logic
- `backend/influx_client.py`: InfluxDB writes
- `frontend/index.html`: HMI page
- `frontend/dockercompose.yml`: Docker stack

## AI Appendix Support

Keep a short log of:

- prompts you used
- errors you hit
- fixes applied
- what AI suggestions were accepted or corrected
