"""Serve the interactive demo: the FastAPI decision service + the static web UI."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .service import app, get_model  # noqa: F401
from .signals import SIGNALS, STAGE_LABELS

WEB = Path(__file__).resolve().parents[1] / "web"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(WEB / "index.html")


@app.get("/signals.json", include_in_schema=False)
def signals_json():
    return {"stages": STAGE_LABELS,
            "signals": [{"key": s.key, "stage": s.stage, "source": s.source,
                         "why": s.why, "not_collected": s.not_collected} for s in SIGNALS]}


app.mount("/static", StaticFiles(directory=WEB), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
