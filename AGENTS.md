# AGENTS.md — Gaming Shorts Factory

These rules apply to every coding agent, Codex task, and technical chat working in this repository.

## One-command default for coding requests

Every **coding request** automatically enters the GSF **one-command** workflow in `docs/runbooks/gsf-one-command-workflow.md` unless the user explicitly asks for analysis/design only.

The agent owns the technical transitions from intake through claim, isolated implementation, tests, integration, Production Gate, Railway verification, guarded rollback when eligible, and factual handoff. Do not make the user manually prompt each intermediate technical step when intent and safety are already clear.

A normal chat must never promise background continuation before the documented GitHub handoff boundary has actually been reached.

## Before touching product code

1. Read `PROJECT_STATUS.md` completely.
2. Refresh `main` and inspect the latest commits.
3. Inspect `.gsf/claims/index.json` on the latest `main`.
4. Determine a narrow scope and the file/path patterns the task needs.
5. Acquire ownership before editing product code:

   `python tools/gsf_task.py start --scope "<scope>" --paths <path> [<path> ...]`

6. Work only on the returned `chat/<task>-<suffix>` branch/worktree.
7. Inspect relevant source and tests before editing.

If the claim command reports `BLOCKED`, do not edit overlapping files. Narrow the task, use an explicit handoff, or serialize the work.

When no local Git CLI/worktree is available, an authenticated GitHub connector/API may perform the equivalent claim + dedicated-branch protocol. It must preserve the same fail-closed conflict semantics and may not bypass ownership just because the local helper cannot run.

## Ownership and parallel work

- One independent coding chat/agent = one active claim + one dedicated branch/worktree.
- `.gsf/claims/index.json` is the live ownership registry; `PROJECT_STATUS.md` is the human-readable project memory, not the lock table.
- Claim acquisition is fail-closed. Product editing starts only after ownership is acquired.
- Keep ownership narrow and explicit: Home/UI, Game Editor, AI/worker, CI/deploy, etc.
- Do not edit paths blocked by another `active` or `handoff` claim without an explicit handoff.
- `completed` and `abandoned` claims are historical and do not block new work.
- If two tasks require the same file, serialize them or merge/rebase the first before the second continues.
- Product code must not use `main` as a shared scratch branch. Direct `main` updates are limited to coordination/status metadata under the documented protocol.

## Completing or handing off a task

Use:

`python tools/gsf_task.py finish --claim <claim-id> --state completed --evidence-json '<json>'`

Use `handoff` when another agent must continue the same ownership, and `abandoned` when work is intentionally stopped. Preserve factual evidence: commit/PR, tests, gate result and Railway state when applicable.

Machine-readable progress is available with:

`python tools/gsf_task.py status --claim <claim-id> --json`

The status payload must never invent test/gate/Railway success that has not been recorded as evidence.

## Production safety

- Runtime changes must pass **GSF Production Gate** before Railway promotion.
- Do not manually bypass `.railway/frontend-deploy.txt` or `.railway/worker-deploy.txt` unless the user explicitly requests an emergency intervention.
- Coordination-only `.gsf/**`, status and runbook updates must not trigger runtime deployment.
- Do not call a change `LIVE`, `SUCCESS`, `fixed`, or `done` until fresh evidence confirms it.
- Frontend health is verified with `/healthz`; worker health with `/health` when awake. A sleeping worker is not a failure when Railway sleep mode is enabled.
- A failed Production Gate means production remains on the previous known-good deployment.
- Hard post-deploy failures follow `docs/runbooks/gsf-automatic-rollback.md`; ambiguous 5xx/provider/network failures are notify-only.

## Testing

- Run tests relevant to the touched area.
- Preserve regression coverage already represented in the Production Gate.
- For runtime-impacting changes, verify the Production Gate after integration to `main`.
- If Railway deploys, verify deployment state and health before reporting success.

## PROJECT_STATUS.md is mandatory

At completion or handoff, update `PROJECT_STATUS.md` with factual evidence while preserving concurrent handoffs. Live ownership details stay in `.gsf/claims/index.json`.

Record when applicable:

- branch / claim
- scope/files changed
- commit or PR
- tests actually run
- merge state
- Production Gate result
- Railway deployment/status
- unresolved or unverified items

Never store secrets, tokens, API keys, passwords, secret environment values, or personal data in `PROJECT_STATUS.md`, `.gsf/**`, or this file.

## Communication rule

If live GitHub/Railway evidence disagrees with an older chat, memory, note, or assumption, trust the live evidence, update project state, and state the discrepancy clearly. Never invent progress to fill a gap.
