# Gaming Shorts Factory — Project Status

> **CANONICAL SOURCE OF TRUTH FOR ALL TECHNICAL CHATS / AGENTS.**
> Read this file before changing code. Refresh live GitHub/Railway evidence before changing production claims.

## Snapshot

- **Repository:** `danilo222barbieri-ai/GamingShortsFactory`
- **Production branch:** `main`
- **Current product baseline:** **V402 — Game Brain / Auto Highlights 2.0**
- **Current `main` HEAD:** always query GitHub live; documentation/coordination commits may advance `main` without changing production.
- **Last fully tested runtime source commit:** `001802a00a9b33694b1c01729dd8054132c2e672`
- **Last runtime promotion commit:** `abd4f83c512366d0a24792fa022c88363b260750` — `deploy: promote tested 001802a00a9b [skip ci]`

## Production state — last freshly verified 2026-10-13

### Frontend

- Railway service: `gaming-shorts-factory-v79`
- Service ID: `89ae81ec-54d7-4f22-98f4-c88d6361a6a2`
- Environment: `production` (`5cb868d5-9936-4ff0-be2d-ef42be7fe0ec`)
- Verified deployment: `d4897ce8-f071-4557-9c36-e376c5c1e032`
- Status: **SUCCESS / online**
- Replicas: 1 running / 0 crashed
- Warnings/criticals: 0 / 0
- Deployed runtime promotion commit: `abd4f83c512366d0a24792fa022c88363b260750`
- Healthcheck: `/healthz`
- Railway deploy trigger: only changes to `.railway/frontend-deploy.txt`

### AI worker

- Railway service: `gsf-ai-worker`
- Service ID: `8cd8b98c-43b7-4c3f-bf9a-9c0968286ada`
- Environment: `production`
- Verified deployment: `cdec6ace-2151-4d23-aa8a-2d597d2589b2`
- State: **SLEEPING** — expected healthy idle state because Railway sleep mode is enabled
- Warnings/criticals: 0 / 0
- Current worker baseline: V402 / commit `1192e00b32c975d0296ffef718fd8baab50785ef`
- Healthcheck: `/health` when awake
- Railway deploy trigger: only changes to `.railway/worker-deploy.txt`

## Production Gate

Workflow: `.github/workflows/v397-production-gate.yml`  
Workflow name: **GSF Production Gate**

The runtime gate currently verifies V397/V398/V399/V400/V401/V402 contracts, current Python syntax guards, worker + frontend image builds, composite `/healthz`, blocking runtime smoke, and V343/V389/V391/V393/V394/V395/V396 UI regressions.

Only after the current runtime-changing `main` commit passes may GitHub update the applicable Railway marker. Stale tested commits are refused when a newer `main` exists.

## New orchestration system — implementation branch

Branch: `chat/parallel-rollback-one-command`

**Integration state:** implementation verified on the isolated branch; not yet merged to `main`, so do not describe these additions as production-live until the PR/main gate and Railway verification complete.

### Parallel chat isolation

Implemented on the branch:

- `tools/gsf_claims.py` — conservative ownership conflict engine.
- `tools/gsf_task.py` — atomic global claim acquisition, unique branch/worktree bootstrap, finish/handoff and machine-readable status.
- `.gsf/claims/index.json` — global live ownership registry.
- `.gsf/claims/README.md` — claim lifecycle/rules.
- Claim states: `active`, `handoff`, `completed`, `abandoned`; only `active`/`handoff` block overlap.
- Atomic coordination uses optimistic `main` updates with retry/re-read after non-fast-forward races.
- Product work remains isolated on `chat/<task>-<suffix>` branches/worktrees.

Commands after integration:

`python tools/gsf_task.py start --scope "<scope>" --paths <path> [<path> ...]`

`python tools/gsf_task.py status --claim <claim-id> --json`

`python tools/gsf_task.py finish --claim <claim-id> --state completed --evidence-json '<json>'`

### Guarded rollback

Implemented policy/state on the branch:

- `tools/gsf_rollback_policy.py`
- `.gsf/state/known-good.json`
- `.gsf/incidents/index.json`
- `docs/runbooks/gsf-automatic-rollback.md`

Hard rollback eligibility only: current new deployment `FAILED`, `CRASHED`, OOM, or sustained frontend health failure. Worker `SLEEPING` with sleep enabled is healthy. Isolated 5xx/provider/network failures are notify-only.

Initial known-good records were seeded from fresh Railway evidence:

- frontend → `d4897ce8-f071-4557-9c36-e376c5c1e032`
- worker → `cdec6ace-2151-4d23-aa8a-2d597d2589b2`

Automatic action invariant: maximum **one** rollback attempt per failing deployment; recovery failure escalates and never recursively rolls back.

Privileged Railway rollback is intentionally kept out of repository secrets and will be wired into the authenticated **GSF Guardian** only after this branch is integrated to `main`.

### One-command workflow

Implemented on the branch:

- `docs/runbooks/gsf-one-command-workflow.md`
- `.gsf/state/task-status.schema.json`
- `AGENTS.md` makes the workflow the default for coding requests.

State machine:

`INTAKE -> CLAIMED -> IMPLEMENTING -> TESTED -> INTEGRATING -> GATE -> DEPLOYING -> VERIFYING -> LIVE|BLOCKED|ROLLED_BACK -> HANDOFF`

Terminal evidence labels: `LIVE`, `BLOCKED`, `ROLLED_BACK`, `HANDOFF_REQUIRED`.

Safe-close boundary: only after **GitHub handoff** — when the commit/PR/push exists on GitHub and CI/Railway/automation owns the next step. Before GitHub handoff there is no guarantee a normal chat continues after the app/session closes.

### Branch verification evidence

Latest orchestration CI for the implementation branch is **SUCCESS** after the final rollback anti-loop extension. Earlier full run #23 verified **31 tests PASS** plus `V397 production hardening structural contract: PASS`; the final run also passed after adding explicit end-to-end anti-loop scenarios.

No intentional production failure/rollback test was performed.

## Deployment model after integration

```text
User coding request
   ↓
Read status + acquire global claim
   ↓
Dedicated chat branch/worktree
   ↓
Implementation + relevant tests
   ↓
PR / integration to main
   ↓
GSF Production Gate
   ├── FAIL → no Railway marker → production unchanged
   └── PASS → required Railway marker(s)
                    ↓
              Railway deploy
                    ↓
            verify service health
              ├── healthy → LIVE / known-good
              └── hard failure → one guarded rollback attempt
                                      ↓
                              verify recovery / escalate
                    ↓
          update project memory + complete claim
```

## Current user-facing verification priorities

These are re-verification priorities, not claims that a feature is currently broken:

1. `Crea con IA` — full path from Home to generated candidate/result.
2. `Game Editor` — open/load media/controls/mobile+desktop/return navigation.
3. `Crea Short` — final generation through share/download.
4. Global Game Bar / Creator Hub navigation — no stale inherited route state.
5. Mobile/desktop shell consistency after UI changes.

Always reproduce against the current deployed build before marking one fixed/broken.

## Active work

Live ownership after integration is read from `.gsf/claims/index.json`. Until this branch is merged, the current orchestration implementation itself is:

| Owner / chat | Branch | Scope | State |
|---|---|---|---|
| current implementation session | `chat/parallel-rollback-one-command` | parallel claims + rollback guard + one-command orchestration | branch tests green; awaiting PR/integration |

## Mandatory coding protocol after integration

1. Read `AGENTS.md` and this file.
2. Refresh `main` and live claims.
3. Acquire a narrow claim before product edits.
4. Work only on the dedicated returned branch/worktree (or equivalent connector-created isolated branch).
5. Run relevant tests.
6. Integrate only with clear ownership and current `main`.
7. Let Production Gate/Railway own runtime deployment.
8. Record fresh evidence at handoff/completion.

**Never write `SUCCESS`, `LIVE`, `fixed`, or `done` without fresh evidence.**

## Automation

- **GSF Guardian:** enabled, hourly condition watch.
- Current production Guardian monitoring remains active.
- Guarded rollback action is intentionally pending until the rollback policy/state files are merged to `main`.

## Recent verified milestones

- **V402:** Game Brain / Auto Highlights 2.0 merged to `main`.
- **2026-10-13:** Production Gate made permanent/version-independent in behavior.
- **2026-10-13:** Railway frontend moved to composite `/healthz`.
- **2026-10-13:** Railway frontend/worker changed to marker-based deploy triggers.
- **2026-10-13:** First marker-based frontend promotion `d4897ce8-f071-4557-9c36-e376c5c1e032` verified `SUCCESS`.
- **2026-10-13:** `PROJECT_STATUS.md` + `AGENTS.md` introduced as shared cross-chat project memory/protocol.
- **2026-10-13:** parallel-claim, rollback-policy and one-command implementation reached green branch verification; integration pending.

---

When this file disagrees with chat memory, verify GitHub/Railway and update this file. Never silently choose the more convenient version of events.
