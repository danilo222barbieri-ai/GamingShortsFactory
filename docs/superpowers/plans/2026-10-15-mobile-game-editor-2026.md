# Mobile Game Editor 2026 Implementation Plan

**Goal:** Replace the mobile-only legacy editor experience with a canonical, professional single-clip gameplay video editor that preserves the approved GSF visual language, offers explicit AI assistance, supports fullscreen pinch/zoom/crop, and hands off safely to Crea Shorts without changing the desktop editor.

**Architecture:** Add one immutable mobile editor component served directly by nginx, select it only below the mobile breakpoint, and keep `/editor-live/` untouched for desktop. The component owns deterministic editing state in a testable ES module; the Streamlit shell owns session-bound persistence and named navigation; the existing V403 editor engine supplies bounded AI suggestions. No build/startup migration may modify the component.

**Tech Stack:** Python 3.12, Streamlit, vanilla ES modules/CSS, nginx, pytest, Node built-in test runner, Playwright WebKit, Docker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-15-mobile-game-editor-2026-design.md`

---

## Global Constraints

- Mobile behavior applies only at `max-width: 760px`; desktop continues to use `/editor-live/` and `web/editor_2027_component/index.html` unchanged.
- The new source of truth is `web/game_editor_mobile_component/`. Do not create `fix_v*.py`, `apply_v*.py`, runtime `replace()`, DOM materialization, or startup mutation for this component.
- AI suggestions are deterministic proposals from the existing editor intelligence. They must be previewed and explicitly applied; no suggestion may silently modify state.
- CSRF, session binding, `X-GSF-Session-ID`, auth, render behavior, and worker behavior must not be weakened or bypassed.
- “Continue” means flush/save, await acknowledgement, close the editor, and navigate through the named `short` route. It must not start rendering.
- Before implementation, re-run `claim_guard.py conflicts`. The active broad CI cleanup claim currently overlaps product paths; do not edit those paths until it releases. Then acquire one exact-path implementation claim and create a fresh isolated worktree from current `origin/main`.
- Each task follows RED → minimal implementation → GREEN → commit. Do not batch unverified work across tasks.

## Review Focus

1. If native fullscreen is rejected on iOS/WebKit, shell fullscreen must activate, hide the Game Bar, and restore the prior layout on exit.
2. Out-of-order autosave acknowledgements must never mark an older snapshot as the current saved state.
3. Missing, invalid, or not-yet-ready editor media must leave the editor usable and must not create reload/polling loops.
4. A cancelled second pointer must release gesture state, restore scrolling, and create at most one history entry for the completed gesture.
5. Empty or malformed AI context must degrade to manual editing; Apply must stay disabled until a valid suggestion is previewed.

## Task 1: Establish the canonical mobile route and explicit navigation contract

**Files:**

- Create: `tests/test_mobile_game_editor_2026.py`
- Create: `web/game_editor_mobile_component/index.html`
- Create: `web/game_editor_mobile_component/editor.css`
- Create: `web/game_editor_mobile_component/editor.mjs`
- Modify: `web/nginx.conf.template`
- Modify: `web/ai_v221_component/index.html`
- Modify: `app.py`

- [ ] **Step 1: Write failing route and bridge tests**

Add focused source-contract tests that assert:

- `/game-editor-mobile/` is an nginx alias to the new canonical directory with the same security/no-stale-cache policy as other embedded surfaces;
- Crea con IA emits distinct `GSF_AI_UI` actions `open_editor` and `create_short`, retaining candidate/media/time-range payload fields;
- the shell selects `/game-editor-mobile/` only when `matchMedia('(max-width: 760px)')` matches and keeps `/editor-live/` for desktop;
- the shell waits for `GSF_GAME_EDITOR_READY`, then sends `GSF_GAME_EDITOR_INIT` with session, project, media, state, and AI context;
- the mobile bridge navigates by the named `short` target and contains no button-text lookup.

Run:

```bash
python3 -m pytest -q tests/test_mobile_game_editor_2026.py
```

Expected: FAIL because the mobile component/route and explicit AI actions do not exist.

- [ ] **Step 2: Add the smallest canonical component scaffold**

Create a semantic standalone document with one application root, status region, stylesheet, and module script. The module must post `GSF_GAME_EDITOR_READY` on initialization and accept only same-origin `GSF_GAME_EDITOR_INIT` messages. Keep this scaffold intentionally small; the complete workspace arrives in Task 4.

- [ ] **Step 3: Serve the component without a materialization layer**

Add exact `/game-editor-mobile` and `/game-editor-mobile/` nginx locations. Serve the source directory directly, add CSP/security headers, and use revalidation/no-stale HTML behavior consistent with the canonical UI pipeline. Do not copy or generate the files in startup scripts.

- [ ] **Step 4: Make AI destinations explicit and preserve payloads**

Change the two Crea con IA primary actions from the ambiguous `preview` intent to explicit `open_editor` and `create_short` messages. In the Python component bridge, forward the complete allow-listed selection payload instead of reducing it to action/duration/engine/index.

- [ ] **Step 5: Select the editor by viewport without altering desktop**

In the existing editor-overlay owner in `app.py`, choose the source when opening:

```text
mobile <= 760px -> /game-editor-mobile/
desktop          -> /editor-live/
```

Do not switch an already-open editor during rotation/resizing. Add the ready/init handshake for the mobile source and retain the existing desktop initialization path.

- [ ] **Step 6: Run the focused tests and syntax checks**

Run:

```bash
python3 -m pytest -q tests/test_mobile_game_editor_2026.py
python3 -m compileall -q app.py
node --check web/game_editor_mobile_component/editor.mjs
```

Expected: PASS.

- [ ] **Step 7: Commit the route contract**

```bash
git add tests/test_mobile_game_editor_2026.py web/game_editor_mobile_component web/nginx.conf.template web/ai_v221_component/index.html app.py
git commit -m "feat: add explicit mobile editor route"
```

## Task 2: Expose session-safe editor state and deterministic AI context

**Files:**

- Create: `tests/test_mobile_game_editor_state.py`
- Modify: `web/direct_upload_server.py`
- Read/reuse: `gsf_editor_v403.py`

- [ ] **Step 1: Write failing backend contract tests**

Cover a pure helper plus the route payload:

- `qualityMode` survives normalization and persistence;
- a valid session editor state returns normalized `event_map` and bounded `ai_suggestions` from V403;
- malformed/missing session intelligence produces empty suggestions without failing manual editor state;
- suggestions contain JSON-safe IDs, labels, reason/impact text, and proposed patches only;
- the save endpoint continues to require the session/CSRF contract already enforced by nginx/runtime.

Use temporary session data; do not depend on a live server.

Run:

```bash
python3 -m pytest -q tests/test_mobile_game_editor_state.py
```

Expected: FAIL because `qualityMode` is absent from the whitelist and `/editor/state` lacks the mobile context.

- [ ] **Step 2: Add one pure context adapter**

Add a helper with a narrow interface:

```python
def _editor_mobile_context(session_state: dict, editor_state: dict) -> dict:
    """Return normalized event_map, brain_context, and bounded AI suggestions."""
```

Reuse `normalize_timeline_markers()` and `game_director_suggestions()` from `gsf_editor_v403.py`. Do not duplicate its heuristics or call an external model.

- [ ] **Step 3: Extend the existing state response minimally**

Add `qualityMode` to `_EDITOR_STATE_KEYS`. Extend the existing `/editor/state` response with:

```json
{
  "event_map": [],
  "brain_context": {},
  "ai_suggestions": []
}
```

Keep all current state fields and session-bound file lookup behavior intact. Sanitize untrusted session data through the pure helper before returning it.

- [ ] **Step 4: Prove security and regression behavior**

Run:

```bash
python3 -m pytest -q tests/test_mobile_game_editor_state.py tests/test_direct_upload_server.py tests/test_security_contracts.py
python3 -m compileall -q web/direct_upload_server.py gsf_editor_v403.py
```

If exact existing filenames differ, select the current focused upload/security suites with `rg --files tests` and record the substituted commands in the execution log.

Expected: PASS; no CSRF/session test is changed or skipped.

- [ ] **Step 5: Commit the state contract**

```bash
git add tests/test_mobile_game_editor_state.py web/direct_upload_server.py
git commit -m "feat: expose mobile editor AI context"
```

## Task 3: Build a deterministic editor state, history, and save engine

**Files:**

- Create: `web/game_editor_mobile_component/editor_state.mjs`
- Create: `tests/js/mobile_game_editor_state.test.mjs`
- Modify: `web/game_editor_mobile_component/editor.mjs`
- Modify: `app.py`

- [ ] **Step 1: Write failing JavaScript unit tests**

Use Node's built-in test runner to specify:

- normalization/clamping for trim, zoom, pan, volume, text, quality, and duration;
- immutable commits with a 50-entry bounded undo/redo history;
- one history entry per completed gesture, not per pointer move;
- AI preview does not change state, Apply creates one reversible commit, and Revert/Undo restores the exact prior state;
- debounced saves use monotonically increasing sequences;
- stale acknowledgements cannot replace the latest saved sequence;
- `flush()` emits the newest state immediately before Continue.

Run:

```bash
node --test tests/js/mobile_game_editor_state.test.mjs
```

Expected: FAIL because the module does not exist.

- [ ] **Step 2: Implement the pure state module**

Export small DOM-free functions/classes for:

```text
normalizeEditorState(raw, duration)
createEditorHistory(initialState, limit)
clampViewport(viewport, bounds)
previewSuggestion(state, suggestion)
applySuggestion(state, suggestion, duration)
createSaveSequencer(send, delayMs)
```

No function may read the DOM, `localStorage`, or global Streamlit state. Preserve the server's editor keys and add `qualityMode` consistently.

- [ ] **Step 3: Implement the shell persistence protocol**

Handle `GSF_GAME_EDITOR_UI` actions in the existing shell owner:

- `autosave`: POST `/editor/state/save`, then return `GSF_GAME_EDITOR_SAVE_STATUS` with the same sequence;
- `save_draft`: flush editor state, wait for state-save success, then POST `/creator-hub/project/save-draft`;
- `continue_to_short`: perform the same save chain, close editor, then dispatch `GSF_SHELL_NAV {target: "short"}`;
- `close` and `fullscreen_changed`: update only overlay/fullscreen UI state.

Use the current session header/CSRF utilities. Never fall back to DOM label matching.

- [ ] **Step 4: Integrate the pure module into the component controller**

Create one controller state owner in `editor.mjs`. Bind the ready/init protocol, reducer/history, save sequencing, and live-region status. Reject cross-origin messages and ignore malformed or stale initialization.

- [ ] **Step 5: Run JS, bridge, and Python syntax tests**

Run:

```bash
node --test tests/js/mobile_game_editor_state.test.mjs
node --check web/game_editor_mobile_component/editor_state.mjs
node --check web/game_editor_mobile_component/editor.mjs
python3 -m pytest -q tests/test_mobile_game_editor_2026.py tests/test_mobile_game_editor_state.py
python3 -m compileall -q app.py
```

Expected: PASS.

- [ ] **Step 6: Commit the state engine**

```bash
git add web/game_editor_mobile_component/editor_state.mjs web/game_editor_mobile_component/editor.mjs tests/js/mobile_game_editor_state.test.mjs app.py
git commit -m "feat: add mobile editor state engine"
```

## Task 4: Build the premium mobile editing workspace

**Files:**

- Modify: `web/game_editor_mobile_component/index.html`
- Modify: `web/game_editor_mobile_component/editor.css`
- Modify: `web/game_editor_mobile_component/editor.mjs`
- Modify: `tests/test_mobile_game_editor_2026.py`

- [ ] **Step 1: Add failing structural and accessibility tests**

Assert the canonical component contains:

- compact header with project title, saved status, Undo/Redo, Save Draft, and Continue;
- central video preview and a single-clip professional timeline;
- five primary tools in this exact product order: Taglio, Inquadratura, Testo, Audio, AI;
- secondary controls under Altro, not competing with the five primary tools;
- semantic buttons/labels, live status, minimum 44px touch targets, safe-area handling, reduced-motion styling;
- no `MutationObserver`, `setInterval`, Streamlit rerun loop, canvas-poster replacement, or inline runtime patch markers.

Run:

```bash
python3 -m pytest -q tests/test_mobile_game_editor_2026.py
```

Expected: FAIL on the scaffold.

- [ ] **Step 2: Build the visual shell in the approved GSF language**

Implement the approved luminous premium mobile treatment using existing brand variables/patterns: dark graphite base, restrained cyan/violet light, crisp hierarchy, safe-area padding, and no redesign of other surfaces. Keep the preview visually dominant and avoid decorative animation that competes with gameplay.

- [ ] **Step 3: Implement the single-clip timeline and tool panels**

Provide:

- draggable playhead and trim handles with timecode readouts;
- event markers supplied by the init payload;
- Inquadratura controls for zoom/pan/reset;
- one editable text overlay with placement/style controls;
- source volume/mute and compact audio controls;
- Altro panel for quality mode and secondary clip settings.

All controls must commit through the state engine and schedule autosave. Do not create a second hidden state model in the DOM.

- [ ] **Step 4: Add media lifecycle and resilient empty/error states**

Load only the media URL supplied by the shell. Handle metadata-ready, absent media, decode error, and retry without page reload, polling, or rerun. Pause playback while trim boundaries are moved and clamp playback to the active range.

- [ ] **Step 5: Verify structure, syntax, and state behavior**

Run:

```bash
python3 -m pytest -q tests/test_mobile_game_editor_2026.py
node --test tests/js/mobile_game_editor_state.test.mjs
node --check web/game_editor_mobile_component/editor.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit the workspace**

```bash
git add web/game_editor_mobile_component tests/test_mobile_game_editor_2026.py
git commit -m "feat: build mobile game editor workspace"
```

## Task 5: Add fullscreen, real crop gestures, and explicit AI assistance

**Files:**

- Modify: `web/game_editor_mobile_component/index.html`
- Modify: `web/game_editor_mobile_component/editor.css`
- Modify: `web/game_editor_mobile_component/editor.mjs`
- Modify: `web/game_editor_mobile_component/editor_state.mjs`
- Modify: `tests/js/mobile_game_editor_state.test.mjs`
- Modify: `tests/visual/gsf_visual_check.py`

- [ ] **Step 1: Add failing browser scenarios**

Extend the WebKit mobile check to initialize the standalone component and verify:

- editor controls and timeline render without critical console errors;
- native fullscreen rejection activates shell fullscreen and emits `fullscreen_changed`;
- the Game Bar hide/show signal is paired correctly on enter/exit;
- pinch and pan visibly change the preview and persist the same normalized transform in emitted editor state;
- a cancelled pointer releases gesture/scroll state;
- selecting an AI card changes preview only, Apply changes state, and Undo restores it;
- empty AI context leaves manual tools functional and Apply disabled;
- Save Draft and Continue expose clear saving/error/retry states.

Run against a locally built/running container when possible:

```bash
python3 tests/visual/gsf_visual_check.py --base-url http://127.0.0.1:8080
```

Expected: FAIL because fullscreen, gestures, and AI cards are not implemented.

- [ ] **Step 2: Implement robust fullscreen ownership**

Attempt native fullscreen from a user gesture. If unavailable/rejected, enable a fixed shell-fullscreen class and notify the parent. In both modes, hide only the Game Bar, preserve the editor session, and restore focus/layout on exit. Listen for native `fullscreenchange` so browser chrome exits cannot leave stale state.

- [ ] **Step 3: Implement pointer-based pinch, pan, and crop**

Use Pointer Events with capture:

- one pointer pans when zoomed;
- two pointers compute scale around their midpoint;
- clamp zoom/pan so the crop never exposes invalid bounds;
- update CSS transforms during the gesture for responsive preview;
- commit one normalized `zoom/panX/panY` history entry on completion;
- handle `pointercancel`, lost capture, rotation, and fullscreen exit.

The committed transform is the render state saved to the backend, not a preview-only effect.

- [ ] **Step 4: Implement AI preview/apply/revert**

Render bounded suggestion cards from `ai_suggestions` with reason and impact. Selection shows a reversible visual diff. Apply creates exactly one history commit; Revert clears preview; Undo uses the common history stack. Never apply on initialization or selection.

- [ ] **Step 5: Run deterministic and WebKit tests**

Run:

```bash
node --test tests/js/mobile_game_editor_state.test.mjs
python3 -m pytest -q tests/test_mobile_game_editor_2026.py tests/test_mobile_game_editor_state.py
python3 tests/visual/gsf_visual_check.py --base-url http://127.0.0.1:8080
```

Expected: PASS, with screenshots/artifacts for the mobile editor and no critical console errors.

- [ ] **Step 6: Commit interaction behavior**

```bash
git add web/game_editor_mobile_component tests/js/mobile_game_editor_state.test.mjs tests/visual/gsf_visual_check.py
git commit -m "feat: add editor fullscreen gestures and AI assist"
```

## Task 6: Enforce canonical immutability and production readiness

**Files:**

- Modify: `tests/test_canonical_ui_pipeline.py`
- Modify: `web/runtime_smoke_v411.py`
- Modify: `.github/workflows/gsf-ci.yml`
- Modify: `.github/workflows/v397-production-gate.yml`
- Modify: `tests/visual/gsf_visual_check.py`
- Modify if required by existing manifest API: `tools/gsf_ui_manifest.py`

- [ ] **Step 1: Write the regression that forbids legacy mutation**

Add a canonical-pipeline test that fails if any build/startup/fix/apply script:

- writes into `web/game_editor_mobile_component/`;
- copies a replacement over that directory;
- references its files in a text `replace()`/append transform;
- materializes a different digest than the repository source.

Also assert the component remains covered by the existing UI manifest. Do not create a second manifest system.

Run:

```bash
python3 -m pytest -q tests/test_canonical_ui_pipeline.py
```

Expected: FAIL until the new source is added to the explicit protection/served-byte checks.

- [ ] **Step 2: Add route and asset checks to runtime smoke**

Verify `/game-editor-mobile/`, `editor.css`, `editor.mjs`, and `editor_state.mjs` return 200 with correct content types/security headers. Keep existing health, Creator Hub, session, and CSRF smoke assertions unchanged.

- [ ] **Step 3: Add JS and canonical checks to CI**

Run `node --test tests/js/mobile_game_editor_state.test.mjs` and `node --check` for both modules in the regular CI job. In Production Gate, compare the served component files byte-for-byte/digest-for-digest with the files copied into the frontend image.

- [ ] **Step 4: Run the complete relevant local verification**

Run:

```bash
python3 -m compileall -q app.py web gsf_editor_v403.py
node --test tests/js/mobile_game_editor_state.test.mjs
node --check web/game_editor_mobile_component/editor_state.mjs
node --check web/game_editor_mobile_component/editor.mjs
python3 -m pytest -q tests/test_mobile_game_editor_2026.py tests/test_mobile_game_editor_state.py tests/test_canonical_ui_pipeline.py tests/test_game_editor_v403.py
python3 -m pytest -q
```

Expected: PASS with no skipped security regression introduced by this branch.

- [ ] **Step 5: Build and inspect the production image**

Use the repository's documented production Docker command and start the image with the same required environment used by Production Gate. Verify:

```text
GET /healthz                         -> 200
GET /creator-hub/state              -> 200 with the valid runtime session contract
GET /game-editor-mobile/            -> 200
GET /game-editor-mobile/editor.css  -> 200
GET /game-editor-mobile/editor.mjs  -> 200
```

Compute and compare SHA-256 digests for every file in `web/game_editor_mobile_component/` across repository, image filesystem, and served response. Inspect container startup logs to prove no patch/materialization step touched the directory.

- [ ] **Step 6: Run the full mobile WebKit visual check against the container**

Verify Crea con IA → Editor → Crea Shorts, autosave, draft save, fullscreen fallback, gesture persistence, Game Bar visibility, no critical console errors, no abnormal navigation/rerun growth, and desktop `/editor-live/` still serving the unchanged component.

- [ ] **Step 7: Commit the gates**

```bash
git add tests/test_canonical_ui_pipeline.py web/runtime_smoke_v411.py .github/workflows/gsf-ci.yml .github/workflows/v397-production-gate.yml tests/visual/gsf_visual_check.py tools/gsf_ui_manifest.py
git commit -m "test: gate canonical mobile game editor"
```

Only add `tools/gsf_ui_manifest.py` if the existing recursive manifest does not already cover the new directory.

## Task 7: Prepare the PR for publication

**Files:**

- Modify only if execution evidence requires it: `docs/superpowers/plans/2026-10-15-mobile-game-editor-2026.md`

- [ ] **Step 1: Reconcile current main and re-run verification**

Fetch `origin/main`, inspect changes since the implementation base, and merge/rebase using the repository policy without discarding concurrent work. Re-run all Task 6 checks after reconciliation.

- [ ] **Step 2: Verify the final diff is scoped**

Confirm:

- no changes to `web/editor_2027_component/`;
- no new runtime patch/migration;
- no AI worker or video-render pipeline changes;
- no CSRF/session relaxation;
- all new mobile assets are canonical and manifest-covered;
- untracked or unrelated user files are absent from the commit.

Run:

```bash
git status --short
git diff --check origin/main...HEAD
git diff --stat origin/main...HEAD
```

- [ ] **Step 3: Push and open the PR**

Use a PR title such as:

```text
feat: introduce canonical mobile Game Editor 2026
```

The PR body must include the approved spec, exact test commands/results, screenshots, container digests, desktop non-regression evidence, and explicit note that it is prepared for publication but not yet merged/deployed.

- [ ] **Step 4: Obtain green publication gates**

Wait for CI, Production Gate, and the WebKit visual workflow. Diagnose and fix real failures through another RED/GREEN cycle; do not rerun blindly, weaken tests, or bypass security.

- [ ] **Step 5: Stop at publication-ready state**

Report branch SHA, PR number/URL, required checks and run URLs, image/served component digest, and any remaining approval needed. Do not merge or deploy from this plan unless the user separately authorizes publication.

## Done Criteria

This implementation is ready for publication only when:

- the mobile Crea con IA → Editor → Crea Shorts flow uses explicit named contracts;
- the mobile editor provides working trim, timeline, framing, text, audio, AI, undo/redo, autosave, Save Draft, Continue, fullscreen, and render-persisted pinch/crop;
- the desktop editor source and behavior are unchanged;
- repository, image, and served mobile component digests match;
- legacy build/startup transforms cannot write the new component and CI proves it;
- focused tests, full pytest, Docker startup, health/session/CSRF smoke, and WebKit checks pass;
- the PR's required publication gates are green.
