# User-reported mobile stabilization — implementation plan

Goal: fix the seven regressions reproduced on the current mobile production UI without adding new product surface.

1. Add regression tests first for the mini Editor header, Home footer race, AI duration selector, Alive header status, Creator Hub Short preview, Instagram OAuth route choice, and non-empty AI fallback.
2. Editor: hide the redundant top HUD only while `is-mini`; expanded Editor keeps its controls.
3. Home: remove the obsolete local footer unconditionally so it cannot flash/peek behind the global Game Bar.
4. Alive: replace the top text pill beside the profile with an icon-only progress/status control; retain aria-label and click-through.
5. Creator Hub: render the actual archived Short video inside each Short card using the existing authenticated `/creator-hub/short/file` endpoint; keep the placeholder only as fallback.
6. Instagram: when the Meta app is configured, prefer the professional Facebook Login path instead of the direct Instagram Login development-role path; direct Instagram Login remains fallback when Meta is unavailable.
7. AI: if a valid analysis completes with an empty rank pool, derive candidates from diagnostics; if diagnostics are empty but the media is valid, provide bounded coverage windows instead of returning zero moments. Never mask decoder/provider exceptions.
8. AI UI: keep 15s/30s/60s on one horizontal row.
9. Run targeted tests, full CI/Editor shell/Production Gate, merge only green, then verify Railway frontend status and live health/UI release.

Targeted V427 regression tests, existing V412 AI contracts, Creator Hub redesign contracts and Python compile verification passed after the canonical fixes were applied. This coordination update intentionally changes no runtime code.
