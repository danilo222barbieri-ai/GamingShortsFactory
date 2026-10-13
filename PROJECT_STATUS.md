# Gaming Shorts Factory — Project Status

> **CANONICAL SOURCE OF TRUTH FOR ALL TECHNICAL CHATS / AGENTS.**
> Read this file before changing code. Refresh it after completing work. Do not rely on an old chat message when this file or live GitHub/Railway evidence says otherwise.

## Snapshot

- **Last verified:** 2026-10-13 23:41 Europe/Rome
- **Repository:** `danilo222barbieri-ai/GamingShortsFactory`
- **Production branch:** `main`
- **Current product baseline:** **V402 — Game Brain / Auto Highlights 2.0**
- **Current `main` HEAD:** `abd4f83c512366d0a24792fa022c88363b260750`
- **Last fully tested source commit:** `001802a00a9b33694b1c01729dd8054132c2e672`
- **Promotion commit:** `abd4f83c512366d0a24792fa022c88363b260750` — `deploy: promote tested 001802a00a9b [skip ci]`

## Production state

### Frontend

- Railway service: `gaming-shorts-factory-v79`
- Environment: `production`
- Latest verified deployment: `d4897ce8-f071-4557-9c36-e376c5c1e032`
- Status: **SUCCESS**
- Deployed commit: `abd4f83c512366d0a24792fa022c88363b260750`
- Healthcheck: `/healthz`
- Railway deploy trigger: only changes to `.railway/frontend-deploy.txt`

### AI worker

- Railway service: `gsf-ai-worker`
- Environment: `production`
- Current deployment: `cdec6ace-2151-4d23-aa8a-2d597d2589b2`
- State: **SLEEPING** (expected when idle; Railway sleep mode is enabled)
- Current worker baseline: V402 / commit `1192e00b32c975d0296ffef718fd8baab50785ef`
- Healthcheck: `/health`
- Railway deploy trigger: only changes to `.railway/worker-deploy.txt`
- The latest promotion did not redeploy the worker because no worker runtime files changed.

## Production Gate

Workflow: `.github/workflows/v397-production-gate.yml`

The workflow name is now **GSF Production Gate** and is version-independent even though the historical filename still contains `v397`.

Before a runtime change can reach Railway, the gate currently verifies:

- V397 structural production hardening
- V398 semantic resilience
- V399 quality contract
- V400 AI + Hi-DPI contract
- V401 performance/stability contract
- V402 Game Brain / Auto Highlights contract
- Python syntax guards for current critical modules
- Worker Docker image build
- Frontend production Docker image build
- Composite `/healthz`
- Blocking runtime smoke test
- V343 global shell contract
- V389/V391/V393/V394/V395/V396 UI regression contracts

Only after the gate passes on the current `main` commit does GitHub update the appropriate Railway deployment marker. A stale tested commit is not promoted if a newer `main` commit already exists.

## Deployment model

```text
User request
   ↓
ChatGPT / Codex change on dedicated branch
   ↓
Tests / PR
   ↓
Merge to main
   ↓
GSF Production Gate
   ├── FAIL → no Railway marker → production unchanged
   └── PASS → update only required Railway marker(s)
                    ↓
              Railway deploy
                    ↓
              healthcheck
                    ↓
                  LIVE
```

## Current user-facing verification priorities

These are **re-verification priorities**, not claims that the feature is currently broken:

1. `Crea con IA` — full end-to-end path from Home to generated candidate/result.
2. `Game Editor` — open, load media, controls, mobile/desktop behavior, return/navigation.
3. `Crea Short` — complete path through final short generation and share/download.
4. Global Game Bar / Creator Hub navigation — verify no route inherits stale page state.
5. Mobile and desktop shell consistency after any UI change.

Do not mark one of these as fixed or broken from historical chat context alone. Reproduce against the current deployed build first.

## Active work

| Owner / chat | Branch | Scope / files | Started | State |
|---|---|---|---|---|
| — | — | No active work registered | — | idle |

### Rules for active work

- One branch/worktree per independent chat or agent.
- A chat must not take ownership of files already listed by another active row without an explicit handoff.
- Keep scope narrow: UI, Editor, worker/AI, deployment/CI, etc.
- If two tasks must touch the same file, serialize them or merge one first.
- Never use `main` as a shared scratch branch.

## Mandatory startup protocol for every coding chat / agent

1. Read `AGENTS.md`.
2. Read this `PROJECT_STATUS.md` completely.
3. Refresh `main` and inspect the latest commits before assuming a version/state.
4. Check the Active work table for overlap.
5. Inspect the relevant code/tests before modifying anything.
6. Work on a dedicated branch/worktree for parallel work.
7. Run the relevant tests plus the project production gate/regressions required by the touched area.
8. Update this file at handoff/completion with factual evidence only.

## Mandatory completion / handoff protocol

At the end of a task, record:

- branch used
- scope/files changed
- commit or PR
- tests actually run and their result
- whether the change is merged to `main`
- Production Gate result if applicable
- Railway deployment ID/status if applicable
- anything still broken, unverified, or intentionally deferred

**Never write `SUCCESS`, `LIVE`, `fixed`, or `done` here without fresh evidence.**

## Status update safety

- Fetch the latest `PROJECT_STATUS.md` before editing it so another chat's row is not overwritten.
- Preserve other chats' active rows and handoff notes.
- Do not put secrets, API keys, tokens, passwords, personal data, or Railway secret values in this file.
- Documentation-only status updates should use a commit message containing `[skip ci]` when appropriate so they do not waste Production Gate capacity.

## Automation

- **GSF Guardian:** enabled, hourly condition watch.
- It checks latest GitHub `main` / Production Gate and Railway frontend/worker health.
- It should notify only on meaningful failures or promotion/deployment mismatches.

## Recent verified milestones

- **V402:** Game Brain / Auto Highlights 2.0 merged to `main`.
- **2026-10-13:** Production Gate made permanent/version-independent in behavior.
- **2026-10-13:** Railway frontend moved to composite `/healthz`.
- **2026-10-13:** Railway frontend and worker changed to marker-based deploy triggers so ordinary untested pushes do not deploy automatically.
- **2026-10-13:** First marker-based frontend promotion completed with Railway deployment `d4897ce8-f071-4557-9c36-e376c5c1e032` = `SUCCESS`.

---

When this file disagrees with a chat summary, **verify GitHub/Railway and update this file**. Do not silently choose the more convenient version of events.
