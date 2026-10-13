# V402 Game Brain / Auto Highlights 2.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, lightweight signal-fusion layer that enriches existing Auto Highlights evidence with gameplay, semantic, diagnostics-derived visual/reaction cues and optional visual/audio observations before the existing Game Brain performs final ranking.

**Architecture:** Create one pure `highlight_fusion_v402` module with no I/O or model calls. `auto_highlights.engine_v129.analysis_to_candidates()` will call it best-effort, build the pool from fused evidence, and continue delegating final selection to `game_brain_v112.rerank_moments()`. Existing V129 metadata-first persistence, V400 render/editor behavior, and V401 performance/recovery remain unchanged.

**Tech Stack:** Python 3.12, existing GSF Game Brain V112/V127 learning stack, Auto Highlights V129, existing diagnostics/event maps, optional V144-style visual observations, GitHub Actions, Docker worker/production images, Railway.

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
- Duplicate same-event peaks close in time: collapse the weaker duplicate without deleting distinct meaningful events that merely share a category.
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

Pin these behaviors: multi-signal kill outranks an equivalent plain kill; clutch/multi-kill priority survives; missing audio/visual is neutral; malformed optional rows are ignored; SILENCE/dead-air cannot become a top candidate; duplicate same-event peaks collapse to the stronger representative; identical inputs produce identical score/reason/order; non-finite/extreme values never escape as non-finite output.

- [ ] **Step 2: Write failing integration expectations**

Using `analysis_to_candidates()` require:

- `meta["fusion"]["engine"] == "highlight-fusion-v402"`;
- `meta["fusion"]["fallback"] is False` on normal input;
- every selected `game_brain.selected` row can expose `fusion_reason`, `fusion_signals`, `fusion_score` and `fusion_confidence` matched to its selected event evidence;
- 15-second requests yield exactly 15-second candidates and 30-second requests exactly 30 seconds;
- near-duplicate peaks do not crowd out a close-quality reaction/victory alternative;
- requesting more highlights than valid events returns only available real candidates.

Monkeypatch `auto_highlights.engine_v129.fuse_highlight_evidence` to raise and require the original V129 event path to continue with `fusion.fallback == true` and a bounded diagnostic reason.

- [ ] **Step 3: Run the test and verify RED for the intended reason**

Run: `PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py`

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
- Output rows preserve source fields and add `fusion_score`, `fusion_confidence`, `fusion_signals`, `fusion_reason`, `fusion_version`, `peak_time`, `lead_seconds`, `aftermath_seconds`.

- [ ] **Step 1: Implement finite normalization helpers**

Accept arbitrary values and return finite floats/lists only; ignore non-dict observations. Do not import numpy, PIL, boto3, ffmpeg or provider SDKs.

- [ ] **Step 2: Implement nearest-evidence lookup**

For each valid event time, consume event fields first, then nearest compatible diagnostics/optional observations inside a bounded window derived from `target_duration`. Current diagnostics must contribute immediately through `features` keys including `motion_burst`, `motion_avg`, `reaction`, `reaction_cue`, `event_score`, `synergy`, `dead_ratio`, `arc`, `setup_score` and `aftermath_score`. Optional future observation lists are additive, not required.

- [ ] **Step 3: Implement bounded fusion scoring**

Keep source `score`/semantic fields intact. Calculate `fusion_score` in `[0,1]` from only available families, so absent families add neither reward nor penalty. Preserve established semantic priority for `clutch`, `multi_kill`, `victory`, `goal` and related high-value events; apply bounded negative evidence only for explicit dead/silence/very-low-quality signals.

- [ ] **Step 4: Implement synergy, confidence and explanation**

Reward corroboration across independent families. Produce deterministic signal ordering and a stable explanation such as `CLUTCH · Killfeed · Reaction · High Action`. Confidence must represent evidence agreement, not optional-source availability.

- [ ] **Step 5: Implement peak hints and same-peak dedupe**

Preserve source `time`; set `peak_time`; compute lead/aftermath hints whose sum does not exceed requested duration. Collapse only near-identical same-semantic peaks; preserve distant kills and distinct semantic events.

- [ ] **Step 6: Run direct contract**

Run:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
python -m py_compile web/highlight_fusion_v402.py
```

Expected: direct fusion assertions GREEN; integration assertions still RED until Task 3.

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
- Produces: existing `analysis_to_candidates(...) -> (candidates, meta)` with additional `meta["fusion"]` diagnostics and selected-fusion metadata while preserving the candidate dataclass/API.

- [ ] **Step 1: Call V402 best-effort**

Read current events/diagnostics exactly as today. Accept optional payload lists only from:

```python
visual_observations = scan.get("visual_observations") or payload.get("visual_observations") or []
audio_observations = scan.get("audio_observations") or payload.get("audio_observations") or []
```

Call fusion inside a narrow `try/except Exception`. On failure, use original events and return `engine="highlight-fusion-v402"`, `fallback=True`, and a sanitized error type/message capped to 180 characters.

- [ ] **Step 2: Make `_event_pool()` consume fused evidence**

Keep current base/semantic terms and add `fusion_score` as another maximum evidence term. Continue skipping SILENCE, invalid times and non-positive evidence. Use fused `lead_seconds` when available; otherwise retain V129 lead logic.

- [ ] **Step 3: Pass fused events into unchanged Game Brain**

Call existing `rerank_moments(...)` with fused events. Do not edit `game_brain_v112.py` unless a failing regression proves a narrowly scoped compatibility defect.

- [ ] **Step 4: Attach selected fusion explanation after Game Brain returns**

Match each `brain["selected"]` row to the nearest fused event using `event_time` (fall back to selected start + duration center only if event_time is absent). Add `fusion_reason`, `fusion_signals`, `fusion_score`, `fusion_confidence` to that selected metadata row. Preserve existing `reason`, `event`, `confidence`, `director_plan`, candidate dataclass, `candidate_dict()`, worker endpoint fields and stored candidate schema.

- [ ] **Step 5: Preserve top-level metadata compatibility**

Keep `engine="auto-highlights-v129"`, raw `event_count`, `pool_size`, `selected_count`, and `game_brain`; add `fusion` metadata containing raw/fused/deduped counts, signal-family counts and fallback state.

- [ ] **Step 6: Verify integration and syntax**

Run:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
python -m py_compile web/highlight_fusion_v402.py web/auto_highlights/engine_v129.py web/game_brain_v112.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

Commit message: `feat(v402): fuse evidence before Game Brain ranking`

---

### Task 4: Add V402 CI, worker-image contract and documentation

**Files:**
- Create: `.github/workflows/v402-game-brain-auto-highlights-tdd.yml`
- Modify: `web/Dockerfile.worker`
- Modify: `docs/AUTO_HIGHLIGHTS.md`

**Interfaces:**
- Consumes: Tasks 1-3.
- Produces: branch/PR gate that verifies V402, V400/V401 safety and the actual worker image serving `/auto-highlights`.

- [ ] **Step 1: Add V402 branch/PR workflow**

Trigger pushes to `v402-game-brain-auto-highlights-2` and pull requests to `main`. Run on Python 3.12:

```bash
PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py
PYTHONPATH=web python web/test_v400_ai_hidpi.py
PYTHONPATH=web python web/test_v401_performance_stability.py
python -m py_compile web/highlight_fusion_v402.py web/auto_highlights/engine_v129.py web/game_brain_v112.py
```

Then build the real worker image:

```bash
docker build --progress=plain -f web/Dockerfile.worker -t gsf-worker-v402:${{ github.sha }} .
```

- [ ] **Step 2: Bake V402 contract into worker Docker build**

After the existing V129 contract, add:

```bash
python /app/web/test_v402_game_brain_auto_highlights.py
python -m py_compile /app/web/highlight_fusion_v402.py
```

Do not change worker command, semaphore slots, V401 patch application, requirements or resource policy. The existing worker build continues to execute `test_v129_auto_highlights.py`, so V129 remains a blocking regression.

- [ ] **Step 3: Use the production image as the canonical V112/editor regression environment**

Do not try to run V112/editor contracts in the worker image: `web/Dockerfile.worker` intentionally stops its historical app patch chain at V99. The root production `Dockerfile` already applies V112 and runs `test_v112_game_brain.py` against `/app/GamingShortsFactory_V112_GAME_BRAIN.py`, then repeatedly runs `test_editor_2027_component.py` through later production versions. Therefore the PR's existing V397 Production Gate is the exact blocking environment for the original V112/editor regressions. Do not weaken or remove those Dockerfile assertions.

- [ ] **Step 4: Document V402**

Append a `V402 signal fusion` section to `docs/AUTO_HIGHLIGHTS.md`: raw/local/semantic/diagnostics evidence is fused before Game Brain; Game Brain remains final authority; scan-first/no-eager-render stays unchanged.

- [ ] **Step 5: Observe branch CI**

Expected: V402 contract PASS, V400/V401 PASS, worker build (including V129 + V402) PASS.

- [ ] **Step 6: Commit**

Commit message: `ci(v402): gate signal fusion and worker image`

---

### Task 5: Review, PR, production gate, merge and Railway verification

**Files:**
- No product changes unless a verified failing regression requires a narrowly scoped V402 fix.

**Interfaces:**
- Consumes: fully green V402 branch.
- Produces: one reviewed V402 production release, or leaves V401 untouched on any failure.

- [ ] **Step 1: Compare complete branch against V401**

Compare `1c6d47a42a040b6e2342b4e2cd1a8e823592e315...v402-game-brain-auto-highlights-2`. Changed product files must be limited to fusion/Auto Highlights/worker verification/docs/workflow. Reject unexplained Home, Creator Hub, Game Bar, editor component, render-quality or V401 persistence changes.

- [ ] **Step 2: Open PR to `main`**

State explicitly: Game Brain remains final ranker; no eager render/full-VOD copy; V400/V401 unchanged; fusion failure falls back to V129 behavior.

- [ ] **Step 3: Require all branch checks plus V397 Production Gate GREEN**

Do not merge while any check is queued/in progress/failed. The Production Gate must complete root production-image build (which itself runs original V112/editor contracts), startup, composite health, runtime smoke and current UI contracts.

- [ ] **Step 4: Merge and record exact `main` SHA only after GREEN**

On any failure, diagnose/fix on V402 and keep V401 live.

- [ ] **Step 5: Verify Railway exact merged SHA**

Require frontend `gaming-shorts-factory-v79` and `gsf-ai-worker` to settle on the exact merged SHA with healthy deployment state, 0 crashed replicas, zero new warnings/criticals/failures and `pendingWork=[]`.

- [ ] **Step 6: Final report**

Report V402 merge SHA, GitHub gate results, Railway frontend/worker deployment IDs and capabilities verified. Keep V401 identified as rollback point.

---

## Self-review result

- Spec coverage: signal families, neutrality, synergy, explainability, dedupe, peak hints, fallback, exact duration and metadata propagation are owned by Tasks 1-3.
- Boundary clarity: fusion module normalizes evidence; V129 integrates it; Game Brain remains final ranker; CI/Docker owns release verification.
- Type consistency: the public fusion signature is identical in spec, tests and integration.
- Selected explainability: fusion evidence is mapped back onto every `game_brain.selected` row without changing the legacy candidate schema.
- Performance: no network/model/media work is added to fusion and worker dependencies remain unchanged.
- Compatibility: V112/editor regressions run in the root production Dockerfile, their canonical environment; V400/V401 run in V402 branch CI; V129 + V402 run inside the real worker build.
- Review-focus coverage: malformed rows, missing optional families, duplicates, non-finite values and undersupplied candidate sets are explicitly pinned in Task 1.
