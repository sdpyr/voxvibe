"""Small runnable demo for SentioTrace core flow (no external dependencies)."""

from pprint import pprint

from .schemas import BranchNote, EmotionPoint, TranscriptChunk
from .service import SentioTraceService


def run_demo() -> None:
    service = SentioTraceService()

    session = service.create_session(
        therapist_id="therapist-001",
        patient_id="patient-001",
        consent_captured=True,
    )

    service.add_transcript_chunk(
        session.id,
        TranscriptChunk(
            speaker="Patient",
            start_sec=10,
            end_sec=17,
            text="Bu hafta kaygım oldukça yüksekti.",
        ),
    )

    service.add_emotion_point(
        session.id,
        EmotionPoint(timestamp_sec=12, anxiety=0.87, sadness=0.31, anger=0.10, neutral=0.18),
    )

    service.add_branch_note(
        session.id,
        BranchNote(timestamp_sec=12, note_type="follow-up", text="Bir sonraki seansta tetikleyicileri aç."),
    )

    pprint(service.get_session_detail(session.id))


if __name__ == "__main__":
    run_demo()
