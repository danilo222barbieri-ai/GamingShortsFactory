# AGENTS.md — Gaming Shorts Factory

These rules apply to every coding agent, Codex task, and technical chat working in this repository.

## Before touching code

1. Read `PROJECT_STATUS.md` completely.
2. Refresh `main` and inspect the latest commits.
3. Check `PROJECT_STATUS.md` → **Active work** for overlapping ownership.
4. Inspect the relevant source and tests before editing.
5. For parallel work, use a dedicated branch/worktree. Do not use `main` as a shared scratch branch.

## Ownership and parallel work

- One independent chat/agent = one branch/worktree.
- Keep ownership narrow and explicit: e.g. Home/UI, Game Editor, AI/worker, CI/deploy.
- Do not edit files already owned by another active task unless there is an explicit handoff.
- If two tasks require the same file, serialize them or merge/rebase one before the other continues.

## Production safety

- Runtime changes must pass **GSF Production Gate** before Railway promotion.
- Do not manually bypass the `.railway/frontend-deploy.txt` or `.railway/worker-deploy.txt` promotion mechanism unless the user explicitly requests an emergency intervention.
- Do not call a change `LIVE`, `SUCCESS`, `fixed`, or `done` until fresh evidence confirms it.
- Frontend health is verified with `/healthz`; worker health with `/health`.
- A failed Production Gate means production must remain on the previous known-good deployment.

## Testing

- Run the tests relevant to the touched area.
- Preserve regression coverage already represented in the Production Gate.
- For runtime-impacting changes, verify the Production Gate result after merge to `main`.
- If Railway deploys, verify the resulting deployment/health before reporting success.

## PROJECT_STATUS.md is mandatory

At completion or handoff, update `PROJECT_STATUS.md` with factual evidence:

- branch
- scope/files
- commit or PR
- tests actually run
- merge state
- Production Gate result when applicable
- Railway deployment/status when applicable
- unresolved or unverified items

Before editing `PROJECT_STATUS.md`, fetch the latest version and preserve other chats' rows/notes.

Never store secrets, tokens, API keys, passwords, secret environment values, or personal data in `PROJECT_STATUS.md` or this file.

## Communication rule

If live evidence disagrees with an older chat, memory, note, or assumption, trust the live evidence, update `PROJECT_STATUS.md`, and state the discrepancy clearly. Never invent progress to fill a gap.
