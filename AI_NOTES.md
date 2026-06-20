# AI Notes

Use this file as appendix evidence for AI-assisted development.

## Prompts Worth Saving

- Requests to scaffold backend routes
- Requests to fix Docker or Compose paths
- Requests to wire InfluxDB and Grafana
- Requests to debug real terminal errors

## Outputs Worth Saving

- Generated `FastAPI` route code
- Compose and Docker fixes
- Grafana provisioning files
- HMI updates for machine state and defect display

## Bugs And Fixes To Record

- Missing `backend/main.py` while Docker expected `main:app`
- `requirements.txt` existed in `backend/`, not repo root
- Local `python` command missing; used `python3`
- Port `8000` already occupied during local testing
- Compose file paths were wrong because it lived inside `frontend/`
- Simulation needed to stop on faults instead of continuing silently

## Short Appendix Notes

- AI helped inspect the existing project before edits.
- AI suggestions were checked against real runtime errors.
- Path and startup issues were corrected iteratively, not by full rewrite.
