import {
  applySuggestion,
  createEditorHistory,
  createSaveSequencer,
  normalizeEditorState,
  previewSuggestion,
} from "./editor_state.mjs";

const app = document.getElementById("gameEditorApp");
const status = document.getElementById("editorStatus");

let editorContext = {
  session: {},
  project: {},
  media: {},
  initial_state: {},
  event_map: [],
  brain_context: {},
  ai_suggestions: [],
};
let history = createEditorHistory(normalizeEditorState({}, 15));

const saveSequencer = createSaveSequencer((message) => {
  parent.postMessage({ type: "GSF_GAME_EDITOR_UI", ...message }, location.origin);
});

function setStatus(label) {
  if (status) status.textContent = label;
}

function commitEditorState(nextState, autosave = true) {
  const normalized = normalizeEditorState(nextState, history.value.sourceDuration);
  history.commit(normalized);
  if (autosave) saveSequencer.schedule(history.value);
  return history.value;
}

function requestEditorAction(action) {
  return saveSequencer.flush(history.value, action);
}

function receiveInit(event) {
  if (event.origin !== location.origin || event.source !== parent) return;
  if (!event.data || event.data.type !== "GSF_GAME_EDITOR_INIT") return;
  const data = event.data;
  editorContext = {
    session: data.session && typeof data.session === "object" ? data.session : {},
    project: data.project && typeof data.project === "object" ? data.project : {},
    media: data.media && typeof data.media === "object" ? data.media : {},
    initial_state: data.initial_state && typeof data.initial_state === "object" ? data.initial_state : {},
    event_map: Array.isArray(data.event_map) ? data.event_map : [],
    brain_context: data.brain_context && typeof data.brain_context === "object" ? data.brain_context : {},
    ai_suggestions: Array.isArray(data.ai_suggestions) ? data.ai_suggestions : [],
  };
  const duration = Number(editorContext.initial_state.sourceDuration || editorContext.media.duration || editorContext.initial_state.outPoint || 15);
  history = createEditorHistory(normalizeEditorState(editorContext.initial_state, duration));
  app?.setAttribute("aria-busy", "false");
  setStatus(editorContext.media.url ? "Gameplay pronto" : "Editor pronto");
}

function receiveSaveStatus(event) {
  if (event.origin !== location.origin || event.source !== parent) return;
  if (!event.data || event.data.type !== "GSF_GAME_EDITOR_SAVE_STATUS") return;
  const accepted = saveSequencer.acknowledge(event.data.sequence, event.data.ok === true, event.data.error);
  if (!accepted) return;
  const snapshot = saveSequencer.snapshot();
  setStatus(snapshot.status === "saved" ? "Salvato" : "Non salvato · Riprova");
}

window.addEventListener("message", receiveInit);
window.addEventListener("message", receiveSaveStatus);
window.GSFGameEditor2026 = {
  get state() { return history.value; },
  get canUndo() { return history.canUndo; },
  get canRedo() { return history.canRedo; },
  commit: commitEditorState,
  undo: () => history.undo(),
  redo: () => history.redo(),
  previewSuggestion: (suggestion) => previewSuggestion(history.value, suggestion),
  applySuggestion: (suggestion) => commitEditorState(applySuggestion(history.value, suggestion, history.value.sourceDuration)),
  save: requestEditorAction,
  saveStatus: () => saveSequencer.snapshot(),
  context: () => ({ ...editorContext }),
};
parent.postMessage({ type: "GSF_GAME_EDITOR_READY", apiVersion: 1 }, location.origin);
