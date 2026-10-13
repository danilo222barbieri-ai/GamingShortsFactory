# V401 execution ledger

- Base: V400 `6792749447b24c590f350036501235891fae91da`.
- Workspace: isolated GitHub branch `v401-performance-stability` (no local checkout available in this session).
- Task 1 RED: run `38445405234` failed exactly with `ModuleNotFoundError: No module named 'job_state_v401'` before implementation.
- Ruling: worker integration is applied through an idempotent build-time patch (`fix_v401_worker_state.py`) instead of replacing the full `ai_worker_server.py` source in the repository. This follows GSF's existing migration/fix-script architecture and reduces regression risk; the generated worker source is compiled during Docker build.
- Ruling: queued job persistence is performed outside `JOBS_LOCK`; duplicate inspection stays inside the lock. This avoids reacquiring the non-reentrant lock through `_set_job_state`.
- GREEN: run `38445912187` completed with V401 contract, V400 regression, V399 regression, and syntax guard all successful.
- Diff review against V400: branch is ahead only, with no Home/Game Bar/Creator Hub/Game Editor or V399/V400 quality-policy files modified.
