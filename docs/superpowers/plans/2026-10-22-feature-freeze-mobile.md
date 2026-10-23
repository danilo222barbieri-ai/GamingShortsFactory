# Mobile regression fixes — execution plan

Goal: fix the four reported regressions from production main without adding features.
Base: 7c49b04; owner-authorized claim feature-freeze-mobile-regressions-20261022.
Spec: user brief in this chat, 2026-10-22. No merge, promotion marker changes or Railway deployment.

- [x] Refresh main, preserve PR187, atomically transfer only overlapping paths and create dedicated branch.
- [x] Write regression tests before product changes; verify RED on actual canonical UI.
- [x] AI: expose the whole source immediately when shorter than request; keep full scan and audio/context analysis, bound polling, preserve normal ranking for equal/longer sources. Test 9/15,18/30,42/60 and equal/longer cases plus failure.
- [x] OAuth: open existing consent flow from user gesture without replacing parent shell; authenticate popup return by same origin and window reference; preserve Social/source subview and shell dimensions. Test all four iPhone viewports.
- [x] Home: extend persistent Night Arena canvas to Streamlit bottom surfaces; no gap at footer/safe area. Test computed colors in real WebKit.
- [x] Notifications: compact existing service into one line in reserved shell space, retain actions, errors and deduplication. Test geometry and no layout shift.
- [ ] Run dedicated and relevant existing contracts/browser regressions, inspect diff, update project status, push new branch and open PR; record remote checks without merging/deploying.

Review focus: stale AI requests; failed analysis retains whole source; popup denied/closed; source-library return; narrow iPhone header/account hit targets. Provider transport in local browser tests is controlled, not physical iPhone/provider-consent evidence.

Ruling: execute inline under the user's explicit test-first method; no additional plan approval needed.

Evidence checkpoint (2026-10-23): RED on unmodified7c49b04, including actual app request/duration bridge; scanner/context follow-ups separately RED/GREEN. Relevant WebKit suite141passed2skipped93subcases (one Windows-media decoder test explicitly deselected locally, retained in official Linux Gate); actual decoder failure/no-audio and Home-to-Editor duration tests GREEN. Eight UI/security contracts, Night Arena tests,22Node contracts and JS syntax GREEN. Full local Linux-only canonical Gate cannot run on Windows (/bin/sh and privileged symlinks); full official Gate remains required. Independent focused review clear after context and decoder fixes. No Editor or render files changed.

Final dedicated run:14passed50subcases52.09s on four WebKit iPhone viewports; actual Home-to-Editor candidate-duration regression also RED15vs9/GREEN9. Full gate wired to run this file with GSF_BROWSER=webkit, without excluding any existing tests.

Rebase checkpoint2026-10-23: base0f0f01d after concurrentPR190; preserve canonical OAuth/Home-height/Alive/dependency updates, remove its full-source AI bypass, keep actual analysis and all four original tests. Effective-duration policy now accepts any positive source per user brief. Final rebased WebKit146passed2skipped93subcases114.33s; dedicated file18passing tests. No deployment-marker diff.
