# SDD ledger — plan: docs/superpowers/plans/2026-10-13-v403-app-stability-flow-redesign.md

Baseline: `845a36f5c586756743fe6f41b1f07cda3fb5246d`.

Task 1 RED: GitHub Actions run `38464561913` failed in `V403 behavioral contract` before production implementation.

Ruling: the repository source `web/ai_v221_component/index.html` must retain the historical V319/V320-compatible candidate structure until the final V403 runtime migration executes. `start_web.sh` currently runs legacy V319/V320 verification before late runtime migrations. Therefore V403 tests assert the *post-migration Motori output* produced by the V403 runtime patch chain, not require the pre-migration source file itself to have the old candidate DOM deleted. Visible/runtime Motori contains no final candidate cards after V403. Cost if wrong: fresh Railway boot could fail before V403 or Motori could still expose old results; both are covered by the V403 runtime migration test and production image gate.

Task 2 GREEN: `web/app_flow_v403.py` owns the deterministic metadata-only state machine. Analysis/render issue tokens are idempotent; selection, route, final asset, and last-valid profile are reconciled without starting duplicate work. `web/project_state_v157.py` persists the snapshot through the existing lightweight V158 envelope.

Task 3 GREEN: `web/moments_v403_component/index.html` owns candidate selection/fullscreen/internal scrolling and immediately persists selection through `/project/flow`. Historical inline Motori results are retired by the final surface migration only after V319/V320 gates.

Tasks 4–6 GREEN: the public `web/apply_v403_flow.py` is now a small stable wrapper around frozen `apply_v403_flow_core.py`. Production order is: core durable flow/API/routes -> last-valid profile recovery -> single-flight Creator Hub resume -> selected-candidate Editor handoff -> Motori/Crea Short visual ownership. `start_web.sh` still invokes exactly one V403 migrator.

CI evidence: Actions run `38467373129` passed the complete V403 behavioral contract on commit `fe75dbe93c3c823ed80812313ff1658994cac4e9`. On expanded run `38467497963`, job `v403-contract` passed V403 profile/resume plus V402/V401/V400 regressions. Its `production-image` job failed before project build because public ECR returned HTTP 429 `Data limit exceeded`; no source/build step had failed. The V403 workflow now retries the same official `python:3.12-slim` tag from Docker Hub only when the primary public ECR registry is unavailable.

Scope review at `f9280a0aeee02f0447a5ee9bd14c16df9d89b14a`: branch is based exactly on V402 and only changes V403 docs/workflow/state/flow/tests, one metadata persistence extension, and the V403 boot hook. No Home, V402 ranking, render quality, worker runtime, or Editor component source was modified.
