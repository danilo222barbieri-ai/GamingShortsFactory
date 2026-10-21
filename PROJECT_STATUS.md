# Gaming Shorts Factory — Project Status

> **CANONICAL SOURCE OF TRUTH FOR ALL TECHNICAL CHATS / AGENTS.**
> Read this file before changing code. Refresh live GitHub/Railway evidence before changing production claims.

## Runtime dependency audit follow-up — queued while Railway is paused

- PR187 is MERGED as6cebeabd99483eb6f71c4d4bbd986231154dccac. Its final PR contracts39634398604 and browser39634398958 checks PASS; main Production Gate39641711534 SUCCESS and automatic promotion marker1b7e5d1 exists. Official hash-pinned Streamlit PR17589 preview natively supports Pillow13; no package-metadata rewrite or ignored Pillow advisories. The duplicate local artifact experiment was stashed, not committed.
- Actual source deploy attempt returned Railway “Deploys have been paused temporarily”. Production still serves2cde19c1c1076326a2c02e1dbc93d60e73023ae5; post-deploy UI verify39644781325 failed because the expected new digest never became live. User explicitly deferred Railway until the platform works; do not keep retrying deployments or claim187 is online.
- Extended audit of the exact constraints, rather than floating direct requirements alone, exposed certifi2026.7.22 / PYSEC-2026-4320. Pin certifi2026.10.19 and audit both direct requirements and runtime constraint files in CI. Fresh full-resolution audit:84 packages, zero known vulnerabilities, zero skipped packages; normal constrained pip resolution PASS. No advisory suppression or dependency override.
- Local production container installs the exact main Streamlit preview, Pillow13 and corrected certifi normally; pip check PASS, app starts, canonical179-file digest65f0ac41893a3bf9b082c829ab917725e01dab43c7f55bb8960d706c7d610904 matches source. Local bucket/worker are intentionally not configured. Full suite/runtime verification and follow-up PR checkpoint recorded below when available. This follow-up remains queued for review/release; no Railway deployment requested after deferral.

## Publication recovery checkpoint — 2026-10-21

- User locates TikTok failure at pressing Pubblica; exact live provider code remains unavailable. Provider failures now expose sanitized codes and actionable Italian messages, including non-JSON HTTP/network failures, without logging credentials or raw provider payloads. Public rejection no longer silently retries private; explicit private publishing remains supported and unavailable privacy choices never change automatically.
- TikTok confirmation-pending outcomes keep polling and block duplicate submission until the existing backend confirms completion/failure. Guided Facebook/Instagram outcomes no longer leave Alive publishing forever or claim publication. Guided Instagram supports personal accounts through existing native video sharing; API professional-account requirements are unchanged and no automatic Meta publisher is introduced. Real destination links replace async popup opening; denied clipboard access no longer claims text was copied.
- Verification: full WebKit-enabled suite354PASS21SKIP70subcases96.81s; nine targeted publication tests PASS, including four mobile widths, native file-share invocation and clipboard denial. Eight CI contracts PASS. Local production container manifest verified4edf91b6073f2ee1a5642b5ff2e5e4bd535c9265d5a32e0c4821a51a8235f395. Provider transport in publication tests is controlled: actual consent/account publication and physical iPhone share sheet are not verified.
- Correct AI commit SHA: d004d794e1dbc7c86ed34e0563b2062449992f3d. Its Production Gate39626898963 and Editor shell39626898985 SUCCESS; CI39626898947 fails eight Pillow12.3.0 vulnerabilities requiring13.0.0. Fresh PyPI stable1.66.0/nightly1.66.1.dev20261020 still requirePillow<13. No audit bypass, marker mutation or Railway promotion. Publication checkpoint requires fresh remote checks.

## User-reported installed-app AI stall — verified branch fix, 2026-10-21

- User contradicts prior broad AI-success claim: installed app waits~3min and never reaches choices, including3second videos. Reproduced actual3s upload/AI stall locally; ranker intentionally returns no candidates below5s, and no terminal result reached UI. Also discovered FFmpeg encoder wrapper breaks output-less duration probes; existing ffprobe now reads duration independently.
- Fixes: reject unsupported sub5s analysis promptly with clear message and retained source/Editor route; propagate request-scoped failed/empty rank outcomes through existing results sheet/API/poller; ignore stale failure IDs; never cache failed/empty rank runs as successful results. Static Gemini model/format fallbacks share one90s budget (existing configured timeout), per-request SDK retries explicitly bounded; upload/status/cleanup options validated using official worker SDK2.25.0. Fast alternate-model fallback retained; no prompt/FPS/quality reductions.
- Tests: six new regression cases; complete WebKit suite345PASS21SKIP63subcases81.93s; all eight CI UI/security contracts and worker semantic contract PASS. Actual3s standalone-emulated path reports minimum5s in4.41s and opens retained3.067s source in Editor, no JS errors. Actual valid20s local journey reaches one result3.2s, completes edit/render/export1080x1920/draft/resume/back without critical errors. Public baseline Chromium20s reaches one result4.42s, no JS errors; public WebKit upload crashed before analysis, inconclusive. These controlled clips do not prove recognition quality on arbitrary gameplay or fix live provider quota.
- Not deployed. User next requests publication checks: Facebook guided path, Instagram professional-account requirement, TikTok error on pressing Pubblica; own targeted regression scope and preserve truthful guided versus direct outcomes. PR187 remains sole candidate; unchanged dependency audit blocker still requires compatible published Streamlit/Pillow before release.

## PR187 integration preparation — 2026-10-21 Europe/Rome

- User reiterated full Railway release authorization. PR187 marked ready for review; reconciled current main coordination/status conflict while preserving both factual checkpoints. No runtime bytes changed in this reconciliation.
- Latest checked PyPI versions remain stable1.66.0/nightly1.66.1.dev20261020 with Pillow<13. Required security audit remains blocked pending compatible publication. Repository auto-merge is disabled; no auto-merge configuration or check bypass applied. No Railway deployment performed.

## PR187 Gate green / Library inset follow-up — 2026-10-21 Europe/Rome

- Official Gate39612720276 SUCCESS on7549f9c, including full images/health/runtime/WebKit. Promotion skipped on PR. Required CI39612720454 still FAILS dependency audit; no deployment performed.
- New candidate `c80d028d863b822701bf48a307150c65b1556c1f` fixes only missing inset in Library cards, proven RED1px/GREEN15px with WebKit/Chromium and actual local shell. Serial full suite339PASS21SKIP63subcases79.38s. Fresh candidate checks pending; real Twitch consent/import remains unverified.
- Release authorization persists. Official upstream Streamlit Pillow13 compatibility patch is merged but not yet published in checked PyPI stable/nightly. No unsupported override/suppression; PR187 remains BLOCKED until compatible published dependencies and required checks pass.

## Library card inset and successful Gate checkpoint — 2026-10-21 Europe/Rome

- Production Gate39612720276 SUCCESS on7549f9c, including full Docker builds, health, runtime and mobile WebKit. Railway promotion skipped as expected on a PR; CI39612720454 still FAILS dependency audit. No new Railway deployment. Official Pillow13-compatible Streamlit commit exists upstream but remains unpublished in the checked stable/nightly packages.
- Actual local screenshot exposed missing inset in both discovered/imported source cards and the disconnected Twitch card: generic `.card` provides surface/border but no padding. Scoped correction adds14px only to direct Library cards; no other layout or provider logic changed. WebKit regression measured1px before fix on all four required viewports plus disconnected state, then passed in WebKit and Chromium (ten subcases each).
- Full serial suite339PASS21SKIP63subcases in79.38s, `/workspace/scratch/gsf-library-inset-serial-suite.log`. An overlapping suite was interrupted and the redundant local visual/stress replica stopped after official Gate SUCCESS; partial logs retained, neither counted as PASS. New card checkpoint requires fresh GitHub checks after push.

## PR187 upstream dependency unblock identified — 2026-10-21 Europe/Rome

- Official Streamlit commit [`81bdb8a8a207691f17ec94df9eabc96b6b50ea7a`](https://github.com/streamlit/streamlit/commit/81bdb8a8a207691f17ec94df9eabc96b6b50ea7a), Allow Pillow13, merged2026-10-21 10:17UTC. Develop now allows Pillow<14. This supersedes earlier statements that the develop branch also capped Pillow<13.
- Fresh PyPI check: stable1.66.0 and nightly1.66.1.dev20261020 still cap Pillow<13; no newer published candidate or Pillow12.3.1 backport exists. Official nightly workflow schedules04:30UTC; publication/success is not guaranteed. Next safe step is inspect published metadata, then supported resolver update plus audit/full GSF checks. No VCS package swap, metadata rewrite, unsupported override or security suppression performed.
- Current candidate7549f9c: CI39612720454 FAIL dependency audit, Editor shell39612720272 PASS, Production Gate39612720276 in progress at this checkpoint. Release authorization persists; no new permission needed once checks pass. No new Railway deployment performed.

## Twitch import completion follow-up — 2026-10-21 Europe/Rome

- Latest user steering: continue Twitch/Alive work; user takes over Railway monitoring. No new Railway mutation or bypass performed in this follow-up.
- Reproduced a Hub subview race in actual WebKit: start Clip import, open Settings while status is pending, complete import; old callback redirected to IA because only outer Hub route/epoch was checked. Minimal correction also requires current Library subview, retaining completion notification and normal Library→IA behavior. No Editor/provider/publishing changes.
- Regression test failed on the actual unwanted `?gsf_page=ai` navigation before fix, then passed. OAuth/source WebKit103PASS1SKIP36subcases; Chromium two import-flow tests PASS; Hub structural contracts PASS. Full suite339PASS21SKIP63subcases, log `/workspace/scratch/gsf-twitch-subview-full-suite.log`. Provider transport is controlled in these tests; real Twitch creator consent/import remains unverified.

## PR187 release attempt — 2026-10-21 Europe/Rome

- User resumed release; prior deployment pause is superseded. Candidate `f8e83ef556ed89111bc06d5cda5f00a17de37348`, PR187. Corrected stale AI title contract; all eight production/security/UI contract commands PASS locally and corresponding GitHub step PASS. GitHub CI39611417385 passes functional/core/AI/render/UI checks but FAILS dependency audit with eight Pillow12.3 CVEs fixed only13. Official Streamlit stable1.66.0 and nightly1.66.1.dev20261020 still cap Pillow<13. No supported compatible fix found; no check disabled. Fresh Production Gate39611417398 remains pending/in progress, not a recorded PASS.
- Railway production is healthy: frontend deployment `f814cd64-e895-4258-9ec2-7f0741769a93` SUCCESS, public health all true, online commit `2cde19c1c1076326a2c02e1dbc93d60e73023ae5`. PR187 was not merged or deployed. Terminal release state BLOCKED by security compatibility.
- Twitch/Alive implementation and final UX checkpoint remain available in PR187; real local journey/first-frame/timeline evidence below. Real Twitch creator consent/import and physical device acceptance remain unverified.

## PR187 final UX checkpoint / release requested — 2026-10-21 Europe/Rome

- Latest user steering resumes Railway release of PR187, then continuation of remaining work. This supersedes the earlier deploy pause below; release still requires green CI/Gate and verified Railway SUCCESS/health. No deploy marker override or red-CI merge authorized.
- Implemented in existing components: Social identity-only and Twitch content under Creator Hub Live e VOD; canonical legacy OAuth return and expiring one-use Library intent, reset on every new OAuth; sanitized actionable Twitch401/403/429; decorative Home/AI/Crea Short murals removed; truthful AI results heading; direct44px timeline scrub preserving video/recipe/play state, final-trim-frame and suspend cleanup; conflicting legacy height removed. No provider credentials/scopes/callback configuration or YouTube publishing changes.
- Startup cause reproduced in real100ms WebKit capture: Streamlit chrome appeared behind Creator before transient CSS. Hide rules now live in persistent shell. Same canonical GSFNotify is available synchronously from generated bootstrap; startup evolves until verified Home readiness, with real failure/retry handling and no artificial reveal delay. No parallel router/player/notification/video engine.
- Final suite338 PASS/21 SKIP/63 subcases; actual four-viewport Safari + standalone-emulated first-frame Gate test PASS/8 subcases, captures first DOM/+100ms/+300ms/ready; runtime navigation17 PASS/8 subcases(three cycles); Node/publishing contracts and in-container UI/security smoke PASS. Independent review found trim-OUT and stale-OAuth-intent P2s, reproduced/fixed; final review found no concrete remaining P0/P1/P2. Real loaded-project timeline audit four viewport cases PASS with44px fully reachable, same video/no reload, edits/pause preserved and Game Bar restored.
- Real local journey PASS: upload20s→AI(one valid moment2.8s)→selection→Editor preview/edit/save→Crea Short→render/export1080x1920→draft save/resume→Hub/Bozze/Shorts/Profile/Social→deep link/refresh/Back, zero critical runtime errors. Canonical repo/runtime digest e00beca6ca7af22c8a7e702e6b9743a9e2e7237f8e20c6d5c0383458de84d71e. Evidence under `/workspace/scratch/gsf-final-ux-*`, `/workspace/scratch/gsf-startup-gate-evidence/first-frames`, `/workspace/scratch/gsf-real-timeline-geometry`.
- Existing GitHub head921fcc4: CI39572807878 FAIL security audit; Gate39572807860 FAIL on about:blank test-origin issue now corrected without removing any assertion; Editor shell39572807852 PASS. New checkpoint must run fresh GitHub checks. Latest official Streamlit1.66.0 and nightly1.66.1.dev20261020 still requirepillow<13; eight Pillow12.3.0 CVEs require13.0.0, and older compatible versions are affected. No supported dependency update found, no audit bypass applied.
- Not yet deployed. Real Twitch provider consent/API/import and physical iPhone/PWA remain unverified; local bucket/worker not configured. Do not declare full Twitch E2E, closed beta or Railway release complete from browser fixtures/local fallback alone.

## Release queue / deploy paused by user — 2026-10-21 Europe/Rome

User explicitly requested keeping blocked work queued for a later Railway release. Continue from draft PR187; do not merge, trigger Railway, or change deployment markers to bypass the hold. This is a tracked backlog, not a Railway deployment queue or a claim that all requested work is implemented.

1. **Implemented candidate awaiting release:** source catalog/discovery/reuse/import integration, Creator Hub Library, unified Alive notifications, persistent mobile iframe sizing, same-video transitions/buffering, native Back including delayed frame loads. Runtime commit `921fcc4756b8944fea0fb42c5c66feec4d6f1a0c`, PR187 draft. Local real upload→AI→Editor→render1080×1920→draft-resume→refresh/Back PASS; targeted50 PASS/10 subcases, navigation17 PASS/8 subcases, ten background/resume cycles PASS207s. Real Twitch provider consent/import and physical installed iPhone remain unverified.
2. **Release blocker:** Pillow12.3.0 has eight CVEs requiring13.0.0; official Streamlit caps pillow<13. Older compatible versions are affected. No audit suppression/unsupported resolver override. Latest CI39572807878 FAILURE; Editor shell39572807852 SUCCESS; Production Gate39572807860 in progress at snapshot (prior Gate39518557392 SUCCESS on530201). No new Railway deployment. Recheck all statuses before any later release.
3. **New final UX brief queued, not completed:** first report evidence-backed Twitch cause → startup-glitch cause → actual missing Editor behavior → exact files to touch. Investigate existing OAuth/session/token persistence/refresh/user id/Helix/status/timeout/frontend fetch/abort/refresh before UI changes; never mask provider failures or fabricate Live/VOD imports. Preserve provider configuration and YouTube publishing.
4. **Then implement within existing systems:** finish Editor touch controls/timeline/Alive/FLIP while retaining the same video and all playback/project/edit state; remove remaining decorative mural panels without replacement banners; keep Social for account identity/connect/disconnect only and put all Twitch Live/VOD/Clip/Importati content in Creator Hub Live e VOD/Sorgenti, with return to requested section after connect. No second player/router/Hub/Library/Alive/notification/video pipeline.
5. **Startup and geometry:** inspect actual first paint (FOUC/background/Streamlit/late CSS/fonts/iframe dimensions/safe area/bootstrap), fix causes without artificial delay or scale workaround. Verify Home/AI/results/Editor/Crea Short/Hub/Profile/Social/Library/settings/fullscreen/OAuth return. Capture first paint,~100ms,~300ms,ready on WebKit Safari + standalone emulation at375x667,390x844,393x852,430x932; distinguish emulation from physical device evidence.
6. **Acceptance before later release:** Twitch disconnected/connected/offline/live/VOD-empty-and-present/clips/already-imported/provider-errors/expired-token/refresh/leave-return; real authorized Twitch import through existing GSF pipeline; Editor moment→play→scrub→edit→fullscreen→Back→continue→save→Crea Short with no state loss. One evolving Alive notification per real operation, respecting controls/safe areas. All required CI/Gate checks green, then explicit resumption of deferred Railway release and verified SUCCESS/health/online SHA. Never label queued work complete or deployed prematurely.


## Twitch Library + Alive continuity — candidate, 2026-10-21 Europe/Rome

- Active claim/branch `complete-existing-social-oauth-meta-tiktok-twitc-eb5961`; current main OAuth hotfix preserved. No provider IDs, secrets, callbacks or scopes changed. Source catalog/discovery commits `d369842`/`8489b22`, mobile/notification checkpoint `aa1d286`.
- Creator Hub Sorgenti/Libreria now exposes Upload and Twitch Live/VOD/Clip/Importati; YouTube sources remain explicitly unavailable. Live/VOD only official metadata/links, no recording/download workaround. Imported assets remain reusable after disconnect. Owner-scoped private receipts, captured upload provenance, HEAD validation, source activation through existing marker/materializer, and conditional S3 writes prevent stale receipt replacement; interrupted imports become retryable after ten minutes. Never reassign unproven legacy assets after account changes.
- Existing GSFNotify consolidated in parent: stable process updates/actions/focus, bounded queue, dark/glass safe zone, one shared monitor, reduced motion and cleanup on project reset/network timeout. Alive and source import use that service. Canonical iframe sizing is persistent in the shell. Existing player uses transform transition without replacing the video; buffering state remains inside the player.
- Independent final review found four P2 edge cases and then a metadata/CAS completion race; all reproduced and fixed with regression tests. Last targeted review: no residual blocker in corrected completion path; six tests/four subcases PASS. Real Twitch provider consent was not exercised.
- Real local WebKit iPhone journey now PASS: Home/upload20s/AI(one valid moment3.2s)/selection/Editor preview-edit-save/Crea Short/render/export1080×1920/draft save-resume preserving edits/Hub/Bozze/Shorts/Profile/Social/deep link-refresh/native Back; zero critical runtime errors. Evidence `/tmp/gsf-alive-candidate-e2e-final/evidence.json`. Fixed the real native Back regression: Hub, Editor, AI and Social iframe loaders replace their own history entry instead of consuming the parent Back, including delayed Editor completion after Hub opens. Deterministic delayed-document regression RED before/GREEN after; targeted WebKit50 PASS/10 subcases. Local candidate manifest digest `b9c1d2a9bd9f4e8bd4697a91660637aa0d2bb2caa66bda3aaad8346ee41f39c6`. Bucket/worker and real Twitch provider consent remain unverified locally.
- PR [#187](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/187) remains draft. Production Gate39518557392 and Editor shell integration PASS on530201; no Railway promotion on PR runs. General CI39518557591 FAIL: eight Pillow12.3.0 CVEs require13.0.0, while official stable/nightly Streamlit still declares pillow<13. No audit suppression, unsupported resolver override or dependency change applied. Deployment blocked until a compatible verified fix exists. New Back fix requires fresh GitHub checks after push. Local runtime suite347 PASS/4 SKIP/55 subcases with two failures: container-name configuration rerun PASS; navigation stress rerun17 PASS/8 subcases (three cycles); ten background/resume cycles PASS207s with real3/30/60s waits. Four viewport Safari/standalone emulation56 cases completed with zero page errors; physical installed iPhone not claimed.
- New work is not deployed. Public baseline at audit was `2cde19c1c1076326a2c02e1dbc93d60e73023ae5`; do not claim the new work live, closed beta ready, or real Twitch E2E completed until verified.

## Mobile closed beta bugfix pass — 2026-10-19, deployed runtime verified; urgent icon rebuild blocked

- Claim `closed-beta-mobile-ux-bugfix-pass-hub-profile-sc-7ec364` remains **active**. No features/redesign; gaming/glass Editor preserved, desktop remains intentionally mobile-only gated. Persistent Hub CSS reserves header/Game Bar overlap and safe area; duplicate focus preserves internal scroll. Local Creator name/photo saves persist without assigning authenticated identity; connected profiles retain identity/providers. Header avatar corrected; guest Accedi removed and connected logout preserved.
- Durable CSRF-protected notification preference is separate from browser permission. Default/OFF prevents subscription and delivery; failed activation rollback respects newer intent. Alive preserves shared facts/effects while cancelling per-route transients/fetches/listeners/timers and follows DOM geometry without interpolation. Portrait uses PWA/API lock where supported and a Safari landscape guard that preserves route/project and excludes keyboard resize.
- AI root cause reproduced: backend returned one valid moment while UI required three, causing a 180-second UI failure. UI now accepts all expected complete previews (one/two/three), still rejecting stale requests and incomplete previews. No analysis quality settings reduced. Public 20-second synthetic fixture reached results with all four engines in 4.2–6.1 seconds. This verifies timing/routing, not qualitative recognition of arbitrary gameplay.
- Merged runtime PR [#175](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/175), cancellation-provenance regression PR [#176](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/176), and promotion-history recovery PR [#177](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/177). Invalid/manual/deleted deploy markers recover a valid ancestor marker; no history falls back conservatively to the whole tree. Blocking JS/HTTP/transport checks retained; only proven inactive-route aborts are excluded.
- Verified live source `c562f4e72643f3a42b02e26b733dadb320c8ec45`: main [Production Gate39272734934](https://github.com/danilo222barbieri-ai/GamingShortsFactory/actions/runs/39272734934) **SUCCESS**; automatic promotion `3bf2c946aaa60cad9b5457105b2c52e8629362b4`; Railway frontend deployment `d502f669-dc57-4564-b9ec-bdceb195d367` **SUCCESS**; Production UI Verify39275272079 **SUCCESS**. Composite public health ok/companion/Streamlit/bucket/worker true, UI digest `fe9d030c654a422fe583b69fcca7115b930ff93c8d222d3deb2bcd5280586818`. Worker runtime unchanged; no unnecessary worker redeploy.
- Public real-services journey on that release passed Home/upload/AI (one valid moment)/selection/Editor preview-edit-save/Crea Short/render/export1080×1920/draft save-resume preserving edits/Hub/Bozze/Shorts/Profile/Social settings/deep link-refresh/back; zero critical runtime errors. All four engines passed separately with zero runtime errors.
- Final public mobile audit found a real profile race: pre-save Hub GET could arrive after successful save, restore Creator, then photo upload saved the old name. Minimal presentation-only epoch guard merged as [PR178](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/178), source `daf121755a4f81e5c83b9b83bd73f84bf98010ac`. Server identity/provider state stays authoritative. Deterministic stale-response regression RED before/GREEN after; independent review no P0/P1/P2. Actual WebKit suite **204 passed,19 skipped,7 subtests passed**. Local real four-device audit after fix passed name/photo/refresh, notification OFF, Alive ring and safe area; no runtime errors, minimum last-card clearance27.625px.
- Previous GitHub queue blocker cleared for this release: PR178 Gate39277890546 and main [Gate39281638597](https://github.com/danilo222barbieri-ai/GamingShortsFactory/actions/runs/39281638597) **SUCCESS**. Automatic promotion `c2259515edd7c5714d05051d161eaa129d994771`; frontend deployment `7260dd5e-196e-40d2-8a84-3b489979fc0a` **SUCCESS**. [Production UI Verify39286196033](https://github.com/danilo222barbieri-ai/GamingShortsFactory/actions/runs/39286196033) **SUCCESS**, explicitly checked source `daf121755a4f81e5c83b9b83bd73f84bf98010ac`; public canonical digest `ef33273a88ced5e77f8352703a727d62233f32b455ba4a22be3ec1c934e134e1`.
- Final public audit on release `c225951` **PASS**: all four mobile viewports retain profile name/photo after refresh, safe-area/Game Bar clearance and Alive lifecycle pass, zero runtime errors. Four real-service AI engines each reach results with one valid moment; latest20s synthetic-fixture UI times AUTO4.4s/AZIONE39.1s/STORIA39.2s/REAZIONI39.1s. Longer cases spend about35s waiting for pre-scan; worker logs show a provider504 deadline and fallback, so latency is variable. No quality settings reduced. Real E2E **21 checks PASS** through Editor preview/edit/save, render, export1080×1920 (15.594s), draft save/resume, Hub/Bozze/Shorts/Profile/Social settings, refresh/deep link/back; errors[]. Desktop1366×900 mobile-only gate/copy/legal links pass with no runtime errors. Post-run composite health all true. Evidence `/workspace/scratch/gsf-public-final/`.
- **Current blocker: urgent icon rebuild, not the running frontend.** Later icon commits `9e78f32`/`30584bf` and decoder/trigger commits `c6f2df6`/`ad35a23` introduced/retained an incomplete PNG. Both frontend failures `3afb4662-87d9-4bd8-ad42-71cbaf4337ce` and `4510e8c6-470a-45fe-9ce4-cf18c281ecae` are build failures on that source: FFmpeg chunk-too-big/Invalid data, then Pillow image-file-is-truncated. Tracked PNG7506bytes declares an IDAT42363bytes; zlib stream does not finish, so missing pixels cannot be losslessly recovered. Existing frontend `c225951` remains healthy; worker sleeping is expected and has no failed deployments.
- Original icon ZIP received and fully decoded1254×1254RGB; approved crop `(57,46,1189,1178)` removes outer black padding to glass, with no color/filter/redraw changes. PNG180/192/512 verified with Pillow and FFmpeg. PR179 merged source `81a4c880c4226dd5d3daf935992f1077128e7715`; main Production Gate39331281499 SUCCESS and Production UI Verify39333281638 SUCCESS. Automatic promotion `0d876814f97fe1755f772b8900ed33dec03d3372`, Railway frontend `56a5d085-d2ff-4218-a078-86a23ff33aff` SUCCESS. Public verification confirms exact approved180PNG bytes and full192/512/Apple180 decodes, all composite health flags true; UI digest `3bd41cc32e082d51db8fb7572d987edb7e43d05bd63ef1df41c870cb0b3d056b`. No manual marker override.
- PR180 source `558cf5302c0abf04e1e068d16741c9383ba523d3`, release `511c81ef9dd76413af17c37b4b76fa69c14c4dc9`: main Gate39388328149 SUCCESS, production UI verify39390237888 SUCCESS, Railway frontend9a34e6e9-06de-43ea-b766-f27c7e60a8f8 SUCCESS; public UI digest943fedb122e81a139fb8f5be5fc6314c319b9ab31d332bd8822e82f6d2922fb4 and composite health verified. Actual public core E2E passed21 checks through upload, one valid AI moment, Editor preview/edit/draft, render/export1080x1920 with visible caption, save, Hub, direct refresh and browser Back; no runtime errors in that journey. Four AI engine paths reached valid result selection (AUTO3.7s; other engines around39s on synthetic20sec fixture; gameplay semantic quality and physical-device behavior not established). Public icon/manifest/dark canvas/Alive immediate-subview checks and intended iPad/desktop gates passed. Final general pass found a real fixed Hub modal overlapping Game Bar, so current task remains ACTIVE and incomplete.
- Responsive audit (66geometrysamples plus24proportion samples) found no confirmed stretching or stale viewport sizing across phone Chromium/WebKit, Android, emulated standalone and iPad gate. At390px width AIorb195×195; Editor stage370×657.77 at844height and311.63×554 at704height, always9:16. Same viewport browser/standalone geometry matches; reduced420height does not show portrait guard. User delegated iPad decision: retain intended smartphone-only access for this closed beta. Physical Safari chrome/installed PWA/keyboard/safe-area behavior remains unverified; emulation is not a device proof.
- Limits: synthetic20-second media and emulated mobile browsers; no physical iPhone, authenticated social publication or actual push delivery tested. Safari tabs cannot enforce OS portrait lock; landscape guard is the supported fallback.

## Closed beta stabilization — 2026-10-18, verified LIVE

- Claim `closed-beta-stabilization-production-gate-reliab-bd6c6c` completed after explicit user handoff of the necessary mobile/navigation/backend files. No new features or redesign; gaming/glass Editor preserved. Desktop intentionally remains mobile-only gated.
- Merged PRs: [#168](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/168), [#169](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/169), [#170](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/170), [#171](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/171), [#172](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/172), [#173](https://github.com/danilo222barbieri-ai/GamingShortsFactory/pull/173). Final tested integration `b606861b9cdd7a271c1b6b60f7a34dbdcb4aefef`. Runtime Editor CSS fix is PR171; PR172/173 only correct test classification/actionability.
- Fixed nested render semaphore deadlock; saved trim/zoom/manual-caption/frozen recipe handoff; stale exports after upload/edit; Home CTA/rerun feedback; draft405/CSRF routing; history/deep links; health/startup/WebKit deadlines; coordination-safe automatic promotion; readable generated icons. Real nginx reproduction identified cold asset503 at cap40; cap128 accepts initial64 while overload rejection/upload/API protections remain tested.
- Final visual inspection found transient Streamlit CSS left the cold Editor at304×154. PR171 mounts the same five CSS blocks verbatim with the persistent surface; RED actual-bootstrap geometry before/GREEN after; independent review confirmed unchanged CSS bytes/order. PR172 retains blocking first-party/JS/HTTP/network errors while logging cancelled optional Google fonts; PR173 waits for the restored control to be actually hit-testable beyond a transient parent toast, retaining native pointer/fullscreen assertions.
- Tests: Python183passed,18skipped,3subtests; real nginx routes/burst3passed,5subtests; official WebKit Gate passed navigation, video, background/resume and resource stability. Chromium BFCache with uploaded video passed after correcting pointer reachability. Independent review found no blockers. One earlier local WebKit browser-process crash was not reproduced on the official dependency-complete GitHub gate.
- Final main Production Gate **SUCCESS**: https://github.com/danilo222barbieri-ai/GamingShortsFactory/actions/runs/39149112043. Automatic promotion `41e583b9558feb7622496bdbf035e3c099b5ee10`; Railway frontend deployment `c5001f0d-f24a-4d62-b1b9-9d36fcc9676d` **SUCCESS**. Worker deployment603fb67a-09b3-43de-aa3c-5fba9a539f2a previously reached SUCCESS and may enter expected SLEEPING; worker composite health true after the real AI/render journey. Superseded gate runs cancelled by normal concurrency are not deployment failures.
- Fresh public health: ok/companion/Streamlit/bucket/worker true; release `41e583b9558feb7622496bdbf035e3c099b5ee10`; canonical UI digest `a7b9924c82f3ababc0e059077dcc944cf8831e28af62c4d55f772a256d2cafb9`. No manual marker override or deploy bypass.
- Final deployed public journey passed Home→upload→real AI→3 moments→selection→Editor preview/edit→render→1080×1920 export→draft save→Creator Hub/Bozze/Shorts/Profile/Social settings→resume preserving edits→Editor deep link/refresh→browser back; zero critical runtime errors. Subsequent edit invalidated old export; a new render/download and new caption in the actual exported frame were verified.
- Final public iPhone geometry/screenshots passed: full-size Editor iframe, hidden legacy notes, same global Home/Editor header, dark html/body through bottom and scroll, viewport-fit=cover, anchored Game Bar. Desktop gate/QR verified. Three fresh sessions on this final release passed without5xx/runtime errors. The first immediate post-rollout attempt had transport ERR_FAILED before Home initialization; the subsequent network probe and three cold sessions did not reproduce it, and its failed log was preserved separately.
- All15 requested checks passed for the tested path. Limits: synthetic32s media exercised actual services without mocks; no physical iPhone or authenticated social post was tested. Export/draft save and social settings navigation were tested. CLOSED BETA base verified within these explicit limits; no remaining blocker found in this scope.

## Snapshot

- **Repository:** `danilo222barbieri-ai/GamingShortsFactory`
- **Production branch:** `main`
- **Current product baseline:** **V411 UI on the canonical UI pipeline** (repo files == served files; see `docs/architecture/gsf-canonical-ui.md`)
- **Cross-chat orchestration:** **LIVE**
- **Last fully tested main source commit:** `daf121755a4f81e5c83b9b83bd73f84bf98010ac` (main Gate39281638597 SUCCESS; public runtime verified)
- **Last runtime promotion commit:** `c2259515edd7c5714d05051d161eaa129d994771` — automatic promotion after main Gate
- **Served canonical UI digest:** `ef33273a88ced5e77f8352703a727d62233f32b455ba4a22be3ec1c934e134e1` (fresh public health after final E2E)
- **Current `main` HEAD:** always query GitHub live; coordination/status-only commits may advance `main` without changing production.

## Production state — verified 2026-10-15 08:15 UTC

### Frontend

- Railway service: `gaming-shorts-factory-v79`
- Service ID: `89ae81ec-54d7-4f22-98f4-c88d6361a6a2`
- Environment: `production` (`5cb868d5-9936-4ff0-be2d-ef42be7fe0ec`)
- Verified deployment: `2df871ae-527d-471f-b14c-95fec3d51082`
- Status: **SUCCESS / Online** — startup log `GSF UI manifest verify PASS digest=fbe1875d… files=571`
- Promotion commit: `460102f077d8465a345fac45ca43284c30d3bfd6`
- Start command `sh /app/web/start_web.sh` = canonical startup (verify manifest + launch; no migrations)
- Healthcheck: `/healthz`
- Railway deploy trigger: only changes to `.railway/frontend-deploy.txt`

### AI worker

- Railway service: `gsf-ai-worker`
- Service ID: `8cd8b98c-43b7-4c3f-bf9a-9c0968286ada`
- Verified deployment: `31b06ef0-a4c1-49c1-95df-8f0b0b7d88f7`
- State: **SUCCESS** — the service may return to expected `SLEEPING` after idle because sleep mode is enabled
- Worker baseline commit: `fb0edf871c8fc178c7a4381ff1e15efe7c8730ba`
- Healthcheck: `/health` when awake
- Railway deploy trigger: only changes to `.railway/worker-deploy.txt`

## Production Gate

Workflow: `.github/workflows/v397-production-gate.yml`  
Workflow name: **GSF Production Gate**

Latest integration verification:

- PR `#123` merged by squash into `main` as `e89541f42cca0412465bf9629bbf0c0f13f5ee4f`.
- PR head Production Gate run `38630205476`: **SUCCESS**.
- Main Production Gate run `38631006544`: **SUCCESS**.
- Gate promotion created `e2f1de18e634d4308b1255b2a2e83396107522cd` and updated both Railway markers to tested SHA `e89541f42cca0412465bf9629bbf0c0f13f5ee4f`.
- Railway frontend deployment `c348c7d9-c6f4-48e3-b469-1ad9638c49f9`: **SUCCESS / Online**.
- Railway worker deployment `ba536c6a-9544-42d6-9482-4ff0ba0d50d4`: **SUCCESS**.
- Live `/healthz`: **200 / ok**, with companion, Streamlit and worker checks true.
- Live Creator Hub security contract: stable `gsf_sid`, stable `csrf_token`, missing-CSRF POST `403`, authorized missing draft `404`.

The gate continues to verify V397/V398/V399/V400/V401/V402 contracts, Python syntax guards, worker/frontend image builds, composite `/healthz`, blocking runtime smoke, and V343/V389/V391/V393/V394/V395/V396 UI regressions before runtime promotion.

## Parallel chat isolation — LIVE

Files:

- `tools/gsf_claims.py` — conservative ownership conflict engine.
- `tools/gsf_task.py` — atomic global claim acquisition, unique branch/worktree bootstrap, handoff/finish and machine-readable status.
- `.gsf/claims/index.json` — live global ownership registry shared by all technical chats.
- `.gsf/claims/README.md` — lifecycle and safety rules.

Claim states:

- `active` — blocks overlap
- `handoff` — blocks overlap while ownership transfers
- `completed` — historical, does not block
- `abandoned` — historical, does not block

Atomic acquisition uses latest `origin/main`, conflict detection, optimistic push and retry/re-read after races. Two chats racing for overlapping paths cannot both win.

Commands when a Git worktree is available:

`python tools/gsf_task.py start --scope "<scope>" --paths <path> [<path> ...]`

`python tools/gsf_task.py status --claim <claim-id> --json`

`python tools/gsf_task.py finish --claim <claim-id> --state completed --evidence-json '<json>'`

When a local worktree is unavailable, an authenticated GitHub connector may perform the equivalent claim + dedicated-branch protocol, but it must preserve the same fail-closed ownership semantics.

## Guarded automatic rollback — LIVE

Policy/state:

- `tools/gsf_rollback_policy.py`
- `.gsf/state/known-good.json`
- `.gsf/incidents/index.json`
- `docs/runbooks/gsf-automatic-rollback.md`

Current verified known-good targets:

- frontend → `c348c7d9-c6f4-48e3-b469-1ad9638c49f9`
- worker → `ba536c6a-9544-42d6-9482-4ff0ba0d50d4`

GSF Guardian is enabled as an **hourly condition watch** and now applies the guarded rollback policy.

Automatic rollback eligibility is deliberately narrow:

- current new deployment `FAILED`
- current new deployment `CRASHED`
- current new deployment OOM-killed
- sustained frontend `/healthz` failure tied to the new deployment

Not automatic rollback triggers:

- isolated HTTP 5xx
- Gemini/provider/API transient errors
- temporary network error
- one failed user request while service health remains good
- worker `SLEEPING` when sleep mode is enabled

Safety invariant: maximum **one automatic rollback attempt per failing deployment ID**. The target must be an exact previously verified known-good deployment. Invalid/missing state fails closed. Failed recovery escalates and never recursively rolls back.

The scheduled Guardian runs hourly; Railway `/healthz` remains the immediate protection during the initial deploy rollout.

## One-command workflow — LIVE

Files:

- `AGENTS.md`
- `docs/runbooks/gsf-one-command-workflow.md`
- `.gsf/state/task-status.schema.json`

Every coding request automatically enters this workflow unless the user explicitly asks for analysis/design only:

`INTAKE -> CLAIMED -> IMPLEMENTING -> TESTED -> INTEGRATING -> GATE -> DEPLOYING -> VERIFYING -> LIVE|BLOCKED|ROLLED_BACK -> HANDOFF`

Evidence-backed terminal labels are exactly:

- `LIVE`
- `BLOCKED`
- `ROLLED_BACK`
- `HANDOFF_REQUIRED`

### Safe-close boundary

A normal ChatGPT conversation is not treated as guaranteed background execution before **GitHub handoff**.

Once the relevant commit/PR/push exists on GitHub and GitHub CI/Railway/automation owns the next deterministic step, the user may close the app without stopping GitHub Actions or Railway. The GSF Guardian then continues on its scheduled cadence.

## Verification evidence

Final isolated-branch orchestration CI after safety fixes:

- **36/36 tests PASS**
- `V397 production hardening structural contract: PASS`
- real CLI invocation `python tools/gsf_task.py --help` verified
- corrupt known-good state fails closed
- corrupt incident state fails closed
- rollback anti-loop scenarios verified

PR integration checks on final head:

- V398: **PASS**
- V399: **PASS**
- V400: **PASS**
- V402: **PASS**
- GSF Production Gate #50: **PASS**

No intentional destructive production rollback test was performed. Rollback execution will only occur for a naturally eligible hard failure or an explicitly approved controlled failure test.

### Game Editor V403 support handoff — 2026-10-14

- Support engine merged via PR `#112` as `f88217ed1aa9c762483962397e81219f90bc5127`.
- Added non-destructive editor state normalization, Undo/Redo history, Smart Timeline marker normalization and deterministic Game Director suggestions.
- V403 TDD workflow demonstrated intentional RED before implementation, then GREEN after implementation.
- CI also applied `scripts/apply_v403_game_editor.py` to a disposable copy of the then-current `app.py` and successfully Python-compiled the fully patched app.
- **Runtime UI is not yet integrated into `app.py`.** The active `alive-core-v405-b6f2a1` claim currently owns `app.py`; forcing an overlap would violate the repository isolation protocol.
- The deterministic V403 app patch is staged on `main` and can be applied after that `app.py` claim is completed/released, then must pass the Production Gate and Railway verification before any LIVE claim.

### Canonical UI pipeline — 2026-10-15 (PR #136)

- **Root cause of "new in repo, old online":** the served UI was not in the repository. `app.py` was never copied into the image; the real app was generated from the V77 payload through 94 intermediate versions. `test_v269_creator_hub_recovery.py` ran `materialize_runtime_patches.sh`, which replayed the V285–V373 chain from `start_web.sh` over old component bases (Creator Hub 22 writes, Home 12, Editor 10 incl. nested V389–V396, app 22), then V403/V410/V411 patched again; some patches rewrote other patch scripts. Railway's start command ran the repo `start_web.sh` that still held the chain. Deploy trigger ignored `gsf_core/` and root `gsf_*.py`.
- **Fix:** canonical files committed byte-identical to production (proved by the `legacy-equivalence` job with a real Docker build of the old image); Dockerfile copies 1:1; `start_web.sh` verifies `tools/gsf_ui_manifest.py` and launches; `materialize_runtime_patches.sh` retired (fails closed); `/healthz` exposes `ui_digest` + `release`; gate checks image == repo, served pages == repo bytes, no runtime rewrite; deploy trigger extended; V397/V410/V403 workflows no longer re-apply legacy patches.
- **Guard:** `tests/test_canonical_ui_pipeline.py` (7 checks; mutation-tested) fails CI if a legacy migration returns to build/startup or an old UI is re-injected; also keeps V286/V302/V366 Game Bar + Hub-state and V370 navigation contracts on canonical files.
- **Evidence:** PR head `beed9d0` 11/11 checks success; main gate success; promotion `460102f`; frontend `2df871ae` SUCCESS, worker `31b06ef0` SUCCESS; public `/healthz` ok with `ui_digest` == repo digest; `/creator-hub/state` ok + CSRF token.
- **Unverified / follow-up:** `GSF Production UI Verify` (post-deploy byte comparison from the public domain) did not start — GitHub reported failed payment / spending limit for Actions. No real-browser visual pass on Safari was performed. Items 9–10 of the owner brief (Safari freeze audit, deprecated-component cleanup) not yet done. Edit mobile screens directly in the canonical files; never add a build/startup patch.

### Claims registry repair + CLAUDE.md — 2026-10-15

- `tools/gsf_task.py start` was failing for every new task (`claim paths must be a non-empty list`): five V405–V409 claims (`core-infra-v406-c81426`, `publish-short-v405-7d91c4`, `desktop-mobile-shell-v407-7e31ca`, `project-state-v408-3f4b21`, `alive-notifications-v409-4d7c2e`) were still `active` with `paths: []` after handing all paths to the completed `production-queue-20261014`. Fixed in coord commit `bbd6713`: marked `completed` with their historical handoff paths and PR `#123` evidence. The validator requires non-empty `paths` on every claim, including completed ones.
- `CLAUDE.md` added (imports `AGENTS.md` + orientation) via PR `#133`, claim `docs-add-claude-md-pointing-agents-to-agents-md--e73cb7`, squash `caf08569327c91137aa06cbede43b336ff8d7e54`. All PR checks passed, including Production Gate. Merged with `[skip ci]` because `CLAUDE.md` is not in the gate's `paths-ignore`; no promotion, no Railway redeploy.
- Railway production re-checked 2026-10-15 ~06:50 UTC: frontend `c348c7d9-c6f4-48e3-b469-1ad9638c49f9` **SUCCESS**; worker `ba536c6a-9544-42d6-9482-4ff0ba0d50d4` **SLEEPING** (expected).
- Social publishing configuration (variable names only, frontend service): YouTube and TikTok credentials are set; no Meta (`GSF_META_APP_ID`/`GSF_META_APP_SECRET`) credentials are set, so Instagram cannot connect; Facebook publishing is still a disabled placeholder (not implemented). Owner reports TikTok, Instagram and Facebook are not connected.
- Follow-up: consider adding `CLAUDE.md` to the Production Gate `paths-ignore`.

### Canonical mobile Game Editor 2026 — 2026-10-15 (PR #146)

- Claim `feat-canonical-mobile-game-editor-2026-with-ai-f-c38434`, squash `74fc1a3259c1f19858c54e09adec4f778411b49e`.
- Main Production Gate run `38741480103`: **SUCCESS**; promotion `bcfe40e32d5165998569e11257e998ae68a0bb5f` (frontend marker only).
- Railway frontend deployment `baaed85b-58f4-4a87-8cbe-594eaddd9b02`: **SUCCESS** — startup `GSF UI manifest verify PASS digest=c0d117f0… files=169`, `release=bcfe40e`. Worker not redeployed (marker unchanged, expected).
- `GSF Production UI Verify` run `38742178354`: **SUCCESS** — public domain serves release `bcfe40e` with digest `c0d117f0…`, pages byte-identical, Home 200, `/creator-hub/state` 200 with CSRF enforced.
- The owning chat merged but did not close the claim; closed by owner-authorized handoff (coord `f870816`). No real-device Safari pass recorded.

### Crea con IA V412 — holographic AI engines page — 2026-10-15 (PR #147)

- Claim `ui-ai-holographic-ai-engines-page-real-results-b-eada74`, squash `cd25ce33ea8b89af8f4857e8e315100bf8dec1a2`.
- Files: `web/ai_v221_component/index.html` (new one-screen page, no scrolling), `web/ai_engines_v412.py` (new: results sheet, merge, replacement/selection helpers), `app.py`, `web/home_v154_component/index.html`, `web/direct_upload_server.py`, `web/test_v412_ai_engines.py` (new, in GSF CI), `web/test_v404_crea_con_ia_simple.py`, `.github/workflows/gsf-ci.yml`.
- Fixed root causes found in the audit: (1) results never reached the AI page (canonical page no longer polled `/ai/results`, Home always sent an empty list) → page polls `/ai/results` with a per-search `request_id`; (2) the AI cache key ignored the engine, so on the same video every engine returned the first engine's results → profile added to the key; border refinement only for AUTO/STORIA; (3) the short picked on the page was ignored, so Pubblica used short #1 → `auto_clip_scelta` follows the selection; opening the editor from results no longer drops the AI run; (4) Cambia short re-enabled on real AI alternates (V125 UI was `if False`), with restore.
- Autosave: every result/selection/swap updates one Creator Hub draft `draft_ai_<upload>` via the internal `/drafts/save` (background thread).
- Tests: local V397/V410/V404/V412/V405/V407/V403 PASS, `tests/` 36 passed (`test_gsf_core_infra.py` not run locally: no pytest in sandbox); PR CI + Production Gate success; browser flow with mocked `/ai/results` (stale results ignored, request match, swap and publish payloads).
- Main Production Gate run `38752227187`: **SUCCESS**; promotion `f28a38b` (frontend only).
- Railway frontend `3e2c45ff-e010-4a63-8302-a2676b13fc6e`: **SUCCESS** — startup `GSF UI manifest verify PASS digest=3023c491… files=171`, `release=f28a38b`. Worker not redeployed (expected).
- `GSF Production UI Verify` run `38752986530`: **SUCCESS** — public domain serves release `f28a38b`, digest `3023c491…` (== repo), pages byte-identical, Home 200, `/creator-hub/state` 200 + CSRF.
- Unverified / follow-up: no end-to-end AI run on production with a real uploaded video yet; AZIONE profile weights are weakly differentiated from AUTO (Game Brain tuning, not changed here); `/drafts/save-current` used by Home and Share has no nginx route (pre-existing, not touched).

### Game Editor V414 — gaming overlay editor — 2026-10-15 (PR #149, PR #150)

- Claim `gaming-overlay-editor-v414-7c2a9e` (completed, coord `8491a03`). Files: `web/game_editor_mobile_component/{index.html,editor.mjs,editor_state.mjs,overlay_v414.css,overlay_v414.mjs}`, `tests/test_gaming_overlay_editor_v414.py`, `tests/test_mobile_game_editor_2026.py`, `tests/js/gaming_overlay_editor_v414_*.test.mjs`, `tests/visual/gsf_visual_check.py`.
- PR #149 squash `4049bb7`: video-first glass overlay editor. WebKit gate root cause (reproduced with the gate's own sequence on an iPhone 13 viewport): a `max-width:420px` rule hid `#saveDraftButton`, so phones could not save a draft; the button is now compacted, never hidden (contract test added). The visual check also read `postMessage` results synchronously; it now waits for them. Gestures stay disabled in the mini-player.
- PR #150 squash `154eac8`: vertical tool rail Frame/Camera/Look/HUD/Testo/Audio/AI (`data-tool` keys unchanged), Game AI button in the top bar, two-phase quick AI + local natural-language command (Preview never commits, Apply commits once, one undo reverts), Focus Map contract `time -> x/y -> confidence -> subject/action` (preview-only while playing, never persisted), auto-hiding chrome during playback, slimmer timeline, stage `overflow: clip` (a focused drawer input used to scroll the stage and shift every overlay).
- Main Production Gate runs `38790231577` (4049bb7) and `38792712945` (154eac8): **SUCCESS**, including Mobile WebKit interaction gate; promotions `518e8fb` and `36ff303` (frontend only).
- Railway frontend `c92759e3-6a72-40e3-b269-0ba61c3fdd66` (release `518e8fb`) then `cb0bff7b-9a2b-4545-9c7b-7b1151479a18` (release `36ff303`): **SUCCESS** — startup `GSF UI manifest verify PASS digest=b3a16c29… files=173`; `/healthz` 200 after start. `GSF Production UI Verify` run `38793356058`: **SUCCESS**. Worker not redeployed (SLEEPING, expected).
- Unverified / follow-up: WebKit only verified in CI (sandbox has Chromium only); no real-device Safari pass; Game Vision does not emit Focus Map coordinates yet, so Follow Action tracking in preview stays inactive until the backend sends `focus_map` in `GSF_GAME_EDITOR_INIT`.

### Crea con IA V413 — Home mural style — 2026-10-16 (PR #155)

- Claim `ui-crea-con-ia-in-home-mural-style-big-circle-or-e0c710`, squash `b515c5f34cc0087dc7f8173fcf758c1986e66ded`; only `web/ai_v221_component/index.html` changed.
- Redesign approved by the owner from a preview: big glass circle (search button) with the four engines orbiting it, handwritten murals that follow the state, scan inside the circle (real timer, sweeping ring); results as three portal circles (ring = AI score), one detail card with "Cambia short", pill actions Apri nell'editor / Pubblica. Owner follow-up: no "Gameplay caricato" pill, no mural above the duration. One screen, no scrolling (390×760, 390×680, 360×600, 1280×800). V412 behaviour unchanged.
- Tests: local V404/V412/V397/V410 PASS, `tests/` 58 passed (`test_gsf_core_infra.py` not run locally); PR contracts + production-gate success.
- Main Production Gate: **SUCCESS**; promotion `9c04f10` (frontend). Railway frontend `857af3ea-042d-4463-8928-ee849b6c151f`: **SUCCESS**.
- `GSF Production UI Verify` run `38817687407`: **SUCCESS** — release `9c04f10`, digest `d50c4044…` == repo, pages byte-identical, Home 200, `/creator-hub/state` 200 + CSRF.
- Unverified: no end-to-end AI run with a real uploaded video on production.

### Creator Hub V415 redesign — 2026-10-16 (PR #157)

- Claim `ui-creator-hub-redesign-social-status-row-counte-92c367` (completed). The Hub file was released from `stability-unified-navigation-and-mobile-resume-l-395391` by owner-authorized priority (coord `88b842e`; that branch had no Hub commits). Squash `58762de`.
- Files: `web/creator_hub_v156_component/index.html` (one canonical page, single runtime, no MutationObservers; replaces the stacked V300–V403 layers), `web/direct_upload_server.py`, `tests/test_creator_hub_redesign_v415.py` (new, in GSF CI), `.github/workflows/gsf-ci.yml`.
- Layout (owner-approved): header (photo, name, plan, settings) → social row YouTube/TikTok/Instagram/Facebook/Twitch with green tick if connected, grey if not → counters Bozze/Shorts/Pubblicati → Bozze and Shorts cards with menu (Riprendi or Scarica, Rinomina, Elimina with confirmation) → Live e VOD (empty "In arrivo") → Impostazioni (photo auto-resized to 512px, name, connect/disconnect social, plan shown once, notifications, language, login/logout). Desktop two columns. Brand tokens. The empty "Pubblicità" placeholder was removed.
- Root cause fixed: nginx sends `/shorts/*` to Streamlit (8501), so the old Hub's short download/delete never reached the companion server. New CSRF-protected `/creator-hub/short/rename` and `/creator-hub/short/delete`, plus the `/creator-hub/short/file` download alias, under the existing `/creator-hub/` proxy (8502).
- Tests: V415 contract, canonical UI pipeline (incl. V286/V366 on canonical files), V397, V410, V404, V412, V405, V413, V407, V403, mobile polish shell PASS locally; Chromium mock-data pass at 390px and 1366px with no console errors. PR CI `contracts` + `production-gate` success.
- Main gate: run `38818632289` (58762de) cancelled by the #156 push; run `38818872801` on `a942adb` (contains 58762de) success, its promotion skipped because a coord commit landed mid-run; promoted by owner-requested commit `7298444`.
- Railway frontend `6e36f303-a5f3-4fb6-8511-1ecded777754`: **SUCCESS** — `GSF UI manifest verify PASS digest=ed479e93…` (== repo digest at `7298444`), `release=7298444`; `/healthz`, `/creator-hub-v156/`, `/creator-hub/state` 200. Worker not redeployed (expected).
- Unverified / follow-up: no real-device Safari pass; short rename/delete not exercised on production with real data; Shorts have no project link, so the menu offers Scarica instead of Riprendi; Twitch OAuth not implemented ("In arrivo"). Coordination commits pushed during a main gate run make its promotion skip (seen twice tonight); a gate change to tolerate coord-only commits was proposed but not made (owner chose to wait).

### Crea con IA — fits between shell header and Game Bar on phones — 2026-10-16 (PR #160)

- Claim `ui-crea-con-ia-fits-between-shell-header-and-gam-76ec0a` (took over the idle `ui-crea-con-ia-respects-the-shell-header-and-gam-10462c`, abandoned with no commits, at the owner's request). Squash `a4f9d86f1d82279700f435e740b8e3db8ac81a3f`.
- Owner report: on phones the page did not respect the shell header and Game Bar, hiding elements. Fix in `web/ai_v221_component/index.html` only (`GSF_AI_SHELL_FIT`): the page measures from the parent how much of its frame the shell header and Game Bar/footer cover and pads content and the Cambia short sheet by that; 0 when already fitted. "CREA CON IA" label row removed (owner request). `app.py` untouched.
- Tests: mock shell at 390×844, 375×667, 360×640 (full-screen and fitted frames): nothing under header/Game Bar, no scrolling; local V404/V412/V397/V410 PASS, `tests/` 73 passed; PR contracts + production-gate success.
- Main Production Gate: **SUCCESS**; promotion `1e596cd`. Railway frontend `831d768f-e364-4a2e-bd79-574b2e449197`: **SUCCESS**. `GSF Production UI Verify` run `38865042951`: **SUCCESS** — digest `e32d92a6…` == repo.
- Unverified: not checked on a real phone.

### Night Arena single look — 2026-10-16 (PR #162)

- Claim `ui-night-arena-single-look-shared-theme-creator--1fc1b7` (completed; took over the idle Home/shell/editor claims with the owner's OK). Squash `ed1e8bde44e5f244e8883035dbe2517ff229ec02`.
- One look for the whole app: canonical theme `web/gsf_night_arena.css` inlined verbatim (between `GSF_NIGHT_ARENA:BEGIN/END`) in Home, Creator Hub, Crea con IA, Crea Short (`/share-v156/`), mobile Game Editor (`night_arena_v417.css`: no kicker/ratio badge over the player, mini player fills its slot, heat strip) and desktop Editor 2027; legal pages restyled; shell with wordmark header, vector Game Bar icons, no `GSF - V362` footer (version lives in Creator Hub > Info). Hub empty states with a next-step CTA, social rings (connected = solid green, otherwise dashed "+"). "Crea Short" from the old router opens the canonical Crea Short page and starts the render when needed.
- Tests: new `tests/test_night_arena_theme.py`, updated `test_gsf_editor_home_style.py` and V302 gamebar test; PR and main Production Gate **SUCCESS** on `ed1e8bd`.
- The main gate's promotion step skipped as stale because a coord commit (`69d2317`) landed during the run; promoted by marker commit `bdd2ed3` at the owner's request. Railway frontend deployment `68a34a7b-9bc2-4361-898b-3d8b7f2de4e7`: **SUCCESS**; `/healthz` ok, release `bdd2ed34068e…`, ui_digest `5c85b7e3…`.
- Unverified: no live visual pass of production from the agent sandbox (egress blocked); no real-device Safari pass. Navigation lifecycle work continues separately in PR #163 (`chat/nav-ab-baseline-1fc1b7`).

### Alive 2 app-wide + phone fixes — 2026-10-17 (PR #165, PR #166)

- Claim `alive-app-wide-alive-2-runtime-heard-guided-carr-1d6ebe`. Mobile Editor shell files (`app.py`, `web/game_editor_mobile_component/index.html`, `editor.css`) handed over by the owner from `fix-mobile-editor-global-shell-20261017` (coord `92fc2de`).
- PR #165 (merge `719ed28`): `web/gsf_alive_v418.js` — one browser runtime inlined verbatim (`tools/gsf_alive_inline.py`) in Home, Crea con IA, Crea Short, Creator Hub. Heard (tap echo, orb heartbeat, handwritten whisper), guided (`data-alive-next` guide ring + one idle nudge per state), carried (companion bubble across pages for upload/AI/render/publish, celebration, "Short pronto · Pubblica"). Facts only from page lifecycles, `/share/state`, `/publish/status`, `/job/status` (render followed only when the server reports it running). AI/Crea Short/Hub keep their single-script contracts. Tests `tests/test_alive_runtime_v418.py`, `tests/js/gsf_alive_v418.test.mjs`. Promoted with #164 in `01faeb7`; Railway frontend `728bbd9b-4769-468b-aa32-d3a91cac595c` SUCCESS (two earlier attempts FAILED at container start with `cp: target '-'`, before the app's own startup lines; owner's manual redeploy succeeded).
- PR #166 (squash `38c1458`): Home cards no longer under the shell Game Bar on iPhone (Night Arena removed the hidden footer reserve; `GSF_HOME_SHELL_FIT` sizes the hidden nav row to what the Game Bar covers), upload label kept inside the ring; open mobile Editor no longer near-white (`v393EditorShellCleanup` out-ranked the Night Arena shell rule) — shell surfaces not covered by Night Arena now `#050D16`. Alive: `/job/status` `missing` no longer raises a render error; errors calm after 3 min, Riprova bubble lasts 90 s; stronger halo.
- PR #166 checks: contracts, browsers, production-gate success. Main gate run `39043610465` success, promotion skipped (coord-only `af7fcc8` landed mid-run); owner-requested promotion commit `bf452af` (frontend marker → `38c1458`).
- Railway frontend `1ab38740-7e8b-474e-aefc-e228e9157949`: **SUCCESS** — `GSF UI manifest verify PASS digest=b8e17298… files=181`, `release=bf452af`; Railway `/healthz` healthcheck passed. Worker not redeployed (expected).
- Unverified / follow-up: no real-device pass (owner screenshots only); Alive not yet in the mobile/desktop Game Editor (desktop editor still in the stability claim); Railway logs show Streamlit `st.components.v1.html` deprecation lines and a per-minute `GSF_FINAL_BUCKET_RESTORE_WARN` (not errors, left untouched).

## Current user-facing verification priorities

These are re-verification priorities, not claims that a feature is currently broken:

1. `Crea con IA` — full path from Home to generated candidate/result.
2. `Game Editor` — open/load media/controls/mobile+desktop/return navigation.
3. `Crea Short` — final generation through share/download.
4. Global Game Bar / Creator Hub navigation — no stale inherited route state.
5. Mobile/desktop shell consistency after UI changes.

Always reproduce against the current deployed build before marking one fixed/broken.

## Active work

Live ownership is read from `.gsf/claims/index.json` and is authoritative. As of the Game Editor V403 handoff, multiple isolated claims are active; notably `alive-core-v405-b6f2a1` owns `app.py`. Never infer that a completed CI run releases a claim: only the registry state does.

## Mandatory coding protocol

1. Read `AGENTS.md` and this file.
2. Refresh `main` and `.gsf/claims/index.json`.
3. Acquire a narrow claim before product edits.
4. Work only on the dedicated branch/worktree or equivalent isolated connector branch.
5. Run relevant tests.
6. Reconcile current `main` before integration.
7. Let Production Gate and Railway own runtime promotion.
8. Verify Railway health or guarded rollback outcome.
9. Update factual project memory and release/complete the claim.

**Never write `SUCCESS`, `LIVE`, `fixed`, or `done` without fresh evidence.**

## Recent verified milestones

- **V402:** Game Brain / Auto Highlights 2.0 remains the current product baseline.
- **2026-10-13:** Production Gate made version-independent in behavior and marker-gated.
- **2026-10-13:** Railway frontend moved to composite `/healthz` and marker-only deploy trigger.
- **2026-10-13:** `PROJECT_STATUS.md` + `AGENTS.md` established as shared cross-chat memory/protocol.
- **2026-10-13:** PR #110 integrated atomic multi-chat claims, guarded rollback policy and one-command workflow.
- **2026-10-13:** Main Production Gate #51 PASS; frontend deployment `eb0d89ed-9cc1-4719-8682-032cbad307de` verified SUCCESS/Online.
- **2026-10-13:** GSF Guardian updated to guarded automatic rollback policy.
- **2026-10-14:** Game Editor V403 support engine and deterministic integration patch merged via PR #112; runtime UI integration intentionally deferred while `app.py` remains under an active non-overlapping owner claim.

---

When this file disagrees with chat memory, verify GitHub/Railway and update this file. Never silently choose the more convenient version of events.


## Navigation / mobile resume structural investigation — 2026-10-16

- Claim/branch: `stability-unified-navigation-and-mobile-resume-l-395391` / `chat/stability-unified-navigation-and-mobile-resume-l-395391`.
- Explicit handoff authorized by the user for mobile `editor.mjs` and its test; preserves the merged Editor restyle, Hub V415 and AI shell fit.
- Confirmed causes: independent route owners bypassed Editor cleanup; stale async saves/bootstrap replayed old routes/state; parent bridges depended on transient Streamlit iframes; legacy cleanup removed React-owned V249 navigation (native DOM instrumentation recorded the exact node before React `removeChild` failed); reconnect selected the wrong Python `web/web` package after late `sys.path` mutations.
- Fix: one parent navigation/lifecycle registry, persistent top-owned surfaces and controllers, abortable bridge replacement and route epochs, Editor suspend/resume without history reset, explicit canonical Python package/bootstrap. Clean Streamlit socket closure only on pagehide; ordinary background retains transport. Completed bridge timers release their abort handlers.
- Evidence: import-resolution regression failed before correction and passes four reloads; 100-timer retention regression failed before correction and passes afterward. Current selected suite: 26 passed / 12 browser skips without running URL; JavaScript contracts 16 passed. Production-image browser checks use real uploaded media and fail on JS, console, HTTP and request errors.
- Full final browser stress, integration PR, main Production Gate and Railway verification remain pending. No new production fix is claimed by this entry. Physical OS switching and physical iOS/Safari remain unverified.
- Investigation and regression design: `docs/architecture/gsf-navigation-lifecycle.md`.
- PR181 Hub dialog fix is LIVE: source `af360f80be41b9a63aff05a368fc17716942151a`, release `d25963d2e986ba214efccbc7f3195eeaaddd1c3f`, Railway frontend `785a10dd-91d5-461b-bfbb-7b9c4b588d64` SUCCESS. Main Gate `39422951850` and Production UI Verify `39425058847` SUCCESS. Exact live UI digest `6582b512405a0c8b1ddfda69ddbb09ee11965c920ee456f5488d1bbb0361552f` and composite health verified. Fresh public Chromium audit across four phone viewports and full 30-check upload/AI/Editor/edit/render/export/save/refresh/Back/Hub rename/download/delete/cancel journey PASS with no runtime errors. Dark canvas/Alive, icons and existing desktop/iPad gates PASS. PR182 tests-only source `2d3d519fb3db73d76682c1bd2c4e1730c1ee372e`: CI `39424692491` and main Gate `39425201220` SUCCESS; promotion correctly detected no runtime changes and did not redeploy.
- PR183 final mobile stabilization runtime is LIVE: source `1f175d4c26a942ffe7ec007ebfab96d263bb3941`, release `28af3c6bd610bdee44828e77a7ea17b66bbc9b4c`, UI digest `9a2fb8e66b70525305066023215ccd4cf80c781b55f7b33f9298e745c79f3d7e`. Main Production Gate `39432052107` and Production UI Verify `39434485854` SUCCESS; Railway frontend `ce1eda10-5611-4b0b-8d17-e80adc40eea1` SUCCESS. Final unmodified public verification PASS: 30-check upload/AI/moment/Editor/edit/render/export/save/refresh/Back/Hub CRUD journey with no runtime errors; four Chromium and four WebKit phone viewports; Alive and dark safe area; valid source/192/512 icons and dark manifest; existing desktop/iPad gates. Fresh composite health and served monitor bytes match the release. PR184 tests-only follow-up is merged (`d3cc447e42719a89276d06019abb76d9f24b4d34`); CI `39470402408` and main Production Gate `39470650331` SUCCESS: actual native reload-and-dismiss catches WebKit microtask ordering, prevents false cancellation exemptions, and waits for asserted scroll geometry. Local WebKit suite 45 passed, 10 skipped, 13 subtests; Chromium two targeted browser tests PASS. Current stabilization work is verified; broader beta readiness remains separate. Physical iPhone Safari/installed PWA and real-gameplay semantic accuracy remain unverified; synthetic fixture timing is not gameplay-quality evidence. Social files were explicitly transferred on main to active claim `social-oauth-master-youtube-tiktok-meta-fb-ig-tw-cdbf69`; do not start overlapping Meta/TikTok/Twitch implementation here. Broader pre-beta/WOW work remains queued.


### OAuth PR185 and Source Library design — current 2026-10-20

- OAuth PR185 merged source593a53e1e43d9e0592ffd14a33c7c0c94ce1fb24. CI39481339171, PRGate39481339130 and mainGate39483685079 SUCCESS. Automatic promotion f0bbff6b406ef3a4d330166284c2509e689f051e references source593a. Local full suite259pass/20skip, final OAuth49tests/2skip, real WebKit and independent security review passed.
- New release is NOT online. User explicitly authorized unchanged frontend repo/main reconnection with «vai». Two authorized Railway attempts returned Deploys have been paused temporarily before creating a deployment. Previous release28af3c6bd610bdee44828e77a7ea17b66bbc9b4c remains live, frontendce1eda10 SUCCESS, fresh compositehealthalltrue. Do not re-ask deployment authorization or bypass pause. Missing Meta/Instagram/Twitch credentials and real provider consent remain blockers.
- User subsequently requested Twitch Stream/VOD Source Library while awaiting Railway. Existing implementation has official own-clip import but no durable library/dedup/live listing. Current phase: repository/API analysis and written design; no new source-library runtime implementation or deployment. Preserve Editor/AI/render and YouTube OAuth.
- Coordination correction: earlier helper callbacks wrote PROJECT_STATUS.md in temporary worktrees but did not stage it (_mutate_main stages .gsf only). Claim evidence was committed; this entry explicitly stages current factual project memory, preserving all prior entries.
