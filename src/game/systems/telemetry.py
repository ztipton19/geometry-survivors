"""Run telemetry logger for balance tuning."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TELEMETRY_PATH = Path(__file__).resolve().parent.parent / "data" / "run_telemetry.jsonl"


def append_run_telemetry(entry: dict[str, Any]) -> None:
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **entry,
    }
    TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TELEMETRY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
