# One-Command Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn one natural-language coding request into a deterministic GSF workflow from isolated task bootstrap through tested integration, Railway verification, rollback handling, and project-memory handoff.

**Architecture:** This is an agent protocol, not a fake local AI daemon. `AGENTS.md` makes orchestration mandatory; `tools/gsf_task.py` supplies deterministic claim/branch/status mechanics; GitHub Production Gate and Railway markers remain the runtime handoff; Guardian handles post-deploy recovery.

**Tech Stack:** Repository instructions, Python task CLI from Parallel Task Isolation plan, GitHub Actions, Railway, GSF Guardian automation.

**Spec:** `docs/superpowers/specs/2026-10-13-parallel-work-rollback-one-command-design.md`

## Global Constraints

- A user request should not require manual prompting at every pipeline stage when intent/safety are already clear.
- Normal chat is not claimed to run indefinitely after app closure; background continuity begins only after work is handed to GitHub/Railway/automation.
- Product edits require a valid active claim and isolated branch.
- Integration requires relevant tests and no unresolved ownership conflict.
- Runtime production still requires GSF Production Gate and marker-based Railway deploy.
- Rollback follows the separate guarded rollback policy; ambiguous failures do not auto-rollback.

## Review Focus

- Vague requests whose file scope cannot be safely derived must stop before claiming broad overlapping ownership rather than grabbing the whole repo.
- A request that touches both frontend and worker must claim both scopes and expect both Railway markers after a passing gate.
- Documentation-only work must complete without waiting for a Railway deploy that should never occur.
- If a newer main commit appears while a task is finishing, the agent must refresh/rebase/revalidate instead of merging stale assumptions.
- If the chat closes before GitHub handoff, the system must not falsely report that work will continue automatically.

---

### Task 1: Define the mandatory one-command agent state machine

**Files:**
- Modify: `AGENTS.md`
- Create: `docs/runbooks/gsf-one-command-workflow.md`

**Interfaces:**
- Consumes: `tools/gsf_task.py start|status|finish`, Production Gate, Railway marker deploys, rollback guard.
- Produces: ordered states `INTAKE -> CLAIMED -> IMPLEMENTING -> TESTED -> INTEGRATING -> GATE -> DEPLOYING -> VERIFYING -> LIVE|BLOCKED|ROLLED_BACK -> HANDOFF`.

- [ ] **Step 1: Add the state machine to the runbook** with entry/exit evidence for each state.

- [ ] **Step 2: Update `AGENTS.md`** so a coding request automatically enters this protocol unless the user explicitly asks for analysis/design only.

- [ ] **Step 3: Define stop conditions**: ownership conflict, missing required user decision, test failure, Production Gate failure, failed rollback recovery.

- [ ] **Step 4: Define user-facing terminal statuses** exactly `LIVE`, `BLOCKED`, `ROLLED_BACK`, `HANDOFF_REQUIRED`, each backed by evidence.

- [ ] **Step 5: Commit**

`git add AGENTS.md docs/runbooks/gsf-one-command-workflow.md && git commit -m "docs: define GSF one-command agent pipeline"`

---

### Task 2: Add machine-readable task status output

**Files:**
- Modify: `tools/gsf_task.py`
- Create: `.gsf/state/task-status.schema.json`
- Extend: `tools/test_gsf_claims.py`

**Interfaces:**
- Produces CLI: `python tools/gsf_task.py status --claim <id> --json` returning keys `claim_id`, `branch`, `scope`, `state`, `paths`, `commit`, `pr`, `tests`, `gate`, `railway`, `terminal_status`, `updated_at`.

- [ ] **Step 1: Write failing tests** for JSON status shape, missing claim, completed claim, and preservation of unknown concurrent claims.

- [ ] **Step 2: Run tests to verify RED**

Run: `python tools/test_gsf_claims.py`
Expected: FAIL for missing status interface.

- [ ] **Step 3: Implement status serialization** without storing secrets or credentials.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `python tools/test_gsf_claims.py`
Expected: PASS.

- [ ] **Step 5: Commit**

`git add tools/gsf_task.py tools/test_gsf_claims.py .gsf/state/task-status.schema.json && git commit -m "feat: expose GSF task orchestration status"`

---

### Task 3: Make integration/gate/deploy handoff explicit

**Files:**
- Modify: `docs/runbooks/gsf-one-command-workflow.md`
- Modify: `PROJECT_STATUS.md`
- Create: `tools/test_gsf_one_command_contract.py`

**Interfaces:**
- Consumes: latest main, branch test evidence, Production Gate result, Railway deployment state.
- Produces: deterministic rules for when the agent can move from branch work to CI handoff and when the user may safely close the app.

- [ ] **Step 1: Write failing static contract tests** asserting the runbook contains required handoff boundaries and never promises background continuation before GitHub handoff.

- [ ] **Step 2: Run to verify RED**

Run: `python tools/test_gsf_one_command_contract.py`
Expected: FAIL before final runbook wording is present.

- [ ] **Step 3: Document the safe-close boundary**: once the relevant commit/PR/push is on GitHub and CI owns the next step, closing ChatGPT does not stop GitHub/Railway; before that point no guarantee is made.

- [ ] **Step 4: Document integration evidence**: tests pass, claim valid, overlap clear, current main refreshed, integration commit known.

- [ ] **Step 5: Update `PROJECT_STATUS.md`** to point future chats at the one-command protocol.

- [ ] **Step 6: Run contract test**

Run: `python tools/test_gsf_one_command_contract.py`
Expected: PASS.

- [ ] **Step 7: Commit**

`git add docs/runbooks/gsf-one-command-workflow.md PROJECT_STATUS.md tools/test_gsf_one_command_contract.py && git commit -m "ops: codify GSF CI handoff boundary"`

---

### Task 4: Full protocol verification without breaking production

**Files:**
- Tests only / no intentional production fault.

**Interfaces:**
- Consumes: Phase A claims, Phase B rollback policy, tasks 1-3 protocol.
- Produces: proof that one request has one deterministic path and coordination-only operations do not deploy runtime code.

- [ ] **Step 1: Run all coordination tests**

Run: `python tools/test_gsf_claims.py && python tools/test_gsf_coordination_gate.py`
Expected: PASS.

- [ ] **Step 2: Run rollback tests**

Run: `python tools/test_gsf_rollback_policy.py`
Expected: PASS.

- [ ] **Step 3: Run orchestration contract**

Run: `python tools/test_gsf_one_command_contract.py`
Expected: PASS.

- [ ] **Step 4: Run existing production structural regression**

Run: `python web/test_v397_production_hardening.py .`
Expected: PASS.

- [ ] **Step 5: Perform a non-runtime dry task** using the new claim/bootstrap/status/finish protocol and verify no Railway runtime deployment marker changes.

- [ ] **Step 6: Record handoff** in `PROJECT_STATUS.md` only after fresh GitHub/Railway evidence, then mark the implementation claim completed.

- [ ] **Step 7: Commit final verification notes**

`git add PROJECT_STATUS.md && git commit -m "docs: record verified GSF one-command workflow"`
