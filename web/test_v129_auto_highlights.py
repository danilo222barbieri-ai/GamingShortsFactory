from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0,"/app/web")

from auto_highlights.engine_v129 import analysis_to_candidates, apply_analysis_to_job, candidate_dict
from auto_highlights.models import LiveProvider, LiveSource, LiveScanJob, LiveJobStatus

events=[
    {"time":18.0,"kind":"IMPACT","score":.82,"semantic":"kill","semantic_score":.91,"semantic_confidence":.94,"source":"local+gemini-v117","focus_x":57,"focus_y":42,"focus_confidence":.88,"hud_elements":["killfeed"]},
    {"time":62.0,"kind":"REACTION","score":.80,"semantic":"reaction","semantic_score":.89,"semantic_confidence":.92,"semantic_reaction":.98,"source":"local+gemini-v117"},
    {"time":109.0,"kind":"PEAK","score":.93,"semantic":"clutch","semantic_score":.98,"semantic_confidence":.97,"source":"gemini-v117","focus_x":63,"focus_y":41,"focus_confidence":.93,"hud_elements":["killfeed","minimap"]},
    {"time":150.0,"kind":"IMPACT","score":.86,"semantic":"multi_kill","semantic_score":.95,"semantic_confidence":.96,"source":"gemini-v117"},
    {"time":180.0,"kind":"SILENCE","score":.99},
]
analysis={
    "engine_version":"v52-keyframe-turbo",
    "scan":{
        "event_map_v108":events,
        "meta":{"duration":220.0},
    },
}
candidates,meta=analysis_to_candidates(
    analysis,target_highlights=3,target_duration=30,genre="FPS"
)
if len(candidates)!=3:
    raise SystemExit("V129 expected 3 Auto Highlights candidates: "+repr(candidates))
if any(x.duration!=30 for x in candidates):
    raise SystemExit("V129 candidate duration contract failed")
if not all(x.director_plan for x in candidates):
    raise SystemExit("V129 candidates missing Director plans")
if not any(x.event in ("clutch","multi_kill","kill","reaction") for x in candidates):
    raise SystemExit("V129 semantic events did not reach Auto Highlights")
if meta.get("game_brain",{}).get("selected_count")!=3:
    raise SystemExit("V129 did not reuse Game Brain selection")

job=LiveScanJob(
    source=LiveSource(
        provider=LiveProvider.TWITCH,
        account_id="creator1",
        broadcast_id="stream42",
        title="Test live",
        vod_id="vod99",
    ),
    status=LiveJobStatus.READY_TO_SCAN,
    target_highlights=3,
    target_duration=30,
)
job_meta=apply_analysis_to_job(job,analysis,genre="FPS")
if job.status!=LiveJobStatus.HIGHLIGHTS_READY or len(job.candidates)!=3:
    raise SystemExit("V129 LiveScanJob transition failed")
row=candidate_dict(job.candidates[0])
if "director_plan" not in row or "confidence" not in row:
    raise SystemExit("V129 serialized candidate metadata missing")

worker=Path("/app/web/ai_worker_server.py").read_text(encoding="utf-8")
for marker in (
    "from auto_highlights.engine_v129 import analysis_to_candidates, candidate_dict",
    'clean not in ("/prescan","/auto-highlights")',
    "def _build_auto_highlights(data):",
    "GSF_V129_AUTO_HIGHLIGHTS",
    '"rendered_media":[]',
    "auto-highlights/",
):
    if marker not in worker:
        raise SystemExit("V129 worker endpoint marker missing: "+marker)

compile(worker,"<v129-worker>","exec")
print("V129 Auto Highlights Game Brain contracts: PASS")
