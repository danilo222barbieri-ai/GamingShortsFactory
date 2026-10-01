from pathlib import Path
import importlib.util
p=Path("/app/web/vision_consumers_v137.py")
spec=importlib.util.spec_from_file_location("v137",p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
e={"game":{"recognition":{"game":"fortnite"}},"frames":{"frames":[{"path":"a.jpg","time":1,"bytes":10},{"path":"b.jpg","time":2,"bytes":20}]}}
r=m.consume_vision_evidence(e,[{"path":"a.jpg","labels":["action"],"ocr":["discord notification"],"action_score":.9},{"path":"b.jpg","labels":["action"],"ocr":[],"action_score":.8,"sharpness":.9}])
assert r["publish_guard"]=="clear" or r["cleanup_recommended"]
assert r["cover_candidates"][0]["path"]=="b.jpg"
assert len(m.content_fingerprint(e))==64
print("V137 Vision Consumers: PASS")
