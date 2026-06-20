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

## Assignment Checklist

- `4` assembly stages: implemented in `backend/simulation.py`
- Python backend: implemented with `FastAPI`
- HMI with Start / Stop / Reset: implemented in `frontend/index.html`
- Visible machine state: shown in the state badge
- Visible fault and defect reason: shown in the HMI defect panel
- InfluxDB integration: implemented in `backend/influx_client.py`
- Grafana metric dashboard: provisioned under `grafana/provisioning`

## Git And Docker Notes

- Git should be used to save each major milestone such as backend setup, HMI wiring, Docker integration, and Grafana setup.
- Docker is used to run the backend, InfluxDB, and Grafana together with one compose command.
- The current compose entrypoint for the stack is `frontend/dockercompose.yml`.

Useful manual commands:

```bash
git status
git add .
git commit -m "Finish glue stick production line simulator"
```

```bash
docker compose -f frontend/dockercompose.yml --env-file frontend/.env config
docker compose -f frontend/dockercompose.yml --env-file frontend/.env up --build
```

## Grafana Notes

- Grafana is preconfigured to use the InfluxDB service in Docker.
- The default dashboard shows:
  - total products logged
  - defective products
  - defects over time
- If the dashboard is empty at first, start the line in the HMI and let a few products run so data is written to InfluxDB.

## AI Appendix Support

Keep a short log of:

- prompts you used
- errors you hit
- fixes applied
- what AI suggestions were accepted or corrected

Suggested evidence to save:

- the prompt where the backend routes were created
- the prompt where Docker paths were fixed
- the terminal error showing missing `requirements.txt`
- the terminal error showing port `8000` already in use
- the prompt where fault handling was improved
