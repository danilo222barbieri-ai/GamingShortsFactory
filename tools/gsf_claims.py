from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from typing import Any

VALID_STATES = {"active", "handoff", "completed", "abandoned"}
BLOCKING_STATES = {"active", "handoff"}
_WILDCARDS = "*?["


@dataclass
class Claim:
    id: str
    branch: str
    scope: str
    paths: list[str]
    owner: str
    created_at: str
    state: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "branch": self.branch,
            "scope": self.scope,
            "paths": list(self.paths),
            "owner": self.owner,
            "created_at": self.created_at,
            "state": self.state,
        }
        if self.evidence:
            data["evidence"] = dict(self.evidence)
        return data


def normalize_paths(paths: list[str]) -> list[str]:
    cleaned = {str(path).strip().replace("\\", "/") for path in paths if str(path).strip()}
    return sorted(cleaned)


def _has_glob(value: str) -> bool:
    return any(ch in value for ch in _WILDCARDS)


def _fixed_prefix(pattern: str) -> str:
    positions = [pattern.find(ch) for ch in _WILDCARDS if ch in pattern]
    return pattern[: min(positions)] if positions else pattern


def _fixed_suffix(pattern: str) -> str:
    positions = [pattern.rfind(ch) for ch in _WILDCARDS if ch in pattern]
    return pattern[max(positions) + 1 :] if positions else pattern


def patterns_overlap(a: str, b: str) -> bool:
    """Conservative glob intersection check used for ownership locking.

    False negatives are more dangerous than false positives here, so two glob
    patterns are considered overlapping whenever their fixed prefix and suffix
    constraints are compatible.
    """
    a = a.strip().replace("\\", "/")
    b = b.strip().replace("\\", "/")
    if a == b:
        return True

    a_glob = _has_glob(a)
    b_glob = _has_glob(b)
    if not a_glob and not b_glob:
        return False
    if a_glob and not b_glob:
        return fnmatchcase(b, a)
    if b_glob and not a_glob:
        return fnmatchcase(a, b)

    a_prefix, b_prefix = _fixed_prefix(a), _fixed_prefix(b)
    if a_prefix and b_prefix and not (a_prefix.startswith(b_prefix) or b_prefix.startswith(a_prefix)):
        return False

    a_suffix, b_suffix = _fixed_suffix(a), _fixed_suffix(b)
    if a_suffix and b_suffix and not (a_suffix.endswith(b_suffix) or b_suffix.endswith(a_suffix)):
        return False

    return True


def validate_claim_dict(data: dict[str, Any]) -> Claim:
    required = ("id", "branch", "scope", "paths", "owner", "created_at", "state")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"claim missing required keys: {', '.join(missing)}")
    if data["state"] not in VALID_STATES:
        raise ValueError(f"invalid claim state: {data['state']}")
    if not isinstance(data["paths"], list) or not data["paths"]:
        raise ValueError("claim paths must be a non-empty list")
    return Claim(
        id=str(data["id"]),
        branch=str(data["branch"]),
        scope=str(data["scope"]),
        paths=normalize_paths([str(path) for path in data["paths"]]),
        owner=str(data["owner"]),
        created_at=str(data["created_at"]),
        state=str(data["state"]),
        evidence=dict(data.get("evidence") or {}),
    )


def find_conflicts(requested_paths: list[str], active_claims: list[Claim]) -> list[Claim]:
    requested = normalize_paths(requested_paths)
    conflicts: list[Claim] = []
    for claim in active_claims:
        if claim.state not in BLOCKING_STATES:
            continue
        if any(patterns_overlap(left, right) for left in requested for right in claim.paths):
            conflicts.append(claim)
    return conflicts
