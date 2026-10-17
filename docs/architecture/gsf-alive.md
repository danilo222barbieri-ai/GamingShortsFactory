# GSF Alive Core V405

GSF Alive is the product-wide reaction layer for Gaming Shorts Factory. It is not a decorative animation system: it translates real product state into restrained motion, short contextual copy, next-action hints and graceful system-health feedback.

## Principles

1. **State before animation.** Motion is always derived from a real state or event.
2. **One nervous system.** Upload, AI, editor, render, publish and system health share one state model.
3. **Stable navigation.** Alive may change emphasis and recommendations, but it must not move controls around unpredictably.
4. **Quiet by default.** Idle motion is slow. Working motion accelerates. Completion gets a short celebration. Errors become calmer, clearer feedback rather than flashing UI.
5. **Accessible motion.** `prefers-reduced-motion` disables the pulse.
6. **No Streamlit dependency in the core.** `gsf_alive.py` is pure Python; Streamlit is only an injected rendering bridge.

## Global modes

- `idle` — no active media/work; slow breathing.
- `active` — a video/project is ready for the next action.
- `working` — upload, AI, render or publish is in progress.
- `celebrate` — a short or publication has completed.
- `error` — a recoverable failure or unavailable service needs attention.

System health is separate: `healthy`, `degraded`, `down`.

## Event contract

New components should emit explicit events with `emit_alive(st.session_state, ...)`.

```python
from gsf_alive import AliveEventType, emit_alive

emit_alive(st.session_state, AliveEventType.UPLOAD_STARTED)
emit_alive(st.session_state, AliveEventType.UPLOAD_PROGRESS, progress=0.42)
emit_alive(st.session_state, AliveEventType.UPLOAD_COMPLETED)

emit_alive(st.session_state, AliveEventType.AI_STARTED)
emit_alive(
    st.session_state,
    AliveEventType.AI_PROGRESS,
    progress=0.55,
    message="Sto confrontando i momenti migliori.",
)
emit_alive(st.session_state, AliveEventType.AI_MOMENTS_FOUND, count=3)
emit_alive(st.session_state, AliveEventType.MOMENT_SELECTED, index=1)

emit_alive(st.session_state, AliveEventType.EDITOR_OPENED)
emit_alive(st.session_state, AliveEventType.EDITOR_DIRTY)
emit_alive(st.session_state, AliveEventType.EDITOR_SAVED)

emit_alive(st.session_state, AliveEventType.RENDER_STARTED)
emit_alive(st.session_state, AliveEventType.RENDER_PROGRESS, progress=73)
emit_alive(st.session_state, AliveEventType.RENDER_COMPLETED)

emit_alive(st.session_state, AliveEventType.PUBLISH_STARTED)
emit_alive(st.session_state, AliveEventType.PUBLISHED)
```

Errors should pass a user-facing message, not a traceback:

```python
emit_alive(
    st.session_state,
    AliveEventType.FAILURE,
    message="Il render si è fermato. Riproviamo.",
)
```

System-health integrations can use:

```python
emit_alive(
    st.session_state,
    AliveEventType.SYSTEM_HEALTH_CHANGED,
    health="degraded",
)
```

## Compatibility bridge

`sync_alive_from_session()` observes a small set of generic legacy session aliases for page, current video and render state. It never deletes or rewrites application state. This makes V405 useful immediately in the monolithic app while explicit events are added to new/rebuilt components.

Explicit events are the long-term contract. The compatibility bridge is not the architecture.

## Product voice

Alive copy stays short and contextual. Current examples:

- Idle: `Pronto quando vuoi.`
- Upload: `Carico il gameplay.`
- AI: `Vediamo cosa c’è dentro.`
- Moments found: `Ho trovato 3 momenti forti.`
- Selection: `Questa merita attenzione.`
- Render: `Ci sto lavorando.`
- Complete: `È pronto.`
- Degraded system: `Coda un po’ più lunga del solito.`

Avoid chatty assistant copy, fake progress narration, or decorative messages unrelated to actual work.

## Visual contract

`render_alive()` injects CSS variables and a restrained breathing animation. Existing `.ai-orb` elements are supported; new components should prefer `data-gsf-alive-orb` or `.gsf-alive-orb`.

The global bootstrap only surfaces the compact Alive status while `working`, `celebrate` or `error`, keeping idle/active pages visually clean.

## Integration path for active branches

The currently rebuilt Creator Hub, Crea con IA, Game Editor and Publish Short flows should call explicit Alive events at their real lifecycle boundaries after their own claims merge. They do not need to duplicate motion logic or message-state logic.

## Verification

Core behavior is covered by `tests/test_gsf_alive.py`. The deterministic patcher `scripts/apply_v405_alive.py` inserts the import/bootstrap into `app.py`, validates the resulting AST, and is idempotent.

## Alive 2 (V418) — app-wide browser runtime

`web/gsf_alive_v418.js` is the browser half of the nervous system. It is inlined verbatim in every surface between `GSF_ALIVE:BEGIN` / `GSF_ALIVE:END` (`python tools/gsf_alive_inline.py --write`; drift fails `tests/test_alive_runtime_v418.py`). Pages are served byte-identical from the repo; no build or startup step rewrites them.

One state, shared by every page iframe through `BroadcastChannel("gsf-alive-v418")` + `localStorage`, reduced by the same pure rules as `gsf_alive.py` (`tests/js/gsf_alive_v418.test.mjs`).

- **Heard** — an echo ring under every tap; each real event gives the orb (`[data-alive-orb]`) a heartbeat and a short handwritten whisper. The breath speed, scale and hue follow the mode (idle, active, working, celebrate, error).
- **Guided** — `nextAction()` picks the real next step (upload, create_with_ai, choose_moment, create_short, publish, connect_social, retry, new_video). The visible element marked `data-alive-next~="<step>"` gets a breathing guide ring; after 9 quiet seconds one whisper points at it, once per state.
- **Carried** — while upload, AI search, render or publish runs, every other page shows a companion bubble with the real progress or elapsed time; tapping it goes back. A finished Short celebrates (brand-colour burst, haptic on Android) and the bubble becomes "Short pronto · Pubblica". Returning after two minutes greets with where things stand.

Facts only come from real signals: Home upload lifecycle, Crea con IA search/results/selection, `/share/state` (Short ready, connected socials), `/publish/status`, and `/job/status` for renders. A page that asks for a Short calls `GSFAlive.watchRender()`; the render is followed only if the server reports it running. One page (a `localStorage` leader) polls `/job/status`, and only while a render is tracked.

Page API: `GSFAlive.mount({page, voiceAnchor, dock})`, `emit(type, data)`, `say(text)`, `watchRender()`, `state()`, `next()`. `prefers-reduced-motion` turns off echoes, bursts and breathing. Wired surfaces: Home, Crea con IA, Crea Short, Creator Hub; the mobile and desktop Game Editor join when their claims release.
