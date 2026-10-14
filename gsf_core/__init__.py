"""Infrastructure primitives for Gaming Shorts Factory.

This package deliberately stays independent from Streamlit so web, AI and render
workers can share the same durable contracts.
"""

from .assets import AssetKind, AssetRef
from .jobs import InvalidJobTransition, JobRecord, JobStatus, JsonJobStore

__all__ = [
    "AssetKind",
    "AssetRef",
    "InvalidJobTransition",
    "JobRecord",
    "JobStatus",
    "JsonJobStore",
]
