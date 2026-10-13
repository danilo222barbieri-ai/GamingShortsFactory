# GSF one-command workflow

A normal **coding request** enters this one-command protocol unless the user explicitly asks for analysis/design only.

Example user request:

> Sistema il Game Editor mobile.

The agent must carry the work through the deterministic states below without asking the user to manually steer every technical transition.

## State machine

`INTAKE -> CLAIMED -> IMPLEMENTING -> TESTED -> INTEGRATING -> GATE -> DEPLOYING -> VERIFYING -> LIVE|BLOCKED|ROLLED_BACK -> HANDOFF`

### INTAKE

Read `AGENTS.md`, `PROJECT_STATUS.md`, fresh `main`, and the live claim registry. Derive the narrowest safe ownership scope and paths.

Exit evidence: scope and requested paths are explicit.

### CLAIMED

Acquire global ownership using `tools/gsf_task.py start` or the equivalent GitHub connector/API flow when a local Git CLI/worktree is not available. Connector-based execution must preserve the same fail-closed conflict semantics and create a dedicated `chat/<task>-<suffix>` branch.

Exit evidence: active claim + isolated branch/worktree exist.

### IMPLEMENTING

Inspect relevant source/tests and make product changes only inside the isolated task branch.

Exit evidence: intended implementation committed on the task branch.

### TESTED

Run the tests required by the touched area. Test failure stops progression and results in `BLOCKED` until corrected.

Exit evidence: concrete passing test output/CI status.

### INTEGRATING

Refresh current `main`, re-check ownership conflicts, rebase/revalidate stale assumptions when necessary, and create/update the integration PR or approved merge path.

Exit evidence: integration commit/PR is known and current.

### GATE

For runtime-impacting work, GSF Production Gate must pass. A failed gate means no Railway marker and production remains unchanged.

Exit evidence: Production Gate result tied to the integration commit.

### DEPLOYING

After a passing runtime gate, marker-based Railway promotion owns the deploy. Documentation/coordination-only work skips this state and proceeds directly toward handoff.

Exit evidence: Railway deployment ID or explicit no-runtime-deploy determination.

### VERIFYING

Verify Railway settled state and health. Frontend requires healthy `/healthz`; worker `SLEEPING` is valid when sleep mode is enabled. Hard new-release failure invokes the guarded rollback policy.

Exit evidence: current Railway state and health, or rollback evidence.

### LIVE

Use terminal status `LIVE` only when the requested runtime change is integrated, Production Gate passed, Railway deployment settled successfully, and fresh health evidence is positive.

### BLOCKED

Use terminal status `BLOCKED` for unresolved ownership conflict, required test failure, failed Production Gate, or another hard stop that leaves production unchanged.

### ROLLED_BACK

Use terminal status `ROLLED_BACK` only after a new bad release was restored to the exact verified previous known-good deployment and recovery health was re-verified.

### HANDOFF

Update factual project memory/status and complete or hand off the claim. If another person/agent or user decision is required, terminal status is `HANDOFF_REQUIRED`.

## Exact terminal statuses

The only user-facing terminal status labels for this protocol are:

- `LIVE`
- `BLOCKED`
- `ROLLED_BACK`
- `HANDOFF_REQUIRED`

They are evidence labels, never optimistic progress labels.

## Stop conditions

Stop automatic forward progression when any of these occurs:

- ownership conflict cannot be narrowed or handed off safely;
- a genuinely required user/product decision is missing;
- relevant tests fail and cannot be corrected within the task;
- Production Gate fails;
- rollback recovery fails;
- known-good rollback state is missing/corrupt for an eligible failure.

Do not bypass these stops to manufacture a successful terminal status.

## GitHub handoff and safe-close boundary

**GitHub handoff** begins when the relevant commit/PR/push exists on GitHub and GitHub CI/Railway/automation owns the next deterministic step.

After GitHub handoff, GitHub Actions and Railway continue independently of whether the ChatGPT app remains open. The Guardian can perform its scheduled monitoring according to its automation schedule.

**Before GitHub handoff there is no guarantee** that a normal chat continues working if the app/session is closed. Never tell the user that work is safely continuing in the background before this boundary has actually been reached.

## Integration evidence required before GitHub handoff

Before handing runtime work to CI, confirm all of the following:

1. the active claim is still valid;
2. no unresolved ownership overlap exists;
3. relevant branch tests passed;
4. latest `main` has been refreshed and stale assumptions reconciled;
5. the exact integration commit/PR is known.

## Frontend + worker changes

If one request touches both frontend and worker runtime paths, claim both areas and expect the Production Gate to update both deployment markers after PASS. Verify each resulting Railway service independently.

## Documentation-only changes

If the task changes only coordination/status/runbook documentation excluded from runtime deployment, do not wait for or invent a Railway deployment. Complete the claim with factual test/CI evidence and handoff.

## Failure recovery

Hard production failures follow `docs/runbooks/gsf-automatic-rollback.md`. Ambiguous 5xx/provider/network signals remain notify-only and do not automatically roll back.
