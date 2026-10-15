const FRAME_PRESETS = new Set(["center", "gameplay", "face", "free"]);
const LOOKS = new Set(["Clean", "Competitive", "Boss Cinematic"]);
const HUD_MODES = new Set(["Off", "Smart Safe"]);
const CAPTION_MODES = new Set(["Auto", "Fixed", "Off"]);
const AUDIO_MODES = new Set(["Originale", "Game Boost"]);
const AI_MODES = new Set(["Auto Gaming", "Manuale"]);
const QUALITY_MODES = new Set(["Fast HQ", "Max Quality", "Adaptive AI"]);
const COVER_MODES = new Set(["Auto", "AI", "Current", "Manual"]);
const HEX_COLOR = /^#[0-9a-f]{6}$/i;

const clone = (value) => JSON.parse(JSON.stringify(value));
const number = (value, fallback) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};
const clamp = (value, low, high, fallback = low) => Math.max(low, Math.min(high, number(value, fallback)));
const rounded = (value, digits = 3) => Number(Number(value).toFixed(digits));
const choice = (value, allowed, fallback) => allowed.has(String(value)) ? String(value) : fallback;
const color = (value, fallback) => HEX_COLOR.test(String(value || "")) ? String(value).toLowerCase() : fallback;

export function clampViewport(viewport = {}, bounds = {}) {
  const zoom = rounded(clamp(viewport.zoom, bounds.minZoom ?? 0.8, bounds.maxZoom ?? 2, 1));
  const naturalLimit = Math.max(0, (1 - (1 / Math.max(1, zoom))) * 50);
  const maxPanX = Math.max(0, Math.min(number(bounds.maxPanX, naturalLimit), naturalLimit));
  const maxPanY = Math.max(0, Math.min(number(bounds.maxPanY, naturalLimit), naturalLimit));
  return {
    zoom,
    panX: rounded(clamp(viewport.panX, -maxPanX, maxPanX, 0)),
    panY: rounded(clamp(viewport.panY, -maxPanY, maxPanY, 0)),
  };
}

export function projectGestureViewport(startViewport = {}, gesture = {}) {
  const startDistance = Math.max(1, number(gesture.startDistance, 1));
  const currentDistance = Math.max(1, number(gesture.currentDistance, startDistance));
  const width = Math.max(1, number(gesture.width, 1));
  const height = Math.max(1, number(gesture.height, 1));
  return clampViewport({
    zoom: number(startViewport.zoom, 1) * (currentDistance / startDistance),
    panX: number(startViewport.panX, 0) + ((number(gesture.deltaX, 0) / width) * 100),
    panY: number(startViewport.panY, 0) + ((number(gesture.deltaY, 0) / height) * 100),
  });
}

export function normalizeEditorState(raw = {}, durationValue = 15) {
  const source = raw && typeof raw === "object" ? raw : {};
  const sourceDuration = rounded(clamp(source.sourceDuration ?? durationValue, 0.5, 21600, 15));
  let inPoint = rounded(clamp(source.inPoint, 0, Math.max(0, sourceDuration - 0.5), 0));
  let outPoint = rounded(clamp(source.outPoint, 0.5, sourceDuration, Math.min(15, sourceDuration)));
  if (outPoint - inPoint < 0.5) {
    if (inPoint + 0.5 <= sourceDuration) outPoint = rounded(inPoint + 0.5);
    else {
      outPoint = sourceDuration;
      inPoint = rounded(Math.max(0, sourceDuration - 0.5));
    }
  }
  const viewport = clampViewport(source);
  const captionMode = choice(source.captionMode, CAPTION_MODES, source.captionOn === false ? "Off" : "Auto");
  return {
    zoom: viewport.zoom,
    panX: viewport.panX,
    panY: viewport.panY,
    framePreset: choice(source.framePreset, FRAME_PRESETS, "free"),
    coverMode: choice(source.coverMode, COVER_MODES, "Auto"),
    coverTime: rounded(clamp(source.coverTime, 0, sourceDuration, 0)),
    coverLocked: source.coverLocked === true,
    look: choice(source.look, LOOKS, "Clean"),
    intensity: Math.round(clamp(source.intensity, 0, 100, 64)),
    brightness: Math.round(clamp(source.brightness, 70, 130, 100)),
    contrast: Math.round(clamp(source.contrast, 70, 150, 100)),
    hudMode: choice(source.hudMode, HUD_MODES, "Off"),
    captionOn: captionMode !== "Off",
    captionMode,
    captionText: String(source.captionText || "").slice(0, 240),
    captionSize: Math.round(clamp(source.captionSize, 18, 72, 36)),
    captionY: Math.round(clamp(source.captionY, 5, 95, 76)),
    textColor: color(source.textColor, "#ffffff"),
    activeColor: color(source.activeColor, "#ffd400"),
    outlineColor: color(source.outlineColor, "#000000"),
    muted: source.muted === true,
    volume: Math.round(clamp(source.volume, 0, 100, 100)),
    speed: rounded(clamp(source.speed, 0.5, 2, 1), 2),
    audioMode: choice(source.audioMode, AUDIO_MODES, "Originale"),
    inPoint,
    outPoint,
    aiMode: choice(source.aiMode, AI_MODES, "Auto Gaming"),
    visionEnabled: source.visionEnabled === true,
    qualityMode: choice(source.qualityMode, QUALITY_MODES, "Adaptive AI"),
    editorVersion: "2026.1",
    sourceDuration,
  };
}

export function createEditorHistory(initialState, limitValue = 50) {
  const limit = Math.max(1, Math.floor(number(limitValue, 50)));
  let current = clone(initialState);
  let past = [];
  let future = [];
  const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);
  return {
    get value() { return clone(current); },
    get canUndo() { return past.length > 0; },
    get canRedo() { return future.length > 0; },
    commit(nextState) {
      const next = clone(nextState);
      if (same(next, current)) return this.value;
      past.push(clone(current));
      if (past.length > limit) past = past.slice(-limit);
      current = next;
      future = [];
      return this.value;
    },
    undo() {
      if (!past.length) return this.value;
      future.push(clone(current));
      current = past.pop();
      return this.value;
    },
    redo() {
      if (!future.length) return this.value;
      past.push(clone(current));
      if (past.length > limit) past = past.slice(-limit);
      current = future.pop();
      return this.value;
    },
    reset(nextState) {
      current = clone(nextState);
      past = [];
      future = [];
      return this.value;
    },
    snapshot() {
      return { value: this.value, pastLength: past.length, futureLength: future.length };
    },
  };
}

export function applySuggestion(state, suggestion, duration = state?.sourceDuration ?? 15) {
  const patch = suggestion && typeof suggestion.patch === "object" ? suggestion.patch : {};
  return normalizeEditorState({ ...(state || {}), ...clone(patch) }, duration);
}

export function previewSuggestion(state, suggestion) {
  return applySuggestion(state, suggestion, state?.sourceDuration ?? 15);
}

export function createSaveSequencer(send, delayMs = 650) {
  if (typeof send !== "function") throw new TypeError("send must be a function");
  const wait = Math.max(0, Math.floor(number(delayMs, 650)));
  let timer = null;
  let pendingState = null;
  let sequence = 0;
  let latestDispatched = 0;
  let acknowledged = 0;
  let status = "idle";
  let error = "";

  const clear = () => {
    if (timer !== null) clearTimeout(timer);
    timer = null;
  };
  const dispatch = (action = "autosave") => {
    clear();
    if (!pendingState) return null;
    sequence += 1;
    latestDispatched = sequence;
    status = "saving";
    error = "";
    const message = { action, sequence, state: clone(pendingState) };
    pendingState = null;
    send(clone(message));
    return message;
  };
  return {
    schedule(state) {
      pendingState = clone(state);
      status = "dirty";
      error = "";
      clear();
      timer = setTimeout(() => dispatch("autosave"), wait);
      return this.snapshot();
    },
    flush(state, action = "autosave") {
      if (state !== undefined) pendingState = clone(state);
      return dispatch(action);
    },
    acknowledge(receivedSequence, ok, message = "") {
      const received = Number(receivedSequence);
      if (!Number.isFinite(received) || received !== latestDispatched) return false;
      acknowledged = received;
      status = ok ? "saved" : "error";
      error = ok ? "" : String(message || "Salvataggio non riuscito");
      return true;
    },
    snapshot() {
      return { sequence, latestDispatched, acknowledged, status, error, pending: Boolean(pendingState) };
    },
    dispose() {
      clear();
      pendingState = null;
    },
  };
}
