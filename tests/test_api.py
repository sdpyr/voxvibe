import json
import threading
import time
import unittest
from urllib import error, request

from app.api import run_server


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = 8020
        cls.thread = threading.Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": cls.port}, daemon=True)
        cls.thread.start()
        time.sleep(0.2)
        cls.base = f"http://127.0.0.1:{cls.port}"

    def _call(self, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(f"{self.base}{path}", method=method, data=data, headers=headers)
        try:
            with request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8"))
            return exc.code, body

    def test_health(self) -> None:
        status, payload = self._call("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")

    def test_end_to_end_workflow(self) -> None:
        status, created = self._call(
            "POST",
            "/sessions",
            {"therapist_id": "t-1", "patient_id": "p-1", "consent_captured": True},
        )
        self.assertEqual(status, 201)
        session_id = created["session"]["id"]

        status, _ = self._call(
            "POST",
            f"/sessions/{session_id}/transcript",
            {"speaker": "Patient", "start_sec": 1, "end_sec": 3, "text": "Kaygılıyım."},
        )
        self.assertEqual(status, 201)

        status, _ = self._call(
            "POST",
            f"/sessions/{session_id}/emotion",
            {"timestamp_sec": 2, "anxiety": 0.9, "sadness": 0.2, "anger": 0.1, "neutral": 0.3},
        )
        self.assertEqual(status, 201)

        status, _ = self._call(
            "POST",
            f"/sessions/{session_id}/notes",
            {"timestamp_sec": 2, "note_type": "risk", "text": "Panik atağı tetikleyicileri takip."},
        )
        self.assertEqual(status, 201)

        status, detail = self._call("GET", f"/sessions/{session_id}")
        self.assertEqual(status, 200)
        self.assertEqual(detail["session"]["id"], session_id)
        self.assertEqual(len(detail["transcript"]), 1)
        self.assertEqual(len(detail["emotion_timeline"]), 1)
        self.assertEqual(len(detail["branch_notes"]), 1)

    def test_consent_required(self) -> None:
        status, payload = self._call(
            "POST",
            "/sessions",
            {"therapist_id": "t-1", "patient_id": "p-1", "consent_captured": False},
        )
        self.assertEqual(status, 400)
        self.assertIn("consent", payload["error"])


if __name__ == "__main__":
    unittest.main()
