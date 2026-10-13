# V397 AI Monument + Quality Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AI a persistent assistant across touch editing and rendering while tightening final Short quality and improving Editor visual legibility without destabilizing the locked Home/global shell.

**Architecture:** Add a small pure-policy AI layer that turns editor/director context into render and touch-assist decisions. Wire it into the existing Editor and Director pipeline, then add a restart-safe Editor asset migration for the persistent AI control and touch gestures. Strengthen final-output inspection around the canonical 1080x1920/60fps H.264 High/yuv420p/AAC target.

**Tech Stack:** Python, Streamlit custom component HTML/JS/CSS, FFmpeg/ffprobe, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-13-v397-structural-hardening.md` plus the 2026-10-13 user requirement that AI assist creation, touch editing, rendering, final quality and graphic quality.

## Global Constraints

- Work only on `v397-structural-hardening`; V396 live must remain untouched.
- Preserve 9:16 canonical output at 1080x1920, 60 fps, H.264 High, AAC.
- Preserve quality before adding effects; AI may drop nonessential effects under pressure, not output quality.
- Touch gestures must never replace Undo/Redo or manual controls.
- Do not alter the locked Home/global shell geometry for this feature.
- Full V397 Production Gate must remain the final acceptance gate.

## Review Focus

- Saved/manual Editor state must not be silently overwritten by AI defaults.
- Pinch/pan must remain bounded and must not steal touches from controls outside the video stage.
- High worker pressure must reduce optional AI passes rather than resolution/fps/codec quality.
- Final quality inspection must tolerate 59.94/60 fps but reject non-canonical dimensions.
- Restarting the container must not duplicate the AI monument or touch handlers.

---

### Task 1: AI render/touch policy

**Files:**
- Create: `web/ai_monument_v397.py`
- Create: `web/test_v397_ai_monument.py`

**Interfaces:**
- Produces: `build_render_policy(load_ratio=0.0, ai_operations=None) -> dict`, `enhance_editor_kwargs(kwargs, state) -> dict`, `quality_actions(report) -> list[dict]`.

- [ ] Write the failing contract test for canonical quality, load-aware pass limits, Auto Gaming assistance and quality remediation.
- [ ] Run it and verify RED because `ai_monument_v397.py` is absent.
- [ ] Implement the pure policy module.
- [ ] Run the contract and verify GREEN.

### Task 2: Wire AI into Editor and Director render

**Files:**
- Modify: `web/editor_2027_embed.py`
- Modify: `web/director_pipeline_v142.py`
- Modify: `web/director_render_exec_v143.py`
- Test: `web/test_v397_ai_monument.py`

**Interfaces:**
- Consumes: Task 1 policy helpers.
- Produces: recipe metadata `ai_render_policy`; render execution honors `max_ai_reencodes` while preserving canonical output settings.

- [ ] Add failing integration assertions to the Task 1 contract.
- [ ] Verify RED.
- [ ] Wire Auto Gaming to smart reframe/audio polish and attach adaptive render policy to recipes.
- [ ] Bound optional Director re-encodes using policy priority.
- [ ] Verify GREEN and run existing V139/V143-related contracts.

### Task 3: Touch-first AI monument and visual polish

**Files:**
- Create: `web/fix_v397_ai_monument.py`
- Modify: `web/start_web.sh`
- Test: `web/test_v397_ai_monument.py`

**Interfaces:**
- Produces: restart-safe `__GSF_AI_MONUMENT_V397` asset marker, persistent AI control, one-finger pan, pinch zoom, double-tap AI framing, improved small-label legibility.

- [ ] Add failing asset/startup assertions.
- [ ] Verify RED.
- [ ] Implement idempotent HTML/CSS/JS injection scoped to `#ng27` and the video stage.
- [ ] Add startup migration before Streamlit launch.
- [ ] Verify GREEN twice to prove restart idempotency.

### Task 4: Final Short quality gate

**Files:**
- Modify: `web/quality_control_v124.py`
- Test: `web/test_v397_ai_monument.py`

**Interfaces:**
- Produces: canonical-target facts plus explainable remediation actions consumed by the AI policy.

- [ ] Add failing assertions for canonical dimensions, fps tolerance, pixel format/profile/audio facts and remediation.
- [ ] Verify RED.
- [ ] Extend inspection without weakening existing broken-file checks.
- [ ] Verify GREEN.

### Task 5: CI and production verification

**Files:**
- Modify: `.github/workflows/v397-branch-tdd.yml`

- [ ] Run the new V397 AI contract automatically on branch pushes.
- [ ] Run the branch TDD gate.
- [ ] Run the full V397 Production Gate and fix any first failing real contract without bypasses.
- [ ] Verify final branch SHA, successful run ID, required jobs green, and V396 untouched.
