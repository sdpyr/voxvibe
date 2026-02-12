import unittest

from app.schemas import BranchNote, EmotionPoint, TranscriptChunk
from app.service import NotFoundError, SentioTraceService, ValidationError


class SentioTraceServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SentioTraceService()

    def test_create_session_requires_consent(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create_session("t1", "p1", consent_captured=False)

    def test_happy_path_session_detail(self) -> None:
        session = self.service.create_session("t1", "p1", consent_captured=True)

        self.service.add_transcript_chunk(
            session.id,
            TranscriptChunk(
                speaker="Patient",
                start_sec=1,
                end_sec=4,
                text="Gece uykuya dalmakta zorlandım.",
            ),
        )
        self.service.add_emotion_point(
            session.id,
            EmotionPoint(timestamp_sec=2, anxiety=0.8, sadness=0.4, anger=0.1, neutral=0.2),
        )
        self.service.add_branch_note(
            session.id,
            BranchNote(timestamp_sec=2, note_type="homework", text="Nefes egzersizi verildi."),
        )

        detail = self.service.get_session_detail(session.id)
        self.assertEqual(detail["session"]["id"], session.id)
        self.assertEqual(len(detail["transcript"]), 1)
        self.assertEqual(len(detail["emotion_timeline"]), 1)
        self.assertEqual(len(detail["branch_notes"]), 1)

    def test_unknown_session_raises_not_found(self) -> None:
        with self.assertRaises(NotFoundError):
            self.service.get_session_detail("missing")


if __name__ == "__main__":
    unittest.main()
