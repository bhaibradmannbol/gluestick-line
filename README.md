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
- `grafana/Dockerfile`: Railway-friendly Grafana image with provisioning
- `frontend/index.html`: HMI page
- `frontend/dockercompose.yml`: Docker stack

## Railway Deployment

Deploy this as `3` services inside one Railway project:

1. `backend`
   - Source directory: `backend`
   - Dockerfile: `backend/Dockerfile`
   - Public networking: enabled

2. `influxdb`
   - Deploy from image: `influxdb:2.7`
   - Add a volume mounted at `/var/lib/influxdb2`
   - Keep private unless you specifically need public access

3. `grafana`
   - Source directory: `grafana`
   - Dockerfile: `grafana/Dockerfile`
   - Add a volume mounted at `/var/lib/grafana`
   - Public networking: enabled

Shared variables to create in Railway:

```text
INFLUX_TOKEN=mytoken123
INFLUX_ORG=gluestick
INFLUX_BUCKET=production
INFLUX_ADMIN_USER=admin
INFLUX_ADMIN_PASSWORD=adminpass123
GRAFANA_PASSWORD=admin
```

Service variables:

- `backend`
  - `INFLUX_URL=http://influxdb.railway.internal:8086`
  - `INFLUX_TOKEN=${{shared.INFLUX_TOKEN}}`
  - `INFLUX_ORG=${{shared.INFLUX_ORG}}`
  - `INFLUX_BUCKET=${{shared.INFLUX_BUCKET}}`
  - `PUBLIC_GRAFANA_URL=https://<your-grafana-public-domain>`

- `influxdb`
  - `DOCKER_INFLUXDB_INIT_MODE=setup`
  - `DOCKER_INFLUXDB_INIT_USERNAME=${{shared.INFLUX_ADMIN_USER}}`
  - `DOCKER_INFLUXDB_INIT_PASSWORD=${{shared.INFLUX_ADMIN_PASSWORD}}`
  - `DOCKER_INFLUXDB_INIT_ORG=${{shared.INFLUX_ORG}}`
  - `DOCKER_INFLUXDB_INIT_BUCKET=${{shared.INFLUX_BUCKET}}`
  - `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${{shared.INFLUX_TOKEN}}`

- `grafana`
  - `GF_SECURITY_ADMIN_PASSWORD=${{shared.GRAFANA_PASSWORD}}`
  - `INFLUX_URL=http://influxdb.railway.internal:8086`
  - `INFLUX_ORG=${{shared.INFLUX_ORG}}`
  - `INFLUX_BUCKET=${{shared.INFLUX_BUCKET}}`
  - `INFLUX_TOKEN=${{shared.INFLUX_TOKEN}}`

Deployment flow:

1. Create an empty Railway project.
2. Add the `backend` service from this repo using source directory `backend`.
3. Add the `grafana` service from this repo using source directory `grafana`.
4. Add the `influxdb` service from the official image `influxdb:2.7`.
5. Attach the required volumes to `influxdb` and `grafana`.
6. Generate public domains for `backend` and `grafana`.
7. Set `PUBLIC_GRAFANA_URL` on `backend` to the generated Grafana domain.
8. Redeploy `backend` so the dashboard button points to the live Grafana instance.

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
