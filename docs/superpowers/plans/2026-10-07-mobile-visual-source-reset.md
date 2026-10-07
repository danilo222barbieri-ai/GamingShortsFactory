# Mobile Visual Source Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove every legacy desktop-only visual layer from the production assembly path while preserving GSF behavior, then make the existing mobile presentation the only visual source for desktop and mobile.

**Architecture:** Keep functional patches and event bridges intact. Stop invoking desktop rebuild/rebalance scripts, then run one final sanitizer after all functional/mobile patches. The sanitizer removes desktop-only media blocks and legacy desktop marker/runtime layers, unwraps mobile viewport rules so they apply at every width, and bumps component cache keys.

**Tech Stack:** Python 3, static HTML/CSS/JS components, Streamlit component embeds, Railway startup shell.

**Spec:** User directive in current project conversation: delete the desktop graphics completely, keep logic, then carry the mobile presentation to desktop.

## Global Constraints

- Preserve upload, AI, Editor, Creator Hub, drafts/projects, social, navigation, rendering and Game Bar behavior.
- Preserve the current mobile visual rules as the source of truth.
- No V294/V296/V297/V298/V301/V305 desktop visual layer may be invoked or survive in served components.
- No viewport `min-width` desktop CSS may survive in the final served Home, AI, Hub, Editor, Share or structural shell.
- Mobile-only viewport CSS must become width-agnostic rather than creating a second desktop design.

## Review Focus

- Desktop-specific CSS re-entering through startup patch order.
- V297/V298 DOM wrappers reappearing around functional controls.
- Mobile rules depending on shared base rules that must remain intact.
- Cache keys serving stale pre-reset component assets.
- Sanitization accidentally changing JavaScript/Python logic.

---

### Task 1: Add purge contract

**Files:**
- Create: `web/test_v307_mobile_visual_source.py`

- [ ] Write unit coverage for removing `min-width` media, unwrapping mobile `max-width` media, removing legacy desktop marker/script blocks, and preserving JS logic text.
- [ ] Add integration assertions for the final production component files.

### Task 2: Implement final visual sanitizer

**Files:**
- Create: `web/fix_v307_mobile_visual_source.py`

- [ ] Implement brace-safe media parsing.
- [ ] Remove legacy desktop marker/runtime layers.
- [ ] Remove every viewport `min-width` media block.
- [ ] Unwrap mobile/tablet `max-width` viewport media up to 1024px so the current mobile presentation becomes global.
- [ ] Process Home, AI, Hub, Editor, Share and the structural Streamlit shell.
- [ ] Bump component/embed cache identifiers to V307 where applicable.

### Task 3: Remove desktop assembly path

**Files:**
- Modify: `web/start_web.sh`

- [ ] Stop invoking V294, V296, V297, V297.1 and the V299 pre-V297 restore chain.
- [ ] Keep functional/mobile patches V285–V293, V295, V300, V302, V306, V303, V304.
- [ ] Run V307 last, then its integration test, before generating the V293 production app.

### Task 4: Verify production deployment

- [ ] Confirm V307 contract PASS in Railway logs.
- [ ] Confirm legacy desktop patch markers are absent from the served assembly path.
- [ ] Confirm application starts successfully with functional contracts still passing.
