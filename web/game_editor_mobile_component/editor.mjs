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
  app?.setAttribute("aria-busy", "false");
  if (status) status.textContent = editorContext.media.url ? "Gameplay pronto" : "Editor pronto";
}

window.addEventListener("message", receiveInit);
parent.postMessage({ type: "GSF_GAME_EDITOR_READY", apiVersion: 1 }, location.origin);
