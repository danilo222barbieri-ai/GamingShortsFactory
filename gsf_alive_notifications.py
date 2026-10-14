"""One-shot global notifications for GSF Alive.

This module deliberately sits beside ``gsf_alive`` instead of owning product
state. It observes Alive's last real action, emits a small notification once,
and stores only its own deduplication/pending state in the caller's session.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import escape
from typing import Any, Mapping, MutableMapping

from gsf_alive import AliveState


SESSION_KEY = "_gsf_alive_notifications_v1"


@dataclass(frozen=True)
class AliveNotification:
    message: str
    kind: str = "info"
    action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> "AliveNotification | None":
        if not raw:
            return None
        message = str(raw.get("message") or "").strip()
        if not message:
            return None
        kind = str(raw.get("kind") or "info")
        action_raw = raw.get("action")
        action = str(action_raw) if action_raw else None
        return cls(message=message, kind=kind, action=action)


_NOTIFICATION_BY_ACTION: dict[str, AliveNotification] = {
    "upload_completed": AliveNotification("Video caricato", "success"),
    "render_completed": AliveNotification("Short completato", "success", "publish"),
    "published": AliveNotification("Short pubblicato", "success"),
    "recovered": AliveNotification("Ci siamo.", "info"),
}


def sync_alive_notification(
    session_state: MutableMapping[str, Any],
    state: AliveState,
) -> AliveNotification | None:
    """Observe an Alive state and queue at most one notification per action transition."""
    raw = session_state.get(SESSION_KEY)
    center = dict(raw) if isinstance(raw, Mapping) else {}
    action = state.last_action

    if action == center.get("last_seen_action"):
        return None

    center["last_seen_action"] = action
    note: AliveNotification | None = None

    if action == "failure":
        note = AliveNotification(
            message=str(state.message or "Qualcosa si è fermato."),
            kind="error",
            action="retry",
        )
    elif action:
        note = _NOTIFICATION_BY_ACTION.get(action)

    if note is not None:
        center["pending"] = note.to_dict()

    session_state[SESSION_KEY] = center
    return note


def pop_alive_notification(
    session_state: MutableMapping[str, Any],
) -> AliveNotification | None:
    """Return and consume the currently pending notification, if any."""
    raw = session_state.get(SESSION_KEY)
    if not isinstance(raw, Mapping):
        return None

    center = dict(raw)
    pending = center.pop("pending", None)
    session_state[SESSION_KEY] = center
    return AliveNotification.from_dict(pending if isinstance(pending, Mapping) else None)


def build_alive_notification_css() -> str:
    return """
<style id="gsf-alive-notification-style">
.gsf-alive-notification {
  position:fixed; left:50%; bottom:84px; transform:translateX(-50%) rotate(-1deg);
  z-index:2147483640; pointer-events:none; width:max-content; max-width:min(88vw, 520px);
  display:flex; align-items:center; gap:.52rem; padding:.58rem .82rem;
  border-radius:16px; border:1px solid rgba(24,87,130,.10);
  background:rgba(255,255,255,.84); color:#294761;
  box-shadow:0 10px 28px rgba(16,40,61,.09); backdrop-filter:blur(16px);
  font-size:.86rem; line-height:1.2; font-weight:650;
  animation:gsfAliveToast 4.4s cubic-bezier(.22,.8,.22,1) forwards;
}
.gsf-alive-notification__dot {
  width:.5rem; height:.5rem; border-radius:999px; flex:none; background:#56cfa0;
}
.gsf-alive-notification--error .gsf-alive-notification__dot { background:#ff6673; }
.gsf-alive-notification--info .gsf-alive-notification__dot { background:#42baff; }
@keyframes gsfAliveToast {
  0% { opacity:0; transform:translateX(-50%) translateY(10px) rotate(-1deg) scale(.97); }
  10%, 82% { opacity:1; transform:translateX(-50%) translateY(0) rotate(-1deg) scale(1); }
  100% { opacity:0; transform:translateX(-50%) translateY(6px) rotate(-1deg) scale(.985); }
}
@media (prefers-reduced-motion: reduce) {
  .gsf-alive-notification { animation:none; transform:translateX(-50%) rotate(-1deg); }
}
</style>
""".strip()


def build_alive_notification_markup(note: AliveNotification) -> str:
    action = escape(note.action or "", quote=True)
    kind = escape(note.kind or "info", quote=True)
    message = escape(note.message)
    return (
        f"<div class='gsf-alive-notification gsf-alive-notification--{kind}' "
        f"data-alive-action='{action}' role='status' aria-live='polite'>"
        "<span class='gsf-alive-notification__dot' aria-hidden='true'></span>"
        f"<span class='gsf-alive-notification__message'>{message}</span>"
        "</div>"
    )


def render_alive_notification(
    st_module: Any,
    session_state: MutableMapping[str, Any],
    state: AliveState,
) -> AliveNotification | None:
    """Sync, consume and render a notification without changing page layout."""
    sync_alive_notification(session_state, state)
    note = pop_alive_notification(session_state)
    if note is None:
        return None
    st_module.markdown(build_alive_notification_css(), unsafe_allow_html=True)
    st_module.markdown(build_alive_notification_markup(note), unsafe_allow_html=True)
    return note

