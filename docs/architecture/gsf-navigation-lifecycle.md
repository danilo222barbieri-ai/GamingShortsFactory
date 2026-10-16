# Navigation and resume investigation

## ROOT CAUSE (confirmed on production, 2026-10-15)

Navigation has multiple owners. V343 Game Bar calls its private route directly,
which only toggles surface DOM. The V220 Editor bridge owns fullscreen, its
session key and iframe lifecycle, but only runs cleanup for selected postMessages.
Consequently Game Bar Home does not close the Editor lifecycle. `projects`,
`live`, and `short` are missing from several legacy close lists. Streamlit bridge
recreation can then restore an Editor which the user already left, using that
stale session key. Parent listeners also retain bridge-local DOM references. Completed bridge timers also retained their abort handlers until controller replacement; a 100-timer regression fails before cleanup and passes after removing each handler when its timer fires.

## Additional confirmed root cause: React DOM ownership

The production-image test with a real uploaded video triggers a Streamlit rerun.
React throws `NotFoundError: removeChild` and then Editor module requests abort.
A pre-React instrument of `Node.removeChild` and `Element.remove` records the
exact object: `NAV#gsf-page-nav-v249`, originally inside `stMarkdownContainer`,
is removed by `retireLegacyChrome -> keepGlobalShellMounted`. React subsequently
tries to remove the same object from its original parent, but its actual parent
is null. This is framework-tree corruption, not a broken click handler.

Correction: remove obsolete V249 markup at its Python source and delete the
parent DOM-deletion routine. The existing shell styles already retire historical
chrome. Parent controllers may create/remove their own portal content but must
never move or remove React-owned nodes. Real media upload plus delayed Editor
save is the regression trigger; console and network errors remain fatal.

## Confirmed rerun import failure

Container logs after reconnect show `ModuleNotFoundError: web.living_ui` at
app.py import time, while composite health remains green. Six app code paths
insert `/app/web` at the front of the shared interpreter path. With the outer
web directory a namespace package, Python can select the inner regular package
`web/web`, which has a render-gate shim but no living_ui. A subprocess regression
reproduces `find_spec('web.living_ui') is None` before the fix.

One entry bootstrap now sets canonical repository/package paths in a stable
order, `web/__init__.py` makes the canonical package explicit, and the six later
path mutations are removed. Legacy bare helper imports retain the web path in
second position. The regression clears user modules and resolves both canonical
and legacy helpers on four simulated reruns.

## BFCache transport evidence

A real Chromium BFCache hit preserves native Editor DOM/state and pointer
controls, but the browser aborts Streamlit's open WebSocket with console errors
`Page entered Back-Forward Cache` and `Client Error: WebSocket onerror`. The
lifecycle tracks only Streamlit sockets and closes an OPEN transport cleanly on
pagehide. Ordinary freeze/background keeps the socket open so it does not
force reconstruction of the React-owned Home. Streamlit retains ownership of retry/reconnection; no sockets
are manually recreated and no errors are filtered. The history regression also
requires Streamlit's connection state to return to CONNECTED.

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
`web/install_adsense_bridge.py`. Four canonical surface markup literals (`_GSF_SURFACE_*`) are also installed
once into the top document. Streamlit renders their styles and data but never
creates their iframes, preventing temporary surface mounts and module request
cancellation on rerun. No React-owned node is moved into the portal.

The eight existing controller script literals
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

The real-media + delayed-save regression failed with React removeChild before
retiring the DOM-deletion code and passed afterward. A true Streamlit button
rerun then exposed transient Editor module aborts; after persistent top-owned
surfaces, both delayed-save and rerun tests pass, with state and Undo preserved.
The current rerun test additionally compares the actual host, iframe and
contentDocument identities across rerun.

The selected Python suite on the updated main baseline passes 45 tests (browser
cases skip without GSF_BASE_URL). JavaScript unit tests pass all 16 cases. The
historical navigation guards now inspect the actual canonical Game Bar instead
of requiring the removed V249 markup and its unused icon.

A complete Chromium mobile run passed seven requested sequences ten times each:
310 measured transitions after warming, nodes 1024 -> 1024, iframes 13 -> 13,
MutationObservers 9 -> 9, ResizeObservers 1 -> 1, parent listener counts unchanged,
heap 40,056,772 -> 35,584,204 bytes. The desktop companion run caught a media
request cancelled while the initial warm-up left before the video was ready.
The stress helper now waits for actual media metadata with the valid fixture;
no JS/console/network failures are filtered.

Final combined stress and full-duration resume results are pending. Chromium
BFCache `persisted:true` was observed; a native DOM probe confirms the restored
Editor document, API and zoom 1.7. Playwright loses cached iframe targets on this
restore, so the history regression reads native same-origin DOM and performs
real pointer clicks, and waits for pageshow/current DOM rather than a second
DOMContentLoaded. This test's final pass is still pending.

Resume cycles use synthetic visibility/page transition events and actual CDP
renderer freeze/active where supported. Physical OS app switching and physical
iOS/Safari remain unverified. Production deployment is not claimed until Gate
and Railway evidence is recorded.

Claim: `stability-unified-navigation-and-mobile-resume-l-395391`.
