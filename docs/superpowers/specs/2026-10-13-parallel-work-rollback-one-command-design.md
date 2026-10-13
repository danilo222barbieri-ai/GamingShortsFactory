# GSF Parallel Work + Automatic Rollback + One-Command Pipeline

Date: 2026-10-13
Branch: `chat/parallel-rollback-one-command`
Status: Design specification for review

## 1. Goal

Make Gaming Shorts Factory safe and easy to operate even when many independent ChatGPT/Codex sessions work on the repository in parallel.

Success means:

- each technical chat/agent gets an isolated branch/worktree;
- concurrent tasks can see which areas/files are already claimed;
- overlapping work is blocked or explicitly handed off instead of silently colliding;
- runtime changes still pass the existing GSF Production Gate before Railway promotion;
- a newly deployed unhealthy release can be automatically rolled back to the last known-good deployment;
- the user can issue a single natural-language request and the system carries the change through branch creation, testing, merge/promotion, deploy verification, rollback if needed, and status handoff;
- `PROJECT_STATUS.md` remains the human-readable canonical project memory, without becoming a high-conflict lock file for every active task.

## 2. Non-goals

This change does not:

- allow normal ChatGPT chats to communicate directly with each other;
- bypass review/testing or deploy directly from feature branches to production;
- make `main` a shared scratch branch;
- automatically roll back on every transient upstream/provider error;
- treat an idle Railway worker in `SLEEPING` state as unhealthy;
- introduce a full blue/green platform or new external orchestrator unless later needed.

## 3. Existing production baseline

The current repository already has:

- `AGENTS.md` with mandatory project rules;
- `PROJECT_STATUS.md` as the cross-chat source of truth;
- a permanent-behavior workflow currently stored as `.github/workflows/v397-production-gate.yml` and named `GSF Production Gate`;
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
   ├─ derive task slug + ownership scope
   ├─ check claims
   └─ create chat/<task>-<unique> branch
          ↓
     isolated work
          ↓
     tests on branch
          ↓
     PR / integration
          ↓
         main
          ↓
 GSF Production Gate
   ├─ FAIL → no marker → production unchanged
   └─ PASS → marker commit
                   ↓
               Railway
                   ↓
            health verification
               ├─ healthy → LIVE + handoff
               └─ unhealthy → automatic rollback guard
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

The unique suffix prevents branch collisions when two users/chats choose similar task names.

### 5.2 Claims directory

Active ownership is stored outside `PROJECT_STATUS.md` under:

`.gsf/claims/<claim-id>.json`

Each claim contains only non-secret coordination data:

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

Claims are deliberately separate files so two chats can register independent work without repeatedly rewriting the same status document.

### 5.3 Conflict rule

Before editing, a task compares its intended paths/scope with active claims.

If there is no overlap, it proceeds.

If there is overlap, it must do one of:

1. narrow its scope to non-overlapping files;
2. wait for the current owner to finish;
3. use an explicit handoff recorded in the claim/status;
4. serialize the work by merging/rebasing the first task before the second continues.

Automatic merge is forbidden when active ownership overlap remains unresolved.

### 5.4 Claim lifecycle

States:

- `active`
- `handoff`
- `completed`
- `abandoned`

A task creates a claim during bootstrap and marks/removes it only after the task has a factual handoff state.

Stale claims must not be silently deleted. A stale-claim cleanup must verify branch/PR activity before changing state.

## 6. PROJECT_STATUS.md role

`PROJECT_STATUS.md` remains the human-readable canonical project memory, but it is not the primary live lock table.

It records:

- current baseline/version;
- last verified runtime promotion;
- current Railway state;
- production gate status;
- high-level active work summary;
- completed handoffs and unresolved issues.

Detailed active ownership lives under `.gsf/claims/`.

At task completion, the agent updates `PROJECT_STATUS.md` with factual evidence and either completes or removes its claim.

## 7. Task bootstrap command

A repository helper will implement deterministic setup for one-command work.

Proposed entry point:

`python tools/gsf_task.py start --scope "Game Editor mobile" --paths web/editor_2027_embed.py ...`

Responsibilities:

1. confirm repo cleanliness or isolate using a new worktree;
2. refresh `main`;
3. read `AGENTS.md` and `PROJECT_STATUS.md`;
4. load active claims;
5. detect ownership conflicts;
6. generate a unique branch name;
7. create branch/worktree;
8. create the claim file;
9. print the exact working context for the agent.

The helper must fail closed if ownership cannot be determined safely.

## 8. Task completion command

Proposed entry point:

`python tools/gsf_task.py finish --claim <claim-id>`

Responsibilities:

1. verify tests actually passed;
2. record commit/PR identifiers;
3. update `PROJECT_STATUS.md` using the latest copy;
4. mark claim `completed` or `handoff`;
5. never claim LIVE/SUCCESS unless fresh evidence exists.

## 9. One-command pipeline behavior

The user-facing intent is:

> “Sistema il Game Editor mobile.”

The technical pipeline becomes:

1. classify task scope;
2. bootstrap isolated branch/worktree and claim;
3. inspect relevant code and tests;
4. implement using the repository development/test discipline;
5. run branch-level tests;
6. create/update PR or integrate using the approved repository path;
7. merge to `main` only when overlap is clear and required checks pass;
8. let `GSF Production Gate` verify runtime-impacting `main` changes;
9. if gate passes, marker-based Railway promotion occurs;
10. observe Railway deployment and health;
11. if healthy, record LIVE evidence;
12. if deployment/runtime is unhealthy, invoke rollback policy;
13. verify rollback recovery;
14. update `PROJECT_STATUS.md` and release/complete the claim.

A normal ChatGPT session does not have to remain open after the GitHub-side work has been handed off to CI/Railway/monitoring.

## 10. Automatic rollback policy

### 10.1 Rollback triggers

Automatic rollback is allowed for clear deployment/runtime failure signals associated with the newly promoted release:

- Railway deployment status `FAILED`;
- Railway deployment status `CRASHED`;
- OOM-killed deployment;
- frontend fails `/healthz` after deployment and does not recover within the defined verification window;
- a newly live deployment transitions into a clear service failure shortly after promotion.

The worker state `SLEEPING` is explicitly healthy when sleep mode is enabled.

### 10.2 No automatic rollback for ambiguous/transient signals

The first implementation must not auto-rollback solely because of:

- isolated HTTP 5xx responses;
- Gemini/provider/API transient errors;
- temporary external network failure;
- a single user request error when service health is otherwise good.

Those conditions notify the Guardian but require evidence before rollback policy expands.

### 10.3 Known-good target

Before each promotion, store enough metadata to identify the currently active known-good deployment per service.

For each service track:

- Railway service ID;
- environment ID;
- current known-good deployment ID;
- source/promotion commit;
- verification timestamp.

A new deployment is promoted to `known-good` only after successful Railway status and health verification.

### 10.4 Rollback action

If the new release meets a rollback trigger:

1. identify the immediately previous known-good deployment for that service;
2. execute Railway rollback/redeployment to that known-good build;
3. verify deployment status;
4. verify health (`/healthz` frontend, `/health` worker when awake/applicable);
5. record the incident and restored deployment;
6. notify the user with failing deployment, restored deployment, and likely cause when available.

### 10.5 Loop protection

Rollback automation must include:

- at most one automatic rollback attempt per failing deployment ID;
- no rollback of a rollback without explicit new evidence/user action;
- stop-and-notify if the known-good recovery also fails;
- persistent incident marker/state so hourly Guardian runs do not repeat the same rollback endlessly.

## 11. Rollback controller placement

Recommended first implementation: keep detection/orchestration in the existing GSF Guardian/ChatGPT automation layer because it already has authenticated GitHub and Railway access and can inspect live deployment objects without storing a new Railway secret in the repository.

Repository code should provide machine-readable state/metadata and clear policy, while privileged Railway rollback remains outside GitHub Actions unless a later requirement justifies introducing a dedicated Railway token/secret.

This minimizes secret sprawl and reduces the chance that a compromised CI workflow gains unnecessary production rollback credentials.

## 12. Production Gate changes

The existing gate remains the only runtime promotion path.

Required changes are limited to making the pipeline aware of the coordination system where useful, for example:

- optionally validate claim metadata format when claim files change;
- ensure task/coordination documentation itself does not trigger Railway runtime promotion;
- preserve existing stale-main protection before marker promotion;
- do not auto-merge conflicting feature branches.

The gate must continue to fail closed.

## 13. Merge policy

Preferred policy:

- feature work happens on dedicated branches;
- PRs/checks are used for integration;
- runtime-changing merges to `main` trigger Production Gate;
- marker commits remain the only Railway trigger;
- documentation/coordination-only commits should not create unnecessary Railway deploys.

If GitHub plan/repository permissions prevent enforcing branch protection server-side, the repository tooling and agent rules still enforce the same workflow behaviorally.

## 14. Observability and incident record

Add a machine-readable coordination directory such as:

`.gsf/`

with subdirectories:

- `.gsf/claims/`
- `.gsf/incidents/`
- `.gsf/state/`

No secrets are stored there.

Rollback incidents should record:

- failing deployment ID;
- trigger/reason;
- previous known-good deployment ID;
- rollback result;
- timestamps;
- verification result.

These files support cross-chat continuity and prevent repeated rollback loops.

## 15. Safety invariants

The implementation must preserve all of the following:

1. Untested runtime code does not deploy to Railway.
2. A failing Production Gate does not update Railway markers.
3. One chat does not silently overwrite another chat's active ownership.
4. `main` is not used as a shared scratch branch.
5. A rollback target must be a previously verified known-good deployment.
6. `SLEEPING` worker is not treated as a failure by itself.
7. Automatic rollback executes at most once for the same failing deployment.
8. If rollback recovery fails, automation stops and notifies instead of looping.
9. No Railway/GitHub secrets are committed to the repository.
10. LIVE/SUCCESS claims always require fresh evidence.

## 16. Testing strategy

### Coordination tests

- branch-name uniqueness;
- claim creation and schema validation;
- conflict detection for exact and pattern-overlapping paths;
- non-overlapping claims allowed concurrently;
- stale/handoff/completed claim handling;
- status update preserves other tasks' data.

### Pipeline tests

- runtime merge with passing gate writes correct marker;
- failing gate writes no marker;
- documentation/claim-only commit produces no Railway runtime marker;
- stale main commit cannot promote after a newer main exists.

### Rollback policy tests

Use deterministic fake deployment snapshots/state tests for:

- SUCCESS → no rollback;
- FAILED → rollback eligible;
- CRASHED → rollback eligible;
- OOM → rollback eligible;
- worker SLEEPING → healthy/no rollback;
- ambiguous 5xx → notify-only/no rollback;
- repeated Guardian check for same failing deployment → no second rollback;
- rollback target failure → stop and escalate.

A live destructive rollback test is not required against healthy production. Production verification should use non-destructive status inspection plus the next naturally failing deployment if/when one occurs, or an explicitly approved controlled test environment later.

## 17. Delivery phases

### Phase A — parallel task isolation

- `.gsf/claims/` schema and helpers;
- branch/worktree bootstrap/finish tooling;
- AGENTS/PROJECT_STATUS integration;
- conflict tests.

### Phase B — rollback state and policy

- known-good state model;
- incident model;
- rollback decision tests;
- Guardian instructions updated to perform one guarded rollback for hard failures.

### Phase C — one-command orchestration

- compose bootstrap → implementation handoff → tests → integration → gate → deploy verification → rollback/handoff into one documented workflow;
- keep privileged deployment actions behind existing authenticated connectors/automation.

## 18. Acceptance criteria

The system is accepted when:

- two non-overlapping chat tasks can run concurrently on distinct branches with distinct claims;
- an overlapping task is blocked with a clear ownership conflict;
- a completed task leaves a factual handoff in project status without overwriting another task;
- a runtime change cannot trigger Railway before Production Gate passes;
- the known-good Railway deployment is identifiable at all times;
- hard failure policy can choose exactly one previous known-good rollback target and suppress duplicate rollback attempts;
- worker sleep does not trigger an incident;
- the user can give a single task request and the documented automation path has a deterministic next step from start through production verification.

## 19. Recommended implementation choice

Use repository-native branch/claim tooling plus the existing Production Gate and marker deploys, while keeping privileged Railway rollback in the existing Guardian/connector layer.

This delivers the safety and convenience goals with the smallest new operational surface, avoids adding production secrets to CI, and builds directly on infrastructure that is already proven live.
