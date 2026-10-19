# Closed Beta Mobile Bugfix Pass Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans in this chat. Implement task by task with regression-first verification and one final independent review.

**Goal:** Correct the eight reported mobile UX/performance defects and verify the deployed result.

**Architecture:** Preserve the canonical shell, internal Hub scroll, account identity boundaries and Alive's shared job state. Fix geometry/lifecycle at its owner; keep notification preference separate from browser permission. Measure the existing AI pipeline before changing a proven bottleneck.

**Tech Stack:** Python/Streamlit companion, nginx, vanilla JavaScript, Playwright Chromium/WebKit, ffmpeg, Railway.

**Spec:** `docs/superpowers/specs/2026-10-18-closed-beta-bugfix-pass.md`

## Global Constraints

- No new features, redesign, reduced AI quality, disabled Alive or weakened gates.
- Home remains non-scrollable; Hub retains its internal scroll container.
- Preserve existing login/logout and distinguish local profile data from authenticated identity.
- Notifications OFF persists and prevents automatic subscription; browser denial remains visible.
- Measure comparable AI input before/after, with stage timings and cache/cold distinctions.
- Finish only after main Production Gate, Railway SUCCESS/health and Production UI Verify are green.

## Review Focus

- Short/tall phone layouts and expanded settings: last card must be wholly visible above the Game Bar, including nonzero safe area.
- A profile save must survive reload without claiming authenticated identity; failed persistence must not report success.
- OFF followed by reload, granted browser permission and an existing subscription must remain OFF.
- Scroll, hidden iframe, quick navigation and delayed async callbacks must never resurrect old Alive transients.
- AI cache identity must change with source/engine/parameters; measurements must not compare a cold run against an unlabelled cache hit.

### Task 1: Reproduce and establish baseline

**Files:** visual regression driver, spec, this plan; read existing Hub/Alive/push/AI code.
**Interfaces:** consumes canonical main502038f and public release41e583b; produces reproducible failures and before timings.

- [ ] Exercise public Hub/settings on iPhone375×667,390×844,430×932 and Android412×915; record visible/scroll geometry, profile controls, notification state and Alive ring displacement.
- [ ] Instrument actual stage boundaries for one fixed AI input without optimizing: materialization/prescan, audio/video scan, voice/refinement, semantic call, ranking and frontend delivery. Record cold and repeated runs separately.
- [ ] Run baseline `python -m pytest tests -q`; expected183passed,18skipped.

### Task 2: Hub scroll and profile editing

**Files:** `web/creator_hub_v156_component/index.html`, `web/direct_upload_server.py`, `app.py` header refresh only, `tests/test_closed_beta_bugfix_pass.py`, visual driver.
**Interfaces:** `/creator-hub/state`, `/creator-hub/profile`, `/creator-hub/avatar`; connected flag continues to represent authenticated identity.

- [ ] Add failing geometry checks for the last element in every Hub view and fixed Home; add real profile-save persistence/error and guest/connected boundary cases.
- [ ] Correct Hub scroll viewport/reserve using actual frame/header/Game Bar geometry. Correct the existing photo/name edit/save chain and immediate shared-avatar refresh, retaining compression and visible backend errors. Remove only the redundant Accedi row; preserve reachable logout behavior.
- [ ] Run targeted regressions and baseline suite; inspect all four viewport screenshots; commit after green.

### Task 3: Notification preference

**Files:** Hub HTML, companion `_push_client_bytes` and subscription handlers, nginx companion routes, regression tests.
**Interfaces:** keep `GSFPush.enable/ensure`; provide the existing setting with persistent enable/disable/status behavior, independently of Notification.permission.

- [ ] Add failing tests for OFF→reload with granted permission, existing subscription cancellation, ON, denied/unsupported permission, backend failure and resubscription races.
- [ ] Implement the minimum preference/unsubscribe path required for this setting; reject late subscribe after OFF, retain preference on refresh and show meaningful UI states.
- [ ] Verify no automatic requestPermission/subscription against saved OFF; real browser/handler tests, full suite, commit.

### Task 4: Alive geometry and route lifecycle

**Files:** `web/gsf_alive_v418.js`, its four canonical inline consumers, `app.py`/navigation bridge only as necessary, JS and browser regressions.
**Interfaces:** retain `GSFAlive.mount/emit/state` and cross-surface job facts; route resources and transient effects have an explicit active lifetime.

- [ ] Add failing real scroll checks for guide/whisper alignment and rapid route changes, including stale timers, echoes, bubbles and repeated mount/resource counts.
- [ ] Anchor geometry to the actual DOM on internal scroll/resize; avoid interpolated positional lag. Suspend/clean old surface resources synchronously at navigation; cancel stale async callbacks while preserving global job facts and current-page Alive behavior.
- [ ] Refresh existing canonical blocks using `python tools/gsf_alive_inline.py --write`; verify inline guard, Node and real Chromium/WebKit interactions; full suite; commit.

### Task 5: Measured AI latency fix

**Files:** proven hot path in `app.py`, existing worker/semantic/AI frontend helpers only if evidence requires; regression tests and timing report.
**Interfaces:** preserve candidate quality, engine-specific cache keys and selected-moment behavior.

- [ ] Record the baseline's dominant cost and add a failing test for its duplicated work/cache/polling behavior before the fix.
- [ ] Optimize only the demonstrated cost, retaining signals, model quality and correct cache invalidation. Expose safe stage durations in existing diagnostics/logs, without sensitive paths or credentials.
- [ ] Repeat the identical input/mode/parameters and cold/cache conditions; compare timings and candidate invariants; record before/after breakdown and commit after relevant/full tests pass.

### Task 6: Release and live verification

**Files:** existing Production Gate test list only if needed, PROJECT_STATUS and claim evidence.
**Interfaces:** unchanged guarded marker promotion; public health/manifest and Production UI Verify are authoritative.

- [ ] Independent whole-branch review; fix blockers with regression evidence. Refresh current main, ensure ownership, create PR and pass relevant checks.
- [ ] Integrate, await main Production Gate and automatic Railway promotion. Verify frontend/worker deployment states and fresh health.
- [ ] Require Production UI Verify SUCCESS. Repeat public Hub/profile/name/notifications/Alive transitions on the four mobile sizes; preserve upload→AI→Editor→render/save navigation coverage with no new critical console/runtime errors.
- [ ] Record causes/fixes, comparable AI timings, test evidence, source/promotion/deployment IDs and limits; complete claim only after all requested checks pass.
