import sys
sys.path.insert(0,"/app/web")
from semantic_video_v114 import normalize_semantic_events, merge_semantic_events, choose_processing_mode, choose_input_method

if choose_processing_mode(45.0)!="static":
    raise SystemExit("V119 short video must use static processing")
if choose_processing_mode(299.9)!="static":
    raise SystemExit("V119 sub-5-minute video must use static processing")
if choose_processing_mode(300.0)!="agentic":
    raise SystemExit("V119 5-minute video must use agentic processing")
if choose_processing_mode(1800.0)!="agentic":
    raise SystemExit("V119 long video must use agentic processing")
print("V119 adaptive video processing policy: PASS")

if choose_input_method(10*1024*1024)!="inline":
    raise SystemExit("V119 small video must use inline input")
if choose_input_method(70*1024*1024)!="files":
    raise SystemExit("V119 large video must use Files API")
print("V119 adaptive video input policy: PASS")

raw={"events":[
 {"timestamp_seconds":10.2,"event":"multi_kill","category":"action","confidence":0.95,"excitement":0.98,"reaction":0.55,"reason":"three enemies eliminated","subject":"player","focus_x_percent":61,"focus_y_percent":44,"focus_confidence":0.91,"hud_elements":["killfeed","minimap"],"caption_safe_y_percent":80},
 {"timestamp_seconds":10.9,"event":"kill","category":"action","confidence":0.70,"excitement":0.72,"reaction":0.30,"reason":"duplicate nearby","subject":"player","focus_x_percent":60,"focus_y_percent":45,"focus_confidence":0.70,"hud_elements":["killfeed"],"caption_safe_y_percent":80},
 {"timestamp_seconds":48.0,"event":"reaction","category":"reaction","confidence":0.91,"excitement":0.80,"reaction":0.99,"reason":"strong vocal reaction","subject":"facecam","focus_x_percent":84,"focus_y_percent":76,"focus_confidence":0.86,"hud_elements":["facecam"],"caption_safe_y_percent":22}
]}
events=normalize_semantic_events(raw,max_events=12)
if len(events)!=2:
    raise SystemExit("V114 cloud event dedupe failed: "+repr(events))
base=[{"time":10.0,"kind":"ACTION","score":0.70},{"time":48.3,"kind":"AUDIO","score":0.60}]
merged=merge_semantic_events(base,events,max_events=24)
if len(merged)!=2:
    raise SystemExit("V114 merge count failed: "+repr(merged))
if merged[0].get("semantic")!="multi_kill" or merged[1].get("semantic")!="reaction":
    raise SystemExit("V114 semantic annotation failed: "+repr(merged))
if merged[0].get("source")!="local+gemini-v117":
    raise SystemExit("V117 local/cloud fusion marker missing")
if merged[0].get("focus_x")!=61.0 or merged[0].get("focus_y")!=44.0:
    raise SystemExit("V117 semantic focus coordinates missing")
if merged[0].get("hud_elements")!=["killfeed","minimap"]:
    raise SystemExit("V117 semantic HUD metadata missing")
if merged[1].get("caption_safe_y")!=22.0 or merged[1].get("subject")!="facecam":
    raise SystemExit("V117 Editor framing metadata missing")
print("V117 semantic video + Editor metadata fusion: PASS")

from pathlib import Path
worker=Path("/app/web/ai_worker_server.py").read_text(encoding="utf-8")
requirements=Path("/app/web/requirements-worker.txt").read_text(encoding="utf-8")
for marker in (
    "analyze_gameplay_video",
    "merge_semantic_events",
    "semantic_events_v114",
    "semantic_video_v114",
    "semantic_video",
    "GSF_V114_SEMANTIC",
):
    if marker not in worker:
        raise SystemExit("V114 worker integration missing: "+marker)
if "google-genai==" not in requirements:
    raise SystemExit("V114 google-genai worker dependency missing")
print("V114 worker semantic integration: PASS")

semantic=Path("/app/web/semantic_video_v114.py").read_text(encoding="utf-8")
for marker in (
    "choose_processing_mode",
    "_probe_duration_seconds",
    "choose_input_method",
    "_inline_video_content",
    "_response_format",
    "_direct_semantic_interaction",
    '"processing":processing_mode',
    '"stream":True',
    'event_type=="step.delta"',
    'getattr(event.delta,"type",None)=="text"',
    "json_parts.append",
    'processing_mode=="agentic"',
    '"static"',
    "focus_x_percent",
    "hud_elements",
    "caption_safe_y_percent",
    "focus_confidence",
):
    if marker not in semantic:
        raise SystemExit("V120 semantic stream marker missing: "+marker)
if "background=True" in semantic:
    raise SystemExit("V120 must not use background multimodal interactions")
for marker in (
    "def _response_format(max_events):",
    '"mime_type":"application/json"',
    '"schema":_schema(max_events)',
    'direct_mode=(processing_mode=="static" and input_method=="inline")',
    'if processing_mode=="agentic":',
    'kwargs["response_format"]=_response_format(max_events)',
    '"-direct-v120" if direct_mode else "-stream-v120"',
):
    if marker not in semantic:
        raise SystemExit("V120 direct/stream compatibility marker missing: "+marker)
inline_start=semantic.find("def _inline_video_content")
inline_end=semantic.find("def _response_format",inline_start)
inline_block=semantic[inline_start:inline_end]
if 'payload["processing"]="agentic"' not in inline_block:
    raise SystemExit("V120 inline helper must add processing only for agentic mode")
if '"processing":processing_mode' in inline_block:
    raise SystemExit("V120 static inline request must rely on documented default processing")
print("V120 documented direct-inline + agentic-stream compatibility: PASS")

for marker in (
    "def _generate_content_semantic(",
    "client.models.generate_content(",
    "types.Content(",
    "types.Part(",
    "inline_data=types.Blob(",
    "video_metadata=types.VideoMetadata(",
    '"response_format":{"text":{"mime_type":"application/json","schema":_schema(max_events)}}',
    'processing_mode=="static"',
    '"generate-v121"',
    '"agentic-stream-v121"',
):
    if marker not in semantic:
        raise SystemExit("V121 native Generate Content video marker missing: "+marker)
print("V121 native video Generate Content + long agentic split: PASS")
