# V372 Primary Routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore Crea con IA, Game Editor, and Crea Short from the Home while preserving the currently working Creator Hub unchanged.

**Architecture:** Keep V343 as the single parent navigation owner. Validate the executable V343 bridge at the final generated V293 runtime stage, reproduce the broken route behavior in an isolated Railway service, then patch only the final primary-route bridge and add a final-stage regression gate. Do not modify Creator Hub HTML or Hub patch files.

**Tech Stack:** Python, Streamlit components, embedded JavaScript, Railway, GitHub.

**Spec:** User request in the current conversation.

## Global Constraints

- Creator Hub must remain unchanged and working.
- V372 is not complete until the final runtime regression passes and Railway deployment is successful.
- Scope is only Crea con IA, Game Editor, and Crea Short.
- V343 remains the single navigation owner; no new competing global router.

## Review Focus

- Home postMessage reaches the V343 owner for `ai`, `editor`, and `short`.
- Each target opens exactly its intended surface and closes competing non-Hub surfaces.
- Editor lazy-loads `/editor-live/` before becoming visible.
- Short opens the V343 Short surface rather than invoking render directly.
- No file under `web/creator_hub_v156_component/` is modified.

---

### Task 1: Final-runtime failing regression

**Files:**
- Create: `web/test_v372_primary_routes_runtime.py`
- Modify: `web/start_web.sh`

**Interfaces:**
- Consumes: final `GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py` executable V343 bridge.
- Produces: a regression gate that fails on the current broken route contract.

- [ ] Write the final-runtime test first.
- [ ] Run it in an isolated Railway deployment and confirm RED for the broken primary-route contract.
- [ ] Capture the exact failing route/bridge evidence.

### Task 2: Minimal V372 route repair

**Files:**
- Create: `web/fix_v372_primary_routes_runtime.py`
- Modify: `web/start_web.sh`

**Interfaces:**
- Consumes: V343 executable bridge extracted from final V293 runtime.
- Produces: one canonical route handler for `ai`, `editor`, and `short`, without changing Hub routing.

- [ ] Patch only the executable V343 bridge after all existing runtime generators have run.
- [ ] Make the patch idempotent/restart-safe.
- [ ] Run V372 test and existing V343/V370 route-related gates until GREEN.

### Task 3: Isolated deploy and promotion

**Files:** none beyond Tasks 1-2.

- [ ] Deploy branch to a temporary Railway service with no production traffic.
- [ ] Verify startup/build/runtime gates are GREEN.
- [ ] Compare branch against main and confirm no Creator Hub source changes.
- [ ] Fast-forward main only after validation.
- [ ] Verify the production Railway deployment reaches SUCCESS before calling V372 live.
