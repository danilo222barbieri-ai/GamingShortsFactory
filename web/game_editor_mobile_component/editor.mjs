import {
  applySuggestion,
  createEditorHistory,
  createSaveSequencer,
  normalizeEditorState,
} from "./editor_state.mjs";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, Number(value) || 0));
const app = $("#gameEditorApp");
const video = $("#gameplayVideo");
const previewStage = $("#previewStage");
const mediaEmptyState = $("#mediaEmptyState");
const editorStatus = $("#editorStatus");
const projectTitle = $("#projectTitle");
const playButton = $("#playButton");
const scrubRange = $("#scrubRange");
const trimInRange = $("#trimInRange");
const trimOutRange = $("#trimOutRange");
const panelInRange = $("#panelInRange");
const panelOutRange = $("#panelOutRange");
const captionOverlay = $("#captionOverlay");
const hudSafeOverlay = $("#hudSafeOverlay");
const selectedRange = $("#selectedRange");
const playhead = $("#playhead");
const eventMarkers = $("#eventMarkers");
const undoButton = $("#undoButton");
const redoButton = $("#redoButton");
const fullscreenButton = $("#fullscreenButton");

const toolTitles = {
  clip: "Taglio",
  frame: "Inquadratura",
  text: "Testo",
  audio: "Audio",
  ai: "Game AI",
  more: "Altro",
};

let context = {
  session: {},
  project: {},
  media: {},
  event_map: [],
  brain_context: {},
  ai_suggestions: [],
};
let activeTool = "clip";
let mediaUrl = "";
let history = createEditorHistory(normalizeEditorState({}, 15), 50);
let previewState = null;
let isMediaReady = false;

function postToShell(message) {
  parent.postMessage(message, location.origin);
}

const saveSequencer = createSaveSequencer((message) => {
  setStatus("Salvataggio…");
  postToShell({ type: "GSF_GAME_EDITOR_UI", ...message });
});

function formatTime(rawSeconds) {
  const seconds = Math.max(0, Number(rawSeconds) || 0);
  const minutes = Math.floor(seconds / 60);
  const rest = seconds - (minutes * 60);
  return `${minutes}:${rest.toFixed(1).padStart(4, "0")}`;
}

function setStatus(label, state = "") {
  editorStatus.textContent = label;
  editorStatus.dataset.state = state;
}

function stateValue() {
  return previewState || history.value;
}

function boundsFor(state) {
  const duration = Math.max(0.5, Number(state.sourceDuration) || 15);
  return { duration, inPoint: Number(state.inPoint) || 0, outPoint: Number(state.outPoint) || duration };
}

function updateHistoryButtons() {
  undoButton.disabled = !history.canUndo;
  redoButton.disabled = !history.canRedo;
}

function renderTransport(state) {
  const { duration, inPoint, outPoint } = boundsFor(state);
  const current = clamp(video.currentTime || inPoint, inPoint, outPoint);
  scrubRange.min = String(inPoint);
  scrubRange.max = String(outPoint);
  scrubRange.value = String(current);
  $("#currentTime").textContent = formatTime(current);
  $("#durationTime").textContent = formatTime(duration);
  playhead.style.left = `${clamp((current / duration) * 100, 0, 100)}%`;
}

function syncTrimControls(state) {
  const { duration, inPoint, outPoint } = boundsFor(state);
  const inMaximum = Math.max(0, duration - 0.5);
  const outMinimum = Math.min(duration, 0.5);
  for (const control of [trimInRange, panelInRange]) {
    control.min = "0";
    control.max = String(inMaximum);
    control.value = String(inPoint);
  }
  for (const control of [trimOutRange, panelOutRange]) {
    control.min = String(outMinimum);
    control.max = String(duration);
    control.value = String(outPoint);
  }
  $("#inTime").textContent = `IN ${formatTime(inPoint)}`;
  $("#outTime").textContent = `OUT ${formatTime(outPoint)}`;
  $("#panelInValue").textContent = formatTime(inPoint);
  $("#panelOutValue").textContent = formatTime(outPoint);
  selectedRange.style.left = `${(inPoint / duration) * 100}%`;
  selectedRange.style.right = `${100 - ((outPoint / duration) * 100)}%`;
}

function renderChoiceButtons(state) {
  $$('[data-frame]').forEach((button) => button.classList.toggle("is-selected", button.dataset.frame === state.framePreset));
  $$('[data-caption-mode]').forEach((button) => button.classList.toggle("is-selected", button.dataset.captionMode === state.captionMode));
  $$('[data-audio-mode]').forEach((button) => button.classList.toggle("is-selected", button.dataset.audioMode === state.audioMode));
  $$('[data-text-color]').forEach((button) => button.classList.toggle("is-selected", button.dataset.textColor.toLowerCase() === state.textColor));
}

function renderState(state = stateValue()) {
  const normalized = normalizeEditorState(state, state.sourceDuration);
  const transform = `translate(${normalized.panX}%, ${normalized.panY}%) scale(${normalized.zoom})`;
  video.style.transform = transform;
  video.playbackRate = normalized.speed;
  video.muted = normalized.muted;
  video.volume = normalized.volume / 100;
  captionOverlay.textContent = normalized.captionMode === "Off" ? "" : normalized.captionText;
  captionOverlay.hidden = normalized.captionMode === "Off" || !normalized.captionText;
  captionOverlay.style.top = `${normalized.captionY}%`;
  captionOverlay.style.fontSize = `${normalized.captionSize}px`;
  captionOverlay.style.color = normalized.textColor;
  hudSafeOverlay.classList.toggle("is-visible", normalized.hudMode === "Smart Safe");

  $("#zoomRange").value = String(normalized.zoom);
  $("#zoomValue").textContent = `${normalized.zoom.toFixed(2)}×`;
  $("#panXRange").value = String(normalized.panX);
  $("#panYRange").value = String(normalized.panY);
  $("#captionTextInput").value = normalized.captionText;
  $("#captionSizeRange").value = String(normalized.captionSize);
  $("#captionYRange").value = String(normalized.captionY);
  $("#volumeRange").value = String(normalized.volume);
  $("#volumeValue").textContent = `${normalized.volume}%`;
  $("#muteButton").textContent = normalized.muted ? "Riattiva audio" : "Disattiva audio";
  $("#muteButton").setAttribute("aria-pressed", String(normalized.muted));
  $("#lookSelect").value = normalized.look;
  $("#coverModeSelect").value = normalized.coverMode;
  $("#hudModeSelect").value = normalized.hudMode;
  $("#speedSelect").value = String(normalized.speed);
  $("#qualityModeSelect").value = normalized.qualityMode;
  renderChoiceButtons(normalized);
  syncTrimControls(normalized);
  renderTransport(normalized);
  updateHistoryButtons();
}

function previewPatch(patch) {
  previewState = normalizeEditorState({ ...history.value, ...patch }, history.value.sourceDuration);
  renderState(previewState);
}

function commitPatch(patch, { autosave = true } = {}) {
  previewState = null;
  const current = history.value;
  const next = normalizeEditorState({ ...current, ...patch }, current.sourceDuration);
  history.commit(next);
  renderState(next);
  if (autosave) {
    saveSequencer.schedule(next);
    setStatus("Modifiche da salvare", "dirty");
  }
  return next;
}

function requestEditorAction(action) {
  saveSequencer.flush(history.value, action);
}

function renderMarkers() {
  eventMarkers.replaceChildren();
  const duration = Math.max(0.5, history.value.sourceDuration);
  context.event_map.slice(0, 18).forEach((event, index) => {
    const time = clamp(event.time ?? event.start_time ?? event.start ?? 0, 0, duration);
    const marker = document.createElement("button");
    marker.type = "button";
    marker.className = "event-marker";
    marker.style.left = `${(time / duration) * 100}%`;
    marker.setAttribute("aria-label", `${String(event.label || event.type || `Evento ${index + 1}`)} a ${formatTime(time)}`);
    marker.title = String(event.label || event.type || "Evento Game AI");
    marker.addEventListener("click", () => {
      video.currentTime = clamp(time, history.value.inPoint, history.value.outPoint);
      renderTransport(history.value);
    });
    eventMarkers.append(marker);
  });
}

function renderAiContext() {
  const list = $("#aiSuggestionList");
  list.replaceChildren();
  if (!context.ai_suggestions.length) {
    const empty = document.createElement("p");
    empty.className = "panel-empty";
    empty.textContent = "Nessun suggerimento disponibile per questo momento.";
    list.append(empty);
    return;
  }
  context.ai_suggestions.slice(0, 6).forEach((suggestion, index) => {
    const card = document.createElement("article");
    card.className = "ai-suggestion-card";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const reason = document.createElement("p");
    const apply = document.createElement("button");
    title.textContent = String(suggestion.label || `Suggerimento ${index + 1}`);
    reason.textContent = String(suggestion.reason || suggestion.impact || "Migliora questo momento senza cambiare il contenuto.");
    apply.type = "button";
    apply.textContent = "Applica";
    apply.addEventListener("click", () => {
      history.commit(applySuggestion(history.value, suggestion));
      renderState(history.value);
      saveSequencer.schedule(history.value);
      setStatus("Suggerimento applicato", "dirty");
    });
    copy.append(title, reason);
    card.append(copy, apply);
    list.append(card);
  });
}

function selectTool(tool) {
  if (!(tool in toolTitles)) return;
  activeTool = tool;
  $$('[data-tool]').forEach((button) => {
    const selected = button.dataset.tool === tool;
    button.classList.toggle("is-active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  $$('[data-panel]').forEach((panel) => { panel.hidden = panel.dataset.panel !== tool; });
  $("#activeToolTitle").textContent = toolTitles[tool];
  const showingMore = tool === "more";
  $("#moreButton").setAttribute("aria-expanded", String(showingMore));
}

function showMediaUnavailable(message = "Gameplay non disponibile") {
  isMediaReady = false;
  mediaEmptyState.hidden = false;
  mediaEmptyState.querySelector("strong").textContent = message;
  playButton.disabled = true;
}

function loadMedia(url = mediaUrl) {
  mediaUrl = String(url || "");
  if (!mediaUrl) {
    showMediaUnavailable("Gameplay non ancora disponibile");
    return;
  }
  isMediaReady = false;
  mediaEmptyState.hidden = false;
  mediaEmptyState.querySelector("strong").textContent = "Caricamento gameplay…";
  playButton.disabled = true;
  if (video.src !== new URL(mediaUrl, location.href).href) video.src = mediaUrl;
  video.load();
}

function receiveInit(message) {
  context = {
    session: message.session && typeof message.session === "object" ? message.session : {},
    project: message.project && typeof message.project === "object" ? message.project : {},
    media: message.media && typeof message.media === "object" ? message.media : {},
    event_map: Array.isArray(message.event_map) ? message.event_map : [],
    brain_context: message.brain_context && typeof message.brain_context === "object" ? message.brain_context : {},
    ai_suggestions: Array.isArray(message.ai_suggestions) ? message.ai_suggestions : [],
  };
  const proposedDuration = Number(message.initial_state?.sourceDuration || context.media.duration || 15);
  const initial = normalizeEditorState(message.initial_state || {}, proposedDuration);
  history.reset(initial);
  previewState = null;
  projectTitle.textContent = String(context.project.title || context.project.name || "Nuovo gameplay").slice(0, 80);
  renderMarkers();
  renderAiContext();
  renderState(initial);
  loadMedia(context.media.url || context.media.video_url || "");
  app.setAttribute("aria-busy", "false");
  setStatus("Pronto", "saved");
}

function receiveSaveStatus(message) {
  if (!saveSequencer.acknowledge(message.sequence, message.ok === true, message.error)) return;
  if (message.ok === true) setStatus(message.draft ? "Bozza salvata" : "Salvato", "saved");
  else setStatus(String(message.error || "Salvataggio non riuscito"), "error");
}

window.addEventListener("message", (event) => {
  if (event.origin !== location.origin || event.source !== parent || !event.data) return;
  if (event.data.type === "GSF_GAME_EDITOR_INIT") receiveInit(event.data);
  if (event.data.type === "GSF_GAME_EDITOR_SAVE_STATUS") receiveSaveStatus(event.data);
});

video.addEventListener("loadedmetadata", () => {
  isMediaReady = true;
  mediaEmptyState.hidden = true;
  playButton.disabled = false;
  const duration = Number.isFinite(video.duration) && video.duration > 0 ? video.duration : history.value.sourceDuration;
  const normalized = normalizeEditorState({ ...history.value, sourceDuration: duration }, duration);
  history.reset(normalized);
  renderMarkers();
  renderState(normalized);
  video.currentTime = normalized.inPoint;
  setStatus("Pronto", "saved");
});

video.addEventListener("error", () => showMediaUnavailable("Impossibile caricare il gameplay"));
video.addEventListener("timeupdate", () => {
  const state = history.value;
  if (video.currentTime >= state.outPoint) {
    video.pause();
    video.currentTime = state.inPoint;
  }
  renderTransport(state);
});
video.addEventListener("play", () => { playButton.textContent = "Ⅱ"; playButton.setAttribute("aria-label", "Pausa"); });
video.addEventListener("pause", () => { playButton.textContent = "▶"; playButton.setAttribute("aria-label", "Riproduci"); });

playButton.addEventListener("click", async () => {
  if (!isMediaReady) return;
  if (!video.paused) {
    video.pause();
    return;
  }
  const state = history.value;
  if (video.currentTime < state.inPoint || video.currentTime >= state.outPoint) video.currentTime = state.inPoint;
  try { await video.play(); } catch (_error) { setStatus("Tocca di nuovo per avviare l’anteprima", "error"); }
});

scrubRange.addEventListener("input", () => {
  video.currentTime = clamp(scrubRange.value, history.value.inPoint, history.value.outPoint);
  renderTransport(history.value);
});

function bindTrimPair(control, field) {
  control.addEventListener("input", () => {
    const raw = Number(control.value);
    const state = history.value;
    const patch = field === "inPoint"
      ? { inPoint: Math.min(raw, state.outPoint - 0.5) }
      : { outPoint: Math.max(raw, state.inPoint + 0.5) };
    previewPatch(patch);
  });
  control.addEventListener("change", () => {
    const raw = Number(control.value);
    const state = history.value;
    const patch = field === "inPoint"
      ? { inPoint: Math.min(raw, state.outPoint - 0.5) }
      : { outPoint: Math.max(raw, state.inPoint + 0.5) };
    const committed = commitPatch(patch);
    video.currentTime = field === "inPoint" ? committed.inPoint : Math.min(video.currentTime, committed.outPoint);
  });
}

bindTrimPair(trimInRange, "inPoint");
bindTrimPair(panelInRange, "inPoint");
bindTrimPair(trimOutRange, "outPoint");
bindTrimPair(panelOutRange, "outPoint");

function bindRange(selector, field, parse = Number) {
  const control = $(selector);
  control.addEventListener("input", () => previewPatch({ [field]: parse(control.value) }));
  control.addEventListener("change", () => commitPatch({ [field]: parse(control.value) }));
}

bindRange("#zoomRange", "zoom");
bindRange("#panXRange", "panX");
bindRange("#panYRange", "panY");
bindRange("#captionSizeRange", "captionSize");
bindRange("#captionYRange", "captionY");
bindRange("#volumeRange", "volume");

$("#captionTextInput").addEventListener("input", (event) => previewPatch({ captionText: event.target.value }));
$("#captionTextInput").addEventListener("change", (event) => commitPatch({ captionText: event.target.value }));

$$('[data-frame]').forEach((button) => button.addEventListener("click", () => commitPatch({ framePreset: button.dataset.frame })));
$$('[data-caption-mode]').forEach((button) => button.addEventListener("click", () => commitPatch({ captionMode: button.dataset.captionMode })));
$$('[data-audio-mode]').forEach((button) => button.addEventListener("click", () => commitPatch({ audioMode: button.dataset.audioMode })));
$$('[data-text-color]').forEach((button) => button.addEventListener("click", () => commitPatch({ textColor: button.dataset.textColor })));

for (const [selector, field, transform] of [
  ["#lookSelect", "look", String],
  ["#coverModeSelect", "coverMode", String],
  ["#hudModeSelect", "hudMode", String],
  ["#speedSelect", "speed", Number],
  ["#qualityModeSelect", "qualityMode", String],
]) {
  $(selector).addEventListener("change", (event) => commitPatch({ [field]: transform(event.target.value) }));
}

$("#muteButton").addEventListener("click", () => commitPatch({ muted: !history.value.muted }));
$("#resetTrimButton").addEventListener("click", () => commitPatch({ inPoint: 0, outPoint: history.value.sourceDuration }));
$$('[data-tool]').forEach((button) => button.addEventListener("click", () => selectTool(button.dataset.tool)));
$("#moreButton").addEventListener("click", () => selectTool(activeTool === "more" ? "clip" : "more"));
$("#retryMediaButton").addEventListener("click", () => loadMedia());

undoButton.addEventListener("click", () => {
  const next = history.undo();
  previewState = null;
  renderState(next);
  saveSequencer.schedule(next);
  setStatus("Modifica annullata", "dirty");
});
redoButton.addEventListener("click", () => {
  const next = history.redo();
  previewState = null;
  renderState(next);
  saveSequencer.schedule(next);
  setStatus("Modifica ripristinata", "dirty");
});

$("#backButton").addEventListener("click", () => requestEditorAction("close"));
$("#saveDraftButton").addEventListener("click", () => requestEditorAction("save_draft"));
$("#continueButton").addEventListener("click", () => requestEditorAction("continue_to_short"));

fullscreenButton.addEventListener("click", () => {
  const active = fullscreenButton.getAttribute("aria-pressed") !== "true";
  fullscreenButton.setAttribute("aria-pressed", String(active));
  app.classList.toggle("is-fullscreen", active);
  postToShell({ type: "GSF_GAME_EDITOR_UI", action: "fullscreen_changed", active });
});

document.addEventListener("keydown", (event) => {
  const editingText = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement?.tagName || "");
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
    event.preventDefault();
    (event.shiftKey ? redoButton : undoButton).click();
    return;
  }
  if (editingText) return;
  if (event.code === "Space") {
    event.preventDefault();
    playButton.click();
  } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
    event.preventDefault();
    const direction = event.key === "ArrowLeft" ? -1 : 1;
    video.currentTime = clamp(video.currentTime + (direction * 0.1), history.value.inPoint, history.value.outPoint);
    renderTransport(history.value);
  }
});

window.addEventListener("pagehide", () => saveSequencer.dispose(), { once: true });

window.GSFGameEditor2026 = {
  getState: () => history.value,
  commitEditorState: (patch) => commitPatch(patch),
  requestEditorAction,
  selectTool,
};

selectTool("clip");
renderState(history.value);
showMediaUnavailable("Gameplay in preparazione");
postToShell({ type: "GSF_GAME_EDITOR_READY" });
