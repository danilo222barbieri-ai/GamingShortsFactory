# Full Production Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify and harden the complete Gaming Shorts Factory production path so current navigation, upload, AI, editor, render, sharing/social, memory and performance are proven by production-image tests and Railway runtime evidence.

**Architecture:** Audit the exact Docker-built runtime instead of source fragments in isolation. Add a current-version production audit that checks static contracts plus executable smoke tests, fix only root-cause failures with focused regression tests, then merge only after CI is green and re-check Railway production health/logs.

**Tech Stack:** Python 3.12, Streamlit, FFmpeg/libx264, Faster-Whisper, HTML/JS embedded components, nginx, GitHub Actions, Docker, Railway.

**Spec:** Current project requirements captured in the 2026-10-05 full-audit request and existing V285-V291 regression contracts.

## Global Constraints

- Final video format remains 1080x1920, 9:16 only.
- Preserve the approved unified player/editor behavior and current visual language; this audit is not a redesign.
- Game Bar must navigate globally: Home, Hub, I miei Shorts, Bozze, Social.
- AI must preserve 15s/30s selection and return three usable moments through four distinct engine modes.
- Do not mark third-party OAuth publishing as end-to-end verified without provider credentials/live authorization.
- Do not merge or deploy a fix until its regression test and production-image audit pass.

## Review Focus

- Session/navigation state surviving transitions between Home, Hub, Profile, Shorts, Drafts and Social.
- Engine/duration/video cache-key isolation so one AI mode cannot reuse another mode's results.
- Uploads without audio, mobile-origin media, large files and restarted sessions.
- Final render compatibility: exact geometry, H.264/AAC/pixel format and valid no-audio fallback.
- Production runtime drift between frontend, worker and the code/tests built from the current commit.

---

### Task 1: Establish production baseline

**Files:**
- Inspect: `Dockerfile`, `.github/workflows/v290-full-flow-audit.yml`
- Inspect: Railway frontend and worker deployments/logs

**Interfaces:**
- Consumes: current `main` commit and Railway production deployment metadata.
- Produces: baseline SHA, health status, failure/log inventory.

- [ ] Capture current main SHA and Railway production deployment IDs/statuses.
- [ ] Inspect frontend and worker runtime/build/HTTP logs for errors, crashes, 5xx, OOM and repeated warnings.
- [ ] Confirm whether frontend and worker are built from compatible current code.

### Task 2: Add current production audit gate

**Files:**
- Create: `web/audit_v292_production.py`
- Create: `.github/workflows/v292-production-audit.yml`

**Interfaces:**
- Consumes: Docker-generated final app, component HTML, upload server, nginx config, current regression scripts.
- Produces: one CI gate that fails on broken current production contracts.

- [ ] Write failing/current audit assertions for navigation, upload/session, four AI modes, three moments, 15/30 duration, editor bridge, render contract, share/social routes and memory/performance hooks.
- [ ] Run the audit in the exact production Docker image and ensure it catches any current mismatch.
- [ ] Add HTTP smoke checks for home, share and social surfaces plus process startup.
- [ ] Run current regression scripts (V285-V291 and key render/worker contracts) from the built image.

### Task 3: Fix root-cause failures with regression tests

**Files:**
- Modify only the current owning patch/module/component identified by each failure.
- Test: add or tighten the nearest `web/test_v*.py` regression for every code fix.

**Interfaces:**
- Consumes: failures from Task 2 and Railway evidence from Task 1.
- Produces: minimal verified fixes without unrelated UI changes.

- [ ] For each failure, reproduce it with the smallest targeted test.
- [ ] Implement the minimal root-cause fix.
- [ ] Re-run the targeted test, then the V292 production audit.

### Task 4: Performance and resource audit

**Files:**
- Inspect: `web/gsf_perf.py`, `web/v105_render_benchmark.py`, upload/AI/render modules and Dockerfile.
- Modify only when a measured bottleneck has a safe regression-tested fix.

**Interfaces:**
- Consumes: build/runtime timings, telemetry contracts and Railway logs.
- Produces: measured bottlenecks, safe optimizations, technical-debt list.

- [ ] Measure Docker build/startup and inspect render/upload/AI telemetry paths.
- [ ] Verify memory-safe/no-audio/fps guards are present in the final generated runtime.
- [ ] Identify avoidable repeated build work and patch-chain risk without destabilizing production.
- [ ] Apply only optimizations whose behavior is covered by tests.

### Task 5: Release verification

**Files:**
- Review: complete branch diff and CI logs.

**Interfaces:**
- Consumes: green audit branch and all targeted fixes.
- Produces: merge-ready production build and final verified report.

- [ ] Review branch diff for accidental visual/functional regressions.
- [ ] Require green GitHub Actions production audit.
- [ ] Merge to `main` only after all gates pass.
- [ ] Poll Railway until the new frontend deployment settles, then inspect runtime/HTTP logs again.
- [ ] Report verified areas, fixes, remaining external dependencies and next technical-debt improvements.
