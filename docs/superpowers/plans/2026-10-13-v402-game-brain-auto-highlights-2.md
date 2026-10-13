# V402 Game Brain / Auto Highlights 2.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, lightweight signal-fusion layer that enriches existing Auto Highlights evidence with gameplay, semantic, diagnostics-derived visual/reaction cues and optional visual/audio observations before the existing Game Brain performs final ranking.

**Architecture:** Create one pure `highlight_fusion_v402` module with no I/O or model calls. `auto_highlights.engine_v129.analysis_to_candidates()` will call it best-effort, build the pool from fused evidence, and continue delegating final selection to `game_brain_v112.rerank_moments()`. Existing V129 metadata-first persistence, V400 render/editor behavior, and V401 performance/recovery remain unchanged.

**Tech Stack:** Python 3.12, existing GSF Game Brain V112/V127 learning stack, Auto Highlights V129, existing diagnostics/event maps, optional V144-style visual observations, GitHub Actions, Docker worker image, Railway.

**Spec:** `docs/superpowers/specs/2026-10-13-v402-game-brain-auto-highlights-2-design.md`

## Global Constraints

- Baseline is V401 production commit `1c6d47a42a040b6e2342b4e2cd1a8e823592e315`.
- Game Brain remains the final ranking/diversity/Director authority; V402 must not add a second ranker.
- Keep Editor 2027 component identity exactly `gsf_editor_2027_v1086`.
- Keep the V400 1080x1920, 60 fps, libx264 medium Adaptive AI quality contract unchanged.
- Keep V401 bounded upload streaming, persistent job-state and restart recovery unchanged.
- No Home, Creator Hub, Game Bar, Editor UI or share-surface visual changes.
- No network calls, video decode, model downloads, persistence, full-VOD materialization or eager rendering in the fusion layer.
- Missing optional signal families are neutral; malformed optional rows are ignored rather than failing the scan.
- Fusion must be deterministic for identical inputs and use finite bounded numeric output.
- Existing V129 no-events behavior and metadata-first `rendered_media=[]` architecture remain intact.

## Review Focus

- Malformed/non-dict visual or audio observations: ignore them and still produce candidates from valid event/diagnostic evidence.
- Missing all optional visual/audio evidence: preserve a valid V129/Game Brain path instead of depressing scores simply because data is absent.
- Duplicate same-event peaks close in time: collapse/mark the weaker duplicate without deleting distinct meaningful events that merely share a category.
- NaN, infinity, strings and extreme numeric inputs: clamp or ignore them so no non-finite `fusion_score`, confidence or ordering value can escape.
- Fewer meaningful events than requested highlights: return the available candidates without fabricating filler or failing the job.

---

### Task 1: Lock the V402 behavior with a RED contract

**Files:**
- Create: `web/test_v402_game_brain_auto_highlights.py`

**Interfaces:**
- Consumes: current V401/V129/V112 behavior.
- Produces: executable V402 contract that imports `fuse_highlight_evidence(...)` and exercises direct fusion plus Auto Highlights integration expectations.

- [ ] **Step 1: Write the failing direct-fusion tests**

Use deterministic fixtures and assert:

```python
from highlight_fusion_v402 import fuse_highlight_evidence

fused, meta = fuse_highlight_evidence(
    events,
    diagnostics=diagnostics,
    visual_observations=visual,
    audio_observations=audio,
    target_duration=30,
    genre="FPS",
)
assert all(row.get("fusion_version") == "v402" for row in fused)
assert all(0.0 <= float(row["fusion_score"]) <= 1.0 for row in fused)
assert all(0.0 <= float(row["fusion_confidence"]) <= 1.0 for row in fused)
```

The fixture set must pin these behaviors:

- multi-signal `kill + high action + reaction + killfeed` scores above an otherwise equivalent plain kill;
- clutch/multi-kill semantic priority survives fusion;
- missing audio is neutral;
- missing visual evidence is neutral;
- malformed optional rows are ignored;
- SILENCE/dead-air cannot become a top fused candidate;
- duplicate same-event peaks inside the dedupe window do not both survive when a stronger representative exists;
- identical inputs produce identical score/reason/order;
- NaN/infinite/extreme values do not escape as non-finite output.

- [ ] **Step 2: Write failing integration expectations**

Using `analysis_to_candidates()` require:

- returned metadata contains `fusion.engine == "highlight-fusion-v402"`;
- `fusion.fallback` is false on normal input;
- 15-second requests yield exactly 15-second `HighlightCandidate.duration`;
- 30-second requests yield exactly 30-second duration;
- near-duplicate peaks do not crowd out a close-quality reaction/victory alternative;
- requesting more highlights than valid events returns only the available real candidates.

Add a test-only monkeypatch/stub of `auto_highlights.engine_v129.fuse_highlight_evidence` that raises, then require `analysis_to_candidates()` to continue on the original V129 events and expose `fusion.fallback == true` with a bounded diagnostic reason.

- [ ] **Step 3: Run the test and verify RED for the intended reason**

Run:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'highlight_fusion_v402'` before product code exists.

- [ ] **Step 4: Commit RED contract only**

Commit message: `test(v402): define signal fusion contract`

---

### Task 2: Implement the pure V402 signal-fusion layer

**Files:**
- Create: `web/highlight_fusion_v402.py`
- Test: `web/test_v402_game_brain_auto_highlights.py`

**Interfaces:**
- Consumes: event rows, existing diagnostics dictionaries, optional time-stamped visual/audio observation rows.
- Produces: `fuse_highlight_evidence(events, diagnostics=None, visual_observations=None, audio_observations=None, target_duration=30, genre="Auto") -> tuple[list[dict], dict]`.
- Output event rows preserve source fields and add `fusion_score`, `fusion_confidence`, `fusion_signals`, `fusion_reason`, `fusion_version`, plus bounded peak/window hints.

- [ ] **Step 1: Implement finite numeric and row normalization helpers**

Define internal helpers that accept arbitrary values and return finite floats/lists only. Reject non-dict observations. Do not import numpy, PIL, boto3, ffmpeg or provider SDKs.

- [ ] **Step 2: Implement nearest-evidence lookup**

For each valid event time, use existing event fields first, then the nearest compatible diagnostics/visual/audio evidence inside a bounded window derived from `target_duration`. Diagnostics must contribute immediately using current `features` keys such as `motion_burst`, `motion_avg`, `reaction`, `reaction_cue`, `event_score`, `synergy`, `dead_ratio`, `arc`, `setup_score` and `aftermath_score`; optional future observation lists are additive, not required.

- [ ] **Step 3: Implement bounded fusion scoring**

Keep source `score`/semantic fields intact. Calculate one bounded `[0,1]` `fusion_score` from available families only, so absent families contribute zero weight and zero penalty. Preserve established high-value semantic ordering for events such as `clutch`, `multi_kill`, `victory` and `goal`; apply only bounded penalties for explicit dead/silence/very-low-quality evidence.

- [ ] **Step 4: Implement synergy, confidence and explanation**

Reward corroboration when two or more independent signal families are strong. Produce deterministic `fusion_signals` ordering and stable `fusion_reason` such as `CLUTCH · Killfeed · Reaction · High Action`. Confidence must depend on evidence agreement/quality, not on missing optional sources.

- [ ] **Step 5: Implement peak/window hints and same-peak dedupe**

Preserve the original event `time`, set `peak_time` from the decisive evidence, and compute `lead_seconds` + `aftermath_seconds` whose sum does not exceed the requested clip duration. Collapse only near-identical same-event evidence around the same peak; do not collapse distant kills or different semantic events.

- [ ] **Step 6: Run the direct V402 contract**

Run:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
python -m py_compile web/highlight_fusion_v402.py
```

Expected: direct fusion assertions GREEN; integration assertions may still fail because V129 is not wired yet.

- [ ] **Step 7: Commit**

Commit message: `feat(v402): add deterministic highlight signal fusion`

---

### Task 3: Integrate fusion into V129 without replacing Game Brain

**Files:**
- Modify: `web/auto_highlights/engine_v129.py`
- Test: `web/test_v402_game_brain_auto_highlights.py`
- Regression: `web/test_v129_auto_highlights.py`
- Regression: `web/test_v112_game_brain.py`

**Interfaces:**
- Consumes: `fuse_highlight_evidence(...)` from Task 2.
- Produces: existing `analysis_to_candidates(...) -> (candidates, meta)` with additional `meta["fusion"]` diagnostics while preserving the candidate dataclass/API.

- [ ] **Step 1: Import and call the V402 fusion layer best-effort**

In `analysis_to_candidates()` read current `event_map_v108` and diagnostics exactly as today. Also accept optional lists only from these explicit payload fields when present:

```python
visual_observations = scan.get("visual_observations") or payload.get("visual_observations") or []
audio_observations = scan.get("audio_observations") or payload.get("audio_observations") or []
```

Call `fuse_highlight_evidence(...)` inside a narrow `try/except Exception` boundary. On exception, use the original event list and return fusion metadata with `engine="highlight-fusion-v402"`, `fallback=True`, and a sanitized error type/message capped to 180 characters.

- [ ] **Step 2: Make `_event_pool()` consume fused evidence**

Keep current semantic/base score terms and add `fusion_score` as another maximum candidate-evidence term when present. Continue skipping `SILENCE`, invalid times and non-positive evidence. If V402 provides `lead_seconds`, use it to anchor the pool start; otherwise keep the current V129 lead calculation.

- [ ] **Step 3: Pass fused events into unchanged Game Brain final ranking**

Call existing `rerank_moments(...)` with the fused event list. Do not change `game_brain_v112.py` unless a failing regression proves a V402-scoped compatibility defect.

- [ ] **Step 4: Surface fusion metadata without breaking existing metadata**

Preserve `engine="auto-highlights-v129"`, `game_brain`, `event_count`, `pool_size`, and `selected_count`; add `fusion` metadata. Do not change `HighlightCandidate`, `candidate_dict()`, worker endpoint fields or persistence format required by V129.

- [ ] **Step 5: Verify V402 integration**

Run:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
```

Expected: PASS.

- [ ] **Step 6: Verify legacy Auto Highlights/Game Brain in the worker image context**

Because legacy tests reference `/app/...`, use the real worker image as their canonical environment in Task 4. At source level, run syntax now:

```bash
python -m py_compile web/highlight_fusion_v402.py web/auto_highlights/engine_v129.py web/game_brain_v112.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

Commit message: `feat(v402): fuse evidence before Game Brain ranking`

---

### Task 4: Add V402 CI, worker-image contract and regression gate

**Files:**
- Create: `.github/workflows/v402-game-brain-auto-highlights-tdd.yml`
- Modify: `web/Dockerfile.worker`
- Modify: `docs/AUTO_HIGHLIGHTS.md`

**Interfaces:**
- Consumes: Tasks 1-3.
- Produces: branch/PR gate that verifies V402, V400/V401 safety and the actual worker image that serves `/auto-highlights`.

- [ ] **Step 1: Add V402 branch/PR workflow**

Trigger on pushes to `v402-game-brain-auto-highlights-2` and pull requests to `main`. The workflow must run on Python 3.12 and include these host-safe commands:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
PYTHONPATH=web python web/test_v144_visual_scoring.py
PYTHONPATH=web python web/test_v400_ai_hidpi.py
PYTHONPATH=web python web/test_v401_performance_stability.py
python -m py_compile web/highlight_fusion_v402.py web/auto_highlights/engine_v129.py web/game_brain_v112.py
```

Then build the real worker image:

```bash
docker build --progress=plain -f web/Dockerfile.worker -t gsf-worker-v402:${{ github.sha }} .
```

- [ ] **Step 2: Bake V402 contract into worker Docker build**

In the existing Docker `RUN` verification chain, after the existing V129 contract and before final py_compile, add:

```bash
python /app/web/test_v402_game_brain_auto_highlights.py
python -m py_compile /app/web/highlight_fusion_v402.py
```

Do not change worker runtime command, semaphore slots, V401 patch application, requirements or resource policy.

- [ ] **Step 3: Verify V129 and V112 inside the built worker image**

The V129 test is already executed during Docker build. After build, execute:

```bash
docker run --rm --entrypoint python gsf-worker-v402:${{ github.sha }} /app/web/test_v112_game_brain.py /app/GamingShortsFactory_V112_GAME_BRAIN.py
```

If the historical generated filename differs in the built image, use the exact generated app path that the existing patch chain produced; do not weaken V112 assertions. Also run:

```bash
docker run --rm --entrypoint python gsf-worker-v402:${{ github.sha }} /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V107_PRODUCTION_UI.py
```

If the worker image does not contain the editor-generated production filename required by that legacy test, move the editor invariant check to the production-image V397 gate rather than altering the test. The non-negotiable invariant is that `gsf_editor_2027_v1086` remains present and the existing editor contract passes in its canonical production image.

- [ ] **Step 4: Document V402 in Auto Highlights docs**

Append a short `V402 signal fusion` section stating that raw/local/semantic/diagnostics evidence is fused before Game Brain, the ranking authority remains Game Brain, and the architecture remains scan-first/no eager render.

- [ ] **Step 5: Run/observe branch CI**

Expected: V402 workflow PASS, worker image build PASS, V400/V401 regressions PASS.

- [ ] **Step 6: Commit**

Commit message: `ci(v402): gate signal fusion and worker image`

---

### Task 5: Review, PR, production gate, merge and Railway verification

**Files:**
- No product files unless a failing verified regression requires a narrowly scoped V402 fix.

**Interfaces:**
- Consumes: fully green V402 branch.
- Produces: one reviewed V402 production release or leaves V401 untouched if any gate fails.

- [ ] **Step 1: Compare the complete branch against V401**

Run repository compare `1c6d47a42a040b6e2342b4e2cd1a8e823592e315...v402-game-brain-auto-highlights-2` and require that changed product files are limited to V402 fusion/Auto Highlights/worker verification/docs/workflow. Any Home, Creator Hub, Game Bar, editor component, render-quality or V401 persistence change must be explained and rejected unless a concrete failing test requires it.

- [ ] **Step 2: Open a PR to `main`**

PR summary must explicitly state:

- Game Brain remains final ranker;
- no eager render/full-VOD copy;
- V400 and V401 contracts remain unchanged;
- V402 fallback returns original V129 behavior on fusion failure.

- [ ] **Step 3: Require branch checks and V397 Production Gate GREEN**

Do not merge while any workflow is queued, in progress or failed. The V397 production image gate must complete build, startup, composite health, runtime smoke and current UI contracts.

- [ ] **Step 4: Merge only after all checks pass**

Record the exact resulting `main` commit SHA. If a gate fails, diagnose/fix on the V402 branch and keep V401 production live.

- [ ] **Step 5: Verify Railway deploys the exact merged SHA**

Require both services to settle:

- frontend `gaming-shorts-factory-v79`: deployment `SUCCESS`, 1/1 running, 0 crashed;
- `gsf-ai-worker`: deployment `SUCCESS` or healthy settled state expected by its configuration;
- zero critical/warnings, zero new failed deployments, `pendingWork=[]`.

- [ ] **Step 6: Inspect logs if Railway reports any issue**

Do not call V402 live if the commit differs, a service is still building/deploying, or there is a new crash/failure.

- [ ] **Step 7: Final release report**

Report the V402 merge commit, GitHub gate results, Railway frontend/worker deployment IDs and the specific V402 capabilities verified. Keep V401 identified as rollback point.

---

## Self-review checklist for execution

- Spec coverage: all required signal families, neutrality of missing evidence, synergy, explainability, dedupe, peak hints, fallback, exact duration and metadata propagation are owned by Tasks 1-3.
- Boundary clarity: `highlight_fusion_v402.py` is pure evidence normalization; `engine_v129.py` integrates it; `game_brain_v112.py` stays final ranker; Docker/CI owns release verification.
- Type consistency: the single public fusion signature is identical in spec, tests and integration.
- Performance: no task adds network/model/media work to fusion; worker image dependency list remains unchanged.
- Compatibility: no task requires a UI/editor/render-quality/V401 state change; those areas are regression-only.
- Review-focus coverage: malformed rows, missing optional families, duplicates, non-finite values and undersupplied candidate sets are all explicitly tested in Task 1.
