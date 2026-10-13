# V402 — Game Brain / Auto Highlights 2.0 Design

## Goal

Upgrade the existing Auto Highlights path so GSF combines gameplay, semantic, visual, reaction/audio and quality signals before final Game Brain ranking, producing more accurate, diverse and explainable highlight candidates without adding eager rendering, full-VOD duplication, or a second competing ranking engine.

## Production baseline

V402 starts from V401 commit `1c6d47a42a040b6e2342b4e2cd1a8e823592e315`.

V401 remains the performance/stability contract: bounded frontend upload streaming, persistent worker state, retryable restart recovery, and stable progress. V402 must not weaken those guarantees.

V400 remains the quality/editor contract: 1080x1920 final master, 60 fps pipeline, libx264 medium quality policy, Adaptive AI/Hi-DPI behavior, and stable Editor 2027 component identity `gsf_editor_2027_v1086`.

## Existing architecture to preserve

- `web/auto_highlights/engine_v129.py` converts existing worker analysis into candidates and delegates final selection to `game_brain_v112.rerank_moments()`.
- `web/game_brain_v112.py` already provides semantic injection, learned event multipliers, candidate scoring, anti-overlap selection, Director plans and alternates.
- `web/visual_scoring_v144.py` already exposes cheap local visual signals such as motion-derived action, subject strength, sharpness, contrast and visual quality.
- Auto Highlights stores timestamps/metadata first and does not eagerly render every candidate.

V402 must reuse these pieces rather than replace them.

## Chosen approach

Add one focused fusion layer between raw analysis events and existing Game Brain ranking.

The new module is responsible for normalizing and fusing independent signals into richer event/candidate evidence. Game Brain remains the final authority for ranking and Director planning.

This approach is preferred over:

1. **A second standalone V402 ranker** — rejected because it would duplicate Game Brain logic, create contradictory scores, and make learning/debugging harder.
2. **A new heavy multimodal model for every scan** — rejected because it would increase cost/latency and work against the V401 stability/performance objective.
3. **Directly expanding `game_brain_v112.py` with all fusion logic** — rejected because the file already owns ranking/diversification; signal normalization belongs in a smaller isolated unit.

## New component

Create `web/highlight_fusion_v402.py`.

### Public contract

`fuse_highlight_evidence(events, diagnostics=None, visual_observations=None, audio_observations=None, target_duration=30, genre="Auto") -> tuple[list[dict], dict]`

The function returns:

- a normalized event list compatible with the existing Game Brain/Auto Highlights flow;
- fusion metadata describing which signal families contributed and how many events were enriched.

The module must be deterministic for the same inputs and must not perform network calls, rendering, video decode, model downloads, or persistence.

## Signal families

V402 fuses only signals already available or naturally carried by the analysis payload.

### Gameplay / semantic

Preserve and normalize:

- `kind`
- `semantic`
- `score`
- `semantic_score`
- `semantic_confidence`
- `semantic_excitement`
- event labels such as kill, multi-kill, clutch, victory, goal, reaction, overtake, save, boss, impact, assist and death.

### Visual

Use available observations near each event time:

- `action_score`
- motion/action burst equivalents
- `subject_score`
- `visual_quality`
- `sharpness`
- focus confidence
- HUD evidence such as killfeed/minimap when already present.

Visual evidence must be optional. Missing visual data must never suppress a valid Game Brain event.

### Reaction / audio

Use available reaction/audio evidence near the event:

- reaction strength
- audio/excitement spike
- semantic reaction
- speech/reaction cue when already present.

Audio evidence must be optional. Missing tracks or observations are a neutral condition, not an error.

### Negative evidence

Apply bounded penalties for:

- silence/dead-air
- repeated duplicate evidence for the same event peak
- very low visual quality when visual data exists
- explicit death/low-value event labels where the existing Game Brain already treats them negatively.

No single missing signal family may create a negative penalty by itself.

## Fusion behavior

Each event receives additive V402 metadata rather than destructive rewrites of the source fields.

Required fields after fusion:

- `fusion_score` in a bounded range suitable for reuse as candidate evidence;
- `fusion_confidence`;
- `fusion_signals`: compact list of contributing families such as `event`, `semantic`, `visual`, `reaction`, `hud`;
- `fusion_reason`: stable human-readable explanation assembled from the strongest evidence;
- `fusion_version`: `v402`.

Strong multi-signal agreement must rank above an otherwise equivalent single-signal event. Example: kill + high action + reaction + killfeed must receive stronger fusion evidence than a generic kill with no corroboration.

Clutch/multi-kill/victory/goal and similar high-value semantic events keep the established Game Brain semantic priority; V402 corroborates them rather than replacing those priors.

## Peak window behavior

V402 does not render or cut clips. It improves event evidence and peak anchoring only.

For enriched events, preserve the source event time and optionally expose:

- `peak_time`
- `lead_seconds`
- `aftermath_seconds`

Lead/aftermath values are hints for the existing candidate construction/Director flow. Final clip duration remains controlled by `target_duration` (15/30 seconds or existing caller value).

The window logic must favor seeing enough setup before the decisive action and enough aftermath/reaction after it, without changing the total requested candidate duration.

## Integration

Modify `web/auto_highlights/engine_v129.py` so `analysis_to_candidates()`:

1. reads the existing event map and diagnostics;
2. obtains optional visual/audio evidence from the analysis payload when present;
3. calls `fuse_highlight_evidence()`;
4. builds the candidate pool from fused events;
5. passes the fused event list into the unchanged `rerank_moments()` final ranking path;
6. surfaces fusion metadata alongside existing Auto Highlights/Game Brain metadata.

The existing worker endpoint and metadata-first persistence contract remain unchanged unless a marker/version field is needed for observability.

## Diversity and duplicate handling

Existing Game Brain MMR/overlap logic remains final selection authority.

V402 may collapse or mark near-identical evidence peaks before Game Brain when they refer to the same semantic event within a short time window. It must not remove distinct meaningful events simply because they share a category.

Success for a top-3 set means:

- no duplicate windows around the same peak when better alternatives exist;
- category/event diversity is preferred when candidate quality is close;
- a clearly superior event is not discarded only to manufacture diversity.

## Explainability

Every selected Auto Highlight must be able to expose a concise reason derived from real evidence, for example:

`CLUTCH · Killfeed · Reaction · High Action`

V402 stores explanation metadata only. No Home, Creator Hub, Game Bar or Editor UI changes are part of this release.

The existing `reason`, `event`, `confidence` and `director_plan` fields remain backward compatible. Fusion-specific explanation may be surfaced as additional metadata, not by deleting existing fields.

## Error and fallback behavior

V402 must fail soft.

- No visual evidence: continue with gameplay/semantic/reaction signals.
- No audio/reaction evidence: continue with gameplay/semantic/visual signals.
- No semantic provider result: continue with local/base event evidence.
- Malformed optional observation: ignore that observation, do not fail the scan.
- Empty/invalid event map: retain current `no-events` behavior.
- Fusion exception at integration boundary: Auto Highlights must fall back to the original V129 event path rather than losing all candidates.

Fallbacks must be visible in returned metadata for diagnosis.

## Performance constraints

- No network calls in the fusion layer.
- No additional video materialization.
- No eager highlight render.
- No full VOD copy.
- Work must be linear or near-linear in the small event/observation lists used by the existing scan path.
- V401 upload streaming and persistent job-state behavior must remain untouched.

## Compatibility constraints

V402 must not change:

- approved Home UI;
- Creator Hub layout/navigation;
- global Game Bar behavior;
- Editor 2027 component identity `gsf_editor_2027_v1086`;
- V400 render quality contract;
- V401 job persistence/recovery contract;
- Auto Highlights metadata-first/no-eager-render architecture.

## Test contract

Create `web/test_v402_game_brain_auto_highlights.py` with deterministic fixtures covering at least:

1. multi-signal agreement: kill + high action + reaction + killfeed outranks an equivalent generic event;
2. high-value semantic priority: clutch/multi-kill remains stronger than a generic event with similar base score;
3. missing audio is neutral and does not crash;
4. missing visual observations fall back cleanly to existing Game Brain behavior;
5. malformed optional observations are ignored;
6. silence/dead-air receives a bounded penalty or is excluded consistently with existing behavior;
7. near-duplicate evidence peaks do not produce duplicate top selections when alternatives exist;
8. top selections preserve diversity when quality is close;
9. requested clip duration remains exact for 15-second and 30-second candidates;
10. deterministic input produces deterministic fused scores/reasons/order;
11. fusion metadata reaches Auto Highlights output;
12. original V129 tests remain green;
13. Game Brain V112 regression tests remain green;
14. V400 quality/editor contract tests remain green;
15. V401 performance/stability contract remains green.

## Release gate

V402 is not production-ready until:

- V402 tests pass;
- relevant V129/Game Brain regressions pass;
- V400 and V401 regression contracts pass;
- syntax/import verification passes;
- branch CI/PR checks are green;
- after merge, `main` points to the expected V402 commit;
- Railway deploys that exact commit successfully;
- production frontend and worker are online with zero critical issues and no new deployment failure.

Until those checks pass, V401 remains the production baseline and rollback point.
