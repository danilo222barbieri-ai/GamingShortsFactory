import sys
sys.path.insert(0,"/app/web")
from semantic_video_v114 import normalize_semantic_events, merge_semantic_events

raw={"events":[
 {"timestamp_seconds":10.2,"event":"multi_kill","category":"action","confidence":0.95,"excitement":0.98,"reaction":0.55,"reason":"three enemies eliminated"},
 {"timestamp_seconds":10.9,"event":"kill","category":"action","confidence":0.70,"excitement":0.72,"reaction":0.30,"reason":"duplicate nearby"},
 {"timestamp_seconds":48.0,"event":"reaction","category":"reaction","confidence":0.91,"excitement":0.80,"reaction":0.99,"reason":"strong vocal reaction"}
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
if merged[0].get("source")!="local+gemini-v114":
    raise SystemExit("V114 local/cloud fusion marker missing")
print("V114 semantic video fusion: PASS")
