import {
  applySuggestion,
  cameraPresetPatch,
  createEditorHistory,
  createSaveSequencer,
  gamingQuickActionPatch,
  inferCameraPreset,
  normalizeEditorState,
  previewSuggestion,
  projectGestureViewport,
} from "./editor_state.mjs";
import { installOverlay } from "./overlay_v414.mjs";

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
const enterEditorButton = $("#enterEditorButton");
const closeToolSheetButton = $("#closeToolSheetButton");
const toolDock = $("#toolDock");

// Keys stay stable for the shell API (selectTool); labels follow V414 categories.
const toolTitles = {
  clip: "Frame",
  frame: "Camera",
  look: "Look",
  hud: "HUD",
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
  focus_map: [],
};
let activeTool = "clip";
let mediaUrl = "";
let history = createEditorHistory(normalizeEditorState({}, 15), 50);
let previewState = null;
let isMediaReady = false;
let fullscreenFallback = false;
let activeSuggestionId = "";
const activePointers = new Map();
let gestureStart = null;
let gestureFrame = 0;
let overlay = null;

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
  return {
    duration,
    inPoint: Number(state.inPoint) || 0,
    outPoint: Number(state.outPoint) || duration,
  };
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
  $$('[data-look]').forEach((button) => button.classList.toggle("is-selected", button.dataset.look === state.look));
  $$('[data-hud-mode]').forEach((button) => button.classList.toggle("is-selected", button.dataset.hudMode === state.hudMode));
  const camera = inferCameraPreset(state);
  $$('[data-camera-mode]').forEach((button) => button.classList.toggle("is-selected", button.dataset.cameraMode === camera));
}

function renderState(state = stateValue()) {
  const normalized = normalizeEditorState(state, state.sourceDuration);
  video.style.transform = `translate(${normalized.panX}%, ${normalized.panY}%) scale(${normalized.zoom})`;
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
  $("#coverModeSelect").value = normalized.coverMode;
  $("#speedSelect").value = String(normalized.speed);
  $("#qualityModeSelect").value = normalized.qualityMode;
  renderChoiceButtons(normalized);
  syncTrimControls(normalized);
  renderTransport(normalized);
  updateHistoryButtons();
  overlay?.ensureFocus();
}

function previewPatch(patch) {
  previewState = normalizeEditorState({ ...history.value, ...patch }, history.value.sourceDuration);
  renderState(previewState);
}

function commitPatch(patch, { autosave = true, status = "Modifiche da salvare" } = {}) {
  overlay?.cancelAiPreview({ render: false });
  previewState = null;
  const current = history.value;
  const next = normalizeEditorState({ ...current, ...patch }, current.sourceDuration);
  history.commit(next);
  renderState(next);
  if (autosave) {
    saveSequencer.schedule(next);
    setStatus(status, "dirty");
  }
  return next;
}

function commitState(nextState, status = "Modifiche da salvare") {
  overlay?.cancelAiPreview({ render: false });
  previewState = null;
  const next = normalizeEditorState(nextState, history.value.sourceDuration);
  history.commit(next);
  renderState(next);
  saveSequencer.schedule(next);
  setStatus(status, "dirty");
  return next;
}

function requestEditorAction(action) {
  saveSequencer.flush(history.value, action);
}

function closeToolSheet() {
  app.classList.remove("is-tool-open");
  toolDock.setAttribute("aria-hidden", "true");
  $$('[data-tool]').forEach((button) => {
    button.classList.remove("is-active");
    button.setAttribute("aria-pressed", "false");
  });
  $("#moreButton").setAttribute("aria-expanded", "false");
}

function selectTool(tool, { toggle = false } = {}) {
  if (!(tool in toolTitles)) return;
  if (toggle && activeTool === tool && app.classList.contains("is-tool-open")) {
    closeToolSheet();
    return;
  }
  activeTool = tool;
  app.classList.add("is-tool-open");
  toolDock.setAttribute("aria-hidden", "false");
  $$('[data-tool]').forEach((button) => {
    const selected = button.dataset.tool === tool;
    button.classList.toggle("is-active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  $$('[data-panel]').forEach((panel) => { panel.hidden = panel.dataset.panel !== tool; });
  $("#activeToolTitle").textContent = toolTitles[tool];
  $("#moreButton").setAttribute("aria-expanded", String(tool === "more"));
}

function notifyFullscreen(active) {
  const expanded = Boolean(active);
  fullscreenButton.setAttribute("aria-pressed", String(expanded));
  fullscreenButton.setAttribute("aria-label", expanded ? "Esci da schermo intero" : "Schermo intero");
  app.classList.toggle("is-fullscreen", expanded);
  app.classList.toggle("is-expanded", expanded);
  app.classList.toggle("is-mini", !expanded);
  if (!expanded) {
    closeToolSheet();
    overlay?.cancelAiPreview();
  }
  overlay?.wake();
  postToShell({ type: "GSF_GAME_EDITOR_UI", action: "fullscreen_changed", active: expanded });
}

async function toggleFullscreen() {
  const nativeActive = document.fullscreenElement === app;
  if (nativeActive) {
    await document.exitFullscreen();
    return;
  }
  if (fullscreenFallback) {
    fullscreenFallback = false;
    notifyFullscreen(false);
    fullscreenButton.focus();
    return;
  }
  try {
    if (typeof app.requestFullscreen !== "function") throw new Error("Fullscreen API unavailable");
    await app.requestFullscreen({ navigationUI: "hide" });
    notifyFullscreen(true);
  } catch (_error) {
    fullscreenFallback = true;
    notifyFullscreen(true);
  }
}

async function exitFullscreenForShellClose() {
  fullscreenFallback = false;
  if (document.fullscreenElement === app && typeof document.exitFullscreen === "function") {
    try { await document.exitFullscreen(); } catch (_error) { /* shell close still restores chrome */ }
  }
  notifyFullscreen(false);
}

function pointerCenter(points) {
  const [first, second = first] = points;
  return { x: (first.x + second.x) / 2, y: (first.y + second.y) / 2 };
}

function pointerDistance(points) {
  if (points.length < 2) return 1;
  return Math.max(1, Math.hypot(points[1].x - points[0].x, points[1].y - points[0].y));
}

function beginGesture() {
  overlay.cancelAiPreview();
  const points = [...activePointers.values()].slice(0, 2);
  const center = pointerCenter(points);
  gestureStart = {
    viewport: { zoom: history.value.zoom, panX: history.value.panX, panY: history.value.panY },
    center,
    distance: pointerDistance(points),
  };
  previewStage.classList.add("is-gesturing");
}

function updateGesturePreview() {
  gestureFrame = 0;
  if (!gestureStart || !activePointers.size) return;
  const points = [...activePointers.values()].slice(0, 2);
  const center = pointerCenter(points);
  const rect = previewStage.getBoundingClientRect();
  const viewport = projectGestureViewport(gestureStart.viewport, {
    startDistance: gestureStart.distance,
    currentDistance: pointerDistance(points),
    deltaX: center.x - gestureStart.center.x,
    deltaY: center.y - gestureStart.center.y,
    width: rect.width,
    height: rect.height,
  });
  previewState = normalizeEditorState({ ...history.value, ...viewport }, history.value.sourceDuration);
  renderState(previewState);
}

function scheduleGesturePreview() {
  if (!gestureFrame) gestureFrame = requestAnimationFrame(updateGesturePreview);
}

function releaseCapturedPointers() {
  for (const pointerId of activePointers.keys()) {
    try {
      if (previewStage.hasPointerCapture(pointerId)) previewStage.releasePointerCapture(pointerId);
    } catch (_error) { /* pointer ownership already ended */ }
  }
  activePointers.clear();
}

function finishGesture({ cancelled = false } = {}) {
  if (gestureFrame) cancelAnimationFrame(gestureFrame);
  gestureFrame = 0;
  const next = previewState;
  releaseCapturedPointers();
  gestureStart = null;
  previewStage.classList.remove("is-gesturing");
  if (cancelled || !next) {
    previewState = null;
    renderState(history.value);
    return;
  }
  commitState(next, "Inquadratura aggiornata");
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
    if (!suggestion.patch || typeof suggestion.patch !== "object") return;
    const suggestionId = String(suggestion.id || `suggestion-${index + 1}`);
    const card = document.createElement("article");
    card.className = "ai-suggestion-card";
    card.dataset.suggestionId = suggestionId;

    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const reason = document.createElement("p");
    const impact = document.createElement("p");
    const actions = document.createElement("div");
    const preview = document.createElement("button");
    const apply = document.createElement("button");
    const revert = document.createElement("button");

    title.textContent = String(suggestion.label || suggestion.title || `Suggerimento ${index + 1}`);
    reason.textContent = String(suggestion.reason || "Migliora questo momento senza cambiare il contenuto.");
    impact.textContent = String(suggestion.impact || "Mostra l’anteprima prima di applicare.");
    preview.type = "button";
    preview.textContent = "Anteprima";
    preview.setAttribute("data-ai-action", "preview");
    apply.type = "button";
    apply.textContent = "Applica";
    apply.setAttribute("data-ai-action", "apply");
    apply.disabled = true;
    revert.type = "button";
    revert.textContent = "Annulla anteprima";
    revert.setAttribute("data-ai-action", "revert");
    revert.disabled = true;

    preview.addEventListener("click", () => {
      overlay.cancelAiPreview({ render: false });
      activeSuggestionId = suggestionId;
      previewState = previewSuggestion(history.value, suggestion);
      renderState(previewState);
      $$('.ai-suggestion-card').forEach((item) => item.classList.toggle("is-previewing", item === card));
      $$('.ai-suggestion-card [data-ai-action="apply"], .ai-suggestion-card [data-ai-action="revert"]').forEach((button) => {
        button.disabled = !button.closest(".ai-suggestion-card").classList.contains("is-previewing");
      });
      setStatus("Anteprima AI · nessuna modifica applicata");
    });
    apply.addEventListener("click", () => {
      if (activeSuggestionId !== suggestionId || !previewState) return;
      commitState(applySuggestion(history.value, suggestion), "Suggerimento applicato");
      activeSuggestionId = "";
      renderAiContext();
    });
    revert.addEventListener("click", () => {
      if (activeSuggestionId !== suggestionId) return;
      activeSuggestionId = "";
      previewState = null;
      renderState(history.value);
      renderAiContext();
      setStatus("Anteprima annullata", "saved");
    });

    copy.append(title, reason, impact);
    actions.className = "ai-suggestion-actions";
    actions.append(preview, apply, revert);
    card.append(copy, actions);
    list.append(card);
  });
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
    focus_map: Array.isArray(message.focus_map) ? message.focus_map : [],
  };
  const proposedDuration = Number(message.initial_state?.sourceDuration || context.media.duration || 15);
  const initial = normalizeEditorState(message.initial_state || {}, proposedDuration);
  history.reset(initial);
  previewState = null;
  projectTitle.textContent = String(context.project.title || context.project.name || "Nuovo gameplay").slice(0, 80);
  renderMarkers();
  renderAiContext();
  overlay.setFocusMap(context.focus_map, initial.sourceDuration);
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
  if (event.data.type === "GSF_GAME_EDITOR_SHELL_CLOSE") exitFullscreenForShellClose();
});

video.addEventListener("loadedmetadata", () => {
  isMediaReady = true;
  mediaEmptyState.hidden = true;
  playButton.disabled = false;
  const duration = Number.isFinite(video.duration) && video.duration > 0 ? video.duration : history.value.sourceDuration;
  const normalized = normalizeEditorState({ ...history.value, sourceDuration: duration }, duration);
  history.reset(normalized);
  renderMarkers();
  overlay.setFocusMap(context.focus_map, duration);
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
video.addEventListener("play", () => {
  playButton.textContent = "Ⅱ";
  playButton.setAttribute("aria-label", "Pausa");
  app.classList.add("is-playing");
});
video.addEventListener("pause", () => {
  playButton.textContent = "▶";
  playButton.setAttribute("aria-label", "Riproduci");
  app.classList.remove("is-playing");
});

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
$$('[data-camera-mode]').forEach((button) => button.addEventListener("click", () => {
  const mode = button.dataset.cameraMode;
  commitPatch(cameraPresetPatch(mode, history.value), { status: `Camera · ${button.textContent.trim()}` });
}));
$$('[data-look]').forEach((button) => button.addEventListener("click", () => commitPatch({ look: button.dataset.look }, { status: `Look · ${button.dataset.look}` })));
$$('[data-hud-mode]').forEach((button) => button.addEventListener("click", () => commitPatch({ hudMode: button.dataset.hudMode }, { status: button.dataset.hudMode === "Off" ? "HUD libero" : "HUD protetto" })));
// Quick actions are two-phase: preview first, the overlay bar applies them.
$$('[data-ai-quick]').forEach((button) => button.addEventListener("click", () => {
  if (!Object.keys(gamingQuickActionPatch(button.dataset.aiQuick, history.value)).length) return;
  overlay.previewQuickActions([button.dataset.aiQuick]);
}));

for (const [selector, field, transform] of [
  ["#coverModeSelect", "coverMode", String],
  ["#speedSelect", "speed", Number],
  ["#qualityModeSelect", "qualityMode", String],
]) {
  $(selector).addEventListener("change", (event) => commitPatch({ [field]: transform(event.target.value) }));
}

$("#muteButton").addEventListener("click", () => commitPatch({ muted: !history.value.muted }));
$("#resetTrimButton").addEventListener("click", () => commitPatch({ inPoint: 0, outPoint: history.value.sourceDuration }));
$("#resetFrameButton").addEventListener("click", () => {
  const presets = {
    center: { zoom: 1, panX: 0, panY: 0 },
    gameplay: { zoom: 1.15, panX: 0, panY: -3 },
    face: { zoom: 1.35, panX: 12, panY: -8 },
    free: { zoom: 1, panX: 0, panY: 0 },
  };
  commitPatch(presets[history.value.framePreset] || presets.free);
});

$$('[data-tool]').forEach((button) => button.addEventListener("click", () => selectTool(button.dataset.tool, { toggle: true })));
$("#moreButton").addEventListener("click", () => selectTool(activeTool === "more" ? "clip" : "more"));
closeToolSheetButton.addEventListener("click", closeToolSheet);
$("#retryMediaButton").addEventListener("click", () => loadMedia());

undoButton.addEventListener("click", () => {
  overlay.cancelAiPreview({ render: false });
  const next = history.undo();
  previewState = null;
  renderState(next);
  saveSequencer.schedule(next);
  setStatus("Modifica annullata", "dirty");
});
redoButton.addEventListener("click", () => {
  overlay.cancelAiPreview({ render: false });
  const next = history.redo();
  previewState = null;
  renderState(next);
  saveSequencer.schedule(next);
  setStatus("Modifica ripristinata", "dirty");
});

$("#backButton").addEventListener("click", () => requestEditorAction("close"));
$("#saveDraftButton").addEventListener("click", () => requestEditorAction("save_draft"));
$("#continueButton").addEventListener("click", () => requestEditorAction("continue_to_short"));

fullscreenButton.addEventListener("click", toggleFullscreen);
enterEditorButton.addEventListener("click", toggleFullscreen);
document.addEventListener("fullscreenchange", () => {
  const active = document.fullscreenElement === app;
  if (active) fullscreenFallback = false;
  if (!active) finishGesture({ cancelled: true });
  notifyFullscreen(active || fullscreenFallback);
  if (!active && !fullscreenFallback) fullscreenButton.focus();
});

previewStage.addEventListener("pointerdown", (event) => {
  if (!app.classList.contains("is-expanded")) return;
  if (event.target.closest("button,input,select,.tool-dock,.timeline-card,.transport")) return;
  if (event.pointerType === "mouse" && event.button !== 0) return;
  activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  try { previewStage.setPointerCapture(event.pointerId); } catch (_error) { /* WebKit can reject capture during rotation */ }
  beginGesture();
});
previewStage.addEventListener("pointermove", (event) => {
  if (!activePointers.has(event.pointerId)) return;
  activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  event.preventDefault();
  scheduleGesturePreview();
});
previewStage.addEventListener("pointerup", (event) => {
  if (!activePointers.has(event.pointerId)) return;
  if (gestureFrame) {
    cancelAnimationFrame(gestureFrame);
    gestureFrame = 0;
    updateGesturePreview();
  }
  activePointers.delete(event.pointerId);
  try { previewStage.releasePointerCapture(event.pointerId); } catch (_error) { /* already released */ }
  finishGesture();
});
previewStage.addEventListener("pointercancel", () => finishGesture({ cancelled: true }));
previewStage.addEventListener("lostpointercapture", (event) => {
  if (activePointers.has(event.pointerId)) finishGesture({ cancelled: true });
});
window.addEventListener("orientationchange", () => finishGesture({ cancelled: true }));

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

overlay = installOverlay({
  app,
  video,
  getState: () => history.value,
  getVisibleState: () => stateValue(),
  previewPatch: (patch) => {
    if (activeSuggestionId) {
      activeSuggestionId = "";
      renderAiContext();
    }
    previewPatch(patch);
  },
  clearPreview: () => {
    previewState = null;
    renderState(history.value);
  },
  commitPatch: (patch, status) => commitPatch(patch, { status }),
  renderBase: () => renderState(),
  selectTool,
  setStatus,
});

window.GSFGameEditor2026 = {
  getState: () => history.value,
  commitEditorState: (patch) => commitPatch(patch),
  requestEditorAction,
  selectTool,
  previewAiCommand: (text) => overlay.previewCommand(text),
};

renderState(history.value);
showMediaUnavailable("Gameplay in preparazione");
postToShell({ type: "GSF_GAME_EDITOR_READY" });
