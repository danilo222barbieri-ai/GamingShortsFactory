# GSF Source Library + Twitch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Twitch an account-isolated source library in the existing Creator Hub, with reusable official clip imports and honest Live/VOD metadata.

**Architecture:** Add a thin source catalog over existing private bucket assets and upload markers. Extend the current Twitch adapter and Hub view; keep the existing materialization, analysis, Editor and render pipeline.

**Tech Stack:** Python companion server, existing S3-compatible storage/Fernet/session infrastructure, canonical Hub HTML/JS/CSS, unittest/pytest and Playwright Chromium/WebKit. No new product dependencies or services.

**Spec:** `docs/superpowers/specs/2026-10-20-source-library-twitch-design.md` (architecture explicitly approved by user on2026-10-20).

## Global Constraints

- No changes to OAuth YouTube, social publishing or Game Editor runtime.
- No Live recording, VOD downloading, scraping or extracted HLS.
- Existing Twitch scope `channel:manage:clips`; no additional mandatory Railway variables.
- Existing clip limits512MiB/120second download/15second socket retained.
- Only real valid1–3 moments; never fabricate three or reject one valid moment.
- Railway deploy remains paused; prepare and test branch without claiming production verified.
- Before product edits extend this chat's existing claim to each new source/test file and updated Hub contract. Reuse the isolated current worktree. Preserve existing deployment authorization and evidence.

## Review Focus

- Account changes on the same SID must never expose the previous owner's catalog/assets.
- A bucket outage must not silently change authenticated ownership to guest or mark an import committed.
- A completed old import must not replace a newer upload or navigate away from another active page.
- Missing category/thumbnail, malformed duration or very long VOD must not break usable content lists.
- An already-imported clip whose object disappeared must not remain falsely ready or trigger uncontrolled duplicate downloads.

---

### Task1: Source records and durable catalog

**Files:** Create `web/gsf_sources_v422.py`, `tests/test_source_library_v422.py`; modify companion source-catalog helpers only.

**Interfaces:** Pure helpers `source_id(owner,kind,provider_user_id,external_id) -> str`, `public_source(record) -> dict`, `duration_seconds(value) -> float|None`; companion `_source_owner(sid) -> str`, `_source_load(sid,source_id) -> dict`, `_source_save(sid,record) -> dict`, `_source_list(sid,provider,folder,after) -> dict`. Owner resolution fails closed on storage/account errors. Catalog responses omit bucket keys, local paths and credentials.

- [ ] Write failing tests `test_ids_are_owner_and_provider_account_scoped`, `test_public_record_excludes_private_fields`, `test_sid_reuse_cannot_read_previous_owner`, `test_storage_failure_does_not_publish_local_record`. Assert different owners produce different IDs; private fields absent; foreign lookup denied; failed durable write leaves committed cache unchanged.
- [ ] Run `/workspace/.venv-beta/bin/python -m pytest -q tests/test_source_library_v422.py`; confirm failures identify missing behavior.
- [ ] Implement helper and catalog on existing bucket storage, separate record keys, bounded pagination and per-record locking. Preserve unknown/unavailable metadata without invented values.
- [ ] Run new tests and `tests/test_social_oauth_v421.py`; require PASS. Commit catalog change.

### Task2: Official Twitch discovery with honest capabilities

**Files:** Companion `_twitch_api` and `_twitch_content`; new source tests.

**Interfaces:** `_twitch_content(sid,kind,after='')` accepts existing `clips`/`videos` plus `live`; returns backward-compatible `data`, `cursor`, `type`, with thumbnail/category/date/duration/source_id/capability fields. `streams` and `games` are added to the exact API whitelist; token lifecycle unchanged.

- [ ] Add failing tests `test_offline_is_real_empty_live_state`, `test_live_has_no_import_capability`, `test_vod_and_highlights_never_offer_media_import`, `test_own_clip_has_thumbnail_category_and_duration`, `test_missing_category_is_not_api_failure`, `test_foreign_broadcaster_is_excluded`, `test_long_vod_metadata_does_not_start_download`.
- [ ] Run focused tests and confirm RED.
- [ ] Implement owner-filtered API queries, batched category lookup, validated HTTPS metadata and explicit `import_reason`. Preserve existing expired/revoked/API failure handling, scopes and routes.
- [ ] Run source/OAuth tests; require PASS. Commit discovery change.

### Task3: Reusable import and safe source activation

**Files:** Companion upload-completion/import/activation helpers; source tests. Do not edit Editor or publisher.

**Interfaces:** `_source_activate(sid,source_id,target) -> dict`; target limited to `ai`/`editor`. Reuse `_persist_fallback_source_to_bucket`, `_materialize_bucket_object` and `.direct_upload_ready.json`. Existing Twitch import response retains upload_id/preparing and adds source_id/reused when applicable.

- [ ] Add failing tests `test_same_clip_downloads_once`, `test_imported_clip_survives_reload`, `test_bucket_reuse_never_calls_twitch_download`, `test_missing_object_is_not_ready`, `test_new_upload_fence_preserves_current_project`, `test_incomplete_import_recovers_after_restart`, `test_account_switch_during_import_cannot_publish_marker`, `test_upload_catalog_has_one_real_entry`, `test_legacy_source_requires_owner_provenance`, `test_failed_activation_keeps_previous_project`.
- [ ] Run targeted tests; record RED.
- [ ] Register real completed assets with private owner provenance, deduplicate before requesting clip media, reconcile existing imports and validate cached/bucket assets. Reuse a verified asset rather than downloading it again. Keep previous marker on persistence/materialization/fence failure; use existing draft-save flow before changing an editable project.
- [ ] Add CSRF-protected POST `/creator-hub/sources/activate` and GET `/creator-hub/sources`; consume only opaque IDs and server-authorized references. Do not relax ordinary upload endpoints' path/key validation. Test missing CSRF403, invalid target400, foreign ID403/404 and storage/provider failure retry behavior.
- [ ] Run source/OAuth/upload and existing mobile project state tests; require PASS. Commit backend integration.

### Task4: Hub Source Library

**Files:** `web/creator_hub_v156_component/index.html`, new source browser tests, relevant assertions in `tests/test_creator_hub_redesign_v415.py`.

**Interfaces:** Existing shell target `hub`, legacy Hub view alias `live` and back behavior retained. Source filters persisted as presentation state, source/job truth fetched from server. Existing Twitch import and status endpoints reused.

- [ ] Add failing actual-browser tests `test_library_folders_are_data_backed`, `test_live_vod_have_no_import_cta`, `test_imported_clip_exposes_ai_editor_actions`, `test_refresh_restores_folder_and_import_status`, `test_stale_fetch_does_not_replace_new_folder`, `test_navigation_cancels_poll_without_hijacking_route`, `test_cards_and_sheet_clear_gamebar_on_small_phone`. Assert zero pageerrors and no tokens/private source fields in DOM/responses.
- [ ] Run browser tests in Chromium, confirm RED against the old placeholder/sheet.
- [ ] Replace the empty Live/VOD view with compact dark/glass Sorgenti using current card/sheet/back/fitHub infrastructure. Upload/Twitch/YouTube folders; Twitch Live/VOD/Clip/Importati. Render real thumbnails and metadata safely, `Importata` status, explicit unsupported reason and reconnect/retry/offline/empty states. YouTube remains clearly unavailable as a source and preserves current publishing connection.
- [ ] Connect explicit AI/Editor actions only after server activation succeeds; retain current pipeline/navigation and1–3 real moment handling. Preserve route epochs, abort polling/fetches on view exit, and avoid resetting scroll from stale responses.
- [ ] Run Chromium and real WebKit source tests plus existing Hub/Alive/navigation/Editor contracts; require PASS. Commit UI integration.

### Task5: Integration, review and factual handoff

**Files:** Source tests; `.github/workflows/v397-production-gate.yml`; project status/report. Add source tests to image/API and real WebKit blocking steps without removing current checks.

- [ ] Run full `GSF_BROWSER=webkit PLAYWRIGHT_BROWSERS_PATH=/workspace/scratch/gsf-webkit-browser PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 /workspace/.venv-beta/bin/python -m pytest -q tests`, canonical/security/publish/Hub contracts and Editor JS tests. Require PASS and report every skip/limit.
- [ ] Exercise controlled Twitch media through the real GSF pipeline to materialization→IA→valid moments→Editor; do not replace GSF behavior with mocks. Retain backend provider fixtures only where external credentials/consent are unavailable.
- [ ] Obtain independent code review, correct concrete issues with regression tests, refresh main and reconcile claim scope before PR. Attach created PR. Let CI/Production Gate validate the branch; do not bypass a failed check.
- [ ] While Railway is suspended, report new feature as tested branch/prepared, never LIVE. After Railway resumes and integration is ready, use existing authorization and gate-owned deployment path; verify actual SUCCESS, health, source/UI identity and public routes.
- [ ] With real Twitch credentials and creator consent, verify OAuth→Library→own Clip→Import→real IA→valid moments→Editor. Until this passes report that exact real-provider gap. Document official VOD/Live limits, files, tests, variables and actual commit/PR/deployment state; update claim/project memory truthfully.

## Self-review

All requested folders and metadata map to tasks1/2/4; persistent deduplication and upload/clip activation to tasks1/3; ownership and failure cases to tasks1–3; Game Bar/refresh/navigation to task4; pipeline and real-provider/production evidence to task5. No new OAuth system, dependency, recorder or publishing changes. Architecture approved; this written execution plan awaits the required user review before product implementation. Execution stays direct in this session as requested.
