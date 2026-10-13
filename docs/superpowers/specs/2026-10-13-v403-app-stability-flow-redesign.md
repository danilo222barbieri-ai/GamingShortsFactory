# V403 — App Stability & Flow Redesign

## Status
Design approved in chat on 2026-10-13. This document captures the agreed architecture before implementation planning.

## Production baseline
- Current production/main baseline: `845a36f5c586756743fe6f41b1f07cda3fb5246d`.
- V402 Game Brain / Auto Highlights 2.0 is already merged and production-verified.
- Preserve the V401/V402 production guarantees: bounded frontend upload streaming, persistent worker state, restart recovery, stable progress, no eager highlight rendering, 1080×1920 / 60 fps render quality, and current AI ranking pipeline.
- Preserve Editor 2027 component identity exactly: `gsf_editor_2027_v1086`.
- Do not redesign or regress the approved Home.

## Problem statement
The current app still behaves like a set of partially independent screens rather than one durable project flow. The user reports:

1. The app can freeze or visually break after going into standby / background, returning from another app, or moving between menus.
2. The profile is not always retained or restored correctly.
3. The Motori page is structurally and visually wrong.
4. When AI moments are created, the page glitches and two of the three results can sit outside the usable viewport.
5. The three generated moments are currently being injected into the Motori screen instead of receiving their own dedicated selection page.
6. Because the moments flow breaks, the user often cannot reach the Game Editor.
7. The Crea Short page still uses an old final/share surface on desktop instead of the intended final creation flow.

These are related symptoms of one architectural weakness: too much important state and UI responsibility lives inside transient screens/components.

## Primary goal
Make GSF behave like one continuous, recoverable application in which changing route, backgrounding the app, resuming it, or reopening a functional surface never destroys or corrupts the current project.

The app must preserve the current video/project, profile identity, AI analysis state, generated moments, selected moment, editor handoff, and final render state independently of which screen is mounted.

## Non-goals
V403 does not add new AI models, change V402 ranking logic, redesign Home, change render quality, change social provider APIs, or replace Editor 2027.

The purpose is stability, flow separation, and restoring the intended product structure.

## Chosen architecture
Use a durable server-authoritative project/session state with thin route views.

No page, iframe, or Streamlit rerender should be the sole owner of important project state. Screens render from durable state and may cache presentation details locally, but the authoritative project state survives route changes, tab/app backgrounding, Streamlit reruns, and component remounts.

### Why this approach
It fixes the root cause instead of stacking more UI patches. It also lets Motori, Moments, Editor, Crea Short, Creator Hub, and Profile share the same project identity without each screen attempting to reconstruct the project independently.

## Rejected approaches
### A. Patch each broken screen independently
Rejected because it would leave the same state-loss problem in place and create more version-specific overrides.

### B. Keep project state only in browser memory/localStorage
Rejected as the authoritative source because mobile/standby lifecycle, iframe reloads, storage clearing, and cross-component state make it too fragile. Browser storage may retain small navigation hints, but not be the source of truth.

### C. Rebuild the whole app/router from scratch
Rejected because the production app already contains working upload, worker, render, Creator Hub, AI, and editor systems. V403 should introduce a stable state boundary and reorganize only the affected flows.

# 1. Durable application/project state

## 1.1 Authoritative state
Introduce or consolidate one project/session snapshot keyed by the existing authenticated/browser session and active project identity.

At minimum the snapshot must be able to represent:
- active project/session id;
- source video reference and readiness;
- current high-level route;
- selected AI engine and requested duration;
- analysis job state and progress;
- generated top-3 moment metadata;
- selected moment id/index and start/end timestamps;
- editor handoff state / editor source reference;
- final render status and final asset reference;
- draft/project identity where applicable;
- lightweight profile/account summary reference/version;
- last successful state update timestamp/version.

The snapshot stores references/metadata, not duplicate video blobs.

## 1.2 State lifecycle
Important state updates are committed at meaningful transitions rather than only when a page unloads:
- video accepted;
- analysis started;
- analysis completed;
- moments stored;
- moment selected;
- editor opened/updated;
- create-short render started;
- render completed;
- project saved as draft;
- explicit new-video/reset action.

`visibilitychange`, resume, and route transitions may trigger reconciliation, but correctness must not depend on receiving a browser unload event.

## 1.3 Resume / foreground behavior
When the app becomes visible again after standby/background:
1. keep the existing shell visible;
2. reconcile current client state with the authoritative project snapshot;
3. restore the current route only if that route is still valid for the recovered project state;
4. otherwise move to the nearest valid route without destroying the project;
5. resume polling only for active jobs;
6. never replace the UI with a permanent blank/broken state because one component failed to remount.

A resume must be idempotent: repeating it cannot duplicate jobs, moments, renders, or navigation.

## 1.4 Navigation behavior
The global Game Bar remains the main navigation system.

Navigation must be stateless/idempotent from the perspective of destinations: clicking Home, Hub, Progetti, Bozze, Live, Motori/AI, Editor or Crea Short always resolves the intended destination from current project state and never inherits a previous screen's internal route.

No destination should require another screen to stay mounted in the background.

# 2. Profile reliability

## 2.1 Profile source of truth
The profile must come from persistent account/session data, not from a transient UI component.

On navigation or resume:
- retain the last valid profile presentation while refreshing;
- never clear a valid name/avatar/plan to an empty placeholder just because refresh is pending;
- update only when a valid newer profile payload arrives;
- distinguish loading, unavailable, signed-out, and valid-profile states.

## 2.2 Failure behavior
A temporary profile fetch failure must not block the rest of the app. The last known valid profile may remain visible with a soft stale state while retry happens.

# 3. Motori page redesign

## 3.1 Responsibility
The Motori page becomes a focused input/configuration page only.

It contains:
- current video/project presence;
- available AI engines / modes;
- duration selection (15s / 30s and existing valid options);
- concise engine explanation/state;
- analysis CTA and analysis progress;
- errors/retry state.

It does **not** render the three final candidate moments in the same page.

## 3.2 Completion transition
When analysis finishes and top candidates are available:
- persist the candidate set first;
- navigate to the dedicated Moments page;
- do not append dynamically growing candidate UI under Motori.

This removes the current viewport/layout collapse that places candidate results outside the page.

# 4. Dedicated “I tuoi 3 momenti” page

## 4.1 Purpose
Create a separate selection surface whose only job is to let the user understand and choose among the three best moments.

## 4.2 Layout
The page uses the existing GSF visual language and may scroll internally while the global shell/Game Bar remains stable.

It contains exactly the available top candidates, normally three.

Each candidate card/player contains:
- vertical 9:16 preview/thumbnail/player;
- candidate number/rank;
- timestamp / duration;
- event/type label;
- confidence/score in a user-readable form;
- concise AI reason / fusion reason when available from V402;
- subtitles on/off preview support where already available;
- selected/unselected state.

Do not expose internal debug scores or raw diagnostics unless already intentionally user-facing.

## 4.3 Video interaction
Tapping/clicking a preview may open the candidate full-screen/full-player and must provide a reliable way to return to the same Moments page and selection state.

## 4.4 Selection model
Exactly one candidate is the active selected moment at a time.

Selection is persisted immediately in the project snapshot so route changes or resume do not lose it.

## 4.5 Actions
From the selected candidate the user gets two primary paths:
- `CREA SHORT` → Crea Short finalization page;
- `MODIFICA NEL GAME EDITOR` → Editor 2027 with the selected candidate already loaded.

A secondary action may allow choosing another moment without leaving the page.

# 5. Game Editor handoff

## 5.1 Contract
Opening Editor from Moments must use the persisted selected-moment reference and timestamps.

Editor must not depend on the Moments DOM still existing.

## 5.2 Preserve Editor 2027
Do not rename or replace `gsf_editor_2027_v1086`.

V403 may fix the handoff/bootstrap around Editor 2027, but not redesign unrelated editor functionality in this release.

## 5.3 Return behavior
Leaving Editor through global navigation must preserve the active project and selected moment. Returning to Editor should restore the project/editor state that already exists under current persistence rules.

# 6. Crea Short final page

## 6.1 Replace the legacy split behavior
The current desktop legacy share component and mobile-only V396 surface must stop behaving as two different products.

Crea Short becomes one responsive surface for desktop and mobile.

## 6.2 Two explicit states
### Pre-render/finalization state
When a selected moment exists but the final short has not yet been rendered, show:
- the selected final candidate clearly;
- preview;
- duration/basic final settings already supported;
- `CREA SHORT` as the primary action;
- `MODIFICA` / open Game Editor;
- `SALVA BOZZA` when the project is eligible and contains actual work;
- option to go back and choose another moment.

### Ready/share state
After final render success, the same route transitions to:
- short ready state;
- download;
- share/publish metadata and supported social actions;
- existing final asset endpoints and social connection state.

No second unrelated page should replace it.

## 6.3 Guard behavior
If Crea Short is opened without a valid selected candidate/project, the app must not show a broken empty final page. It should route to the appropriate valid prior step or show a clear selection-required state while preserving the project.

# 7. Layout and viewport stability

## 7.1 Shell ownership
The global shell/Game Bar/footer owns the outer viewport.

Functional pages that need additional vertical space use internal scrolling instead of resizing the entire application unpredictably.

Home remains fixed/no-scroll as already approved.

## 7.2 No dynamic height thrash
Candidate results, progress, social surfaces, and editor handoffs must not rely on repeated iframe/body height mutations that can push controls off-screen.

The Moments page is a separate route specifically to remove candidate expansion from Motori.

## 7.3 Responsive requirements
Desktop Windows, iPhone, and iPad must remain usable.

A route change or orientation/viewport recalculation may reflow the page, but must not reset project state or candidate selection.

# 8. Error and recovery model

## 8.1 Recoverable UI failures
If a page component fails to initialize:
- preserve shell/navigation;
- show a bounded retry/reload state for that page;
- do not wipe authoritative project state;
- do not automatically start a duplicate AI job/render.

## 8.2 Network interruption
Temporary network loss should pause/retry state reconciliation. Existing completed state must remain visible when possible.

## 8.3 Job idempotency
Restoring/resuming an analysis/render route must inspect the persisted job state before issuing a new job request.

# 9. Data-flow contract

Target flow:

`Home / current project`
→ `Motori`
→ persist analysis request
→ worker/AI analysis
→ persist top-3 candidates
→ `I tuoi 3 momenti`
→ persist selected moment
→ either:
  - `Game Editor` with selected moment loaded
  - `Crea Short` pre-render state
→ final render
→ same `Crea Short` route in ready/share state
→ download/social or Creator Hub.

At every arrow the next screen reconstructs itself from durable state, not from the previous screen's in-memory DOM.

# 10. Compatibility constraints

V403 must not regress:
- approved Home layout/behavior;
- Creator Hub global navigation;
- Game Bar availability;
- V402 Game Brain ranking/fusion;
- V401 upload/recovery/stability work;
- 1080×1920 / 60 fps output quality;
- current worker persistence;
- metadata-first Auto Highlights behavior;
- Editor identity `gsf_editor_2027_v1086`;
- existing final media endpoint contract unless explicitly wrapped compatibly.

# 11. Test contract

Implementation must add regression coverage that proves behavior, not only marker presence.

At minimum:

1. Active project survives route changes.
2. Resume/foreground reconciliation does not duplicate analysis jobs.
3. Resume/foreground reconciliation does not duplicate render jobs.
4. Valid source video reference survives navigation.
5. Profile retains last valid payload during refresh/failure.
6. Motori does not contain/render final candidate cards after completion.
7. Completed analysis transitions to dedicated Moments route.
8. Three candidates fit their dedicated route with internal scrolling contract.
9. Candidate selection persists across route changes.
10. Candidate selection persists across resume/reload reconciliation.
11. Fullscreen candidate preview can return to the same selection page.
12. `CREA SHORT` receives the selected candidate.
13. `MODIFICA NEL GAME EDITOR` receives the selected candidate/timestamps.
14. Editor component identity remains exactly `gsf_editor_2027_v1086`.
15. Crea Short pre-render state exposes create/edit/save-draft/back-to-moments actions as applicable.
16. Crea Short ready state exposes final asset/download/share behavior.
17. Desktop and mobile use the same logical Crea Short surface/state machine.
18. Missing selected candidate fails safely instead of rendering a broken final page.
19. Global Game Bar navigation remains valid from Motori, Moments, Editor, and Crea Short.
20. Existing V400/V401/V402 contracts remain green.
21. Production Gate remains green.

# 12. Rollout strategy

V403 is developed on an isolated branch from the verified V402 production baseline.

Implementation should be staged in this order:
1. state/resume contract;
2. profile recovery;
3. Motori separation;
4. dedicated Moments page;
5. selected-moment handoff to Editor and Crea Short;
6. unified Crea Short surface;
7. full flow regression and production gate.

The release is not considered complete until CI, Production Gate, exact main SHA deployment, and Railway health are all verified.

# 13. Success criteria

V403 is successful when a user can:
- upload/retain a video;
- move among menus without the app freezing or losing the project;
- background the app and return without rebuilding the workflow manually;
- see a stable profile;
- run Motori without layout corruption;
- enter a dedicated page containing the three AI moments and their useful information;
- select one;
- reach either Game Editor or Crea Short reliably;
- create the final short;
- download/share it;
- navigate away and back without losing the active work.

The key product rule is: **navigation and app lifecycle events may change what is visible, but must not destroy the user's work.**
