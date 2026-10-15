# CLAUDE.md — Gaming Shorts Factory

The binding rules for every agent live in `AGENTS.md` and are imported here:

@AGENTS.md

Before touching product code, also read `PROJECT_STATUS.md` completely
(canonical project memory) and `docs/runbooks/gsf-one-command-workflow.md`.
If live GitHub/Railway evidence disagrees with those files, trust the live
evidence and say so.

## Quick orientation

- **Stack:** Python + Streamlit behind nginx, ffmpeg, faster-whisper, boto3
  (S3-compatible bucket), pywebpush; YouTube / TikTok / Instagram publishing.
  Entry point `app.py`; web components and versioned patches under `web/`;
  shared core in `gsf_core/`; coordination tooling in `tools/`.
- **Railway project:** `gaming-shorts-factory`, environment `production`.
  - Frontend service `gaming-shorts-factory-v79` — health `/healthz`.
  - Worker service `gsf-ai-worker` — health `/health` when awake;
    `SLEEPING` is expected (sleep mode), not a failure.
- **Deploys:** never deploy by hand. The **GSF Production Gate**
  (`.github/workflows/v397-production-gate.yml`) promotes a tested SHA by
  updating `.railway/frontend-deploy.txt` / `.railway/worker-deploy.txt`;
  Railway only redeploys on changes to those markers.
- **Verifying production:** prefer the Railway MCP tools (status,
  deployments, logs, metrics) and `gh run list` / `gh run view` for CI.
  Report `LIVE`/`SUCCESS` only with fresh evidence.

## Practical notes

- Claims: `python tools/gsf_task.py start|finish|status`. The registry
  validator requires a **non-empty `paths` list on every claim, including
  completed ones** — never write `"paths": []`, or the tool rejects the
  whole registry for everyone.
- The repo may be a shallow clone: `git fetch origin main` (and rebase)
  before pushing a branch, or the push can be rejected as too large.
- Running the tools creates `tools/__pycache__/`; delete it, never commit it.
- Coordination-only commits (`.gsf/**`, `PROJECT_STATUS.md`, runbooks) use
  the `coord:` prefix and `[skip ci]`.
- Never store secrets, tokens or personal data in the repo, `.gsf/**` or
  status files.
- The project owner writes in Italian: reply to them in Italian; code,
  commits and repo docs stay in English unless asked otherwise.
