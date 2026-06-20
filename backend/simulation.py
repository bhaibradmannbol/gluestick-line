# simulation.py — Glue Stick Production Line Simulation
# Runs 4 assembly stations in a background thread.
# Each product has a 20% chance of defect at each station.

import threading
import time
import random
from datetime import datetime, timezone

# ── Station definitions ───────────────────────────────────────────────────────

STATIONS = [
    {"id": 1, "name": "Glue Core Insertion",     "defect": "glue core missing"},
    {"id": 2, "name": "Twist Mechanism Assembly", "defect": "twist mechanism jammed"},
    {"id": 3, "name": "Outer Body Mounting",      "defect": "body not locked"},
    {"id": 4, "name": "Cap Placement",            "defect": "cap not fitted"},
]

STATION_TIME  = 1.5   # seconds spent at each station
DEFECT_CHANCE = 0.20  # 20% probability of defect per station


# ── Production Line class ─────────────────────────────────────────────────────

class ProductionLine:

    def __init__(self):
        # Machine state: idle | running | faulted
        self.machine_state      = "idle"
        self.current_station    = ""
        self.current_product_id = 0
        self.product_status     = "waiting"
        self.created_at         = None
        self.completed_at       = None
        self.total_produced     = 0
        self.defective_count    = 0
        self.last_defect_reason = ""

        # Optional callbacks — set by main.py
        self.on_product_complete = None
        self.on_machine_state_change = None

        self._running = False
        self._lock    = threading.Lock()   # prevents race conditions
        self._thread  = None
        self._run_token = 0

    def _set_machine_state_locked(self, state: str):
        changed = self.machine_state != state
        self.machine_state = state
        return state if changed else None

    # ── Public controls (called by FastAPI endpoints) ─────────────────────────

    def start(self):
        state_to_emit = None
        with self._lock:
            if self._running:
                return {"ok": False, "msg": "Already running"}
            if self.machine_state == "faulted":
                return {"ok": False, "msg": "Machine faulted — press Reset first"}
            self._running = True
            self._run_token += 1
            self.product_status = "waiting"
            state_to_emit = self._set_machine_state_locked("running")

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        if state_to_emit and self.on_machine_state_change:
            self.on_machine_state_change(state_to_emit)
        return {"ok": True, "msg": "Production started"}

    def stop(self):
        state_to_emit = None
        with self._lock:
            self._running        = False
            self._run_token += 1
            self.current_station = ""
            self.product_status  = "waiting"
            self.created_at      = None
            self.completed_at    = None
            self.last_defect_reason = ""
            state_to_emit = self._set_machine_state_locked("idle")
        self._join_worker()
        if state_to_emit and self.on_machine_state_change:
            self.on_machine_state_change(state_to_emit)
        return {"ok": True, "msg": "Production stopped"}

    def reset(self):
        state_to_emit = None
        with self._lock:
            self._running           = False
            self._run_token += 1
            self.current_station    = ""
            self.current_product_id = 0
            self.product_status     = "waiting"
            self.created_at         = None
            self.completed_at       = None
            self.total_produced     = 0
            self.defective_count    = 0
            self.last_defect_reason = ""
            state_to_emit = self._set_machine_state_locked("idle")
        self._join_worker()
        if state_to_emit and self.on_machine_state_change:
            self.on_machine_state_change(state_to_emit)
        return {"ok": True, "msg": "Line reset — all counters cleared"}

    def get_status(self):
        with self._lock:
            return {
                "machine_state":      self.machine_state,
                "current_station":    self.current_station,
                "current_product_id": self.current_product_id,
                "product_status":     self.product_status,
                "defect_reason":      self.last_defect_reason,
                "created_at":         self.created_at,
                "completed_at":       self.completed_at,
                "total_produced":     self.total_produced,
                "defective_count":    self.defective_count,
                "last_defect_reason": self.last_defect_reason,
            }

    # ── Internal loop (runs in background thread) ─────────────────────────────

    def _join_worker(self):
        thread = self._thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=STATION_TIME + 0.5)

    def _run_loop(self):
        """Keeps producing glue sticks until stopped."""
        while True:
            with self._lock:
                if not self._running:
                    break
                run_token = self._run_token
            self._process_one_product(run_token)
            with self._lock:
                keep_running = self._running
            if keep_running:
                time.sleep(0.3)   # brief gap between products

    def _process_one_product(self, run_token: int):
        """Moves one product through all 4 stations. Stops at first defect."""
        with self._lock:
            if run_token != self._run_token or not self._running:
                return
            self.current_product_id += 1
            pid = self.current_product_id

        created_at    = datetime.now(timezone.utc)
        is_defective  = False
        defect_reason = ""
        failed_station = STATIONS[-1]["name"]   # default fallback
        state_to_emit = None

        with self._lock:
            if run_token != self._run_token or not self._running:
                return
            self.created_at = created_at.isoformat()
            self.completed_at = None
            self.product_status = "processing"
            self.last_defect_reason = ""

        for station in STATIONS:
            with self._lock:
                if not self._running:
                    return   # machine was stopped mid-product
                self.current_station = station["name"]

            time.sleep(STATION_TIME)   # simulate work being done

            with self._lock:
                if run_token != self._run_token or not self._running:
                    return

            # Roll defect check
            if random.random() < DEFECT_CHANCE:
                is_defective   = True
                defect_reason  = station["defect"]
                failed_station = station["name"]
                with self._lock:
                    if run_token != self._run_token or not self._running:
                        return
                    self._running = False
                    state_to_emit = self._set_machine_state_locked("faulted")
                    self.product_status = "defective"
                    self.last_defect_reason = defect_reason
                break   # no point continuing assembly with a defect

        # ── Final product result ──────────────────────────────────────────────
        completed_at = datetime.now(timezone.utc)
        status = "defective" if is_defective else "completed"

        with self._lock:
            if run_token != self._run_token:
                return
            self.total_produced += 1
            if is_defective:
                self.defective_count += 1
            else:
                self.product_status = "completed"
            self.current_station = ""
            self.completed_at = completed_at.isoformat()

        if state_to_emit and self.on_machine_state_change:
            self.on_machine_state_change(state_to_emit)

        # Send data to InfluxDB via callback (set in main.py)
        if self.on_product_complete:
            self.on_product_complete({
                "product_id":    pid,
                "status":        status,
                "defect_reason": defect_reason,
                "station":       failed_station,
                "created_at":    created_at,
                "completed_at":  completed_at,
            })
