# Gaming Shorts Factory — Project Status

> **CANONICAL SOURCE OF TRUTH FOR ALL TECHNICAL CHATS / AGENTS.**
> Read this file before changing code. Refresh live GitHub/Railway evidence before changing production claims.

## Snapshot

- **Repository:** `danilo222barbieri-ai/GamingShortsFactory`
- **Production branch:** `main`
- **Current product baseline:** **V402 — Game Brain / Auto Highlights 2.0**
- **Cross-chat orchestration:** **LIVE**
- **Last fully tested main source commit:** `f9a4624bbfe0aeb8a4fb749ba7e9026c69962c2d`
- **Last runtime promotion commit:** `c3206dc4fceb60c285bbd2057af45bb7acff2e89` — `deploy: promote tested f9a4624bbfe0 [skip ci]`
- **Current `main` HEAD:** always query GitHub live; coordination/status-only commits may advance `main` without changing production.

## Production state — verified 2026-10-13 22:33 UTC

### Frontend

- Railway service: `gaming-shorts-factory-v79`
- Service ID: `89ae81ec-54d7-4f22-98f4-c88d6361a6a2`
- Environment: `production` (`5cb868d5-9936-4ff0-be2d-ef42be7fe0ec`)
- Verified deployment: `eb0d89ed-9cc1-4719-8682-032cbad307de`
- Status: **SUCCESS / Online**
- Replicas: **1 running / 0 crashed**
- Warnings/criticals: **0 / 0**
- Recent failures: **0**
- Promotion commit: `c3206dc4fceb60c285bbd2057af45bb7acff2e89`
- Healthcheck: `/healthz`
- Railway deploy trigger: only changes to `.railway/frontend-deploy.txt`

### AI worker

- Railway service: `gsf-ai-worker`
- Service ID: `8cd8b98c-43b7-4c3f-bf9a-9c0968286ada`
- Verified deployment: `cdec6ace-2151-4d23-aa8a-2d597d2589b2`
- State: **SLEEPING** — expected healthy idle state because Railway sleep mode is enabled
- Warnings/criticals: **0 / 0**
- Recent failures: **0**
- Worker baseline commit: `1192e00b32c975d0296ffef718fd8baab50785ef`
- Healthcheck: `/health` when awake
- Railway deploy trigger: only changes to `.railway/worker-deploy.txt`

## Production Gate

Workflow: `.github/workflows/v397-production-gate.yml`  
Workflow name: **GSF Production Gate**

Latest integration verification:

- PR `#110` merged by squash into `main` as `f9a4624bbfe0aeb8a4fb749ba7e9026c69962c2d`.
- PR head Production Gate `#50`: **SUCCESS**.
- Main Production Gate `#51`: **SUCCESS**.
- Gate promotion created `c3206dc4fceb60c285bbd2057af45bb7acff2e89`.
- Railway frontend deployment `eb0d89ed-9cc1-4719-8682-032cbad307de`: **SUCCESS / Online**.
- Worker deploy for this promotion: **SKIPPED as expected** because no worker runtime files changed.

The gate continues to verify V397/V398/V399/V400/V401/V402 contracts, Python syntax guards, worker/frontend image builds, composite `/healthz`, blocking runtime smoke, and V343/V389/V391/V393/V394/V395/V396 UI regressions before runtime promotion.

## Parallel chat isolation — LIVE

Files:

- `tools/gsf_claims.py` — conservative ownership conflict engine.
- `tools/gsf_task.py` — atomic global claim acquisition, unique branch/worktree bootstrap, handoff/finish and machine-readable status.
- `.gsf/claims/index.json` — live global ownership registry shared by all technical chats.
- `.gsf/claims/README.md` — lifecycle and safety rules.

Claim states:

- `active` — blocks overlap
- `handoff` — blocks overlap while ownership transfers
- `completed` — historical, does not block
- `abandoned` — historical, does not block

Atomic acquisition uses latest `origin/main`, conflict detection, optimistic push and retry/re-read after races. Two chats racing for overlapping paths cannot both win.

Commands when a Git worktree is available:

`python tools/gsf_task.py start --scope "<scope>" --paths <path> [<path> ...]`

`python tools/gsf_task.py status --claim <claim-id> --json`

`python tools/gsf_task.py finish --claim <claim-id> --state completed --evidence-json '<json>'`

When a local worktree is unavailable, an authenticated GitHub connector may perform the equivalent claim + dedicated-branch protocol, but it must preserve the same fail-closed ownership semantics.

## Guarded automatic rollback — LIVE

Policy/state:

- `tools/gsf_rollback_policy.py`
- `.gsf/state/known-good.json`
- `.gsf/incidents/index.json`
- `docs/runbooks/gsf-automatic-rollback.md`

Current verified known-good targets:

- frontend → `eb0d89ed-9cc1-4719-8682-032cbad307de`
- worker → `cdec6ace-2151-4d23-aa8a-2d597d2589b2`

GSF Guardian is enabled as an **hourly condition watch** and now applies the guarded rollback policy.

Automatic rollback eligibility is deliberately narrow:

- current new deployment `FAILED`
- current new deployment `CRASHED`
- current new deployment OOM-killed
- sustained frontend `/healthz` failure tied to the new deployment

Not automatic rollback triggers:

- isolated HTTP 5xx
- Gemini/provider/API transient errors
- temporary network error
- one failed user request while service health remains good
- worker `SLEEPING` when sleep mode is enabled

Safety invariant: maximum **one automatic rollback attempt per failing deployment ID**. The target must be an exact previously verified known-good deployment. Invalid/missing state fails closed. Failed recovery escalates and never recursively rolls back.

The scheduled Guardian runs hourly; Railway `/healthz` remains the immediate protection during the initial deploy rollout.

## One-command workflow — LIVE

Files:

- `AGENTS.md`
- `docs/runbooks/gsf-one-command-workflow.md`
- `.gsf/state/task-status.schema.json`

Every coding request automatically enters this workflow unless the user explicitly asks for analysis/design only:

`INTAKE -> CLAIMED -> IMPLEMENTING -> TESTED -> INTEGRATING -> GATE -> DEPLOYING -> VERIFYING -> LIVE|BLOCKED|ROLLED_BACK -> HANDOFF`

Evidence-backed terminal labels are exactly:

- `LIVE`
- `BLOCKED`
- `ROLLED_BACK`
- `HANDOFF_REQUIRED`

### Safe-close boundary

A normal ChatGPT conversation is not treated as guaranteed background execution before **GitHub handoff**.

Once the relevant commit/PR/push exists on GitHub and GitHub CI/Railway/automation owns the next deterministic step, the user may close the app without stopping GitHub Actions or Railway. The GSF Guardian then continues on its scheduled cadence.

## Verification evidence

Final isolated-branch orchestration CI after safety fixes:

- **36/36 tests PASS**
- `V397 production hardening structural contract: PASS`
- real CLI invocation `python tools/gsf_task.py --help` verified
- corrupt known-good state fails closed
- corrupt incident state fails closed
- rollback anti-loop scenarios verified

PR integration checks on final head:

- V398: **PASS**
- V399: **PASS**
- V400: **PASS**
- V402: **PASS**
- GSF Production Gate #50: **PASS**

No intentional destructive production rollback test was performed. Rollback execution will only occur for a naturally eligible hard failure or an explicitly approved controlled failure test.

### Game Editor V403 support handoff — 2026-10-14

- Support engine merged via PR `#112` as `f88217ed1aa9c762483962397e81219f90bc5127`.
- Added non-destructive editor state normalization, Undo/Redo history, Smart Timeline marker normalization and deterministic Game Director suggestions.
- V403 TDD workflow demonstrated intentional RED before implementation, then GREEN after implementation.
- CI also applied `scripts/apply_v403_game_editor.py` to a disposable copy of the then-current `app.py` and successfully Python-compiled the fully patched app.
- **Runtime UI is not yet integrated into `app.py`.** The active `alive-core-v405-b6f2a1` claim currently owns `app.py`; forcing an overlap would violate the repository isolation protocol.
- The deterministic V403 app patch is staged on `main` and can be applied after that `app.py` claim is completed/released, then must pass the Production Gate and Railway verification before any LIVE claim.

## Current user-facing verification priorities

These are re-verification priorities, not claims that a feature is currently broken:

1. `Crea con IA` — full path from Home to generated candidate/result.
2. `Game Editor` — open/load media/controls/mobile+desktop/return navigation.
3. `Crea Short` — final generation through share/download.
4. Global Game Bar / Creator Hub navigation — no stale inherited route state.
5. Mobile/desktop shell consistency after UI changes.

Always reproduce against the current deployed build before marking one fixed/broken.

## Active work

Live ownership is read from `.gsf/claims/index.json` and is authoritative. As of the Game Editor V403 handoff, multiple isolated claims are active; notably `alive-core-v405-b6f2a1` owns `app.py`. Never infer that a completed CI run releases a claim: only the registry state does.

## Mandatory coding protocol

1. Read `AGENTS.md` and this file.
2. Refresh `main` and `.gsf/claims/index.json`.
3. Acquire a narrow claim before product edits.
4. Work only on the dedicated branch/worktree or equivalent isolated connector branch.
5. Run relevant tests.
6. Reconcile current `main` before integration.
7. Let Production Gate and Railway own runtime promotion.
8. Verify Railway health or guarded rollback outcome.
9. Update factual project memory and release/complete the claim.

**Never write `SUCCESS`, `LIVE`, `fixed`, or `done` without fresh evidence.**

## Recent verified milestones

- **V402:** Game Brain / Auto Highlights 2.0 remains the current product baseline.
- **2026-10-13:** Production Gate made version-independent in behavior and marker-gated.
- **2026-10-13:** Railway frontend moved to composite `/healthz` and marker-only deploy trigger.
- **2026-10-13:** `PROJECT_STATUS.md` + `AGENTS.md` established as shared cross-chat memory/protocol.
- **2026-10-13:** PR #110 integrated atomic multi-chat claims, guarded rollback policy and one-command workflow.
- **2026-10-13:** Main Production Gate #51 PASS; frontend deployment `eb0d89ed-9cc1-4719-8682-032cbad307de` verified SUCCESS/Online.
- **2026-10-13:** GSF Guardian updated to guarded automatic rollback policy.
- **2026-10-14:** Game Editor V403 support engine and deterministic integration patch merged via PR #112; runtime UI integration intentionally deferred while `app.py` remains under an active non-overlapping owner claim.

---

When this file disagrees with chat memory, verify GitHub/Railway and update this file. Never silently choose the more convenient version of events.