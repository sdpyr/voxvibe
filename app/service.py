from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Dict, List

from .schemas import BranchNote, EmotionPoint, Session, TranscriptChunk


class ValidationError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


class SentioTraceService:
    def __init__(self) -> None:
        self.sessions: Dict[str, Session] = {}
        self.transcripts: Dict[str, List[TranscriptChunk]] = defaultdict(list)
        self.emotion_points: Dict[str, List[EmotionPoint]] = defaultdict(list)
        self.branch_notes: Dict[str, List[BranchNote]] = defaultdict(list)

    def create_session(self, therapist_id: str, patient_id: str, consent_captured: bool) -> Session:
        if not therapist_id.strip() or not patient_id.strip():
            raise ValidationError("therapist_id and patient_id are required")
        if not consent_captured:
            raise ValidationError("recording consent must be captured")

        session = Session(
            therapist_id=therapist_id,
            patient_id=patient_id,
            consent_captured=consent_captured,
        )
        self.sessions[session.id] = session
        return session

    def _get_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if session is None:
            raise NotFoundError("session not found")
        return session

    def add_transcript_chunk(self, session_id: str, chunk: TranscriptChunk) -> TranscriptChunk:
        self._get_session(session_id)
        if chunk.end_sec < chunk.start_sec:
            raise ValidationError("end_sec must be >= start_sec")
        if not chunk.text.strip():
            raise ValidationError("text is required")

        self.transcripts[session_id].append(chunk)
        self.transcripts[session_id].sort(key=lambda c: c.start_sec)
        return chunk

    def add_emotion_point(self, session_id: str, point: EmotionPoint) -> EmotionPoint:
        self._get_session(session_id)
        for value in (point.anxiety, point.sadness, point.anger, point.neutral):
            if value < 0 or value > 1:
                raise ValidationError("emotion scores must be between 0 and 1")

        self.emotion_points[session_id].append(point)
        self.emotion_points[session_id].sort(key=lambda p: p.timestamp_sec)
        return point

    def add_branch_note(self, session_id: str, note: BranchNote) -> BranchNote:
        self._get_session(session_id)
        if not note.text.strip():
            raise ValidationError("note text is required")

        self.branch_notes[session_id].append(note)
        self.branch_notes[session_id].sort(key=lambda n: n.timestamp_sec)
        return note

    def get_session_detail(self, session_id: str) -> dict:
        session = self._get_session(session_id)
        return {
            "session": asdict(session),
            "transcript": [asdict(item) for item in self.transcripts[session_id]],
            "emotion_timeline": [asdict(item) for item in self.emotion_points[session_id]],
            "branch_notes": [asdict(item) for item in self.branch_notes[session_id]],
        }
