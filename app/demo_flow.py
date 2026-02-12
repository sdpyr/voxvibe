from __future__ import annotations

import json
import threading
import time
from urllib import request

from .api import run_server


def _call(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, data=data, headers=headers)
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_demo() -> None:
    thread = threading.Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": 8010}, daemon=True)
    thread.start()
    time.sleep(0.2)

    base = "http://127.0.0.1:8010"
    print("Health:", _call("GET", f"{base}/health"))

    created = _call(
        "POST",
        f"{base}/sessions",
        {"therapist_id": "t-101", "patient_id": "p-501", "consent_captured": True},
    )
    session_id = created["session"]["id"]
    print("Session created:", session_id)

    _call(
        "POST",
        f"{base}/sessions/{session_id}/transcript",
        {
            "speaker": "Patient",
            "start_sec": 22,
            "end_sec": 30,
            "text": "Son zamanlarda kaygım yükseldi.",
        },
    )

    _call(
        "POST",
        f"{base}/sessions/{session_id}/emotion",
        {
            "timestamp_sec": 24,
            "anxiety": 0.91,
            "sadness": 0.28,
            "anger": 0.12,
            "neutral": 0.15,
        },
    )

    _call(
        "POST",
        f"{base}/sessions/{session_id}/notes",
        {
            "timestamp_sec": 24,
            "note_type": "follow-up",
            "text": "Gelecek seansta nefes tekniklerini değerlendirelim.",
        },
    )

    _call(
        "POST",
        f"{base}/sessions/{session_id}/reactions",
        {
            "timestamp_sec": 24,
            "kind": "critical",
            "label": "Kritik",
            "emoji": "🚩",
            "intensity": 1,
        },
    )

    detail = _call("GET", f"{base}/sessions/{session_id}")
    summary = _call("GET", f"{base}/sessions/{session_id}/smart-summary")
    print("Session detail:")
    print(json.dumps(detail, indent=2, ensure_ascii=False))
    print("Smart summary:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_demo()
