# Creator Hub Mobile Hierarchy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the mobile Creator Hub into clean folder-first screens with no duplicate headings and no root-level scrolling for Live/Profile.

**Architecture:** Add one final, restart-safe V357 patch after V352. CSS overrides legacy mobile geometry only at <=767px; JS reuses the existing Live platform cards and Profile social rows so existing handlers/state remain intact.

**Tech Stack:** Python startup patcher, HTML/CSS/vanilla JS, Streamlit component runtime.

**Spec:** `docs/superpowers/specs/2026-10-09-creator-hub-mobile-hierarchy.md`

## Global Constraints
- Mobile only: max-width 767px.
- Desktop unchanged.
- Global Game Bar/footer unchanged.
- Existing Live mini-folder and social connect handlers preserved.
- V357 runs after V352 and is restart-safe.

## Review Focus
- Switching between Dashboard, Projects, Live and Profile must restore the correct root/detail state.
- Project landing and Shorts/Drafts destinations must have one title only.
- Live platform detail must show all three existing mini folders without root scrolling.
- Social detail must reuse original rows so connection state remains live.
- Small iPhone widths/heights must not clip the back controls or fixed global navigation.

---

### Task 1: Contract tests

**Files:**
- Create: `web/test_v357_creator_hub_hierarchy.py`

**Interfaces:**
- Consumes: V311/V352 Creator Hub anchors.
- Produces: regression contract for the V357 patch and startup ordering.

- [ ] Write the test first against a minimal normalized Hub fixture.
- [ ] Assert V357 marker, mobile-only selectors, Projects legacy-header suppression, two Live root folders, Live back/detail state, Social folder/detail state, original-row reuse and restart safety.
- [ ] Assert `start_web.sh` invokes V357 after V352.

### Task 2: V357 hierarchy patch

**Files:**
- Create: `web/fix_v357_creator_hub_hierarchy.py`
- Modify: `web/start_web.sh`

**Interfaces:**
- Consumes: `#projectHubCards`, `.livePlatformTwitch`, `.livePlatformYoutube`, `.profileSocialRef`, `.profileSocialRows`, V352 marker.
- Produces: `V357_CREATOR_HUB_HIERARCHY`, `v357LiveRoot`, `v357SocialBack`, mobile state classes.

- [ ] Implement a restart-safe patch inserted before `</body>`.
- [ ] Hide the legacy component top only when Projects or Live is active; preserve Dashboard and desktop.
- [ ] Override Projects spacing and leave one internal title.
- [ ] Build Live root with Twitch/YouTube folder cards; reuse original platform cards for detail and add Back.
- [ ] Collapse Profile Social into one folder card; expand the original social rows in a dedicated detail state with Back.
- [ ] Increase Profile main spacing while keeping it no-scroll on standard mobile heights.
- [ ] Run V357 fix/test from `start_web.sh` after V352.

### Task 3: Deployment verification

**Files:**
- No new files.

**Interfaces:**
- Consumes: merged V357 commit.
- Produces: verified Railway production deployment.

- [ ] Merge V357 to `main`.
- [ ] Verify Railway build/startup logs contain `V357 CREATOR HUB HIERARCHY: PASS` and Streamlit startup.
- [ ] Verify production has one running frontend replica and no current critical/warning state.