from __future__ import annotations

import json
import mimetypes
from dataclasses import asdict
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .schemas import BranchNote, EmotionPoint, ReactionMark, TranscriptChunk
from .service import NotFoundError, SentioTraceService, ValidationError




STATIC_DIR = Path(__file__).with_name("static")


def _read_static(path: str) -> tuple[bytes, str] | None:
    if path == "/":
        file_path = STATIC_DIR / "index.html"
    elif path.startswith("/static/"):
        file_path = STATIC_DIR / path.removeprefix("/static/")
    else:
        return None

    resolved = file_path.resolve()
    if not str(resolved).startswith(str(STATIC_DIR.resolve())) or not resolved.exists() or not resolved.is_file():
        return None

    content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
    return resolved.read_bytes(), content_type

def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


class SentioTraceHandler(BaseHTTPRequestHandler):
    service = SentioTraceService()

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(_to_jsonable(payload)).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        static_file = _read_static(self.path)
        if static_file is not None:
            body, content_type = static_file
            self._send_bytes(HTTPStatus.OK, body, content_type)
            return

        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return

        if self.path.startswith("/sessions/"):
            if self.path.endswith("/smart-summary"):
                session_id = self.path.removeprefix("/sessions/").removesuffix("/smart-summary").rstrip("/")
                try:
                    summary = self.service.generate_smart_summary(session_id)
                    self._send_json(HTTPStatus.OK, {"smart_summary": summary})
                except NotFoundError as exc:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
                return

            session_id = self.path.removeprefix("/sessions/")
            try:
                detail = self.service.get_session_detail(session_id)
                self._send_json(HTTPStatus.OK, detail)
            except NotFoundError as exc:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._read_json()

            if self.path == "/sessions":
                session = self.service.create_session(
                    therapist_id=payload.get("therapist_id", ""),
                    patient_id=payload.get("patient_id", ""),
                    consent_captured=bool(payload.get("consent_captured", False)),
                )
                self._send_json(HTTPStatus.CREATED, {"session": _to_jsonable(asdict(session))})
                return

            if self.path.startswith("/sessions/") and self.path.endswith("/transcript"):
                session_id = self.path.removeprefix("/sessions/").removesuffix("/transcript").rstrip("/")
                chunk = TranscriptChunk(
                    speaker=payload["speaker"],
                    start_sec=float(payload["start_sec"]),
                    end_sec=float(payload["end_sec"]),
                    text=payload["text"],
                )
                created = self.service.add_transcript_chunk(session_id, chunk)
                self._send_json(HTTPStatus.CREATED, {"transcript_chunk": asdict(created)})
                return

            if self.path.startswith("/sessions/") and self.path.endswith("/emotion"):
                session_id = self.path.removeprefix("/sessions/").removesuffix("/emotion").rstrip("/")
                point = EmotionPoint(
                    timestamp_sec=float(payload["timestamp_sec"]),
                    anxiety=float(payload["anxiety"]),
                    sadness=float(payload["sadness"]),
                    anger=float(payload["anger"]),
                    neutral=float(payload["neutral"]),
                )
                created = self.service.add_emotion_point(session_id, point)
                self._send_json(HTTPStatus.CREATED, {"emotion_point": asdict(created)})
                return

            if self.path.startswith("/sessions/") and self.path.endswith("/notes"):
                session_id = self.path.removeprefix("/sessions/").removesuffix("/notes").rstrip("/")
                note = BranchNote(
                    timestamp_sec=float(payload["timestamp_sec"]),
                    note_type=payload["note_type"],
                    text=payload["text"],
                    voice_note_url=payload.get("voice_note_url"),
                )
                created = self.service.add_branch_note(session_id, note)
                self._send_json(HTTPStatus.CREATED, {"branch_note": asdict(created)})
                return

            if self.path.startswith("/sessions/") and self.path.endswith("/reactions"):
                session_id = self.path.removeprefix("/sessions/").removesuffix("/reactions").rstrip("/")
                reaction = ReactionMark(
                    timestamp_sec=float(payload["timestamp_sec"]),
                    kind=payload["kind"],
                    label=payload["label"],
                    emoji=payload["emoji"],
                    intensity=float(payload.get("intensity", 1.0)),
                )
                created = self.service.add_reaction_mark(session_id, reaction)
                self._send_json(HTTPStatus.CREATED, {"reaction": asdict(created)})
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except KeyError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": f"missing field: {exc.args[0]}"})
        except ValidationError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except NotFoundError as exc:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid json"})


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), SentioTraceHandler)
    print(f"SentioTrace API running at http://{host}:{port}")
    print(
        "Endpoints: /health, /sessions, /sessions/{id}, /sessions/{id}/transcript, "
        "/sessions/{id}/emotion, /sessions/{id}/notes, /sessions/{id}/reactions, /sessions/{id}/smart-summary"
    )
    server.serve_forever()


if __name__ == "__main__":
    run_server()
