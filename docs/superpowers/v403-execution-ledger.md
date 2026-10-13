# SDD ledger — plan: docs/superpowers/plans/2026-10-13-v403-app-stability-flow-redesign.md

Baseline: `845a36f5c586756743fe6f41b1f07cda3fb5246d`.

Task 1 RED: GitHub Actions run `38464561913` failed in `V403 behavioral contract` before production implementation.

Ruling: the repository source `web/ai_v221_component/index.html` must retain the historical V319/V320-compatible candidate structure until the final V403 runtime migration executes. `start_web.sh` currently runs legacy V319/V320 verification before late runtime migrations. Therefore V403 tests will assert the *post-migration Motori output* produced by `apply_v403_flow.patch_ai_text`, not require the pre-migration source file itself to have the old candidate DOM deleted. Visible/runtime Motori still must contain no final candidate cards. Cost if wrong: fresh Railway boot could fail before V403 or Motori could still expose old results; both are covered by the V403 runtime migration test and production build gate.
