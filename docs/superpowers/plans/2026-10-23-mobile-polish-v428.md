# GSF Mobile Polish V428 — Implementation Plan

## Goal
Stabilize the current mobile beta without adding product scope: keep editor work as draft state until an explicit Crea Short action, simplify the AI moments screen, unify notifications into one readable handwritten surface, remove the legacy white navigation surface behind the global Game Bar, and make Instagram connection prefer the direct Instagram OAuth flow when its credentials are configured.

## User-approved behavior
- Editor close/shrink saves state only; it never starts final render.
- Final render starts only from explicit Crea Short.
- Expanded editor must not show the placeholder title “Nuovo gameplay”.
- AI moments header contains only Cambia motore and Trova altri momenti; status chips are removed.
- Three AI moments are horizontally swipeable with page dots; the detail card follows the selected moment.
- AI result CTA says Crea Short, not Pubblica.
- One notification system only, outside the profile/header slot, with longer readable lifetime and handwritten GSF styling.
- The old Home navigation surface cannot appear behind the global Game Bar.
- Instagram connection is fixed independently of publication. When direct Instagram credentials exist, use Instagram OAuth; retain Meta/Facebook only as fallback.

## Tasks
1. Add regression tests first for all approved behaviors and run CI to observe RED.
2. Fix Instagram OAuth selection with the smallest server change.
3. Fix Game Editor title/close contract and verify close only persists draft state.
4. Simplify the AI moments screen and add swipe carousel/page indicators without changing the analysis flow.
5. Collapse notifications to the parent-owned GSFNotify presentation, remove header-inline placement, lengthen readable lifetime, and apply handwritten styling.
6. Hide the legacy Home bottom navigation whenever the parent/global shell is active so no white surface can peek under Game Bar.
7. Run targeted tests, JavaScript syntax/contracts, full CI, Production Gate candidate checks, and self-review the branch before requesting merge.

## Constraints
- Feature freeze: no new engines, publishing modes, rendering behavior, or social providers.
- Preserve current working upload → AI moments → editor → Crea Short flow.
- Do not bypass or weaken WebKit/Production Gate checks.
- No automatic Railway promotion from this branch; merge/deploy remains a separate release action.
