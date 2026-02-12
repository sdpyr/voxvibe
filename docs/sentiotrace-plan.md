# SentioTrace — HealthTech SaaS Plan (MVP → Scale)

## 1) Product Positioning

**Product:** SentioTrace  
**Audience:** Clinical psychologists, psychiatrists, licensed therapists, and professional coaches.  
**Core promise:** Reduce post-session note workload from ~60 minutes to ~5 minutes while improving longitudinal emotional insight.

## 2) Problem-Solution Fit

### Key pains
- Session-time note taking breaks rapport and eye contact.
- Post-session transcription and summary work causes burnout.
- Emotion progression/regression across sessions is hard to track manually.
- Existing generic transcription tools miss clinical context and emotional nuance.

### Solution pillars
1. **Secure session capture** (consent-aware audio recording).
2. **Medical-context transcription** (Whisper pipeline + domain prompt tuning).
3. **Emotion timeline** (session-level sentiment/emotion peaks).
4. **Branch notes** (timestamp-linked therapist notes and voice memos).
5. **Cross-session continuity** (topic/branch linking over time).

## 3) MVP Scope (first 8–10 weeks)

### In-scope
1. **Secure recording interface**
   - Start/stop/pause recording.
   - Consent checkbox + legal text per jurisdiction.
   - Encrypted upload after session.

2. **Transcription pipeline**
   - Whisper-based ASR processing.
   - Speaker labels: `Therapist` / `Patient` (simple diarization).
   - Timestamped transcript chunks.

3. **Emotion timeline (v1)**
   - Chunk-level emotion scores (anxiety, sadness, anger, neutral).
   - Timeline markers for peak intensity moments.
   - Click-to-jump playback at marker.

4. **Branch note module**
   - Add note at any timestamp.
   - Attach voice note or text note.
   - Tag note as `risk`, `homework`, `breakthrough`, `follow-up`.

5. **Session summary export**
   - 1-page generated summary.
   - “Top emotional shifts” + “follow-up points”.
   - PDF and EHR-friendly text export.

### Out-of-scope (MVP)
- Fully automated diagnosis recommendations.
- Real-time intervention prompts during live sessions.
- Multi-language clinical coding framework.
- Full EHR bidirectional sync (add after MVP).

## 4) Compliance-by-Design Baseline

> Not legal advice — validate with healthcare counsel before launch.

### Security controls
- Encryption in transit (TLS 1.2+) and at rest (AES-256).
- Per-tenant data isolation.
- RBAC: therapist, supervisor, clinic-admin roles.
- Immutable audit logs for all record access.

### Privacy controls
- Explicit recording consent capture.
- Data retention policy per clinic.
- Configurable auto-delete / archival windows.
- De-identification pipeline for model training datasets.

### Regulatory readiness
- HIPAA-aligned controls for US deployments.
- GDPR/KVKK data rights handling (export/delete requests).
- BAA-ready cloud stack and vendor selection.

## 5) Suggested Technical Architecture

### Frontend
- **Web app:** Next.js + TypeScript.
- **UI:** Accessible component system (e.g., shadcn/ui).
- **Auth:** MFA-ready session management.

### Backend
- **API:** FastAPI or NestJS.
- **Workers:** Queue-based async processing (transcription + emotion inference).
- **Storage:**
  - Relational DB for metadata (PostgreSQL).
  - Object storage for audio/transcripts (S3-compatible, encrypted).
- **Search:** Optional vector/text index for semantic recall.

### AI pipeline
1. Audio normalization.
2. ASR transcription (Whisper).
3. Diarization + timestamp alignment.
4. Emotion scoring model per chunk.
5. Session summary generation.
6. Quality flags (low confidence sections).

## 6) Data Model (MVP Entities)

- `Organization`
- `TherapistUser`
- `PatientProfile` (minimum necessary data)
- `Session`
- `AudioAsset`
- `TranscriptChunk`
- `EmotionPoint`
- `BranchNote`
- `SummaryReport`
- `AuditEvent`

## 7) UX Blueprint

1. **Dashboard:** Upcoming sessions, unresolved follow-ups.
2. **Session page:** Recorder + live waveform + consent state.
3. **Review page:** Transcript + emotion timeline + branch pins.
4. **Summary page:** AI draft + editable final notes + export.

## 8) Validation Plan (first 30 days)

### Customer discovery interviews (10 practitioners)
Ask:
- “How many hours/week do you spend on post-session documentation?”
- “Where do you lose context from prior sessions?”
- “What documentation output must match your clinic/legal process?”

### MVP success metrics
- **Time saved:** ≥50% reduction in documentation time.
- **Activation:** ≥70% of trial users complete 3+ session uploads.
- **Retention signal:** ≥40% week-4 active usage.
- **Quality:** Therapist-rated summary usefulness ≥4/5.

## 9) Go-to-Market (initial)

- 14-day free trial for solo practitioners.
- LinkedIn content funnel: therapist productivity + burnout reduction.
- Conference presence at psychology/mental-health events.
- Founding cohort program with discounted annual plans.

## 10) Pricing Hypothesis

- **Starter:** $49/user/month (single practitioner, limited storage).
- **Pro:** $99/user/month (full timeline + branching + exports).
- **Clinic:** $149/user/month + admin + compliance tooling.
- Add-on: secure storage overage and premium compliance support.

## 11) 90-Day Execution Roadmap

### Phase 1 (Weeks 1–3)
- Discovery interviews.
- Compliance and legal review kickoff.
- Clickable Figma prototype + workflow tests.

### Phase 2 (Weeks 4–7)
- Build recording/upload + session management.
- Integrate Whisper pipeline.
- Implement transcript viewer and timestamp navigation.

### Phase 3 (Weeks 8–10)
- Emotion timeline + branch notes.
- AI summary and export.
- Pilot onboarding (5–10 therapists).

### Phase 4 (Weeks 11–13)
- Iterate from pilot feedback.
- Improve model confidence labels.
- Prepare billing and self-serve onboarding.

## 12) Strategic Expansion (post-PMF)

1. EHR integrations (read/write notes and session metadata).
2. Clinic-level analytics and supervisor dashboards.
3. Vertical expansion:
   - Legal interviews (attorney-client review).
   - HR interviews and coaching workflows.
4. Privacy-safe federated learning options for model improvement.

---

If needed, this plan can be converted next into:
- a technical RFC,
- an investor one-pager,
- or a sprint-by-sprint engineering backlog.
