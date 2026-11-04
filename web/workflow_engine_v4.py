"""Gaming Shorts Factory — Workflow Engine 4.0
Centralized, state-machine-driven progress controller for GSF projects.

Two Official Paths:
- PERCORSO_A (duration >= 15s):
    EMPTY -> UPLOADING -> UPLOADED -> ANALYZING -> MOMENTS_READY -> MOMENT_SELECTED -> EDITOR_READY -> EDITING -> EDIT_CONFIRMED -> SHORT_CREATING -> SHORT_READY -> EXPORTED / PUBLISHED
- PERCORSO_B (duration < 15s):
    EMPTY -> UPLOADING -> UPLOADED -> EDITOR_READY -> EDITING -> EDIT_CONFIRMED -> SHORT_CREATING -> SHORT_READY -> EXPORTED / PUBLISHED
"""

from __future__ import annotations
import enum
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class WorkflowState(str, enum.Enum):
    EMPTY = "EMPTY"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    ANALYZING = "ANALYZING"
    MOMENTS_READY = "MOMENTS_READY"
    MOMENT_SELECTED = "MOMENT_SELECTED"
    EDITOR_READY = "EDITOR_READY"
    EDITING = "EDITING"
    EDIT_CONFIRMED = "EDIT_CONFIRMED"
    SHORT_CREATING = "SHORT_CREATING"
    SHORT_READY = "SHORT_READY"
    EXPORTED = "EXPORTED"
    PUBLISHED = "PUBLISHED"


class WorkflowPath(str, enum.Enum):
    PERCORSO_A = "PERCORSO_A"  # duration >= 15s
    PERCORSO_B = "PERCORSO_B"  # duration < 15s


STAGE_ORDER_A = [
    WorkflowState.EMPTY,
    WorkflowState.UPLOADING,
    WorkflowState.UPLOADED,
    WorkflowState.ANALYZING,
    WorkflowState.MOMENTS_READY,
    WorkflowState.MOMENT_SELECTED,
    WorkflowState.EDITOR_READY,
    WorkflowState.EDITING,
    WorkflowState.EDIT_CONFIRMED,
    WorkflowState.SHORT_CREATING,
    WorkflowState.SHORT_READY,
    WorkflowState.EXPORTED,
    WorkflowState.PUBLISHED,
]

STAGE_ORDER_B = [
    WorkflowState.EMPTY,
    WorkflowState.UPLOADING,
    WorkflowState.UPLOADED,
    WorkflowState.EDITOR_READY,
    WorkflowState.EDITING,
    WorkflowState.EDIT_CONFIRMED,
    WorkflowState.SHORT_CREATING,
    WorkflowState.SHORT_READY,
    WorkflowState.EXPORTED,
    WorkflowState.PUBLISHED,
]


def determine_path(duration: Optional[float]) -> WorkflowPath:
    if duration is not None and float(duration) < 15.0:
        return WorkflowPath.PERCORSO_B
    return WorkflowPath.PERCORSO_A


class ProjectWorkflow:
    """Manages the lifecycle, transitions, and persistence of a GSF project workflow."""

    def __init__(
        self,
        project_id: str = "current",
        state: WorkflowState = WorkflowState.EMPTY,
        duration: Optional[float] = None,
        source_path: str = "",
        moment_selected: Optional[int] = None,
        clip_start: float = 0.0,
        clip_duration: float = 15.0,
        final_video_path: str = "",
        error: Optional[str] = None,
        updated_at: Optional[float] = None,
    ) -> None:
        self.project_id = str(project_id or "current")
        self.state = WorkflowState(state) if isinstance(state, str) else state
        self.duration = float(duration) if duration is not None and duration > 0 else None
        self.source_path = str(source_path or "")
        self.moment_selected = moment_selected
        self.clip_start = float(clip_start)
        self.clip_duration = float(clip_duration)
        self.final_video_path = str(final_video_path or "")
        self.error = str(error) if error else None
        self.updated_at = float(updated_at or time.time())

    @property
    def path(self) -> WorkflowPath:
        return determine_path(self.duration)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "state": self.state.value,
            "path": self.path.value,
            "duration": self.duration,
            "source_path": self.source_path,
            "moment_selected": self.moment_selected,
            "clip_start": self.clip_start,
            "clip_duration": self.clip_duration,
            "final_video_path": self.final_video_path,
            "error": self.error,
            "updated_at": self.updated_at,
            "allowed_actions": self.allowed_actions(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectWorkflow":
        st_val = data.get("state", WorkflowState.EMPTY.value)
        try:
            state = WorkflowState(st_val)
        except ValueError:
            state = WorkflowState.EMPTY
        return cls(
            project_id=data.get("project_id", "current"),
            state=state,
            duration=data.get("duration"),
            source_path=data.get("source_path", ""),
            moment_selected=data.get("moment_selected"),
            clip_start=data.get("clip_start", 0.0),
            clip_duration=data.get("clip_duration", 15.0),
            final_video_path=data.get("final_video_path", ""),
            error=data.get("error"),
            updated_at=data.get("updated_at"),
        )

    def allowed_actions(self) -> Dict[str, bool]:
        """Returns the dictionary of currently unlocked / locked capabilities."""
        p = self.path
        st = self.state

        # Upload is always allowed (starts a new video or safe replacement)
        # Creator Hub is ALWAYS available
        can_upload = True
        can_hub = True

        # Trova i momenti: available ONLY for Percorso A once video is uploaded
        can_find_moments = (
            p == WorkflowPath.PERCORSO_A
            and st in (WorkflowState.UPLOADED, WorkflowState.MOMENTS_READY, WorkflowState.MOMENT_SELECTED)
        )

        # Selezione momenti: available when moments are ready
        can_select_moment = (
            p == WorkflowPath.PERCORSO_A
            and st in (WorkflowState.MOMENTS_READY, WorkflowState.MOMENT_SELECTED, WorkflowState.EDITOR_READY, WorkflowState.EDITING)
        )

        # Game Editor:
        # - Percorso B: available as soon as UPLOADED / EDITOR_READY
        # - Percorso A: available ONLY once a moment has been selected
        if p == WorkflowPath.PERCORSO_B:
            can_editor = st in (
                WorkflowState.UPLOADED,
                WorkflowState.EDITOR_READY,
                WorkflowState.EDITING,
                WorkflowState.EDIT_CONFIRMED,
                WorkflowState.SHORT_READY,
            )
        else:
            can_editor = st in (
                WorkflowState.MOMENT_SELECTED,
                WorkflowState.EDITOR_READY,
                WorkflowState.EDITING,
                WorkflowState.EDIT_CONFIRMED,
                WorkflowState.SHORT_READY,
            )

        # Crea Short: unlocked ONLY once edit is confirmed (or in short creation/ready)
        can_create_short = st in (
            WorkflowState.EDIT_CONFIRMED,
            WorkflowState.SHORT_CREATING,
            WorkflowState.SHORT_READY,
            WorkflowState.EXPORTED,
            WorkflowState.PUBLISHED,
        )

        # Esporta / Pubblica: unlocked ONLY once short is ready
        can_publish = st in (WorkflowState.SHORT_READY, WorkflowState.EXPORTED, WorkflowState.PUBLISHED)
        can_export = can_publish

        return {
            "upload": can_upload,
            "creator_hub": can_hub,
            "find_moments": can_find_moments,
            "select_moment": can_select_moment,
            "open_editor": can_editor,
            "create_short": can_create_short,
            "export": can_export,
            "publish": can_publish,
        }

    def validate_transition(self, target_state: WorkflowState) -> Tuple[bool, str]:
        """Checks if transitioning from current state to target_state is authorized."""
        if target_state == self.state:
            return True, "Same state"

        # Safe reset on new upload
        if target_state in (WorkflowState.EMPTY, WorkflowState.UPLOADING):
            return True, "Upload reset allowed"

        p = self.path

        if p == WorkflowPath.PERCORSO_B:
            # Percorso B skips AI analysis & moment selection entirely
            forbidden_b = (
                WorkflowState.ANALYZING,
                WorkflowState.MOMENTS_READY,
                WorkflowState.MOMENT_SELECTED,
            )
            if target_state in forbidden_b:
                return False, "I video inferiori a 15 secondi passano direttamente al Game Editor (Percorso B)."

            # UPLOADED -> EDITOR_READY
            if self.state == WorkflowState.UPLOADED and target_state == WorkflowState.EDITOR_READY:
                return True, "Percorso B: transizione diretta da UPLOADED a EDITOR_READY"

        if p == WorkflowPath.PERCORSO_A:
            # Cannot enter EDITOR_READY or EDITING without selecting a moment
            if target_state in (WorkflowState.EDITOR_READY, WorkflowState.EDITING):
                if self.state in (WorkflowState.EMPTY, WorkflowState.UPLOADING, WorkflowState.UPLOADED, WorkflowState.ANALYZING):
                    return False, "Completa l'analisi IA e seleziona un momento per aprire il Game Editor."
                if self.state == WorkflowState.MOMENTS_READY and self.moment_selected is None:
                    return False, "Seleziona uno dei tre momenti per aprire il Game Editor."

        # Cannot create short without edit confirmation
        if target_state in (WorkflowState.SHORT_CREATING, WorkflowState.SHORT_READY):
            if self.state not in (WorkflowState.EDIT_CONFIRMED, WorkflowState.SHORT_CREATING, WorkflowState.SHORT_READY):
                return False, "Conferma il montaggio nel Game Editor prima di creare lo Short."

        # Cannot publish or export without final short ready
        if target_state in (WorkflowState.EXPORTED, WorkflowState.PUBLISHED):
            if self.state not in (WorkflowState.SHORT_READY, WorkflowState.EXPORTED, WorkflowState.PUBLISHED):
                return False, "Lo Short deve essere pronto prima di esportare o pubblicare."

        return True, "Transition authorized"

    def transition_to(self, target_state: WorkflowState, **kwargs: Any) -> bool:
        """Executes authorized state transition and updates context fields."""
        ok, reason = self.validate_transition(target_state)
        if not ok:
            self.error = reason
            return False

        self.state = target_state
        self.error = None
        self.updated_at = time.time()

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

        # Automatic path routing on UPLOADED
        if target_state == WorkflowState.UPLOADED:
            if self.path == WorkflowPath.PERCORSO_B:
                self.state = WorkflowState.EDITOR_READY

        return True


# Storage helpers for sessions
def workflow_file(media_or_session_dir: Path) -> Path:
    base = media_or_session_dir if media_or_session_dir.name != "media" else media_or_session_dir.parent
    return base / "workflow_state.json"


def load_workflow(media_or_session_dir: Path) -> ProjectWorkflow:
    f = workflow_file(media_or_session_dir)
    if f.is_file():
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return ProjectWorkflow.from_dict(data)
        except Exception:
            pass
    return ProjectWorkflow()


def save_workflow(media_or_session_dir: Path, wf: ProjectWorkflow) -> Path:
    f = workflow_file(media_or_session_dir)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(wf.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(f)
    return f
