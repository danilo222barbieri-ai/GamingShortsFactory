/* Gaming Shorts Factory — V414 overlay behaviours.
   DOM-only layer on top of editor.mjs: two-phase Game AI, natural commands,
   auto-hiding chrome during playback and the Focus Map preview. It never owns
   editor state; every committed change goes through the editor's history. */
import {
  GAMING_QUICK_ACTIONS,
  combinedQuickActionPatch,
  focusViewport,
  inferCameraPreset,
  normalizeFocusMap,
  planGamingCommand,
  sampleFocusMap,
} from "./editor_state.mjs";

const IDLE_MS = 2600;
const FOCUS_CONFIDENCE = 0.35;
const FOCUS_CAMERA_MODES = new Set(["follow", "dynamic"]);

export function installOverlay(editor) {
  const {
    app,
    video,
    getState,
    getVisibleState = getState,
    previewPatch,
    clearPreview,
    commitPatch,
    renderBase,
    selectTool,
    setStatus,
  } = editor;
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];

  const previewStage = $("#previewStage");
  const bar = $("#aiPreviewBar");
  const barLabel = $("#aiPreviewLabel");
  const applyButton = $("#aiPreviewApplyButton");
  const cancelButton = $("#aiPreviewCancelButton");
  const commandForm = $("#aiCommandForm");
  const commandInput = $("#aiCommandInput");
  const commandHint = $("#aiCommandHint");
  const focusStatus = $("#focusMapStatus");
  const timelineTrack = $("#timelineTrack");

  let pending = null;
  let idleTimer = 0;
  let focusPoints = [];
  let focusDuration = 15;
  let focusFrame = 0;
  let focusDriving = false;

  const focusMarkers = document.createElement("div");
  focusMarkers.className = "focus-markers";
  focusMarkers.setAttribute("aria-hidden", "true");
  timelineTrack?.append(focusMarkers);

  const labelFor = (actions) => actions.map((action) => GAMING_QUICK_ACTIONS[action]).filter(Boolean).join(" + ");

  function markQuickButtons(actions = []) {
    $$("[data-ai-quick]").forEach((button) => button.classList.toggle("is-previewing", actions.includes(button.dataset.aiQuick)));
  }

  function hideBar() {
    bar.hidden = true;
    app.classList.remove("is-ai-previewing");
    markQuickButtons([]);
  }

  /* ---------- two-phase Game AI ---------- */

  function previewQuickActions(actions = []) {
    const valid = actions.filter((action) => action in GAMING_QUICK_ACTIONS);
    const patch = combinedQuickActionPatch(valid, getState());
    if (!valid.length || !Object.keys(patch).length) return false;
    pending = { actions: valid, label: labelFor(valid) };
    previewPatch(patch);
    barLabel.textContent = `${pending.label} · nessuna modifica applicata`;
    bar.hidden = false;
    app.classList.add("is-ai-previewing");
    markQuickButtons(valid);
    setStatus("Anteprima AI · nessuna modifica applicata");
    wake();
    return true;
  }

  function applyAiPreview() {
    if (!pending) return;
    const { actions, label } = pending;
    pending = null;
    hideBar();
    // Recomputed against the current history so Apply == what Preview showed.
    commitPatch(combinedQuickActionPatch(actions, getState()), `Game AI · ${label}`);
    if (commandHint) commandHint.textContent = `Applicato: ${label}. Annulla con ↶.`;
  }

  function cancelAiPreview({ render = true } = {}) {
    if (!pending) return;
    pending = null;
    hideBar();
    if (render) {
      clearPreview();
      setStatus("Anteprima annullata", "saved");
    }
  }

  function previewCommand(text = "") {
    const plan = planGamingCommand(text);
    if (!plan.understood) {
      if (commandHint) commandHint.textContent = "Non ho capito. Prova «segui il giocatore», «zoom sulle kill» o «proteggi l'HUD».";
      return plan;
    }
    previewQuickActions(plan.actions);
    if (commandHint) commandHint.textContent = `Ho capito: ${labelFor(plan.actions)}. Controlla l'anteprima e premi Applica.`;
    return plan;
  }

  applyButton.addEventListener("click", applyAiPreview);
  cancelButton.addEventListener("click", () => cancelAiPreview());
  commandForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    previewCommand(commandInput.value);
  });
  $("#aiTopButton")?.addEventListener("click", () => selectTool("ai"));

  // Safety net for engines without `overflow: clip`: the stage never scrolls.
  previewStage.addEventListener("scroll", () => {
    if (previewStage.scrollTop || previewStage.scrollLeft) {
      previewStage.scrollTop = 0;
      previewStage.scrollLeft = 0;
    }
  }, { passive: true });

  /* ---------- auto-hide chrome while playing ---------- */

  function canHide() {
    return app.classList.contains("is-playing")
      && app.classList.contains("is-expanded")
      && !app.classList.contains("is-tool-open")
      && !pending
      && !previewStage.classList.contains("is-gesturing");
  }

  function wake() {
    app.classList.remove("is-chrome-hidden");
    clearTimeout(idleTimer);
    idleTimer = 0;
    if (canHide()) {
      idleTimer = setTimeout(() => {
        idleTimer = 0;
        if (canHide()) app.classList.add("is-chrome-hidden");
      }, IDLE_MS);
    }
  }

  app.addEventListener("pointerdown", wake, { passive: true });
  app.addEventListener("pointermove", (event) => {
    if (event.pointerType === "mouse" || app.classList.contains("is-chrome-hidden")) wake();
  }, { passive: true });
  document.addEventListener("keydown", wake);

  /* ---------- Focus Map (time -> x/y -> confidence -> subject/action) ---------- */

  function renderFocusMarkers() {
    focusMarkers.replaceChildren();
    let lastTime = -Infinity;
    for (const point of focusPoints) {
      if (!point.action || point.confidence < FOCUS_CONFIDENCE || point.time - lastTime < 0.75) continue;
      lastTime = point.time;
      const marker = document.createElement("span");
      marker.className = "focus-marker";
      marker.style.left = `${Math.min(100, (point.time / focusDuration) * 100)}%`;
      marker.title = [point.subject, point.action].filter(Boolean).join(" · ");
      focusMarkers.append(marker);
      if (focusMarkers.childElementCount >= 24) break;
    }
  }

  function setFocusMap(raw = [], duration = 15) {
    focusDuration = Math.max(0.5, Number(duration) || 15);
    focusPoints = normalizeFocusMap(raw, focusDuration);
    const usable = focusPoints.filter((point) => point.confidence >= FOCUS_CONFIDENCE).length;
    if (focusStatus) {
      focusStatus.dataset.state = usable ? "ready" : "none";
      focusStatus.textContent = usable
        ? `Focus Map attiva · ${usable} punti. Follow Action e Dynamic seguono il soggetto anche in anteprima.`
        : "Follow Action segue l'azione nel render con Game Vision. Il tracking in anteprima si attiva quando è disponibile la Focus Map.";
    }
    renderFocusMarkers();
    stopFocusPreview();
    if (!video.paused) startFocusPreview();
  }

  function focusPreviewActive() {
    return focusPoints.length > 0
      && !video.paused
      && FOCUS_CAMERA_MODES.has(inferCameraPreset(getVisibleState()))
      && !previewStage.classList.contains("is-gesturing");
  }

  function driveFocus() {
    focusFrame = 0;
    if (!focusPreviewActive()) {
      stopFocusPreview();
      return;
    }
    const state = getVisibleState();
    const sample = sampleFocusMap(focusPoints, video.currentTime, { minConfidence: FOCUS_CONFIDENCE });
    const viewport = focusViewport(sample, state);
    video.style.transform = `translate(${viewport.panX}%, ${viewport.panY}%) scale(${viewport.zoom})`;
    focusDriving = true;
    previewStage.classList.toggle("is-focus-tracking", Boolean(sample));
    focusFrame = requestAnimationFrame(driveFocus);
  }

  function startFocusPreview() {
    if (!focusFrame && focusPreviewActive()) focusFrame = requestAnimationFrame(driveFocus);
  }

  function stopFocusPreview() {
    if (focusFrame) cancelAnimationFrame(focusFrame);
    focusFrame = 0;
    previewStage.classList.remove("is-focus-tracking");
    if (focusDriving) {
      focusDriving = false;
      renderBase();
    }
  }

  video.addEventListener("play", () => {
    startFocusPreview();
    wake();
  });
  video.addEventListener("pause", () => {
    stopFocusPreview();
    wake();
  });
  video.addEventListener("ended", stopFocusPreview);

  return {
    previewQuickActions,
    previewCommand,
    applyAiPreview,
    cancelAiPreview,
    hasAiPreview: () => Boolean(pending),
    setFocusMap,
    ensureFocus: startFocusPreview,
    wake,
  };
}
