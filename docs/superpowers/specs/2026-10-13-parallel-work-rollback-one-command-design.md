# GSF Parallel Work + Automatic Rollback + One-Command Pipeline

Date: 2026-10-13
Branch: `chat/parallel-rollback-one-command`
Status: Design specification for review

## 1. Goal

Make Gaming Shorts Factory safe and easy to operate even when many independent ChatGPT/Codex sessions work on the repository in parallel.

Success means:

- each technical chat/agent gets an isolated branch/worktree for product code;
- all chats immediately see which areas/files are already claimed;
- overlapping work is blocked or explicitly handed off instead of silently colliding;
- runtime changes still pass the existing GSF Production Gate before Railway promotion;
- a newly deployed unhealthy release can be automatically rolled back to the last known-good deployment;
- the user can issue a single natural-language request and the system carries the change through branch creation, testing, integration, deploy verification, rollback if needed, and status handoff;
- `PROJECT_STATUS.md` remains the human-readable canonical project memory without becoming the live locking primitive.

## 2. Non-goals

This change does not:

- make normal ChatGPT chats communicate directly with each other;
- bypass review/testing or deploy feature branches directly to production;
- use `main` as a product-code scratch branch;
- automatically roll back on every transient upstream/provider error;
- treat an idle Railway worker in `SLEEPING` state as unhealthy;
- introduce a full blue/green platform or a new external orchestrator unless later needed.

## 3. Existing production baseline

The repository already has:

- `AGENTS.md` with mandatory project rules;
- `PROJECT_STATUS.md` as the cross-chat source of truth;
- `.github/workflows/v397-production-gate.yml`, whose workflow name is `GSF Production Gate`;
- marker-based Railway deploy triggers:
  - `.railway/frontend-deploy.txt`
  - `.railway/worker-deploy.txt`
- frontend Railway healthcheck `/healthz`;
- worker Railway healthcheck `/health`;
- GSF Guardian hourly condition monitoring;
- a verified marker-based frontend promotion already completed successfully.

This design extends that system instead of replacing it.

## 4. Architecture overview

```text
User request
   ↓
Task bootstrap
   ├─ read AGENTS.md + PROJECT_STATUS.md
   ├─ refresh main
   ├─ atomically acquire ownership claim in .gsf/
   └─ create chat/<task>-<unique> branch/worktree
          ↓
     isolated product work
          ↓
       branch tests
          ↓
     PR / integration
          ↓
         main
          ↓
 GSF Production Gate
   ├─ FAIL → no marker → production unchanged
   └─ PASS → Railway marker
                   ↓
               Railway
                   ↓
            health verification
               ├─ healthy → known-good + handoff
               └─ unhealthy → rollback guard
                                  ↓
                       previous known-good build
                                  ↓
                           verify recovery
```

## 5. Parallel work model

### 5.1 Branch naming

Every independent coding session uses a dedicated branch:

`chat/<task-slug>-<unique-suffix>`

Examples:

- `chat/editor-mobile-a83f`
- `chat/home-desktop-91bd`
- `chat/ai-highlights-3c12`

The suffix prevents branch-name collisions.

### 5.2 Global claim registry

Product code never uses `main` as a shared scratch branch. Coordination metadata is the explicit exception.

Active ownership is globally visible on `main` under `.gsf/` and is ignored by runtime CI/deploy triggers.

Use:

- `.gsf/claims/index.json` — atomic active-claim registry;
- `.gsf/claims/<claim-id>.json` — detailed per-task claim/history.

Example claim:

```json
{
  "id": "editor-mobile-a83f",
  "branch": "chat/editor-mobile-a83f",
  "scope": "Game Editor mobile",
  "paths": ["web/editor_2027_embed.py", "web/fix_v*_mobile_editor_*.py"],
  "owner": "chat/editor-mobile-a83f",
  "created_at": "2026-10-13T23:50:00+02:00",
  "state": "active"
}
```

No secrets or personal data are stored in claims.

### 5.3 Atomic claim acquisition

Claim creation must be fail-closed and race-safe.

Algorithm:

1. fetch latest `main` and `.gsf/claims/index.json` including its blob/version SHA;
2. compare requested scope/path patterns with all active claims;
3. if overlap exists, stop with the conflicting claim(s);
4. if clear, append the new claim and update the index using optimistic concurrency / current-file SHA;
5. if the update loses a race because another chat updated the index first, re-read the latest index and repeat conflict detection;
6. only after the claim is acquired may product-code editing begin.

This prevents the classic race where two chats both check “free” and then both start editing the same files.

### 5.4 Conflict rule

If ownership overlaps, a task must do one of:

1. narrow its scope to non-overlapping files;
2. wait for the current owner to finish;
3. use an explicit handoff recorded in the claim;
4. serialize the work by merging/rebasing the first task before the second continues.

Automatic integration is forbidden while conflicting active ownership remains unresolved.

### 5.5 Claim lifecycle

States:

- `active`
- `handoff`
- `completed`
- `abandoned`

Stale claims are never silently deleted. Cleanup must verify branch/PR activity and preserve an audit trail.

## 6. PROJECT_STATUS.md role

`PROJECT_STATUS.md` remains the human-readable canonical project memory, but not the atomic lock table.

It records:

- current baseline/version;
- last verified runtime promotion;
- current Railway state;
- production gate status;
- high-level active work summary;
- completed handoffs and unresolved issues.

Detailed live ownership is read from `.gsf/claims/index.json`.

At task completion/handoff, the agent updates `PROJECT_STATUS.md` using the latest version and then releases/completes its claim.

## 7. Coordination-only main commits

Direct `main` writes are allowed only for non-runtime coordination metadata such as:

- `.gsf/claims/**`
- `.gsf/state/**`
- `.gsf/incidents/**`
- factual `PROJECT_STATUS.md` handoff updates when required.

These paths must be explicitly excluded from GSF Production Gate triggers and Railway runtime promotion logic.

This exception does not permit product source, tests, dependencies, Dockerfiles, or runtime configuration to be edited directly on `main` by parallel chats.

## 8. Task bootstrap helper

Proposed entry point:

`python tools/gsf_task.py start --scope "Game Editor mobile" --paths web/editor_2027_embed.py ...`

Responsibilities:

1. refresh `main`;
2. read `AGENTS.md` and `PROJECT_STATUS.md`;
3. load global active claims;
4. derive unique task/branch identity;
5. atomically acquire a claim;
6. create dedicated branch/worktree from current `main`;
7. print exact working context for the agent.

If ownership cannot be acquired safely, it exits non-zero and does not create an editable work context.

## 9. Task completion helper

Proposed entry point:

`python tools/gsf_task.py finish --claim <claim-id>`

Responsibilities:

1. verify required test evidence is present;
2. record commit/PR/integration identifiers;
3. fetch latest `PROJECT_STATUS.md` and preserve concurrent handoffs;
4. update factual status;
5. mark the claim `completed` or `handoff` atomically;
6. never claim LIVE/SUCCESS without fresh evidence.

## 10. One-command pipeline behavior

User intent can be as simple as:

> “Sistema il Game Editor mobile.”

The technical pipeline is:

1. classify task scope;
2. atomically claim ownership;
3. create isolated branch/worktree;
4. inspect relevant code/tests;
5. implement using repository development discipline;
6. run branch-level tests;
7. create/update PR or approved integration path;
8. merge to `main` only when ownership and checks are clear;
9. let `GSF Production Gate` verify runtime-impacting `main` changes;
10. if gate passes, marker-based Railway promotion occurs;
11. observe Railway deployment and health;
12. if healthy, record the deployment as known-good;
13. if clearly unhealthy, invoke rollback policy;
14. verify rollback recovery;
15. update `PROJECT_STATUS.md` and release/complete the claim.

A normal ChatGPT session does not need to stay open once work has been handed off to GitHub CI/Railway/monitoring. Before that handoff, closing a normal chat is not treated as guaranteed background execution.

## 11. Automatic rollback policy

### 11.1 Rollback triggers

Automatic rollback is allowed only for clear failure signals associated with the newly promoted release:

- Railway deployment status `FAILED`;
- Railway deployment status `CRASHED`;
- OOM-killed deployment;
- frontend `/healthz` remains unhealthy beyond the verification window;
- a newly live deployment enters a clear service failure shortly after promotion.

Worker `SLEEPING` is explicitly healthy when sleep mode is enabled.

### 11.2 Notify-only conditions

Do not auto-rollback solely because of:

- isolated HTTP 5xx responses;
- Gemini/provider/API transient errors;
- temporary external-network failure;
- a single failed user request while service health remains good.

These produce Guardian notification/diagnosis, not automatic rollback.

### 11.3 Known-good state

Store machine-readable verified deployment state under `.gsf/state/known-good.json`.

Per service track:

- Railway service ID;
- environment ID;
- known-good deployment ID;
- source/promotion commit;
- verification timestamp;
- health endpoint/state.

A new deployment becomes known-good only after Railway reports a healthy settled state and the applicable health verification passes.

### 11.4 Rollback action

If a new release meets a rollback trigger:

1. identify the immediately previous verified known-good deployment for that service;
2. redeploy/rollback that exact Railway deployment build;
3. verify resulting deployment state;
4. verify health (`/healthz` frontend; worker `/health` when awake/applicable);
5. record an incident;
6. update known-good/current state only after recovery is proven;
7. notify the user with failing deployment, restored deployment, and diagnosis when available.

### 11.5 Loop protection

Rollback automation must have:

- at most one automatic rollback attempt per failing deployment ID;
- no automatic rollback-of-a-rollback loop;
- stop-and-notify if known-good recovery also fails;
- persistent incident state so later Guardian runs do not repeat the same action.

## 12. Rollback controller placement

Preferred first implementation: privileged rollback remains in the existing authenticated ChatGPT/Guardian connector layer rather than placing a Railway production credential inside the GitHub repository.

Repository state/policy remains machine-readable under `.gsf/`; Railway actions use the already connected Railway capability when the monitoring run has action access.

If scheduled Guardian execution is ever unable to perform privileged Railway actions, the fallback architecture is a dedicated minimal Railway rollback controller with a separately provisioned scoped credential. That fallback is not introduced unless actually necessary.

This avoids secret sprawl in the first implementation.

## 13. Production Gate changes

The current gate remains the only runtime promotion path.

Required changes:

- ignore coordination-only `.gsf/**` changes;
- ignore design/status-only paths that are explicitly non-runtime;
- preserve stale-main protection before marker promotion;
- validate coordination schema in a separate lightweight check where useful, without causing Railway deployment;
- never auto-integrate conflicting feature branches.

The runtime gate must continue to fail closed.

## 14. Merge policy

- Product work happens on dedicated branches/worktrees.
- PRs/checks are preferred for integration.
- Runtime-changing `main` merges trigger GSF Production Gate.
- Marker commits remain the only Railway runtime trigger.
- Coordination-only commits never trigger Railway.
- If GitHub plan/repository permissions prevent server-side branch protection, repository tooling and `AGENTS.md` enforce the workflow behaviorally.

## 15. Observability and incident record

Use:

- `.gsf/claims/`
- `.gsf/incidents/`
- `.gsf/state/`

Rollback incidents record:

- failing deployment ID;
- trigger/reason;
- previous known-good deployment ID;
- rollback attempt count;
- rollback result;
- timestamps;
- final verification result.

No secrets are stored in these files.

## 16. Safety invariants

1. Untested runtime code does not deploy to Railway.
2. A failing Production Gate does not update Railway markers.
3. Claim acquisition is atomic before product editing begins.
4. One chat cannot silently acquire overlapping ownership after another chat has claimed it.
5. Product code is never written directly to shared `main` by parallel tasks.
6. Coordination metadata may update `main` but never triggers runtime deployment.
7. A rollback target must be a previously verified known-good deployment.
8. `SLEEPING` worker is not a failure by itself.
9. Automatic rollback executes at most once for the same failing deployment.
10. If rollback recovery fails, automation stops and notifies instead of looping.
11. No Railway/GitHub secrets are committed to the repository.
12. LIVE/SUCCESS claims require fresh evidence.

## 17. Testing strategy

### Coordination tests

- branch-name uniqueness;
- claim schema validation;
- atomic claim acquisition;
- simulated concurrent claim race: one wins, loser re-reads and detects conflict;
- exact-path and glob-pattern overlap detection;
- non-overlapping claims allowed concurrently;
- handoff/completed/abandoned handling;
- status update preserves other tasks' handoffs.

### Pipeline tests

- runtime merge with passing gate writes correct marker;
- failing gate writes no marker;
- `.gsf/**`/documentation-only commit causes no runtime gate/deploy;
- stale tested `main` cannot promote after a newer runtime commit exists.

### Rollback-policy tests

Use deterministic fake deployment snapshots/state tests for:

- SUCCESS → no rollback;
- FAILED → rollback eligible;
- CRASHED → rollback eligible;
- OOM → rollback eligible;
- frontend sustained unhealthy → rollback eligible;
- worker SLEEPING → healthy/no rollback;
- ambiguous 5xx → notify-only/no rollback;
- repeated check for same failing deployment → no second rollback;
- recovery deployment failure → stop and escalate.

A destructive rollback test is not run against healthy production. Live rollback verification waits for a real eligible failure or an explicitly approved controlled test environment.

## 18. Delivery phases

### Phase A — parallel task isolation

- `.gsf/claims/index.json` and claim schema;
- atomic claim helper;
- branch/worktree bootstrap and finish tooling;
- `AGENTS.md` / `PROJECT_STATUS.md` integration;
- conflict/race tests;
- Production Gate ignores coordination-only commits.

### Phase B — rollback state and policy

- `.gsf/state/known-good.json`;
- incident schema;
- rollback decision tests;
- Guardian updated for one guarded rollback on hard failures;
- recovery verification and duplicate-attempt suppression.

### Phase C — one-command orchestration

- compose bootstrap → isolated work → tests → integration → gate → deploy verification → rollback/handoff into one documented agent workflow;
- keep privileged production actions behind existing authenticated connectors/automation.

## 19. Acceptance criteria

The system is accepted when:

- two non-overlapping chat tasks can concurrently hold distinct claims and branches;
- two overlapping tasks racing for ownership cannot both win;
- an overlapping task receives a clear conflict/handoff path;
- a completed task leaves factual status without overwriting another task's handoff;
- coordination-only commits do not trigger Railway;
- runtime code cannot trigger Railway before Production Gate passes;
- the known-good Railway deployment is identifiable per service;
- hard-failure policy selects exactly one previous known-good target and suppresses duplicate rollback attempts;
- worker sleep does not trigger an incident;
- one natural-language task has a deterministic automation path from start through production verification.

## 20. Recommended implementation

Use repository-native atomic claim metadata + isolated feature branches, preserve the existing Production Gate/marker deployment model, and keep privileged Railway rollback in the existing authenticated Guardian/connector layer unless a dedicated controller proves necessary.

This gives the requested multi-chat safety, automatic recovery, and one-command experience with the smallest additional production surface.
