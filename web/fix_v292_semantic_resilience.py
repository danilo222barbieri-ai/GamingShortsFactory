#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys

MARKER = "GSF_V292_SEMANTIC_RESILIENCE"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"V292 patch anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    target = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/semantic_video_v114.py")
    if not target.exists():
        local = pathlib.Path(__file__).with_name("semantic_video_v114.py")
        target = local if local.exists() else target
    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"V292 semantic resilience already applied: {target}")
        return

    text = replace_once(
        text,
        "import subprocess\nimport time\nfrom pathlib import Path\n",
        "import subprocess\nimport threading\nimport time\nfrom pathlib import Path\n",
        "threading import",
    )

    quota_anchor = '''def is_quota_error(value):\n    text=str(value or "").lower()\n    markers=(\n        "429","resource_exhausted","resource exhausted","quota exceeded",\n        "exceeded your current quota","rate limit","too many requests",\n    )\n    return any(marker in text for marker in markers)\n\n\n'''
    resilience = '''def is_quota_error(value):\n    text=str(value or "").lower()\n    markers=(\n        "429","resource_exhausted","resource exhausted","quota exceeded",\n        "exceeded your current quota","rate limit","too many requests",\n    )\n    return any(marker in text for marker in markers)\n\n\n# GSF_V292_SEMANTIC_RESILIENCE\ndef is_unavailable_error(value):\n    text=str(value or "").lower()\n    markers=(\n        "503","unavailable","service unavailable","high demand","overloaded",\n        "temporarily unavailable","backend error",\n    )\n    return any(marker in text for marker in markers)\n\n\n_SEMANTIC_CIRCUIT_LOCK=threading.Lock()\n_SEMANTIC_CIRCUIT={"until":0.0,"reason":""}\n\n\ndef _semantic_circuit_status(now=None):\n    current=time.monotonic() if now is None else float(now)\n    with _SEMANTIC_CIRCUIT_LOCK:\n        until=float(_SEMANTIC_CIRCUIT.get("until") or 0.0)\n        reason=str(_SEMANTIC_CIRCUIT.get("reason") or "")\n        if until<=current:\n            _SEMANTIC_CIRCUIT["until"]=0.0\n            _SEMANTIC_CIRCUIT["reason"]=""\n            return {"open":False,"reason":"","remaining_seconds":0.0}\n        return {\n            "open":True,\n            "reason":reason,\n            "remaining_seconds":max(0.0,until-current),\n        }\n\n\ndef _semantic_circuit_record_failure(exc,now=None):\n    current=time.monotonic() if now is None else float(now)\n    if is_quota_error(exc):\n        reason="quota"\n        cooldown=max(30.0,float(os.environ.get("GSF_SEMANTIC_COOLDOWN_429_SECONDS","900") or 900))\n    elif is_unavailable_error(exc):\n        reason="unavailable"\n        cooldown=max(15.0,float(os.environ.get("GSF_SEMANTIC_COOLDOWN_503_SECONDS","120") or 120))\n    else:\n        return _semantic_circuit_status(now=current)\n    with _SEMANTIC_CIRCUIT_LOCK:\n        _SEMANTIC_CIRCUIT["until"]=max(\n            float(_SEMANTIC_CIRCUIT.get("until") or 0.0),current+cooldown\n        )\n        _SEMANTIC_CIRCUIT["reason"]=reason\n    return _semantic_circuit_status(now=current)\n\n\ndef _semantic_circuit_record_success():\n    with _SEMANTIC_CIRCUIT_LOCK:\n        _SEMANTIC_CIRCUIT["until"]=0.0\n        _SEMANTIC_CIRCUIT["reason"]=""\n\n\ndef _semantic_circuit_reset_for_tests():\n    _semantic_circuit_record_success()\n\n\n'''
    text = replace_once(text, quota_anchor, resilience, "quota helper")

    timeout_anchor = '''    duration_seconds=_probe_duration_seconds(source)\n    semantic_timeout=max(\n        60.0,float(os.environ.get("GSF_SEMANTIC_TIMEOUT_SECONDS","420") or 420)\n    )\n    model_attempts=[]\n'''
    timeout_replacement = '''    duration_seconds=_probe_duration_seconds(source)\n    semantic_timeout=max(\n        10.0,float(os.environ.get("GSF_SEMANTIC_TIMEOUT_SECONDS","45") or 45)\n    )\n    circuit=_semantic_circuit_status()\n    if circuit.get("open"):\n        return {\n            "enabled":True,\n            "provider":primary_model+"-local-fallback-v292",\n            "events":[],\n            "skipped":"provider-circuit-open",\n            "circuit_reason":circuit.get("reason",""),\n            "retry_after_seconds":round(float(circuit.get("remaining_seconds") or 0.0),1),\n            "model_attempts":[],\n            "model_fallback":False,\n            "elapsed_seconds":0.0,\n        }\n    model_attempts=[]\n'''
    text = replace_once(text, timeout_anchor, timeout_replacement, "semantic timeout/circuit entry")

    text = replace_once(
        text,
        '''        from google import genai\n        client=genai.Client(api_key=key)\n''',
        '''        from google import genai\n        from google.genai import types\n        client=genai.Client(\n            api_key=key,\n            http_options=types.HttpOptions(timeout=int(semantic_timeout*1000)),\n        )\n''',
        "Google client timeout",
    )

    text = replace_once(
        text,
        "            deadline=time.time()+180\n",
        "            deadline=time.time()+semantic_timeout\n",
        "file-processing timeout",
    )

    text = replace_once(
        text,
        '''                if quota and index+1<len(models):\n                    continue\n                raise\n''',
        '''                if quota and index+1<len(models) and _env_bool("GSF_SEMANTIC_RETRY_MODEL_ON_QUOTA",False):\n                    continue\n                raise\n''',
        "quota retry policy",
    )

    success_anchor = '''        events=normalize_semantic_events(payload,max_events=max_events)\n        return {\n'''
    success_replacement = '''        events=normalize_semantic_events(payload,max_events=max_events)\n        _semantic_circuit_record_success()\n        return {\n'''
    text = replace_once(text, success_anchor, success_replacement, "circuit success reset")

    error_anchor = '''    except Exception as exc:\n        return {\n            "enabled":True,\n            "provider":selected_model+"-"+selected_mode+"-"+input_method+\n'''
    error_replacement = '''    except Exception as exc:\n        circuit=_semantic_circuit_record_failure(exc)\n        return {\n            "enabled":True,\n            "provider":selected_model+"-"+selected_mode+"-"+input_method+\n'''
    text = replace_once(text, error_anchor, error_replacement, "circuit failure record")

    error_tail = '''            "error":str(exc)[:240],\n            "elapsed_seconds":round(time.perf_counter()-started,3),\n        }\n'''
    error_tail_replacement = '''            "error":str(exc)[:240],\n            "circuit_open":bool(circuit.get("open")),\n            "circuit_reason":circuit.get("reason",""),\n            "retry_after_seconds":round(float(circuit.get("remaining_seconds") or 0.0),1),\n            "elapsed_seconds":round(time.perf_counter()-started,3),\n        }\n'''
    text = replace_once(text, error_tail, error_tail_replacement, "circuit diagnostics")

    target.write_text(text, encoding="utf-8")
    print(f"V292 semantic resilience applied: {target}")


if __name__ == "__main__":
    main()
