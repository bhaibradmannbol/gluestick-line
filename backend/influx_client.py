# influx_client.py — Writes production data to InfluxDB 2.x
# Two measurements:
#   "production"    — one point per finished product
#   "machine_state" — one point each time the machine state changes
# cspell:words gluestick mytoken

import os
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ── Config from environment variables (set in docker-compose.yml) ─────────────
INFLUX_URL    = os.getenv("INFLUX_URL",    "http://localhost:8086")
INFLUX_TOKEN  = os.getenv("INFLUX_TOKEN",  "mytoken123")
INFLUX_ORG    = os.getenv("INFLUX_ORG",    "gluestick")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "production")

# ── Lazy connection (created on first write) ──────────────────────────────────
_client    = None
_write_api = None

def _get_write_api():
    """Return a shared write API, creating the connection if needed."""
    global _client, _write_api
    if _write_api is None:
        _client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        _write_api = _client.write_api(write_options=SYNCHRONOUS)
    return _write_api


# ── Public write functions ────────────────────────────────────────────────────

def write_product(product: dict):
    """
    Write one data point when a product finishes (completed or defective).
    Tags allow Grafana to filter by status or station.
    """
    try:
        point = (
            Point("production")
            .tag("status",  product["status"])          # completed | defective
            .tag("station", product["station"])          # which station it finished at
            .field("product_id",    product["product_id"])
            .field("is_defective",  1 if product["status"] == "defective" else 0)
            .field("defect_reason", product["defect_reason"] or "none")
            .time(product["completed_at"])
        )
        _get_write_api().write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    except Exception as e:
        # Never crash the simulation — just warn in console
        print(f"[InfluxDB] write_product failed: {e}")


def write_machine_state(state: str):
    """
    Write one data point each time the machine state changes.
    Used to draw a state timeline in Grafana.
    """
    try:
        point = (
            Point("machine_state")
            .tag("state", state)          # idle | running | faulted
            .field("value", 1)            # Grafana needs at least one field
            .time(datetime.now(timezone.utc))
        )
        _get_write_api().write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    except Exception as e:
        print(f"[InfluxDB] write_machine_state failed: {e}")
