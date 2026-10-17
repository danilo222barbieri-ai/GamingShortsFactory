# Gaming Shorts Factory — Project Status

> **CANONICAL SOURCE OF TRUTH FOR ALL TECHNICAL CHATS / AGENTS.**
> Read this file before changing code. Refresh live GitHub/Railway evidence before changing production claims.

## Snapshot

- **Repository:** `danilo222barbieri-ai/GamingShortsFactory`
- **Production branch:** `main`
- **Current product baseline:** **V411 UI on the canonical UI pipeline** (repo files == served files; see `docs/architecture/gsf-canonical-ui.md`)
- **Cross-chat orchestration:** **LIVE**
- **Last fully tested main source commit:** `154eac8006222152b137d2094752cab83f7f5457` (PR `#150`)
- **Last runtime promotion commit:** `36ff30369974ccbc21fa5c0416544acfdc164806` — `deploy: promote tested 154eac800622 [skip ci]`
- **Served canonical UI digest:** `b3a16c2909e0c11a7159830b9875f93c33f84e62014adb3ce5fd7358daf613fb` (`/healthz` → `ui_digest`)
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
