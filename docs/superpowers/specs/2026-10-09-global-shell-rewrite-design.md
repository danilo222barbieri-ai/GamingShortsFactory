# Gaming Shorts Factory — Single Global Shell Rewrite

Date: 2026-10-09
Status: Design approved in chat; implementation not started

## Problem

The current application has accumulated multiple independent systems that all try to own the same global UI chrome: header/logo/account, Game Bar, and footer. At runtime these systems can hide, remount, restyle, or supersede one another. Static startup tests may all pass while the browser still shows no global chrome. Recent examples include V330, V332, V334, V341 and V342 all touching the same shell contract.

The result is unstable global navigation and visibility. The Editor route is now working, but header, Game Bar and footer are not reliably visible across the site.

## Goal

Replace the competing chrome systems with exactly one parent-owned Global Shell that is the sole authority for:

- fixed global header;
- fixed global Game Bar;
- fixed global footer;
- layout reserves around page content;
- account presentation in the header;
- global navigation dispatch;
- global chrome persistence across page/overlay changes.

Every functional page must render only its own page content inside the space reserved by the Global Shell.

## Required visible behavior

### Header

The header is always visible at the top of every page and overlay. It contains:

- official GSF logo;
- text `GAMING SHORTS FACTORY`;
- account area on the right: profile photo + name when available, otherwise `Accedi`.

The header must use iPhone/iPad safe-area insets and must never be hidden by internal pages or overlays.

### Game Bar

The Game Bar is always visible near the bottom of the viewport and above the footer. It is the only global primary navigation bar.

Canonical destinations:

- Home → Home;
- Hub → Creator Hub dashboard;
- Progetti → project area;
- Live → Live area.

The active item reflects the current route/view. Navigation messages are handled by one canonical router only.

### Footer

The footer is always visible below the Game Bar. It contains the approved social shortcuts and `Segnala bug`. It owns the bottom safe-area padding on iPhone.

### Content viewport

All page content is constrained to the rectangle between the header and the combined Game Bar/footer region. Internal pages may scroll internally where already allowed, but the Global Shell itself never scrolls away.

The Home remains fixed/non-scrolling.

## Architecture

### Single owner

Create one new shell implementation, referred to as `GSF_GLOBAL_SHELL_V343` in code/tests.

It runs in the parent Streamlit document and creates exactly three root elements:

- `#gsf-global-header`;
- `#gsf-global-gamebar`;
- `#gsf-global-footer`.

Only this system may create, hide, show, reposition or remount these three elements.

### Canonical CSS variables

The shell defines the authoritative geometry variables on the parent document:

- `--gsf-shell-header-h`;
- `--gsf-shell-gamebar-h`;
- `--gsf-shell-footer-h`;
- `--gsf-shell-safe-bottom`;
- `--gsf-shell-content-top`;
- `--gsf-shell-content-bottom`.

All persistent overlays/surfaces use those values for their top/bottom bounds. No overlay may use a z-index higher than the Global Shell chrome.

### Z-index hierarchy

Use one explicit hierarchy rather than version-specific values:

1. page content / child iframes;
2. page overlays and dialogs;
3. Global Shell chrome;
4. temporary system notices only when truly modal.

The Editor, AI, Short, Creator Hub, Social and Account surfaces must all sit below header/Game Bar/footer.

### Canonical navigation

One parent message listener handles `GSF_SHELL_NAV`. Existing pages may continue emitting the message, but old listeners that also mutate global chrome must be retired.

The navigation handler owns:

- opening/closing known surfaces;
- setting active Game Bar state;
- preserving Home state;
- switching Hub sections;
- ensuring chrome remains mounted.

Editor routing that now works must be preserved. The shell rewrite must not reintroduce the old Editor dependency on a pre-existing overlay.

### Account state

The header fetches account data from the existing Creator Hub state endpoint. Preferred display order:

1. `display_name`;
2. `nickname`;
3. `name`;
4. `username`;
5. email prefix;
6. `Accedi`.

When a profile image exists, show it. Otherwise show a compact initial/avatar placeholder.

## Removal / retirement plan

The following systems must stop owning global chrome behavior:

- V330 global brand/footer behavior;
- V332 global frame-lock visibility behavior;
- V334 global chrome creation/visibility behavior;
- V341/V342 global shell watchdog/suppression behavior.

They may remain in repository history, but startup must no longer execute them as active chrome authorities. If any of their unrelated fixes are still required, extract those responsibilities into focused scripts/tests rather than keeping their shell logic alive.

V328/V331/V333 behavior unrelated to chrome should be preserved only where still necessary. In particular, the working Editor canonical route must survive the cleanup.

## Local page chrome policy

Each child page/iframe is content-only with respect to global chrome.

The new shell applies one child-document policy that hides only known legacy local chrome elements when the parent shell is active. This policy must not hide page-specific titles, Editor controls, or functional page headers that are not duplicates of the global brand.

Home placeholders may reserve geometry if needed, but they must not render a second visible header/Game Bar/footer.

## Persistence model

Use a single MutationObserver/watchdog owned by V343. Its only jobs are:

- verify the three global root elements still exist;
- remount them if Streamlit replaces the parent DOM;
- reapply content bounds to newly mounted known overlays/iframes;
- never create duplicate shell instances.

No interval or observer from older shell versions may independently show/hide global chrome.

## Mobile requirements

On iPhone/iPad:

- honor `safe-area-inset-top`, left, right and bottom;
- footer must remain above the browser/home-indicator safe area;
- Game Bar sits above footer with a fixed visual gap;
- no Home CTA may be covered by the Game Bar/footer;
- no internal page button should be trapped underneath the shell;
- touch targets remain at least the current approved sizes.

## Desktop requirements

The same shell contract is used on desktop. Geometry may be wider/more centered, but the ownership model is identical: one header, one Game Bar, one footer.

## Testing strategy

Tests must move from marker-only/static assertions to contract tests that verify the final generated runtime shell source.

Required tests:

1. Exactly one global header ID, one Game Bar ID, one footer ID in the generated runtime source.
2. Startup no longer runs the legacy shell authorities V330/V332/V334/V341/V342 as active global-chrome controllers.
3. Canonical router contains routes for Home, Hub, Progetti, Live, Editor and Short.
4. Editor surface remains created on demand and points to `/editor-live/`.
5. All known overlays are constrained by the global content top/bottom variables.
6. Global shell z-index is higher than known overlays.
7. Mobile safe-area variables are present and applied.
8. Account label fallback is `Accedi`.
9. Shell watchdog is singular and idempotent.
10. Generated Python runtime compiles.

After Railway deploy, runtime verification must include actual HTTP/browser evidence rather than only startup logs:

- Home: header/Game Bar/footer visible;
- Editor: header/Game Bar/footer still visible after opening Editor;
- Creator Hub: same chrome visible and routes work;
- Short: same chrome visible;
- no duplicated `GAMING SHORTS FACTORY` branding;
- no duplicate Game Bar/footer;
- no CTA covered by fixed chrome.

## Rollout

Implementation is done on an isolated branch. Before promotion to `main`:

- run the new V343 tests;
- run existing navigation/Editor tests that remain relevant;
- inspect diff to ensure only chrome ownership is being consolidated;
- deploy once, not through a chain of speculative intermediate builds;
- verify live runtime before declaring success.

## Non-goals

This rewrite does not redesign the Home, Editor controls, AI engines, Creator Hub cards, render pipeline, upload system or social connection flows. It changes only the ownership and persistence of the global site shell and the minimum routing needed to keep that shell coherent.

## Success criteria

The rewrite is complete only when:

- the working Game Editor still opens;
- the global header is visible on every page;
- the official logo and `GAMING SHORTS FACTORY` text are visible in the header;
- profile/name or `Accedi` is visible at top right;
- Game Bar is visible and functional on every page;
- footer is visible on every page;
- there are no duplicate global chrome elements;
- no internal page or overlay can hide the shell;
- the behavior is stable after navigation and Streamlit rerenders.
