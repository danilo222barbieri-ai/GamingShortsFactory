"""Infrastructure primitives for Gaming Shorts Factory.

This package deliberately stays independent from Streamlit so web, AI and render
workers can share the same durable contracts.
"""

from .assets import AssetKind, AssetRef
from .jobs import InvalidJobTransition, JobRecord, JobStatus, JsonJobStore
from .storage import LocalStorage, S3Storage, UploadTarget
from .ai_scan import (
    find_ffmpeg,
    find_ffprobe,
    get_video_duration,
    source_has_audio,
    gsf_norm_series,
    gsf_ai_scan_profile_for_duration,
    gsf_interpolate_motion_points,
    gsf_ai_scan_base,
)
from .render_client import (
    RenderJobRequest,
    dispatch_render_to_worker,
    get_render_job_status,
    is_worker_configured,
)

__all__ = [
    "AssetKind",
    "AssetRef",
    "InvalidJobTransition",
    "JobRecord",
    "JobStatus",
    "JsonJobStore",
    "LocalStorage",
    "S3Storage",
    "UploadTarget",
    "find_ffmpeg",
    "find_ffprobe",
    "get_video_duration",
    "source_has_audio",
    "gsf_norm_series",
    "gsf_ai_scan_profile_for_duration",
    "gsf_interpolate_motion_points",
    "gsf_ai_scan_base",
    "RenderJobRequest",
    "dispatch_render_to_worker",
    "get_render_job_status",
    "is_worker_configured",
]
