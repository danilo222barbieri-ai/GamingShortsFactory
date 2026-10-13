from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ACTIONS = {"none", "notify", "rollback", "escalate"}
HARD_FAILURES = {"FAILED", "CRASHED", "OOM", "OOM_KILLED", "OUT_OF_MEMORY"}
AMBIGUOUS_HEALTH = {"isolated_5xx", "provider_error", "network_error", "transient_error"}
SECRET_FRAGMENTS = ("token", "password", "secret", "api_key", "apikey", "credential")


@dataclass(frozen=True)
class RollbackDecision:
    action: str
    reason: str
    service_id: str
    failing_deployment_id: str
    target_deployment_id: str | None = None

    def __post_init__(self) -> None:
        if self.action not in ACTIONS:
            raise ValueError(f"invalid rollback action: {self.action}")


def incident_key(service_id: str, deployment_id: str) -> str:
    return f"{service_id}:{deployment_id}"


def _reject_secret_keys(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in SECRET_FRAGMENTS):
                raise ValueError(f"secret-like key forbidden at {path}.{key}")
            _reject_secret_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _reject_secret_keys(child, f"{path}[{idx}]")


def validate_known_good(data: dict[str, Any]) -> dict[str, Any]:
    _reject_secret_keys(data)
    if data.get("version") != 1 or not isinstance(data.get("services"), dict):
        raise ValueError("invalid known-good document")
    required = {
        "service_id",
        "environment_id",
        "deployment_id",
        "promotion_commit",
        "verified_at",
        "health_endpoint",
        "state",
    }
    for service_id, record in data["services"].items():
        if not isinstance(record, dict):
            raise ValueError(f"known-good record must be object: {service_id}")
        missing = required - set(record)
        if missing:
            raise ValueError(f"known-good record missing {sorted(missing)}")
        if record["service_id"] != service_id:
            raise ValueError(f"known-good service id mismatch: {service_id}")
    return data


def validate_incident_index(data: dict[str, Any]) -> dict[str, Any]:
    _reject_secret_keys(data)
    if data.get("version") != 1 or not isinstance(data.get("incidents"), dict):
        raise ValueError("invalid incident index")
    for key, record in data["incidents"].items():
        if not isinstance(record, dict):
            raise ValueError(f"incident record must be object: {key}")
        attempts = record.get("attempt_count", 0)
        if not isinstance(attempts, int) or attempts < 0:
            raise ValueError(f"invalid attempt_count for {key}")
    return data


def classify_service_state(service: dict[str, Any], sleep_enabled: bool = False) -> str:
    status = str(service.get("status") or "UNKNOWN").upper()
    health = str(service.get("health") or "unknown").lower()
    if status == "SLEEPING" and sleep_enabled:
        return "healthy_sleeping"
    if status in HARD_FAILURES:
        return "hard_failure"
    if health == "unhealthy_sustained":
        return "hard_failure"
    if health in AMBIGUOUS_HEALTH:
        return "ambiguous"
    if status in {"SUCCESS", "DEPLOYED", "ONLINE", "SLEEPING"} and health not in {"unhealthy", "unhealthy_sustained"}:
        return "healthy"
    return "unknown"


def should_rollback(
    current: dict[str, Any],
    incident_index: dict[str, Any],
    known_good: dict[str, Any],
) -> RollbackDecision:
    service_id = str(current.get("service_id") or "")
    deployment_id = str(current.get("deployment_id") or "")
    if not service_id or not deployment_id:
        return RollbackDecision("notify", "missing current deployment identity", service_id, deployment_id)

    if current.get("recovery_failed"):
        return RollbackDecision("escalate", "rollback recovery failed", service_id, deployment_id)

    if current.get("is_current") is False:
        return RollbackDecision("none", "failure belongs to superseded deployment", service_id, deployment_id)

    sleep_enabled = bool(current.get("sleep_enabled"))
    state = classify_service_state(current, sleep_enabled=sleep_enabled)
    if state == "healthy_sleeping":
        return RollbackDecision("none", "worker sleeping by configuration", service_id, deployment_id)

    try:
        valid_incidents = validate_incident_index(incident_index)
    except (TypeError, ValueError):
        return RollbackDecision("notify", "invalid incident state; refusing automatic rollback", service_id, deployment_id)

    existing = valid_incidents["incidents"].get(incident_key(service_id, deployment_id), {})
    if int(existing.get("attempt_count", 0) or 0) >= 1:
        return RollbackDecision("notify", "automatic rollback already attempted", service_id, deployment_id)

    if state == "ambiguous":
        return RollbackDecision("notify", "ambiguous transient signal", service_id, deployment_id)
    if state != "hard_failure":
        return RollbackDecision("none", "service is not in a hard failure state", service_id, deployment_id)

    try:
        valid_known_good = validate_known_good(known_good)
    except (TypeError, ValueError):
        return RollbackDecision("notify", "invalid known-good state; refusing automatic rollback", service_id, deployment_id)

    target = valid_known_good["services"].get(service_id)
    target_id = str(target.get("deployment_id")) if isinstance(target, dict) and target.get("deployment_id") else None
    if not target_id:
        return RollbackDecision("notify", "no verified known-good rollback target", service_id, deployment_id)
    if target_id == deployment_id:
        return RollbackDecision("notify", "failing deployment is already the known-good target", service_id, deployment_id)

    return RollbackDecision(
        "rollback",
        "hard failure with verified previous deployment",
        service_id,
        deployment_id,
        target_id,
    )
