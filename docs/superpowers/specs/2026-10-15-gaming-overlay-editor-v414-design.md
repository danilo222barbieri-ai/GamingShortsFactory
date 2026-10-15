# Gaming Overlay Editor V414 — Design Specification

**Date:** 2026-10-15

**Status:** Approved in chat

**Scope:** Canonical mobile Game Editor only. Desktop `/editor-live/` stays unchanged.

## Product intent

Turn the current Mobile Game Editor 2026 from a conventional page of cards and controls into a video-first gaming editor inspired by modern mobile editors such as CapCut and TikTok.

The product rule is: **the gameplay is the editor**.

The normal embedded surface is a compact 9:16 mini player. Entering edit mode expands the editor to fullscreen. In fullscreen, every editing control, timeline, AI action and tool sheet is rendered inside the gameplay stage as translucent gaming glass. No primary editing button may sit outside the video surface.

The existing editor engine is preserved: same-origin shell messaging, state normalization, history, autosave sequencing, trimming, captions, audio, AI suggestions, gestures, fullscreen fallback and final `Crea Shorts` handoff remain the source of truth.

## Architecture

The implementation continues to use the canonical component at `web/game_editor_mobile_component/`.

`editor.css` remains the stable base stylesheet and is currently owned by a parallel mobile-polish task. V414 therefore adds a canonical additive stylesheet, `overlay_v414.css`, loaded after `editor.css`. This is a normal checked-in source file, not a runtime patch or generated asset.

V414 may change:

- `index.html`
- `editor.mjs`
- `editor_state.mjs`
- `overlay_v414.css`

The mobile shell, backend endpoint and desktop editor are not changed in this task.

## Mini player and fullscreen

On entry the component starts in `is-mini` mode:

- the 9:16 gameplay is the dominant visible surface;
- minimal glass chrome lives inside the video: Back, project identity/status and an expand/edit affordance;
- tool sheets, detailed timeline and tool rail stay visually collapsed;
- tapping the explicit in-video edit affordance requests fullscreen.

Fullscreen uses the existing native Fullscreen API with the existing shell fallback. When fullscreen is active, the root becomes `is-expanded`, the complete stage fills the viewport and the global shell chrome remains hidden through the existing `fullscreen_changed` contract.

Exiting fullscreen returns to mini mode without losing edits.

## In-video control hierarchy

All controls are static DOM descendants of `#previewStage`; JavaScript does not continuously reparent controls.

### Top glass HUD

Contains:

- Back
- compact project title/save status
- Undo
- Redo
- fullscreen/exit control
- Done/Continue shortcut

### Gaming tool rail

The existing compatibility tools remain in the same contract order:

1. `clip` — Taglio
2. `frame` — Camera
3. `text` — Testo
4. `audio` — Audio
5. `ai` — Game AI

The labels may be shorter visually, but `data-tool` keys and order stay stable for current regression tests and shell contracts.

### Bottom transport/timeline

The transport and single-clip timeline move into a glass overlay at the bottom of the stage. It keeps the existing element IDs and trim controls, including Game AI event markers.

The play button is visually centered over the gameplay when paused. During playback, nonessential chrome becomes less prominent via CSS state; the video remains the focus.

### Tool sheet

`#toolDock` becomes an in-stage bottom glass sheet. Selecting a tool opens the relevant existing panel over the lower part of the gameplay. The sheet can be closed without changing state. This replaces the permanent external panel layout.

## Realtime editing

Every mutable control continues to use the current preview/commit split:

- `input` events update the gameplay immediately without creating history spam;
- `change`/gesture end commits one normalized history entry;
- autosave occurs only after a committed edit.

Pinch and drag remain direct manipulation of the gameplay. Caption position/size, look, audio and trim update immediately.

## Camera modes without a fake persistence field

The backend currently persists only the existing editor-state whitelist. V414 does **not** invent a `cameraMode` field that would be silently dropped.

Instead, camera modes are deterministic presets over fields already persisted and consumed by the pipeline:

- **Static**: `visionEnabled=false`, `aiMode=Manuale`
- **Follow Action**: `visionEnabled=true`, `aiMode=Auto Gaming`, gameplay framing
- **Dynamic**: Follow Action plus a restrained punch-in
- **Cinematic**: Follow Action plus cinematic look and a stronger but bounded punch-in

The UI infers the active camera preset from the persisted fields, so reload/Undo remain coherent.

This makes Follow Action a real smart-reframe decision, not a preview-only animation. V414 does not claim frame-level subject tracking beyond the intelligence currently available to GSF.

## Game AI quick actions

The AI sheet keeps the current explicit `Anteprima -> Applica -> Undo` contract and adds deterministic one-tap gaming presets rendered inside the video:

- `Segui l'azione`
- `Auto 9:16`
- `Zoom momenti`
- `Proteggi HUD`
- `Auto caption`
- `Migliora tutto`

Quick actions must use the same normalized renderer-compatible state. `Migliora tutto` combines safe deterministic patches and never starts rendering or publishing.

Existing server-provided AI suggestions remain visible below the quick actions and are never silently applied.

## Glass visual language

V414 uses a gaming-glass treatment while staying inside GSF's blue/cyan family:

- dark translucent glass on top of the video rather than opaque cards around it;
- subtle blur and thin cool-white borders;
- cyan/blue active states, restrained violet only for AI;
- rounded controls sized for touch;
- no giant neon frames or decorative clutter;
- readable white foreground against gameplay with shadow/backdrop support;
- safe-area aware positioning.

The mini player remains visually premium and simple. Fullscreen is denser but never resembles a settings page.

## Playback visibility

When playback starts the root receives an `is-playing` class. Tool sheet and nonessential labels recede; the central play control disappears. A direct tap on the in-video transport restores interaction. Playback does not start a polling timer or layout observer.

## Compatibility invariants

V414 preserves:

- all existing bridge-critical IDs;
- tool `data-tool` order and keys;
- `GSF_GAME_EDITOR_READY`, `GSF_GAME_EDITOR_INIT`, `GSF_GAME_EDITOR_UI`, save ACK and shell-close contracts;
- same-origin validation;
- `save_draft`, `continue_to_short`, `close`, `fullscreen_changed` semantics;
- current trim, gesture, history, AI preview/apply and save sequencer behavior;
- no `MutationObserver`, layout polling or canvas poster generation;
- desktop route and legacy desktop editor untouched.

## Test strategy

Implementation is test-first.

New V414 tests must initially fail on the current component and prove that:

- `overlay_v414.css` is loaded after the base stylesheet;
- the header, transport, timeline, tool bar, tool sheet and footer actions are descendants of `#previewStage`;
- the component has an in-video mini-to-fullscreen affordance;
- camera preset helpers map only to existing persisted renderer fields;
- camera modes are inferable after normalization/reload;
- AI quick actions expose the approved labels and produce bounded state patches;
- playback toggles the `is-playing` visual state;
- the old Mobile Game Editor 2026 regression contracts remain intact.

After implementation, run the new Node/Python tests plus existing mobile editor, canonical UI and production contracts. Integration may proceed only after the active `editor.css` owner is reconciled and all relevant CI/Production Gate checks are green.
