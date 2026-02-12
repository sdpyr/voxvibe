let activeSessionId = null;
let sessionStartAt = null;
const reactionButtons = [
  { kind: "critical", label: "Kritik", emoji: "🚩", intensity: 1 },
  { kind: "insight", label: "İçgörü", emoji: "🧠", intensity: 0.8 },
  { kind: "inconsistency", label: "Tutarsızlık", emoji: "⚠️", intensity: 0.9 },
  { kind: "emotional", label: "Duygusal", emoji: "❤️", intensity: 0.7 },
];

function setStatus(message, isError = false) {
  const statusEl = document.getElementById("status");
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b91c1c" : "#065f46";
}

async function apiCall(path, method = "GET", payload = null) {
  const options = { method, headers: {} };
  if (payload) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }

  const response = await fetch(path, options);
  const json = await response.json();
  if (!response.ok) {
    throw new Error(json.error || "Beklenmeyen hata");
  }
  return json;
}

function requireSessionId() {
  if (!activeSessionId) {
    throw new Error("Önce seans oluşturun.");
  }
}

function requireSessionStart() {
  if (sessionStartAt === null) {
    throw new Error("Timestamp için önce seans oluşturun.");
  }
}

async function refreshDetail() {
  requireSessionId();
  const detail = await apiCall(`/sessions/${activeSessionId}`);
  document.getElementById("output").textContent = JSON.stringify(detail, null, 2);
  renderBranchingReactionHints(detail.reactions || []);
}

function renderBranchingReactionHints(reactions) {
  const noteForm = document.getElementById("note-form");
  const panel = document.getElementById("reaction-panel");
  panel.querySelectorAll(".branch-hint").forEach((item) => item.remove());

  reactions.slice(-4).forEach((reaction) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "reaction-btn branch-hint";
    button.textContent = `${reaction.emoji} ${reaction.label} @ ${reaction.timestamp_sec.toFixed(1)}s → nota dallan`;
    button.addEventListener("click", () => {
      noteForm.timestamp_sec.value = reaction.timestamp_sec;
      noteForm.text.focus();
      setStatus(`Branch note için ${reaction.timestamp_sec.toFixed(1)}s seçildi.`);
    });
    panel.appendChild(button);
  });
}

async function createReaction(payload) {
  requireSessionId();
  await apiCall(`/sessions/${activeSessionId}/reactions`, "POST", payload);
  setStatus(`${payload.emoji} ${payload.label} işaretlendi.`);
  await refreshDetail();
}

function addReactionButton(reaction) {
  const panel = document.getElementById("reaction-panel");
  const button = document.createElement("button");
  button.type = "button";
  button.className = "reaction-btn";
  button.textContent = `${reaction.emoji} ${reaction.label}`;
  button.addEventListener("click", async () => {
    try {
      requireSessionStart();
      const timestampSec = (Date.now() - sessionStartAt) / 1000;
      await createReaction({ ...reaction, timestamp_sec: Number(timestampSec.toFixed(1)) });
    } catch (error) {
      setStatus(error.message, true);
    }
  });
  panel.appendChild(button);
}

function initializeReactionPanel() {
  reactionButtons.forEach((reaction) => addReactionButton(reaction));
}

document.getElementById("reaction-config-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.target;
  const reaction = {
    emoji: form.emoji.value.trim(),
    label: form.label.value.trim(),
    kind: form.kind.value.trim(),
    intensity: Number(form.intensity.value),
  };

  if (!reaction.emoji || !reaction.label || !reaction.kind) {
    setStatus("Yeni reaction için emoji/etiket/tip zorunlu.", true);
    return;
  }

  reactionButtons.push(reaction);
  addReactionButton(reaction);
  form.reset();
  form.emoji.value = "✨";
  form.label.value = "Yeni İşaret";
  form.kind.value = "custom";
  form.intensity.value = "0.8";
  setStatus(`${reaction.emoji} ${reaction.label} butonu eklendi.`);
});

document.getElementById("session-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const form = event.target;
    const payload = {
      therapist_id: form.therapist_id.value,
      patient_id: form.patient_id.value,
      consent_captured: form.consent_captured.checked,
    };
    const created = await apiCall("/sessions", "POST", payload);
    activeSessionId = created.session.id;
    sessionStartAt = Date.now();
    document.getElementById("session-id").textContent = activeSessionId;
    setStatus("Seans oluşturuldu.");
    await refreshDetail();
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("transcript-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    requireSessionId();
    const form = event.target;
    await apiCall(`/sessions/${activeSessionId}/transcript`, "POST", {
      speaker: form.speaker.value,
      start_sec: Number(form.start_sec.value),
      end_sec: Number(form.end_sec.value),
      text: form.text.value,
    });
    setStatus("Transcript eklendi.");
    await refreshDetail();
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("emotion-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    requireSessionId();
    const form = event.target;
    await apiCall(`/sessions/${activeSessionId}/emotion`, "POST", {
      timestamp_sec: Number(form.timestamp_sec.value),
      anxiety: Number(form.anxiety.value),
      sadness: Number(form.sadness.value),
      anger: Number(form.anger.value),
      neutral: Number(form.neutral.value),
    });
    setStatus("Emotion point eklendi.");
    await refreshDetail();
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("note-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    requireSessionId();
    const form = event.target;
    const payload = {
      timestamp_sec: Number(form.timestamp_sec.value),
      note_type: form.note_type.value,
      text: form.text.value,
    };
    if (form.voice_note_url.value.trim()) {
      payload.voice_note_url = form.voice_note_url.value.trim();
    }
    await apiCall(`/sessions/${activeSessionId}/notes`, "POST", payload);
    setStatus("Branch note eklendi.");
    await refreshDetail();
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("refresh-detail").addEventListener("click", async () => {
  try {
    await refreshDetail();
    setStatus("Session detayı güncellendi.");
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.getElementById("smart-summary").addEventListener("click", async () => {
  try {
    requireSessionId();
    const payload = await apiCall(`/sessions/${activeSessionId}/smart-summary`);
    document.getElementById("summary-output").textContent = JSON.stringify(payload.smart_summary, null, 2);
    setStatus("AI Smart-Summary üretildi.");
  } catch (error) {
    setStatus(error.message, true);
  }
});

initializeReactionPanel();
