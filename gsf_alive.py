"""GSF Alive Core.

A tiny, dependency-free state engine that makes Gaming Shorts Factory react to
what the product is doing. Streamlit is deliberately kept outside the core:
callers can store the serialised state in ``st.session_state`` and render the
returned CSS/markup with ``st.markdown``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from html import escape
from typing import Any, Mapping, MutableMapping


SESSION_KEY = "_gsf_alive_state_v1"


class AliveMode(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    CELEBRATE = "celebrate"
    ERROR = "error"


class SystemHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class AliveEventType(str, Enum):
    PAGE_VIEWED = "page_viewed"
    VIDEO_SELECTED = "video_selected"
    VIDEO_CLEARED = "video_cleared"
    UPLOAD_STARTED = "upload_started"
    UPLOAD_PROGRESS = "upload_progress"
    UPLOAD_COMPLETED = "upload_completed"
    AI_STARTED = "ai_started"
    AI_PROGRESS = "ai_progress"
    AI_MOMENTS_FOUND = "ai_moments_found"
    MOMENT_SELECTED = "moment_selected"
    EDITOR_OPENED = "editor_opened"
    EDITOR_DIRTY = "editor_dirty"
    EDITOR_SAVED = "editor_saved"
    RENDER_STARTED = "render_started"
    RENDER_PROGRESS = "render_progress"
    RENDER_COMPLETED = "render_completed"
    PUBLISH_STARTED = "publish_started"
    PUBLISHED = "published"
    FAILURE = "failure"
    RECOVERED = "recovered"
    SYSTEM_HEALTH_CHANGED = "system_health_changed"


@dataclass(frozen=True)
class AliveEvent:
    kind: AliveEventType
    payload: Mapping[str, Any] | None = None

    def data(self) -> Mapping[str, Any]:
        return self.payload or {}


@dataclass(frozen=True)
class AliveState:
    mode: AliveMode = AliveMode.IDLE
    system_health: SystemHealth = SystemHealth.HEALTHY
    current_page: str = "home"
    last_action: str | None = None
    message: str = "Pronto quando vuoi."
    progress: float | None = None
    active_job: str | None = None
    video_ready: bool = False
    moments_count: int = 0
    selected_moment: int | None = None
    moment_selected: bool = False
    editor_open: bool = False
    unsaved_changes: bool = False
    short_ready: bool = False
    published: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        data["system_health"] = self.system_health.value
        return data

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> "AliveState":
        if not raw:
            return cls()
        allowed = cls.__dataclass_fields__.keys()
        data = {key: value for key, value in raw.items() if key in allowed}
        try:
            data["mode"] = AliveMode(data.get("mode", AliveMode.IDLE.value))
        except (TypeError, ValueError):
            data["mode"] = AliveMode.IDLE
        try:
            data["system_health"] = SystemHealth(
                data.get("system_health", SystemHealth.HEALTHY.value)
            )
        except (TypeError, ValueError):
            data["system_health"] = SystemHealth.HEALTHY
        return cls(**data)


def _clamp_progress(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number > 1.0 and number <= 100.0:
        number /= 100.0
    return min(1.0, max(0.0, number))


def _calm_mode(state: AliveState) -> AliveMode:
    if state.short_ready:
        return AliveMode.CELEBRATE
    if state.video_ready:
        return AliveMode.ACTIVE
    return AliveMode.IDLE


def reduce_alive(state: AliveState, event: AliveEvent) -> AliveState:
    """Pure reducer: one event in, one new immutable AliveState out."""
    kind = AliveEventType(event.kind)
    data = event.data()
    action = kind.value

    if kind is AliveEventType.PAGE_VIEWED:
        page = str(data.get("page") or "home")
        return replace(state, current_page=page, last_action=action)

    if kind is AliveEventType.VIDEO_SELECTED:
        return replace(state, mode=AliveMode.ACTIVE, video_ready=True,
                       short_ready=False, published=False, error=None,
                       message="Video pronto.", last_action=action)

    if kind is AliveEventType.VIDEO_CLEARED:
        return AliveState(current_page=state.current_page,
                          system_health=state.system_health)

    if kind is AliveEventType.UPLOAD_STARTED:
        return replace(state, mode=AliveMode.WORKING, active_job="upload",
                       progress=0.0, error=None, message="Carico il gameplay.",
                       last_action=action)

    if kind is AliveEventType.UPLOAD_PROGRESS:
        return replace(state, mode=AliveMode.WORKING, active_job="upload",
                       progress=_clamp_progress(data.get("progress")),
                       last_action=action)

    if kind is AliveEventType.UPLOAD_COMPLETED:
        return replace(state, mode=AliveMode.ACTIVE, active_job=None,
                       progress=None, video_ready=True, short_ready=False,
                       published=False, error=None, message="Video pronto.",
                       last_action=action)

    if kind is AliveEventType.AI_STARTED:
        return replace(state, mode=AliveMode.WORKING, active_job="ai",
                       progress=0.0, error=None,
                       message="Vediamo cosa c’è dentro.", last_action=action)

    if kind is AliveEventType.AI_PROGRESS:
        return replace(state, mode=AliveMode.WORKING, active_job="ai",
                       progress=_clamp_progress(data.get("progress")),
                       message=str(data.get("message") or state.message),
                       last_action=action)

    if kind is AliveEventType.AI_MOMENTS_FOUND:
        count = max(0, int(data.get("count") or 0))
        label = "momento forte" if count == 1 else "momenti forti"
        return replace(state, mode=AliveMode.ACTIVE, active_job=None,
                       progress=None, moments_count=count, error=None,
                       message=f"Ho trovato {count} {label}.", last_action=action)

    if kind is AliveEventType.MOMENT_SELECTED:
        index = data.get("index")
        try:
            index = int(index) if index is not None else 0
        except (TypeError, ValueError):
            index = 0
        return replace(state, mode=AliveMode.ACTIVE, selected_moment=index,
                       moment_selected=True, short_ready=False,
                       message="Questa merita attenzione.", last_action=action)

    if kind is AliveEventType.EDITOR_OPENED:
        return replace(state, mode=AliveMode.ACTIVE, editor_open=True,
                       message="Modifichiamola.", last_action=action)

    if kind is AliveEventType.EDITOR_DIRTY:
        return replace(state, mode=AliveMode.ACTIVE, editor_open=True,
                       unsaved_changes=True, message="Sto con te.",
                       last_action=action)

    if kind is AliveEventType.EDITOR_SAVED:
        return replace(state, mode=AliveMode.ACTIVE, editor_open=True,
                       unsaved_changes=False, message="Salvato.",
                       last_action=action)

    if kind is AliveEventType.RENDER_STARTED:
        return replace(state, mode=AliveMode.WORKING, active_job="render",
                       progress=0.0, short_ready=False, error=None,
                       message="Ci sto lavorando.", last_action=action)

    if kind is AliveEventType.RENDER_PROGRESS:
        return replace(state, mode=AliveMode.WORKING, active_job="render",
                       progress=_clamp_progress(data.get("progress")),
                       last_action=action)

    if kind is AliveEventType.RENDER_COMPLETED:
        return replace(state, mode=AliveMode.CELEBRATE, active_job=None,
                       progress=None, short_ready=True, unsaved_changes=False,
                       error=None, message="È pronto.", last_action=action)

    if kind is AliveEventType.PUBLISH_STARTED:
        return replace(state, mode=AliveMode.WORKING, active_job="publish",
                       progress=None, error=None, message="Lo mando fuori.",
                       last_action=action)

    if kind is AliveEventType.PUBLISHED:
        return replace(state, mode=AliveMode.CELEBRATE, active_job=None,
                       progress=None, published=True, error=None,
                       message="Pubblicato.", last_action=action)

    if kind is AliveEventType.FAILURE:
        safe_message = str(data.get("message") or "Qualcosa si è fermato.")
        return replace(state, mode=AliveMode.ERROR, active_job=None,
                       error=safe_message, message=safe_message,
                       last_action=action)

    if kind is AliveEventType.RECOVERED:
        return replace(state, mode=_calm_mode(state), active_job=None,
                       progress=None, error=None, message="Ci siamo.",
                       last_action=action)

    if kind is AliveEventType.SYSTEM_HEALTH_CHANGED:
        try:
            health = SystemHealth(str(data.get("health") or "healthy"))
        except ValueError:
            health = SystemHealth.HEALTHY
        if health is SystemHealth.DOWN:
            return replace(state, system_health=health, mode=AliveMode.ERROR,
                           error="Servizio momentaneamente non disponibile.",
                           message="Servizio momentaneamente non disponibile.",
                           last_action=action)
        if health is SystemHealth.DEGRADED:
            return replace(state, system_health=health,
                           message="Coda un po’ più lunga del solito.",
                           last_action=action)
        service_error = state.error == "Servizio momentaneamente non disponibile."
        return replace(state, system_health=health,
                       error=None if service_error else state.error,
                       mode=_calm_mode(state) if service_error else state.mode,
                       message="Tutto operativo." if service_error else state.message,
                       last_action=action)

    return state


def suggest_next_action(state: AliveState) -> str | None:
    """Return a stable next action without moving or reordering the UI."""
    if state.mode is AliveMode.ERROR:
        return "retry"
    if state.active_job:
        return None
    if state.short_ready and not state.published:
        return "publish"
    if state.published:
        return "new_video"
    if not state.video_ready:
        return "upload"
    if state.moments_count and not state.moment_selected:
        return "choose_moment"
    if state.moment_selected:
        return "create_short"
    return "create_with_ai"


def alive_motion_profile(state: AliveState) -> dict[str, float | str]:
    """Translate product state into a restrained visual pulse profile."""
    profiles: dict[AliveMode, dict[str, float | str]] = {
        AliveMode.IDLE: {"duration_s": 5.8, "scale": 1.025, "glow": 0.16, "name": "idle"},
        AliveMode.ACTIVE: {"duration_s": 3.8, "scale": 1.035, "glow": 0.22, "name": "active"},
        AliveMode.WORKING: {"duration_s": 1.65, "scale": 1.055, "glow": 0.30, "name": "working"},
        AliveMode.CELEBRATE: {"duration_s": 1.10, "scale": 1.085, "glow": 0.38, "name": "celebrate"},
        AliveMode.ERROR: {"duration_s": 2.8, "scale": 1.018, "glow": 0.18, "name": "error"},
    }
    profile = dict(profiles[state.mode])
    if state.mode is AliveMode.WORKING and state.progress is not None:
        profile["duration_s"] = round(max(1.05, 1.9 - (state.progress * 0.75)), 2)
    return profile


def build_alive_css(state: AliveState) -> str:
    profile = alive_motion_profile(state)
    duration = profile["duration_s"]
    scale = profile["scale"]
    glow = profile["glow"]
    mode = profile["name"]
    return f"""
<style id="gsf-alive-core-style">
:root {{
  --gsf-alive-duration: {duration}s;
  --gsf-alive-scale: {scale};
  --gsf-alive-glow: {glow};
}}
[data-gsf-alive-orb], .gsf-alive-orb, .ai-orb {{
  animation: gsfAliveBreath var(--gsf-alive-duration) ease-in-out infinite;
  will-change: transform, box-shadow;
}}
[data-gsf-alive-orb][data-alive-mode="{mode}"],
.gsf-alive-mode-{mode} [data-gsf-alive-orb] {{
  animation-duration: var(--gsf-alive-duration);
}}
@keyframes gsfAliveBreath {{
  0%, 100% {{ transform: scale(1); filter: saturate(1); }}
  50% {{
    transform: scale(var(--gsf-alive-scale));
    filter: saturate(calc(1 + var(--gsf-alive-glow)));
  }}
}}
@media (prefers-reduced-motion: reduce) {{
  [data-gsf-alive-orb], .gsf-alive-orb, .ai-orb {{
    animation: none !important;
    transform: none !important;
  }}
}}
</style>
""".strip()


def build_alive_status_markup(state: AliveState, *, compact: bool = True) -> str:
    """Small, non-blocking product voice. Opt-in: callers decide where to render it."""
    progress = ""
    if state.progress is not None:
        progress = f"<span class='gsf-alive-progress'>{round(state.progress * 100)}%</span>"
    compact_class = " gsf-alive-status--compact" if compact else ""
    return (
        f"<div class='gsf-alive-status{compact_class}' data-alive-mode='{escape(state.mode.value)}'>"
        f"<span class='gsf-alive-dot' aria-hidden='true'></span>"
        f"<span>{escape(state.message)}</span>{progress}</div>"
    )


def build_alive_status_css() -> str:
    return """
<style id="gsf-alive-status-style">
.gsf-alive-status {
  display:flex; align-items:center; justify-content:center; gap:.5rem;
  width:fit-content; max-width:min(92vw, 560px); margin:.35rem auto .55rem;
  padding:.52rem .78rem; border-radius:999px;
  background:rgba(255,255,255,.72); border:1px solid rgba(24,87,130,.10);
  box-shadow:0 8px 24px rgba(16,40,61,.06); backdrop-filter:blur(14px);
  color:#294761; font-size:.84rem; line-height:1.2;
}
.gsf-alive-status--compact { padding:.42rem .68rem; }
.gsf-alive-dot { width:.48rem; height:.48rem; border-radius:50%; background:#56cfa0; flex:none; }
.gsf-alive-status[data-alive-mode='working'] .gsf-alive-dot { background:#42baff; }
.gsf-alive-status[data-alive-mode='celebrate'] .gsf-alive-dot { background:#5ed6a0; }
.gsf-alive-status[data-alive-mode='error'] .gsf-alive-dot { background:#ff6673; }
.gsf-alive-progress { opacity:.64; font-variant-numeric:tabular-nums; }
</style>
""".strip()


def ensure_alive_state(session_state: MutableMapping[str, Any]) -> AliveState:
    raw = session_state.get(SESSION_KEY)
    state = raw if isinstance(raw, AliveState) else AliveState.from_dict(
        raw if isinstance(raw, Mapping) else None
    )
    session_state[SESSION_KEY] = state.to_dict()
    return state


def emit_alive(session_state: MutableMapping[str, Any],
               kind: AliveEventType | str, **payload: Any) -> AliveState:
    state = ensure_alive_state(session_state)
    state = reduce_alive(state, AliveEvent(AliveEventType(kind), payload))
    session_state[SESSION_KEY] = state.to_dict()
    return state


def _first_present(session_state: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in session_state:
            value = session_state.get(key)
            if value is not None:
                return value
    return None


def sync_alive_from_session(session_state: MutableMapping[str, Any]) -> AliveState:
    """Best-effort compatibility bridge for the existing monolithic app.

    It only observes known generic state aliases and never deletes or rewrites
    application state. Explicit ``emit_alive`` calls remain preferred for new
    components.
    """
    state = ensure_alive_state(session_state)

    page = _first_present(session_state,
                          ("current_page", "active_page", "page", "route", "gsf_page"))
    if page is not None and str(page) != state.current_page:
        state = reduce_alive(state, AliveEvent(AliveEventType.PAGE_VIEWED,
                                              {"page": str(page)}))

    video = _first_present(session_state,
                           ("video_path", "current_video", "selected_video",
                            "uploaded_video", "source_video", "input_video",
                            "uploaded_file"))
    if video and not state.video_ready:
        state = reduce_alive(state, AliveEvent(AliveEventType.VIDEO_SELECTED))

    render_progress = _first_present(session_state,
                                     ("render_progress", "final_render_progress",
                                      "short_progress", "export_progress"))
    rendering = _first_present(session_state,
                               ("rendering", "is_rendering", "render_in_progress",
                                "creating_short"))
    if rendering and state.active_job != "render":
        state = reduce_alive(state, AliveEvent(AliveEventType.RENDER_STARTED))
    if state.active_job == "render" and render_progress is not None:
        state = reduce_alive(state, AliveEvent(AliveEventType.RENDER_PROGRESS,
                                              {"progress": render_progress}))

    final_short = _first_present(session_state,
                                 ("final_short", "final_short_path", "short_path",
                                  "rendered_short", "output_video"))
    if final_short and not state.short_ready:
        state = reduce_alive(state, AliveEvent(AliveEventType.RENDER_COMPLETED))

    session_state[SESSION_KEY] = state.to_dict()
    return state


def render_alive(st_module: Any, state: AliveState, *, show_status: bool = False) -> None:
    """Render the lightweight Alive skin using an injected Streamlit module."""
    st_module.markdown(build_alive_css(state), unsafe_allow_html=True)
    if show_status:
        st_module.markdown(build_alive_status_css(), unsafe_allow_html=True)
        st_module.markdown(build_alive_status_markup(state), unsafe_allow_html=True)


__all__ = [
    "AliveEvent", "AliveEventType", "AliveMode", "AliveState", "SystemHealth",
    "SESSION_KEY", "alive_motion_profile", "build_alive_css",
    "build_alive_status_css", "build_alive_status_markup", "emit_alive",
    "ensure_alive_state", "reduce_alive", "render_alive", "suggest_next_action",
    "sync_alive_from_session",
]
