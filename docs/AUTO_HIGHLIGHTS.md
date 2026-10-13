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

The production worker imports the V129 engine for authenticated post-live ranking; provider event detection and Creator Hub presentation remain separate integration layers.


## V129 production engine

The internal post-live ranking path is now implemented:

- an existing worker analysis payload is converted into an event pool;
- the same production Game Brain used by normal uploads performs ranking;
- each highlight receives confidence, semantic event and AI Director plan;
- only timestamps/metadata are written to `auto-highlights/<provider>/<account>/<broadcast>.json`;
- `rendered_media` starts empty: no eager clip rendering.

Worker endpoint: authenticated `POST /auto-highlights` with an existing `analysis_key`.

Provider event detection remains an adapter concern. Twitch EventSub credentials/scopes and YouTube live-stream read scopes are required before automatic provider triggers can be enabled for an account.

- V129 Creator Hub now lists stored highlight sets for the signed-in creator, showing provider, candidate count, duration and top confidence without rendering the VOD.

## V402 signal fusion

V402 adds a lightweight evidence-fusion pass before final Game Brain ranking. Existing local gameplay events, semantic evidence and scan diagnostics can be corroborated by visual, reaction/audio and HUD signals when those observations are available. Missing optional signal families remain neutral, and fusion failures fall back to the original V129 event path.

Game Brain remains the final ranking, diversity and AI Director authority. The architecture is still scan-first and metadata-first: V402 does not eagerly render highlight clips, duplicate full VODs, or add a second competing ranker.
