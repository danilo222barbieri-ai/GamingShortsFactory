# GSF automatic rollback runbook

This runbook governs privileged rollback actions for Gaming Shorts Factory production.

## Inputs

Always refresh these before deciding:

1. latest `main` commit and GSF Production Gate result;
2. Railway production environment status;
3. Railway latest/current deployment for the affected service;
4. `.gsf/state/known-good.json` from current `main`;
5. `.gsf/incidents/index.json` from current `main`.

Never infer a rollback target from an old chat.

## Decision order

1. Confirm the failing deployment is the service's current/newly promoted deployment. A failure belonging to a superseded deployment is not rollback-eligible.
2. Treat `gsf-ai-worker` state `SLEEPING` as healthy when Railway sleep mode is enabled.
3. Normalize the observed state and apply `tools/gsf_rollback_policy.py` semantics.
4. Hard rollback triggers are limited to `FAILED`, `CRASHED`, OOM-killed, or sustained frontend `/healthz` failure associated with the new release.
5. Isolated 5xx, Gemini/provider errors, temporary network errors, or a single request failure are notify-only.
6. Before any privileged Railway action, compute `<service_id>:<failing_deployment_id>` and inspect the incident index. If `attempt_count >= 1`, do not redeploy again.
7. Load the exact previous `deployment_id` from the verified known-good service record. Missing/corrupt known-good state means notify/escalate; never guess.
8. Redeploy that exact stored Railway deployment build once.
9. Verify the recovery deployment reaches a settled healthy state. Frontend must be online and `/healthz` healthy. Worker may be healthy-awake or expected `SLEEPING`.
10. Record the incident result. If recovery succeeds, retain/update verified known-good metadata with fresh evidence. If recovery fails, mark the incident escalated and stop.

## Anti-loop invariant

Automatic rollback attempt count is at most **1 per failing deployment ID**. A rollback deployment is never recursively rolled back by the same incident. Recovery failure produces escalation and notification, not another automatic action.

## Incident record

Record at minimum:

- `key`
- `service_id`
- `failing_deployment_id`
- `trigger`
- `target_deployment_id`
- `attempt_count`
- `status`
- `created_at`
- `updated_at`
- `recovery_deployment_id`
- `verification`

No secrets or credential values may be stored.

## Current authenticated controller

The first implementation keeps privileged Railway `redeploy` actions in the existing authenticated GSF Guardian / connector layer. GitHub repository files contain policy and state only; no Railway token is committed.
