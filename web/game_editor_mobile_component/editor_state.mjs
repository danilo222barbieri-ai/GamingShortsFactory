const FRAME_PRESETS = new Set(["center", "gameplay", "face", "free"]);
const LOOKS = new Set(["Clean", "Competitive", "Boss Cinematic"]);
const HUD_MODES = new Set(["Off", "Smart Safe"]);
const CAPTION_MODES = new Set(["Auto", "Fixed", "Off"]);
const AUDIO_MODES = new Set(["Originale", "Game Boost"]);
const AI_MODES = new Set(["Auto Gaming", "Manuale"]);
const QUALITY_MODES = new Set(["Fast HQ", "Max Quality", "Adaptive AI"]);
const COVER_MODES = new Set(["Auto", "AI", "Current", "Manual"]);
const CAMERA_PRESETS = new Set(["static", "follow", "dynamic", "cinematic"]);
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
    editorVersion: "2026.2",
    sourceDuration,
  };
}

/**
 * V414 camera modes deliberately compile to the existing persisted renderer
 * vocabulary. The backend whitelist therefore keeps the choice without a new
 * preview-only cameraMode field.
 */
export function cameraPresetPatch(modeValue, state = {}) {
  const mode = choice(String(modeValue || "").toLowerCase(), CAMERA_PRESETS, "static");
  const current = normalizeEditorState(state, state?.sourceDuration ?? 15);
  if (mode === "follow") {
    return {
      visionEnabled: true,
      aiMode: "Auto Gaming",
      framePreset: "gameplay",
      zoom: 1,
      look: "Clean",
    };
  }
  if (mode === "dynamic") {
    return {
      visionEnabled: true,
      aiMode: "Auto Gaming",
      framePreset: "gameplay",
      zoom: rounded(clamp(Math.max(1.12, current.zoom), 1.12, 2, 1.12)),
      look: "Clean",
    };
  }
  if (mode === "cinematic") {
    return {
      visionEnabled: true,
      aiMode: "Auto Gaming",
      framePreset: "gameplay",
      zoom: rounded(clamp(Math.max(1.18, current.zoom), 1.18, 2, 1.18)),
      look: "Boss Cinematic",
    };
  }
  return {
    visionEnabled: false,
    aiMode: "Manuale",
    framePreset: "free",
    zoom: 1,
    look: "Clean",
  };
}

export function inferCameraPreset(state = {}) {
  const current = normalizeEditorState(state, state?.sourceDuration ?? 15);
  if (!current.visionEnabled) return "static";
  if (current.look === "Boss Cinematic") return "cinematic";
  if (current.zoom >= 1.08) return "dynamic";
  return "follow";
}

export function gamingQuickActionPatch(actionValue, state = {}) {
  const action = String(actionValue || "").toLowerCase();
  const current = normalizeEditorState(state, state?.sourceDuration ?? 15);
  if (action === "follow_action") return cameraPresetPatch("follow", current);
  if (action === "auto_vertical") {
    return {
      framePreset: "gameplay",
      panX: 0,
      panY: 0,
      zoom: Math.max(1, current.zoom),
      qualityMode: "Adaptive AI",
    };
  }
  if (action === "zoom_moments") return cameraPresetPatch("dynamic", current);
  if (action === "protect_hud") return { hudMode: "Smart Safe", visionEnabled: true };
  if (action === "auto_caption") return {
    captionMode: "Auto",
    captionOn: true,
    captionY: Math.min(78, current.captionY),
  };
  if (action === "improve_all") {
    return {
      ...cameraPresetPatch("dynamic", current),
      look: "Competitive",
      hudMode: "Smart Safe",
      captionMode: "Auto",
      captionOn: true,
      captionY: Math.min(78, current.captionY),
      audioMode: "Game Boost",
      qualityMode: "Adaptive AI",
    };
  }
  return {};
}

export const GAMING_QUICK_ACTIONS = Object.freeze({
  follow_action: "Segui l'azione",
  auto_vertical: "Auto 9:16",
  zoom_moments: "Zoom momenti",
  protect_hud: "Proteggi HUD",
  auto_caption: "Auto caption",
  improve_all: "Migliora tutto",
});

/**
 * Two-phase AI: every quick action (or a combination) is compiled into one
 * bounded, persisted-field patch. The editor previews it first and commits it
 * only on Apply, so a single undo reverts the whole AI application.
 */
export function combinedQuickActionPatch(actions = [], state = {}) {
  const duration = state?.sourceDuration ?? 15;
  let working = normalizeEditorState(state, duration);
  const patch = {};
  for (const action of actions) {
    if (!(action in GAMING_QUICK_ACTIONS)) continue;
    const step = gamingQuickActionPatch(action, working);
    Object.assign(patch, step);
    working = normalizeEditorState({ ...working, ...step }, duration);
  }
  return patch;
}

const COMMAND_RULES = [
  ["improve_all", /\b(migliora tutto|migliora|improve( all)?|ottimizza)\b/],
  ["follow_action", /\b(segui|seguire|follow|traccia|giocatore|player|azione|action)\b/],
  ["zoom_moments", /\b(zoom|zooma|kill|uccision\w*|eliminazion\w*|headshot|clutch|moment\w*|highlight\w*)\b/],
  ["protect_hud", /\b(hud|minimappa|minimap|mappa|killfeed|interfaccia|ui)\b/],
  ["auto_caption", /\b(caption|sottotitol\w*|didascali\w*|testo|scritte|subtitle\w*)\b/],
  ["auto_vertical", /(9:16|9\/16|\bvertical\w*|\bverticale\b|\breframe\b|\binquadra\w*)/],
];

/**
 * Local, deterministic natural-language planner ("segui il giocatore e fai
 * zoom sulle kill"). It only maps the request onto the existing quick actions;
 * nothing is sent to a model and nothing is applied until the user confirms.
 */
export function planGamingCommand(text = "") {
  const normalized = String(text || "").toLowerCase().normalize("NFKC").slice(0, 240);
  const actions = [];
  for (const [action, pattern] of COMMAND_RULES) {
    if (pattern.test(normalized) && !actions.includes(action)) actions.push(action);
  }
  if (actions.includes("improve_all")) return { actions: ["improve_all"], understood: true };
  return { actions, understood: actions.length > 0 };
}

/**
 * Focus Map contract (time -> x/y -> confidence -> subject/action).
 * x and y are normalised source-frame coordinates (0..1, origin top-left).
 * Game Vision does not emit this yet; the editor only previews it when the
 * shell provides `focus_map`, and it is never persisted into editor state.
 */
export function normalizeFocusMap(raw = [], durationValue = 15) {
  const duration = Math.max(0.5, number(durationValue, 15));
  if (!Array.isArray(raw)) return [];
  const points = [];
  for (const item of raw.slice(0, 4000)) {
    if (!item || typeof item !== "object") continue;
    const time = number(item.time ?? item.t, NaN);
    const x = number(item.x, NaN);
    const y = number(item.y, NaN);
    if (![time, x, y].every(Number.isFinite) || time < 0 || time > duration) continue;
    points.push({
      time: rounded(time),
      x: rounded(clamp(x, 0, 1)),
      y: rounded(clamp(y, 0, 1)),
      confidence: rounded(clamp(item.confidence ?? item.score, 0, 1, 0)),
      subject: String(item.subject || "").slice(0, 40),
      action: String(item.action || item.label || "").slice(0, 40),
    });
  }
  return points.sort((left, right) => left.time - right.time);
}

export function sampleFocusMap(points = [], timeValue = 0, { minConfidence = 0.35, holdSeconds = 1.5 } = {}) {
  const time = number(timeValue, 0);
  const usable = points.filter((point) => point.confidence >= minConfidence);
  if (!usable.length) return null;
  let next = usable.findIndex((point) => point.time >= time);
  if (next === -1) {
    const last = usable[usable.length - 1];
    return time - last.time <= holdSeconds ? { ...last } : null;
  }
  const after = usable[next];
  if (next === 0) return after.time - time <= holdSeconds ? { ...after } : null;
  const before = usable[next - 1];
  const span = after.time - before.time;
  if (span > holdSeconds * 2) {
    const nearest = time - before.time <= after.time - time ? before : after;
    return Math.abs(nearest.time - time) <= holdSeconds ? { ...nearest } : null;
  }
  const ratio = span > 0 ? (time - before.time) / span : 0;
  const nearest = ratio < 0.5 ? before : after;
  return {
    time: rounded(time),
    x: rounded(before.x + ((after.x - before.x) * ratio)),
    y: rounded(before.y + ((after.y - before.y) * ratio)),
    confidence: rounded(Math.min(before.confidence, after.confidence)),
    subject: nearest.subject,
    action: nearest.action,
  };
}

/** Viewport that centres a focus sample, bounded exactly like a manual reframe. */
export function focusViewport(sample, base = {}, { minZoom = 1.15 } = {}) {
  const zoom = Math.max(number(base.zoom, 1), minZoom);
  if (!sample) return clampViewport({ zoom: base.zoom, panX: base.panX, panY: base.panY });
  return clampViewport({
    zoom,
    panX: -((sample.x - 0.5) * 100 * zoom),
    panY: -((sample.y - 0.5) * 100 * zoom),
  });
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
