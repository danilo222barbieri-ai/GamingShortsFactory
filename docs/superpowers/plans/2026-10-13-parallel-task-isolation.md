# Parallel Task Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every GSF coding chat an isolated branch/worktree plus an atomic global ownership claim so parallel chats cannot silently collide.

**Architecture:** Product code stays on dedicated `chat/<task>-<suffix>` branches. Coordination metadata is the only direct-to-`main` exception, stored under `.gsf/claims/` and updated with optimistic concurrency/retry so two overlapping tasks cannot both acquire ownership.

**Tech Stack:** Python 3.12 stdlib, Git CLI, JSON, GitHub repository, existing GitHub Actions Production Gate.

**Spec:** `docs/superpowers/specs/2026-10-13-parallel-work-rollback-one-command-design.md`

## Global Constraints

- Product code must never be edited directly on shared `main` by parallel tasks.
- Coordination-only `.gsf/**` commits must not trigger Railway runtime deployment.
- Claim acquisition must fail closed and be race-safe.
- No secrets or personal data in claim files.
- `PROJECT_STATUS.md` remains human-readable project memory, not the lock primitive.
- `LIVE`, `SUCCESS`, `fixed`, and `done` require fresh evidence.

## Review Focus

- Two concurrent overlapping claim attempts: exactly one may succeed; the loser must re-read and report conflict.
- Glob-vs-exact path overlap such as `web/fix_v*_mobile_editor_*.py` versus `web/fix_v403_mobile_editor_x.py` must conflict.
- A claim update racing with another non-overlapping claim must preserve both claims after retry.
- A stale/abandoned claim must never be silently deleted just because of age.
- `.gsf/**`-only commits must not launch the heavyweight Production Gate or Railway marker promotion.

---

### Task 1: Pure claim model and overlap engine

**Files:**
- Create: `tools/gsf_claims.py`
- Create: `tools/test_gsf_claims.py`

**Interfaces:**
- Produces: `Claim` dataclass; `normalize_paths(paths: list[str]) -> list[str]`; `patterns_overlap(a: str, b: str) -> bool`; `find_conflicts(requested_paths: list[str], active_claims: list[Claim]) -> list[Claim]`; `validate_claim_dict(data: dict) -> Claim`.

- [ ] **Step 1: Write failing tests** for exact overlap, glob/exact overlap, glob/glob overlap, non-overlap, malformed state, and duplicate path normalization.

- [ ] **Step 2: Run tests to verify RED**

Run: `python tools/test_gsf_claims.py`
Expected: FAIL because `tools.gsf_claims` does not exist.

- [ ] **Step 3: Implement the minimal pure claim engine** in `tools/gsf_claims.py` with claim states exactly `active`, `handoff`, `completed`, `abandoned`; only `active` and `handoff` participate in conflict blocking.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `python tools/test_gsf_claims.py`
Expected: PASS.

- [ ] **Step 5: Commit**

`git add tools/gsf_claims.py tools/test_gsf_claims.py && git commit -m "feat: add GSF claim conflict engine"`

---

### Task 2: Atomic global claim acquisition and branch bootstrap

**Files:**
- Create: `tools/gsf_task.py`
- Create: `.gsf/claims/index.json`
- Extend test: `tools/test_gsf_claims.py`

**Interfaces:**
- Consumes: Task 1 `Claim`, `find_conflicts`, `validate_claim_dict`.
- Produces: `start_task(scope: str, paths: list[str], owner: str | None = None) -> Claim`; `finish_task(claim_id: str, state: str, evidence: dict) -> None`; CLI commands `start`, `finish`, `status`.

- [ ] **Step 1: Add failing tests** using temporary local bare Git repositories for: first claim succeeds, non-overlapping second claim survives concurrent-main advancement, overlapping loser retries then exits with conflict, and branch names remain unique.

- [ ] **Step 2: Run tests to verify RED**

Run: `python tools/test_gsf_claims.py`
Expected: FAIL because task bootstrap functions are missing.

- [ ] **Step 3: Implement atomic coordination update**: fetch `origin/main`, read latest `.gsf/claims/index.json`, check conflict, create a coordination commit based on current `origin/main`, push to `main`; on non-fast-forward, fetch and retry conflict detection before any product branch/worktree is created.

- [ ] **Step 4: Implement isolated product branch creation** only after the claim push succeeds, naming `chat/<sanitized-scope>-<4+ hex suffix>` from refreshed `origin/main`.

- [ ] **Step 5: Implement `finish`** so claim state changes use the same retry/fail-closed update path and preserve other concurrent claims.

- [ ] **Step 6: Run tests to verify GREEN**

Run: `python tools/test_gsf_claims.py`
Expected: PASS including simulated race.

- [ ] **Step 7: Commit**

`git add tools/gsf_task.py tools/test_gsf_claims.py .gsf/claims/index.json && git commit -m "feat: add atomic GSF task bootstrap"`

---

### Task 3: Make coordination commits invisible to runtime deployment

**Files:**
- Modify: `.github/workflows/v397-production-gate.yml`
- Create: `tools/test_gsf_coordination_gate.py`

**Interfaces:**
- Consumes: `.gsf/**` coordination paths.
- Produces: GitHub Actions trigger/promotion contract where coordination-only changes do not run runtime deployment logic.

- [ ] **Step 1: Write a failing static contract** asserting `paths-ignore` includes `.gsf/**` and that the marker-promotion path matcher cannot classify `.gsf/**`, `PROJECT_STATUS.md`, or design/plan docs as frontend/worker runtime files.

- [ ] **Step 2: Run test to verify RED**

Run: `python tools/test_gsf_coordination_gate.py`
Expected: FAIL on current workflow.

- [ ] **Step 3: Update Production Gate trigger/promotion rules** to ignore `.gsf/**` plus explicitly non-runtime status/spec/plan docs without weakening runtime-path coverage.

- [ ] **Step 4: Run static contract and existing structural contract**

Run: `python tools/test_gsf_coordination_gate.py && python web/test_v397_production_hardening.py .`
Expected: PASS.

- [ ] **Step 5: Commit**

`git add .github/workflows/v397-production-gate.yml tools/test_gsf_coordination_gate.py && git commit -m "ci: exclude GSF coordination metadata from runtime gate"`

---

### Task 4: Make the protocol mandatory for agents

**Files:**
- Modify: `AGENTS.md`
- Modify: `PROJECT_STATUS.md`
- Create: `.gsf/claims/README.md`

**Interfaces:**
- Consumes: `python tools/gsf_task.py start|finish|status`.
- Produces: mandatory startup/handoff instructions for all future coding chats.

- [ ] **Step 1: Update `AGENTS.md`** so every coding task must acquire a claim before product edits and must use its returned branch/worktree.

- [ ] **Step 2: Update `PROJECT_STATUS.md`** so the Active Work section points to `.gsf/claims/index.json` for live ownership and keeps only high-level summaries.

- [ ] **Step 3: Document claim states and emergency handoff rules** in `.gsf/claims/README.md`.

- [ ] **Step 4: Verify documentation contains no secrets and matches CLI names**

Run: `python -m py_compile tools/gsf_claims.py tools/gsf_task.py && python tools/test_gsf_claims.py && python tools/test_gsf_coordination_gate.py`
Expected: PASS.

- [ ] **Step 5: Commit**

`git add AGENTS.md PROJECT_STATUS.md .gsf/claims/README.md && git commit -m "docs: enforce isolated GSF task ownership"`
