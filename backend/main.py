import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

try:
    from .influx_client import write_machine_state, write_product
    from .simulation import ProductionLine
except ImportError:
    from influx_client import write_machine_state, write_product
    from simulation import ProductionLine


app = FastAPI(title="Glue Stick Production Line")
line = ProductionLine()
line.on_product_complete = write_product
line.on_machine_state_change = write_machine_state

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
CONTAINER_FRONTEND_DIR = Path("/frontend")
FRONTEND_DIR = CONTAINER_FRONTEND_DIR if CONTAINER_FRONTEND_DIR.exists() else PROJECT_ROOT / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return JSONResponse(
        {
            "message": "Backend is running, but frontend/index.html is not mounted.",
            "status_endpoint": "/status",
        }
    )


@app.get("/status")
def get_status():
    return line.get_status()


@app.get("/health")
def healthcheck():
    return {"ok": True}


@app.get("/config")
def get_config():
    return {
        "grafana_url": os.getenv("PUBLIC_GRAFANA_URL", "").strip(),
    }


@app.post("/start")
def start_line():
    return line.start()


@app.post("/stop")
def stop_line():
    return line.stop()


@app.post("/reset")
def reset_line():
    return line.reset()
