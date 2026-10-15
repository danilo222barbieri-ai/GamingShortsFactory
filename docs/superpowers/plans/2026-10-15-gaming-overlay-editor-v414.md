# Gaming Overlay Editor V414 — Implementation Plan

**Goal:** Replace the canonical mobile editor's page-like surface with an in-video glass gaming overlay while preserving its stable editor engine and renderer-compatible state.

**Architecture:** Keep the canonical `/game-editor-mobile/` component and existing parent bridge. Add an additive `overlay_v414.css` after the concurrently owned base `editor.css`. Move the existing static controls inside `#previewStage`, then extend `editor_state.mjs` with pure camera/quick-action preset helpers that only emit existing persisted fields. Wire these helpers in `editor.mjs` without observers, polling or runtime DOM patching.

## Task 1 — Lock V414 behavior with failing tests

Files:
- Create `tests/js/gaming_overlay_editor_v414_state.test.mjs`
- Create `tests/test_gaming_overlay_editor_v414.py`

Tests:
- overlay stylesheet loaded after base CSS;
- video stage owns header, transport, timeline, tools, tool sheet and actions;
- mini-to-fullscreen affordance is inside the stage;
- camera preset helper returns only persisted keys and round-trips through normalization;
- AI gaming quick presets are bounded and renderer-compatible;
- playback class contract exists;
- no observers/polling/canvas regression.

Open a draft PR with tests only and record the expected RED result before production edits.

## Task 2 — Add renderer-compatible camera primitives

Files:
- Modify `web/game_editor_mobile_component/editor_state.mjs`

Implementation:
- export `cameraPresetPatch(mode, state)`;
- export `inferCameraPreset(state)`;
- export `gamingQuickActionPatch(action, state)`;
- use only existing whitelist fields (`visionEnabled`, `aiMode`, `framePreset`, `zoom`, `look`, `hudMode`, `captionMode`, etc.);
- keep normalization limits unchanged except version marker may advance to `2026.2`.

Verify Node V414 tests plus existing mobile state tests.

## Task 3 — Rebuild static DOM as video-first overlay

Files:
- Modify `web/game_editor_mobile_component/index.html`
- Create `web/game_editor_mobile_component/overlay_v414.css`

Implementation:
- load V414 CSS after `editor.css`;
- keep every existing bridge/test-critical ID;
- make `previewStage` the static parent of top HUD, transport, timeline, tool bar, tool sheet and editor actions;
- add `enterEditorButton`, `closeToolSheetButton`, camera preset controls and AI quick actions;
- preserve `data-tool` order clip/frame/text/audio/ai;
- mini mode shows only minimal in-video chrome;
- fullscreen exposes glass controls and sheets;
- all touch targets remain >=44px.

Verify static Python tests and existing mobile editor contracts.

## Task 4 — Wire overlay interactions without changing the bridge

Files:
- Modify `web/game_editor_mobile_component/editor.mjs`

Implementation:
- root starts `is-mini`;
- `enterEditorButton` calls existing fullscreen flow;
- fullscreen state toggles mini/expanded classes;
- tool buttons open/close the in-stage glass sheet;
- camera buttons use pure camera preset patches;
- AI quick actions preview/apply deterministic patches using the same history/autosave path;
- video play/pause toggles `is-playing`;
- preserve same-origin messaging, save sequencing, gestures, keyboard shortcuts and navigation actions.

Verify JS syntax, V414 tests, old state tests and existing mobile editor tests.

## Task 5 — Reconcile concurrent CSS polish and integrate

Before merge:
- refresh `main` and claims registry;
- confirm `mobile-polish...` no longer owns conflicting paths or rebase its latest `editor.css` change into V414;
- ensure `overlay_v414.css` remains additive and does not revert the polish work;
- run/observe GSF CI contracts and Production Gate on the PR;
- update `PROJECT_STATUS.md` with factual evidence;
- merge only when checks are green;
- verify main gate, Railway frontend deployment and `/healthz` before reporting LIVE;
- finish the V414 claim with commit/PR/test/gate/deploy evidence.
