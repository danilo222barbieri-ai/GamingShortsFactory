"""Durable project-state boundary for Gaming Shorts Factory.

This module stores only lightweight references and durable workflow facts. It
must never become a second video cache: raw media bytes stay outside session
state and are represented here by stable asset/candidate references.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Any, Mapping, MutableMapping


PROJECT_SESSION_KEY = "_gsf_project_state_v1"
SCHEMA_VERSION = 1


class ProjectStage(str, Enum):
    EMPTY = "empty"
    SOURCE_READY = "source_ready"
    MOMENTS_READY = "moments_ready"
    EDITING = "editing"
    RENDERING = "rendering"
    READY = "ready"
    PUBLISHED = "published"


class ProjectEventType(str, Enum):
    SOURCE_ATTACHED = "source_attached"
    MOMENTS_FOUND = "moments_found"
    MOMENT_SELECTED = "moment_selected"
    EDIT_SAVED = "edit_saved"
    RENDER_STARTED = "render_started"
    RENDER_COMPLETED = "render_completed"
    PUBLISHED = "published"
    NEW_VIDEO = "new_video"


@dataclass(frozen=True)
class ProjectEvent:
    kind: ProjectEventType
    payload: Mapping[str, Any] | None = None

    def data(self) -> Mapping[str, Any]:
        return self.payload or {}


@dataclass(frozen=True)
class ProjectState:
    project_id: str
    schema_version: int = SCHEMA_VERSION
    stage: ProjectStage = ProjectStage.EMPTY
    source_ref: str | None = None
    candidate_refs: tuple[str, ...] = ()
    selected_candidate_ref: str | None = None
    edit_revision: int = 0
    render_job_id: str | None = None
    final_ref: str | None = None
    published_targets: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["stage"] = self.stage.value
        data["candidate_refs"] = list(self.candidate_refs)
        data["published_targets"] = list(self.published_targets)
        return data

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ProjectState":
        if not isinstance(raw, Mapping):
            raise TypeError("project state must be a mapping")
        project_id = _require_project_id(raw.get("project_id"))
        try:
            stage = ProjectStage(str(raw.get("stage", ProjectStage.EMPTY.value)))
        except ValueError:
            stage = ProjectStage.EMPTY
        source_ref = _optional_ref(raw.get("source_ref"), "source_ref")
        final_ref = _optional_ref(raw.get("final_ref"), "final_ref")
        selected = _optional_ref(raw.get("selected_candidate_ref"), "selected_candidate_ref")
        candidate_refs = _refs(raw.get("candidate_refs", ()), "candidate_refs")
        published_targets = _refs(raw.get("published_targets", ()), "published_targets")
        render_job_id = _optional_ref(raw.get("render_job_id"), "render_job_id")
        try:
            edit_revision = max(0, int(raw.get("edit_revision", 0)))
        except (TypeError, ValueError):
            edit_revision = 0
        try:
            schema_version = max(1, int(raw.get("schema_version", SCHEMA_VERSION)))
        except (TypeError, ValueError):
            schema_version = SCHEMA_VERSION
        return cls(
            project_id=project_id,
            schema_version=schema_version,
            stage=stage,
            source_ref=source_ref,
            candidate_refs=candidate_refs,
            selected_candidate_ref=selected,
            edit_revision=edit_revision,
            render_job_id=render_job_id,
            final_ref=final_ref,
            published_targets=published_targets,
        )


def _require_project_id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("project_id must be a non-empty string")
    return value.strip()


def _optional_ref(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_ref(value, field)


def _require_ref(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a lightweight string reference")
    value = value.strip()
    if not value:
        raise ValueError(f"{field} must not be empty")
    return value


def _refs(values: Any, field: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, (str, bytes, bytearray)):
        raise TypeError(f"{field} must be a sequence of string references")
    try:
        return tuple(_require_ref(value, field) for value in values)
    except TypeError:
        raise TypeError(f"{field} must be a sequence of string references") from None


def new_project(project_id: str) -> ProjectState:
    return ProjectState(project_id=_require_project_id(project_id))


def reduce_project(state: ProjectState, event: ProjectEvent) -> ProjectState:
    """Apply one durable project event and return a new immutable state."""
    if not isinstance(state, ProjectState):
        raise TypeError("state must be ProjectState")
    kind = ProjectEventType(event.kind)
    data = event.data()

    if kind is ProjectEventType.NEW_VIDEO:
        project_id = data.get("project_id", state.project_id)
        return new_project(_require_project_id(project_id))

    if kind is ProjectEventType.SOURCE_ATTACHED:
        source_ref = _require_ref(data.get("source_ref"), "source_ref")
        return replace(
            state,
            stage=ProjectStage.SOURCE_READY,
            source_ref=source_ref,
            candidate_refs=(),
            selected_candidate_ref=None,
            edit_revision=0,
            render_job_id=None,
            final_ref=None,
            published_targets=(),
        )

    if kind is ProjectEventType.MOMENTS_FOUND:
        candidate_refs = _refs(data.get("candidate_refs", ()), "candidate_refs")
        return replace(
            state,
            stage=ProjectStage.MOMENTS_READY,
            candidate_refs=candidate_refs,
            selected_candidate_ref=None,
            final_ref=None,
            published_targets=(),
        )

    if kind is ProjectEventType.MOMENT_SELECTED:
        candidate_ref = _require_ref(data.get("candidate_ref"), "candidate_ref")
        if state.candidate_refs and candidate_ref not in state.candidate_refs:
            raise ValueError("selected candidate must belong to the current project")
        return replace(
            state,
            selected_candidate_ref=candidate_ref,
            final_ref=None,
            published_targets=(),
        )

    if kind is ProjectEventType.EDIT_SAVED:
        if state.source_ref is None:
            raise ValueError("cannot save an edit without a source")
        return replace(
            state,
            stage=ProjectStage.EDITING,
            edit_revision=state.edit_revision + 1,
            final_ref=None,
            published_targets=(),
        )

    if kind is ProjectEventType.RENDER_STARTED:
        if state.source_ref is None:
            raise ValueError("cannot render without a source")
        job_id = _require_ref(data.get("job_id"), "job_id")
        return replace(
            state,
            stage=ProjectStage.RENDERING,
            render_job_id=job_id,
            final_ref=None,
            published_targets=(),
        )

    if kind is ProjectEventType.RENDER_COMPLETED:
        if state.source_ref is None:
            raise ValueError("cannot complete a render without a source")
        final_ref = _require_ref(data.get("final_ref"), "final_ref")
        return replace(
            state,
            stage=ProjectStage.READY,
            render_job_id=None,
            final_ref=final_ref,
            published_targets=(),
        )

    if kind is ProjectEventType.PUBLISHED:
        if state.final_ref is None:
            raise ValueError("cannot publish before a final short exists")
        target = _require_ref(data.get("target"), "target")
        targets = state.published_targets
        if target not in targets:
            targets = (*targets, target)
        return replace(state, stage=ProjectStage.PUBLISHED, published_targets=targets)

    return state


def load_project_session(
    session: MutableMapping[str, Any], *, project_id: str | None = None
) -> ProjectState:
    """Load durable project state without mutating unrelated Streamlit keys."""
    raw = session.get(PROJECT_SESSION_KEY)
    if isinstance(raw, Mapping):
        state = ProjectState.from_dict(raw)
    else:
        if project_id is None:
            raise ValueError("project_id is required when no project state exists")
        state = new_project(project_id)
        session[PROJECT_SESSION_KEY] = state.to_dict()
    return state


def save_project_session(
    session: MutableMapping[str, Any], state: ProjectState
) -> ProjectState:
    """Persist only the project-state namespace and preserve all legacy keys."""
    if not isinstance(state, ProjectState):
        raise TypeError("state must be ProjectState")
    session[PROJECT_SESSION_KEY] = state.to_dict()
    return state
