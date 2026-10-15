# Mobile Game Editor 2026 — Design Specification

**Date:** 2026-10-15

**Status:** Approved in chat

**Scope:** Mobile only; desktop behavior remains unchanged

## Intent

Replace the legacy mobile gameplay-video editor with a new canonical editor built from scratch. The editor must feel like a professional 2026 mobile product while retaining Gaming Shorts Factory's approved visual identity and existing rendering semantics.

The user journey is:

`Crea con IA -> Modifica con Editor -> Mobile Game Editor -> Continua a Crea Shorts`

`Crea con IA` may still send a selected moment directly to `Crea Shorts`; choosing `Modifica` opens the new editor with that exact moment. The editor saves the project before handing it to the existing `Crea Shorts` page. It never starts the final render without user confirmation on that page.

## Non-goals

- Do not redesign desktop or replace its current editor implementation.
- Do not build a playable-game or level editor. This product edits recorded gameplay video.
- Do not introduce multi-clip or multitrack editing in this release.
- Do not redesign `Crea con IA`, `Crea Shorts`, the Game Bar, or the publishing page.
- Do not change the AI worker, video-rendering algorithms, product names, or user flows beyond the required navigation contracts.
- Do not add a migration, runtime patch, generated UI, startup transform, or text-matching navigation fallback.

## Current-state findings

The current mobile editor is not a coherent source implementation:

- `web/editor_2027_component/index.html` is about 145 KB and contains successive V389-V395 CSS and JavaScript layers.
- Controls and layout are recreated at runtime, including observers, timers, duplicated transport controls, poster canvases, and fallbacks.
- The same component is also used by desktop, so replacing it in place would violate the mobile-only constraint.
- `Crea con IA` currently emits the generic `preview` action from both `MODIFICA` and `CREA SHORT`; the bridge drops the intent, so neither button has a stable destination contract.
- The editor's final action locates Streamlit buttons by visible text instead of navigating to a named surface.
- The canonical UI pipeline now guarantees repository files equal image and served files. The new editor must enter that pipeline as a normal checked-in file and must never be materialized by a legacy patch.

## Architecture

### Mobile/desktop split

Create a canonical mobile component at:

`web/game_editor_mobile_component/index.html`

Serve it byte-for-byte at:

`/game-editor-mobile/`

The global shell selects the component at the editor navigation boundary:

- mobile (`max-width: 760px`) -> `/game-editor-mobile/`
- desktop -> existing `/editor-live/`

The existing desktop component and desktop route are not modified visually or behaviorally. Mobile never loads the legacy editor after this change.

### Explicit navigation contracts

Navigation must use same-origin `postMessage` events with named actions and validated payloads. No code may search the DOM for a button by its label.

`Crea con IA` emits:

```json
{
  "type": "GSF_AI_UI",
  "action": "open_editor",
  "index": 0,
  "candidate_id": "candidate-id",
  "video": "/media/...",
  "start_time": 12.5,
  "end_time": 27.5,
  "duration": 15,
  "engine": "auto"
}
```

Its direct path uses the same selected-moment payload with `action: "create_short"`.

The shell resolves the selection, records it through the existing Home/Streamlit bridge, opens the correct editor route, and sends `GSF_GAME_EDITOR_INIT` after receiving `GSF_GAME_EDITOR_READY` from the iframe.

The mobile editor emits `GSF_GAME_EDITOR_UI` with one of these actions:

- `autosave`
- `save_draft`
- `continue_to_short`
- `close`
- `fullscreen_changed`

Every message includes a monotonically increasing sequence number and the normalized editor state when applicable. The parent accepts messages only from the editor iframe and only when `event.origin` equals the application origin.

`continue_to_short` has a strict sequence:

1. persist editor state;
2. receive a successful save response;
3. close the editor surface;
4. route to `GSF_SHELL_NAV` target `short`;
5. leave final rendering to the existing `Crea Shorts` page.

### State and persistence

Reuse the existing renderer-compatible state keys and limits:

- trim: `inPoint`, `outPoint`, `speed`
- framing: `zoom`, `panX`, `panY`, `framePreset`
- look: `look`, `intensity`, `brightness`, `contrast`
- captions: `captionOn`, `captionMode`, `captionText`, `captionSize`, `captionY`, `textColor`, `activeColor`, `outlineColor`
- audio: `muted`, `volume`, `audioMode`
- gameplay intelligence: `hudMode`, `aiMode`, `visionEnabled`
- cover, quality, and compatibility: `coverMode`, `coverTime`, `coverLocked`, `qualityMode`, `editorVersion`, `sourceDuration`

The editor-state endpoint whitelist must include `qualityMode`; the current omission is corrected without changing any existing validation or range normalization.

UI-only values such as the open tool, save status, active gesture, and selected AI suggestion are not persisted.

Autosave is debounced after a committed edit, not during every pointer frame. The shell persists via the existing session-bound `/editor/state/save` endpoint and returns a `GSF_GAME_EDITOR_SAVE_STATUS` acknowledgement containing the matching sequence number. The editor displays `Salvataggio...`, `Salvato`, or a recoverable error. Older acknowledgements never overwrite newer status.

`Salva bozza` first saves editor state and then calls `/creator-hub/project/save-draft`, the endpoint already used by the current bridge. Success is reported only after both operations complete.

The existing session boundary and `X-GSF-Session-ID` propagation remain intact. This design does not disable or weaken CSRF, authentication, or session validation.

## Mobile experience

### Normal workspace

The editor occupies the content area above the global Game Bar. The hierarchy is:

1. compact header: Back, project name, Undo, Redo, save status, Fullscreen;
2. dominant 9:16 gameplay preview;
3. compact single-clip timeline and transport;
4. five primary tools: `Clip`, `Inquadratura`, `Testo`, `Audio`, `AI`;
5. secondary `Altro` entry for Look, Cover, HUD, Speed, and Quality;
6. persistent actions: `Salva bozza` and `Continua a Crea Shorts`.

All interactive targets are at least 44 CSS pixels. The layout respects safe-area insets and works from 320 CSS pixels upward without horizontal scrolling.

### Fullscreen and zoom

Fullscreen applies to the whole editor workspace, not just the video. Use the native Fullscreen API on the editor root when available. When a browser rejects the API, the editor emits `fullscreen_changed`; the parent shell expands the editor overlay to the complete viewport and hides the Game Bar until exit. Entering fullscreen therefore hides global chrome in both native and fallback modes. Leaving fullscreen restores the normal shell with the Game Bar visible.

Inside the preview:

- two-pointer pinch changes `zoom`;
- one-pointer drag while zoomed changes `panX` and `panY`;
- a precision slider provides the same zoom value;
- a reset action returns to the selected framing preset;
- live transforms update with `requestAnimationFrame`;
- one history entry is committed at gesture end, so Undo reverses the complete gesture;
- normalized zoom and pan values are used by the final renderer, not only by the preview.

The editor prevents page scrolling only during an active preview gesture.

### Single-clip professional timeline

The timeline provides:

- native playback and scrubbing;
- visible current time and duration;
- IN and OUT handles with a minimum 0.5-second selection;
- precise time values and direct seek;
- AI event markers from the selected gameplay moment;
- selected-range shading;
- speed control under `Altro`;
- keyboard shortcuts when a hardware keyboard is present: Space, Arrow keys, Cmd/Ctrl-Z, and Cmd/Ctrl-Shift-Z.

This release does not add clip splitting, ordering, or multiple tracks.

## Editing tools

### Clip

Trim IN/OUT, scrub, seek to AI markers, and reset to the selected moment. Changes are reversible and update the preview immediately.

### Inquadratura

Offer clear presets (`Centro`, `Gameplay`, `Facecam`, `Libero`) plus pinch, drag, and precision sliders. The fixed output remains 9:16 for this flow.

### Testo

Support `Auto`, `Testo`, and `Off`, with editable text, size, vertical position, and approved colors. Automatic captions use real transcription only; no placeholder text is rendered into the final video.

### Audio

Support mute, original audio, Game Boost, volume, and speed. Controls map to existing renderer semantics and do not invent unavailable audio tracks.

### Altro

Expose Look, Cover, HUD safe zones, Speed, and Quality without crowding the primary toolbar.

## Game AI assistant

Game AI is a contextual assistant, not an autonomous editor. It must never silently apply a change.

Reuse the existing V403 support engine and available gameplay analysis. Extend the editor state response with sanitized timeline markers and deterministic suggestions derived from the current clip, existing event map, and Game Brain context. No new external model call is required.

Suggestions may cover:

- stronger hook or IN/OUT range;
- action-aware zoom and reframe;
- caption safe-zone placement around HUD, minimap, killfeed, and facecam;
- caption style appropriate to the detected moment;
- audio lift or normalization;
- gameplay-specific presets.

Each suggestion shows:

1. what will change;
2. why it is recommended;
3. `Anteprima`;
4. `Applica`;
5. `Annulla` or standard Undo after application.

Previewing a suggestion is transient. Applying it commits exactly one history entry and triggers autosave.

## Visual system

Use the existing GSF premium-light language:

- navy text;
- blue/cyan primary actions;
- mint success and ready states;
- white and very light blue surfaces;
- restrained translucent glass, not heavy blur everywhere;
- rounded cards and controls consistent with the current app;
- clear hierarchy and generous spacing;
- no dark unrelated gaming theme, neon overload, or arbitrary new brand language.

Animation communicates state only. All nonessential motion is removed under `prefers-reduced-motion`.

## Performance and Safari safety

- No `MutationObserver` is permitted inside the new mobile editor.
- No polling interval is permitted for layout, navigation, save state, or playback.
- Use media events and a single `requestAnimationFrame` loop only while playing or during an active gesture.
- Autosave uses one resettable debounce timer.
- Tool panels are static DOM sections toggled by state; controls are not repeatedly appended or reparented.
- Pause video work and cancel animation frames when the editor is hidden or the document is not visible.
- Do not capture video frames to canvas merely to display a paused poster.
- Avoid forced layout reads inside pointer-move or playback loops.

## Error handling

- Missing media: show a stable empty state with Back and Retry; never a dead black surface.
- Autosave failure: preserve dirty state, display `Non salvato`, and retry only after a new edit or explicit Retry.
- Draft failure: remain in the editor and retain all edits.
- Continue failure: do not navigate to `Crea Shorts`; display the save error.
- Fullscreen rejection: activate only the internal fallback and keep all editing controls functional.
- AI context unavailable: keep manual controls fully functional and show `Suggerimenti non disponibili` without blocking editing.

## Canonical build and runtime requirements

- The new component is committed as a normal source file and copied byte-for-byte by Docker through the existing canonical `web` copy.
- Nginx serves the checked-in bytes directly with the repository's current cache/versioning policy.
- No `fix_v*.py`, `apply_v*.py`, startup script, materializer, generated HTML, or temporary transformed component may touch the mobile editor.
- The canonical UI manifest and startup verification must include the new file automatically through the existing `web` directory mapping.
- The mobile shell must never route back to `/editor-live/` after the new path is enabled.

## Test strategy

Implementation follows test-driven development. The first failing tests must prove the current defects before production code changes.

Required regression coverage:

- `Crea con IA` emits distinct `open_editor` and `create_short` actions with the selected moment.
- Mobile editor navigation uses `/game-editor-mobile/`; desktop continues to use `/editor-live/`.
- The mobile source contains no legacy V389-V395 markers, runtime patch blocks, `MutationObserver`, or layout polling.
- Every primary tool is reachable at mobile width and has a 44-pixel target.
- Pinch/drag and slider update normalized zoom/pan, create one Undo entry, and persist values used by the renderer.
- AI suggestions require explicit application and are reversible.
- Autosave sequence ordering prevents stale acknowledgements from replacing newer status.
- `Salva bozza` persists editor state before the draft.
- `Continua a Crea Shorts` persists state and then routes to `short`; it does not click a button by text or start the render.
- Fullscreen hides the Game Bar and exit restores it.
- No console-critical errors, unbounded timers, observers, or rerun loop occur during a representative edit session.
- Canonical UI pipeline detects any build/startup mutation or reinjection of the old mobile editor.
- Python syntax, JavaScript syntax, focused unit tests, production Docker build, container startup, `/healthz`, `/editor/state`, mobile WebKit visual check, and the Production Gate pass before publication readiness is claimed.

## Rollout and completion evidence

The implementation is "ready for publication" only after the isolated branch tests, production Docker/container checks, and PR Production Gate are green. If the user later authorizes publication, completion additionally requires merge, main Production Gate, Railway deployment success, `/healthz` 200, editor-state health, and a real mobile production check showing the new canonical component and correct `Crea con IA -> Editor -> Crea Shorts` navigation.

No status may be reported as live based only on repository or CI state.
