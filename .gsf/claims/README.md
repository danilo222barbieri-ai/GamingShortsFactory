# GSF claim registry

`.gsf/claims/index.json` is the global ownership registry for parallel coding tasks.

## States

- `active`: task owns its declared paths and blocks overlaps.
- `handoff`: ownership is still reserved while another agent takes over; blocks overlaps.
- `completed`: historical record, no longer blocks.
- `abandoned`: stopped task, historical record, no longer blocks.

## Rules

1. Acquire a claim with `python tools/gsf_task.py start` before product edits.
2. The coordinator refreshes `origin/main`, checks all blocking claims, and pushes the coordination update optimistically.
3. A non-fast-forward race causes a refresh and a new conflict check; it never overwrites the other task.
4. Product work happens only on the branch/worktree returned after the claim is acquired.
5. Never delete a stale claim merely because it is old. Verify its branch/PR state and mark it `abandoned` or complete an explicit handoff.
6. Never store secrets or personal data in claims.

Coordination-only `.gsf/**` commits are excluded from the heavyweight Production Gate and Railway runtime promotion.
