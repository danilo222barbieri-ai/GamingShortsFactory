import os
import sys

sys.path.insert(0, "/app/web")

import semantic_video_v114 as semantic

required = (
    "_semantic_circuit_status",
    "_semantic_circuit_record_failure",
    "_semantic_circuit_record_success",
    "_semantic_circuit_reset_for_tests",
    "is_unavailable_error",
)
for name in required:
    if not hasattr(semantic, name):
        raise SystemExit("V292 semantic circuit helper missing: " + name)

os.environ["GSF_SEMANTIC_COOLDOWN_429_SECONDS"] = "900"
os.environ["GSF_SEMANTIC_COOLDOWN_503_SECONDS"] = "120"
semantic._semantic_circuit_reset_for_tests()

if semantic._semantic_circuit_status(now=1000.0).get("open"):
    raise SystemExit("V292 semantic circuit must begin closed")

if not semantic.is_unavailable_error("503 UNAVAILABLE high demand"):
    raise SystemExit("V292 503 unavailable detection failed")
if semantic.is_unavailable_error("invalid_argument"):
    raise SystemExit("V292 unavailable detection false positive")

opened = semantic._semantic_circuit_record_failure(
    RuntimeError("429 RESOURCE_EXHAUSTED quota exceeded"), now=1000.0
)
if not opened.get("open"):
    raise SystemExit("V292 429 must open semantic circuit")
if opened.get("reason") != "quota":
    raise SystemExit("V292 429 circuit reason must be quota: " + repr(opened))
if int(round(opened.get("remaining_seconds", 0))) != 900:
    raise SystemExit("V292 429 cooldown mismatch: " + repr(opened))

mid = semantic._semantic_circuit_status(now=1450.0)
if not mid.get("open") or int(round(mid.get("remaining_seconds", 0))) != 450:
    raise SystemExit("V292 circuit countdown mismatch: " + repr(mid))

expired = semantic._semantic_circuit_status(now=1901.0)
if expired.get("open"):
    raise SystemExit("V292 semantic circuit did not expire: " + repr(expired))

semantic._semantic_circuit_reset_for_tests()
opened_503 = semantic._semantic_circuit_record_failure(
    RuntimeError("503 UNAVAILABLE service overloaded"), now=2000.0
)
if not opened_503.get("open") or opened_503.get("reason") != "unavailable":
    raise SystemExit("V292 503 must open short semantic circuit: " + repr(opened_503))
if int(round(opened_503.get("remaining_seconds", 0))) != 120:
    raise SystemExit("V292 503 cooldown mismatch: " + repr(opened_503))

semantic._semantic_circuit_record_success()
if semantic._semantic_circuit_status(now=2001.0).get("open"):
    raise SystemExit("V292 successful semantic call must close circuit")

source = open("/app/web/semantic_video_v114.py", "r", encoding="utf-8").read()
for marker in (
    "GSF_V292_SEMANTIC_RESILIENCE",
    "_semantic_circuit_status()",
    "provider-circuit-open",
    "_semantic_circuit_record_failure(exc)",
    "_semantic_circuit_record_success()",
    "GSF_SEMANTIC_COOLDOWN_429_SECONDS",
    "GSF_SEMANTIC_COOLDOWN_503_SECONDS",
    'GSF_SEMANTIC_TIMEOUT_SECONDS","45"',
    "types.HttpOptions(timeout=int(semantic_timeout*1000))",
    "deadline=time.time()+semantic_timeout",
):
    if marker not in source:
        raise SystemExit("V292 semantic runtime resilience integration missing: " + marker)

print("V292 semantic provider timeout/cooldown/circuit contract: PASS")
