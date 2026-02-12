let activeSessionId = null;

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

async function refreshDetail() {
  requireSessionId();
  const detail = await apiCall(`/sessions/${activeSessionId}`);
  document.getElementById("output").textContent = JSON.stringify(detail, null, 2);
}

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
