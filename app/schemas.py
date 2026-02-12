from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import uuid4


Speaker = Literal["Therapist", "Patient"]
NoteType = Literal["risk", "homework", "breakthrough", "follow-up"]


@dataclass(slots=True)
class Session:
    therapist_id: str
    patient_id: str
    consent_captured: bool
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class TranscriptChunk:
    speaker: Speaker
    start_sec: float
    end_sec: float
    text: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class EmotionPoint:
    timestamp_sec: float
    anxiety: float
    sadness: float
    anger: float
    neutral: float
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class BranchNote:
    timestamp_sec: float
    note_type: NoteType
    text: str
    voice_note_url: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ReactionMark:
    timestamp_sec: float
    kind: str
    label: str
    emoji: str
    intensity: float = 1.0
    id: str = field(default_factory=lambda: str(uuid4()))
