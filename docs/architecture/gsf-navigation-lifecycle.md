# Navigation and resume investigation

## ROOT CAUSE (confirmed on production, 2026-10-15)

Navigation has multiple owners. V343 Game Bar calls its private route directly,
which only toggles surface DOM. The V220 Editor bridge owns fullscreen, its
session key and iframe lifecycle, but only runs cleanup for selected postMessages.
Consequently Game Bar Home does not close the Editor lifecycle. `projects`,
`live`, and `short` are missing from several legacy close lists. Streamlit bridge
recreation can then restore an Editor which the user already left, using that
stale session key. Parent listeners also retain bridge-local DOM references.

## EVIDENCE

Real production Chromium mobile: Editor -> Game Bar Home leaves
`sessionStorage.gsf_editor_overlay_open_v223 == "1"`; dedicated regression fails
`'1' != '0'`. Editor -> fullscreen -> GSF_SHELL_NAV projects leaves
`html.gsf-mobile-editor-fullscreen`, Editor key "1", and the Game Bar computed
`display: none` while Creator Hub is open. No refresh needed to reproduce.

Initial production probe: all seven requested sequences, five repetitions each,
mobile and desktop, no pageerrors, iframe count stable at 21; finite lazy short
surface adds 16 top-level nodes. This probe does NOT establish absence of freezes
on a real phone and did not check console/network errors or iframe internals.

## Implemented architecture

One parent-owned navigation/lifecycle registry. Game Bar and postMessage use the
same transition, invoke each outgoing surface's cleanup, update explicit route
and session flags, and isolate inactive surfaces. Bridge replacement aborts old
parent handlers. Resume reconciles the existing route, never replays session
flags or reinitializes the project; Editor cancels suspended gestures/fullscreen
and flushes pending saves before background/BFCache. Shell presentation remains
V343. Retire overlapping route handlers rather than layer more CSS patches.

## REGRESSION TEST

`tests/test_navigation_stability.py`: failing key/fullscreen cases and repeated
mobile/desktop sequences, real Game Bar clicks, view and elementFromPoint checks.
`tests/test_mobile_resume_stability.py`: incomplete gestures, BFCache lifecycle,
CDP freeze/resume and repeated navigation with preserved Editor state.

The lifecycle module is injected synchronously into Streamlit's static index by
`web/install_adsense_bridge.py`. The eight existing controller script literals
remain in `app.py`, but execute in the top window. A single host observer mounts
controllers and aborts the previous controller when its host is replaced. They no
longer depend on the lifetime of Streamlit component iframes.

Editor controllers share metadata across replacement and adopt an initialized
iframe without another INIT. Ready/bootstrap messages coalesce initialization;
route epochs and abort signals prevent late bootstrap/save callbacks from
changing a newer route or replacing edits. Explicit draft/project selection and
completed uploads force a fresh load, including when the media URL is unchanged.
An embedded desktop Editor waits for parent metadata instead of independently
loading media after a 900 ms timeout.

Home replacement disconnects its previous parent observers and resize listener.
Blur cancels gestures only: focusing an iframe also blurs its parent and must not
suspend the active editor. Hidden/pagehide/freeze suspend the surface; resume
reconciles the current route without reinitializing history. Persisted pagehide
flushes saves without disposing the reusable save sequencer.

## Verification evidence and limits

The focused browser suite passed all eight selected regressions against local
Streamlit: fullscreen/session cleanup, delayed save navigation, desktop render
routing, dirty-state/history adoption, obsolete bootstrap rejection, explicit
draft reload and generated bundle syntax/idempotence. The selected Python unit
suite passed 107 tests (10 browser tests skipped without GSF_BASE_URL); JavaScript
unit tests passed all three files.

Final repeated-navigation and full-duration resume results against the production
container are pending. Earlier stress runs exposed duplicated media requests and
a measurement baseline taken before Home initialization; both were corrected,
but those runs are not final passing evidence.

Resume coverage uses synthetic visibility/page transition events and actual CDP
renderer freeze/active where supported. This does not establish real OS app
switching, real BFCache eligibility, or physical iOS/Safari behavior. No claim of
production deployment is made here until Gate and Railway evidence is recorded.

Claim: `stability-unified-navigation-and-mobile-resume-l-395391`.

