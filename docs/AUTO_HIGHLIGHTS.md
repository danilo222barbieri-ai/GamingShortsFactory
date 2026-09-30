# GSF Auto Highlights — foundation

This branch prepares the future post-live workflow without changing production.

## Flow

1. User connects Twitch or YouTube.
2. GSF detects that a live has ended.
3. A provider adapter resolves the archived VOD.
4. The worker creates a lightweight scan job.
5. Existing GSF scoring engines produce timestamp candidates.
6. Only metadata/timestamps are stored initially.
7. The user opens an Auto Highlights folder and chooses candidates.
8. Editor 2027 renders only the selected clips.

## Provider triggers

- Twitch: EventSub `stream.offline` webhook.
- YouTube: authenticated Live Streaming API; detect broadcasts whose lifecycle is `complete`, then wait until the archived video is available.

## Cost rule

Do not eagerly render every highlight and do not persist full VOD copies unless required. Scan first, store timestamps/scores, render on selection.

## Future components

- OAuth/account connection records
- Twitch EventSub webhook + signature verification
- YouTube completed-live watcher
- VOD resolver
- Live scan queue for `gsf-ai-worker`
- highlight metadata persistence
- Creator Hub / Auto Highlights UI
- retention/cleanup policy and quotas

No production service imports this module yet.
