# V105 execution ledger

- Task 1 telemetry: GREEN on staging build.
- Task 2 worker-aware prescan: GREEN on staging build.
- Task 3 adaptive upload/materialization: GREEN on staging build.
- Task 4 dedicated worker image: GREEN; dedicated image booted on Railway staging with bucket enabled.
- Task 5 render benchmark: RED pending on web staging.
- Production baseline remains V104.7.

- Render benchmark runner contract: GREEN. Railway benchmark execution: starting from a fresh snapshot so the configured benchmark start command is applied.

- Render benchmark diagnostic: combined 15s+30s run completed all 15s profiles, then 30s fixture FFmpeg exited silently. Hypothesis test: run 30s alone on a fresh container to distinguish codec failure from accumulated container pressure.

- Render benchmark completed: medium/CRF14/1-thread is the measured winner at both 15s and 30s; two-thread candidates are slower and use more memory.
- Dependency lock: GREEN with exact direct pins plus full tested constraints.
- Runtime source stress matrix: starting on Railway staging.
