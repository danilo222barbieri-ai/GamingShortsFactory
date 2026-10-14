# GSF Alive Notifications V409

This layer restores the small global notifications previously used by Gaming Shorts Factory while keeping GSF Alive Core as the single source of product state.

## Product rules

- Notifications are global and can appear while the user is in Home, Creator Hub, Game Editor, AI or Social.
- They are small, pastel, slightly tilted and fixed above the Game Bar. They never reflow the page or create scrolling.
- They appear once per real Alive event transition and fade automatically.
- Repeated Streamlit reruns must not replay the same notification.
- No file names, clip names or technical details are shown.
- Working/progress events stay quiet; the persistent Alive status remains responsible for ongoing work feedback.

## Event mapping

- `upload_completed` -> `Video caricato`
- `render_completed` -> `Short completato` with action metadata `publish`
- `published` -> `Short pubblicato`
- `failure` -> the safe user-facing Alive error message with action metadata `retry`
- `recovered` -> `Ci siamo.`

## State ownership

`gsf_alive_notifications.py` stores only notification deduplication and a pending one-shot payload in `_gsf_alive_notifications_v1`. It never changes GSF project state, Alive Core state, navigation state or media state.

A non-notifiable Alive action still advances the deduplication cursor. This allows the same completion event to notify again after a new upload/render cycle without replaying on ordinary reruns.

## Rendering

`render_alive_notification(st_module, session_state, alive_state)` observes the current Alive state, consumes at most one pending notification and renders fixed CSS/markup. The markup carries optional action metadata but does not force navigation or page refreshes.

The final app bootstrap should call this renderer next to the existing `render_alive(...)` bootstrap once `app.py` ownership is available. Until then the sidecar remains isolated and safe to merge without touching the active Alive Core claim.
