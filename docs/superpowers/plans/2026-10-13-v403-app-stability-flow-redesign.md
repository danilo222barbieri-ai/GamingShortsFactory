# V403 — App Stability & Flow Redesign Implementation Plan

**Spec:** `docs/superpowers/specs/2026-10-13-v403-app-stability-flow-redesign.md`

**Baseline:** `845a36f5c586756743fe6f41b1f07cda3fb5246d` (verified V402 production)

## Global constraints
- Do not redesign Home.
- Preserve V400/V401/V402 behavior and tests.
- Preserve 1080×1920 / 60 fps render quality.
- Preserve metadata-first Auto Highlights; no eager candidate renders.
- Preserve `gsf_editor_2027_v1086` exactly.
- Use server-authoritative metadata/references only; never persist duplicate video blobs.
- All resume/reconciliation/job-start operations must be idempotent.
- V403 enters production as the final runtime migration after the existing V373 chain in `web/start_web.sh`.

## Task 1 — RED: define V403 behavioral contract
**Create:** `web/test_v403_app_stability_flow.py`

Write failing tests first for:
1. active project/source ref survive route transitions;
2. resume reconciliation never duplicates analysis jobs;
3. resume reconciliation never duplicates render jobs;
4. last valid profile survives refresh/fetch failure;
5. completed analysis resolves to `moments` route;
6. candidate selection persists across route and resume;
7. invalid `create_short` route without selection resolves safely;
8. editor handoff contains selected candidate start/end;
9. create-short handoff contains selected candidate;
10. final-render completion keeps the same `create_short` route and flips to ready state;
11. Game Bar destination resolution is stateless/idempotent;
12. Editor identity remains `gsf_editor_2027_v1086`.

Add surface contract assertions:
- Motori component contains no candidate-card/results section.
- Dedicated Moments component exists and owns candidate cards/internal scrolling/fullscreen return.
- unified Crea Short component exposes pre-render and ready/share states.

**RED command:**
`PYTHONPATH=web python web/test_v403_app_stability_flow.py`

Expected first failure: missing `app_flow_v403` / Moments surface contract.

Commit: `test(v403): define durable app flow contract`

## Task 2 — GREEN: durable application flow state
**Create:** `web/app_flow_v403.py`
**Modify:** `web/project_state_v157.py`

Implement a deterministic, dependency-light state machine with:
- canonical project snapshot schema/version `403`;
- route constants and `resolve_route(snapshot, requested_route)`;
- `transition(snapshot, event, payload=None)` for meaningful state transitions;
- `reconcile_snapshot(local, authoritative)` for foreground/resume;
- idempotency keys/state for analysis/render jobs;
- selected-candidate persistence;
- selected-candidate handoff helpers for Editor and Crea Short;
- final-render state transition;
- last-valid-profile cache semantics;
- finite/bounded timestamps/version fields and malformed-payload tolerance.

Extend `project_state_v157.py` to persist the V403 snapshot as lightweight metadata while preserving the old generic project-state compatibility path. No media bytes.

Run:
`PYTHONPATH=web python web/test_v403_app_stability_flow.py`
`PYTHONPATH=web python web/test_v401_performance_stability.py`
`python -m py_compile web/app_flow_v403.py web/project_state_v157.py`

Commit: `feat(v403): add durable project flow state`

## Task 3 — Motori separation + dedicated Moments surface
**Modify:** `web/ai_v221_component/index.html`
**Create:** `web/moments_v403_component/index.html`

Motori becomes configuration/progress only:
- current project/video presence;
- 4 existing engine choices;
- duration;
- start/retry/progress/error state;
- analysis completion emits a transition/action to `moments` but does not render final candidate cards.

Moments surface:
- internally scrollable within fixed global shell;
- renders only available candidates (normally 3);
- 9:16 preview/thumbnail/player contract;
- rank/timestamp/duration/event/confidence/user-readable V402 reason;
- subtitle preview toggle when available;
- exactly one selected candidate;
- fullscreen preview overlay with reliable close/return preserving selection;
- primary actions `CREA SHORT` and `MODIFICA NEL GAME EDITOR`.

Selection changes emit a parent action immediately so the server snapshot is authoritative.

Run V403 test and HTML compile/static checks.

Commit: `feat(v403): split Motori from candidate selection`

## Task 4 — Runtime routing, resume and handoffs
**Create:** `web/apply_v403_flow.py`
**Modify:** `web/start_web.sh`

Patch only the generated production app `/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py` at the end of runtime migrations.

Responsibilities:
- load/restore V403 snapshot after existing project restore;
- make global destination resolution use `resolve_route` rather than inherited transient screen state;
- mount `moments_v403_component` as a dedicated route/surface;
- on analysis completion persist candidates before routing to Moments;
- on candidate selection persist immediately;
- Editor bootstrap consumes persisted selected candidate/timestamps;
- Crea Short bootstrap consumes persisted selected candidate;
- visibility/resume reconciliation is idempotent and does not issue duplicate analysis/render requests;
- bounded page error/retry state leaves shell alive;
- preserve Home/Creator Hub/Game Bar ownership and Editor component identity.

The migration must be restart-safe and marker-idempotent.

Add V403 tests against a synthetic generated-app fixture so the test checks actual patched behavior, not only markers.

Commit: `feat(v403): wire durable routing and resume recovery`

## Task 5 — Unified Crea Short state machine
**Modify:** `web/share_v156_component/index.html`
**Modify through V403 runtime patch:** final-route parent bridge only; keep existing media/social endpoints.

One responsive surface for desktop/mobile:
- pre-render state: selected candidate preview, create, edit, save draft if eligible, back to Moments;
- rendering state: progress/recovery without duplicate render issue;
- ready state: final asset, download, metadata/share/social actions;
- missing selection: safe bounded state/action back to Moments/Motori;
- same logical state machine on desktop and mobile.

Do not alter provider APIs or final asset endpoint contract.

Run V403 tests plus V396/share regressions.

Commit: `feat(v403): unify create short finalization flow`

## Task 6 — Profile recovery and lifecycle hardening
**Modify:** `web/creator_hub_v156_component/index.html` only where needed for profile rendering semantics.
**Modify:** `web/app_flow_v403.py` / runtime bridge.

Profile behavior:
- keep last valid profile while refresh is pending;
- failure does not replace valid profile with blank placeholders;
- distinguish loading/unavailable/signed-out/valid;
- stale profile is soft/non-blocking;
- newer valid payload replaces older cache.

Resume lifecycle:
- reconcile on foreground;
- preserve current shell;
- resume polling only for active jobs;
- repeated foreground events are no-ops if state version/job key did not change.

Commit: `feat(v403): harden profile and foreground recovery`

## Task 7 — CI, production gate and release
**Create:** `.github/workflows/v403-app-stability-flow-tdd.yml`
**Modify:** `Dockerfile` to run host-safe V403 contract tests during build without weakening V397 Production Gate.

Host-safe suite:
- `PYTHONPATH=web python web/test_v403_app_stability_flow.py`
- `PYTHONPATH=web python web/test_v402_game_brain_auto_highlights.py`
- `PYTHONPATH=web python web/test_v401_performance_stability.py`
- `PYTHONPATH=web python web/test_v400_ai_hidpi.py`
- `python -m py_compile web/app_flow_v403.py web/apply_v403_flow.py web/project_state_v157.py`

Production build must additionally prove:
- V403 runtime migration applies to generated production app;
- Editor component test remains green and identity is unchanged;
- V397 Production Gate remains blocking and unchanged;
- no Home contract regressions;
- final output / render quality contracts remain green.

Compare branch against baseline and reject unexplained product changes outside V403 state/flow surfaces.

Open PR to `main`. Merge only after all V403 checks and V397 Production Gate are green. Record exact merged SHA.

Then verify Railway frontend + worker deploy the exact merged SHA, both SUCCESS/healthy, zero crash/warning regression, and no pending work. Only then call V403 live.

## Review focus
- accidental duplicate analysis/render requests on repeated resume;
- selection lost on route changes;
- invalid route loops between Motori/Moments/Crea Short;
- profile refresh blanking a valid cached profile;
- Moments accidentally reintroduced inside Motori;
- desktop/mobile divergent Crea Short logic;
- patch idempotence on container restart;
- any change to Home, V402 ranking, V401 persistence, render quality, or Editor identity.
