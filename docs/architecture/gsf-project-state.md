# GSF ProjectState

## Purpose

`gsf_project_state.py` is the durable project boundary shared by Home, Crea con IA, Game Editor, render and publication flows.

It solves a specific problem: pages must not own competing copies of the active project. A project keeps one identity and one durable state while the UI changes around it.

## Boundary

ProjectState stores durable workflow facts only:

- project identity
- source asset reference
- AI candidate references
- selected candidate
- editor revision
- render job reference
- final short asset reference
- publication targets

It deliberately does **not** store raw video bytes, decoded frames, transient progress, UI animation state or provider-specific clients.

Raw media belongs in storage/cache infrastructure and is represented here by lightweight string references. This keeps Streamlit session memory bounded and makes the state serializable.

## Relationship with Alive Core

`gsf_alive.py` remains the reactive/presentation layer: current activity, progress, health, contextual voice and motion.

`gsf_project_state.py` is the durable product layer: what project the user is working on and what artifacts already exist.

Alive may observe ProjectState transitions, but ProjectState must not depend on Alive. This keeps the durable model deterministic and usable by Home, Editor, worker callbacks and publication flows.

## State flow

Typical project lifecycle:

`EMPTY -> SOURCE_READY -> MOMENTS_READY -> EDITING -> RENDERING -> READY -> PUBLISHED`

Selection itself does not force a page transition. Navigation remains a UI concern; the selected candidate simply becomes part of the same project.

A `NEW_VIDEO` event starts a clean project identity without leaking artifacts from the previous project.

## Session contract

Streamlit stores the serialized state under `_gsf_project_state_v1` only. The bridge never deletes or rewrites unrelated legacy session keys. This allows incremental migration of the existing app instead of a risky all-at-once rewrite.

## Integration order

Because `app.py` is currently owned by the Alive Core claim, V408 does not modify it. Runtime adoption must be serialized after that ownership is released:

1. load/create ProjectState at app bootstrap;
2. map upload completion to `SOURCE_ATTACHED`;
3. map AI candidate generation and selection to ProjectState events;
4. make Game Editor read/write the same project identity;
5. map render lifecycle and final artifact reference;
6. make Crea Short publication update the same ProjectState;
7. remove legacy duplicate state only after regression coverage proves the bridge is stable.

This preserves the current production path while converging toward one project source of truth.
