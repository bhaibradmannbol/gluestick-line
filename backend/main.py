from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from influx_client import write_machine_state, write_product
from simulation import ProductionLine


app = FastAPI(title="Glue Stick Production Line")
line = ProductionLine()
line.on_product_complete = write_product

FRONTEND_DIR = Path("/frontend")
INDEX_FILE = FRONTEND_DIR / "index.html"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _record_machine_state(state: str) -> None:
    """Write machine-state changes without breaking the API if Influx is down."""
    write_machine_state(state)


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


@app.post("/start")
def start_line():
    result = line.start()
    if result["ok"]:
        _record_machine_state("running")
    return result


@app.post("/stop")
def stop_line():
    result = line.stop()
    if result["ok"]:
        _record_machine_state("idle")
    return result


@app.post("/reset")
def reset_line():
    result = line.reset()
    if result["ok"]:
        _record_machine_state("idle")
    return result
