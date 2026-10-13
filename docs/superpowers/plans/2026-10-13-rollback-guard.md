# Automatic Rollback Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically recover from a clearly bad new Railway release by restoring the immediately previous verified known-good deployment exactly once.

**Architecture:** Repository code defines deterministic rollback policy/state but holds no Railway secret. The existing authenticated GSF Guardian performs privileged Railway inspection/redeploy actions, writes incident/known-good metadata through GitHub, and refuses ambiguous/transient rollback triggers.

**Tech Stack:** Python 3.12 stdlib, JSON state files, GitHub repository, Railway deployment connector, ChatGPT automation `GSF Guardian`.

**Spec:** `docs/superpowers/specs/2026-10-13-parallel-work-rollback-one-command-design.md`

## Global Constraints

- Roll back only hard failures: FAILED, CRASHED, OOM, or sustained frontend health failure tied to the new release.
- Worker `SLEEPING` with sleep mode enabled is healthy.
- Isolated 5xx/provider/network errors are notify-only.
- Rollback target must already be recorded as verified known-good.
- At most one automatic rollback attempt per failing deployment ID.
- If recovery fails, stop and notify; never loop.
- No production credentials in repository files.

## Review Focus

- A service that is `SLEEPING` but configured to sleep must never become rollback-eligible.
- A failure for an older superseded deployment must not roll back the currently healthy deployment.
- Missing/corrupt known-good state must fail closed: notify, do not guess a rollback target.
- Repeated hourly checks of the same failure must not trigger repeated redeploys.
- A rollback deployment that itself fails must be marked escalated and excluded from automatic recursive rollback.

---

### Task 1: Deterministic rollback policy

**Files:**
- Create: `tools/gsf_rollback_policy.py`
- Create: `tools/test_gsf_rollback_policy.py`

**Interfaces:**
- Produces: `RollbackDecision` dataclass; `classify_service_state(service: dict, sleep_enabled: bool) -> str`; `should_rollback(current: dict, incident_index: dict, known_good: dict) -> RollbackDecision`; `incident_key(service_id: str, deployment_id: str) -> str`.

- [ ] **Step 1: Write failing tests** for SUCCESS, FAILED, CRASHED, OOM, sustained unhealthy frontend, worker SLEEPING, isolated 5xx notify-only, stale deployment failure, missing known-good, duplicate incident, and failed recovery escalation.

- [ ] **Step 2: Run tests to verify RED**

Run: `python tools/test_gsf_rollback_policy.py`
Expected: FAIL because policy module does not exist.

- [ ] **Step 3: Implement minimal pure policy** with decision actions exactly `none`, `notify`, `rollback`, `escalate`; include `reason`, `service_id`, `failing_deployment_id`, and optional `target_deployment_id`.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `python tools/test_gsf_rollback_policy.py`
Expected: PASS.

- [ ] **Step 5: Commit**

`git add tools/gsf_rollback_policy.py tools/test_gsf_rollback_policy.py && git commit -m "feat: add deterministic GSF rollback policy"`

---

### Task 2: Known-good and incident state schema

**Files:**
- Create: `.gsf/state/known-good.json`
- Create: `.gsf/incidents/index.json`
- Create: `.gsf/state/README.md`
- Extend test: `tools/test_gsf_rollback_policy.py`

**Interfaces:**
- Known-good record fields: `service_id`, `environment_id`, `deployment_id`, `promotion_commit`, `verified_at`, `health_endpoint`, `state`.
- Incident record fields: `key`, `service_id`, `failing_deployment_id`, `trigger`, `target_deployment_id`, `attempt_count`, `status`, `created_at`, `updated_at`, `recovery_deployment_id`, `verification`.

- [ ] **Step 1: Add failing schema tests** asserting required keys/types and forbidding secret-like keys (`token`, `password`, `secret`, `api_key`).

- [ ] **Step 2: Run tests to verify RED**

Run: `python tools/test_gsf_rollback_policy.py`
Expected: FAIL on missing state files/schema helpers.

- [ ] **Step 3: Add empty/initial state documents** with current verified frontend/worker service identifiers only when backed by fresh live evidence during implementation; otherwise leave service records empty and require bootstrap verification.

- [ ] **Step 4: Implement schema validation helpers** in `tools/gsf_rollback_policy.py`.

- [ ] **Step 5: Run tests to verify GREEN**

Run: `python tools/test_gsf_rollback_policy.py`
Expected: PASS.

- [ ] **Step 6: Commit**

`git add .gsf/state .gsf/incidents tools/gsf_rollback_policy.py tools/test_gsf_rollback_policy.py && git commit -m "feat: add GSF known-good and incident state"`

---

### Task 3: Guardian hard-failure rollback contract

**Files:**
- Modify: `PROJECT_STATUS.md`
- Create: `docs/runbooks/gsf-automatic-rollback.md`
- External update: existing `GSF Guardian` automation prompt.

**Interfaces:**
- Consumes: live GitHub main/gate state, Railway environment status/deployments, `.gsf/state/known-good.json`, `.gsf/incidents/index.json`, Task 1 policy semantics.
- Produces: exactly one Railway `redeploy` of the recorded previous known-good deployment for an eligible failure, followed by health verification and GitHub incident-state update.

- [ ] **Step 1: Write the rollback runbook** with exact decision order: verify failing deployment is current → classify → check incident duplicate → load known-good → redeploy exact target → verify → update incident/known-good → notify.

- [ ] **Step 2: Update Guardian automation instructions** so hard failures execute that guarded flow, while ambiguous failures remain notify-only; explicitly treat worker SLEEPING as normal.

- [ ] **Step 3: Add anti-loop wording** requiring a persistent incident check before every privileged redeploy and `attempt_count <= 1` for automatic action.

- [ ] **Step 4: Update `PROJECT_STATUS.md`** with rollback architecture and current known-good metadata only after fresh Railway verification.

- [ ] **Step 5: Verify non-destructively** by reading current Railway environment and evaluating policy against current healthy services; do not intentionally break production.

Expected: frontend healthy/no rollback; sleeping worker healthy/no rollback.

- [ ] **Step 6: Commit repository documentation/state changes**

`git add PROJECT_STATUS.md docs/runbooks/gsf-automatic-rollback.md .gsf/state .gsf/incidents && git commit -m "ops: wire GSF guarded rollback policy"`

---

### Task 4: End-to-end rollback simulation

**Files:**
- Extend: `tools/test_gsf_rollback_policy.py`

**Interfaces:**
- Consumes: complete policy/state model.
- Produces: deterministic simulation proving one-and-only-one recovery attempt.

- [ ] **Step 1: Add scenario test**: known-good A → new deployment B FAILED → decision rollback-to-A → incident attempt recorded → next identical check returns `none`/`notify` but never second rollback.

- [ ] **Step 2: Add recovery-failure scenario**: rollback attempt produces failed recovery C → decision becomes `escalate`, never rollback C again.

- [ ] **Step 3: Run full rollback suite**

Run: `python tools/test_gsf_rollback_policy.py`
Expected: PASS.

- [ ] **Step 4: Commit**

`git add tools/test_gsf_rollback_policy.py && git commit -m "test: prove GSF rollback anti-loop behavior"`
