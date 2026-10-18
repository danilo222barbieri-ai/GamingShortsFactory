# Closed beta stabilization

Goal: verify the existing upload → AI → selection → Editor → render → save/export path and make guarded Railway promotion repeatable. No feature additions or redesign.

Baseline: main 0e25f12; served release e9eae77, UI digest 70ee0842. Desktop is intentionally gated by merged PR167. Active claims own app.py, companion/upload, Hub, Share, Dockerfile, nginx and navigation tests; inspect those read-only until an explicit handoff or completed claim permits edits.

1. Reproduce the journey in a fresh browser session with actual uploaded media. Record request errors, JS errors, state persistence, exported video metadata and navigation targets. Exercise refresh/back and mobile; verify the intentional desktop gate separately.
2. Investigate historical failed gate jobs and current startup, health and image contracts. Add failing tests for confirmed promotion races (coordination-only main commits, push races, runtime changes) and hanging health calls.
3. Apply small gate/promotion/health corrections in owned files. Keep runtime, image byte equality, WebKit and security checks blocking. Bound individual operations and preserve useful failure diagnostics.
4. Fix confirmed product regressions only after acquiring the corresponding paths; preserve the gaming/glass Editor and existing behavior. Add a regression before each fix.
5. Run targeted and main tests, real browser flow, PR gate, main gate, automatic Railway promotion and public health/digest verification. Record all 15 requested readiness checks with exact evidence. Any missing/failed item prevents a CLOSED BETA ready claim.

Review focus: unpromoted runtime merges; coordination commits arriving during a passing gate; hung curl/containers; stale async navigation after save; uploaded project surviving refresh and final export.
