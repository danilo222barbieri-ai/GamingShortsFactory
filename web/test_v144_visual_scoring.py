from pathlib import Path
import tempfile, sys
import numpy as np
from PIL import Image

sys.path.insert(0,"/app/web")
from visual_scoring_v144 import analyze_frame, enrich_frame_manifest, best_visual_frame

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    flat=np.full((108,192,3),120,dtype=np.uint8)
    checker=np.zeros((108,192,3),dtype=np.uint8)
    checker[::2,::2]=[255,80,20]
    checker[1::2,1::2]=[30,220,255]
    a=td/"flat.jpg"; b=td/"checker.jpg"
    Image.fromarray(flat).save(a,quality=92)
    Image.fromarray(checker).save(b,quality=92)
    fa=analyze_frame(a)
    fb=analyze_frame(b,previous=fa.pop("_array"))
    assert fb["sharpness"]>fa["sharpness"]
    manifest={"frames":[{"path":str(a),"time":1.0},{"path":str(b),"time":2.0}]}
    rows=enrich_frame_manifest(manifest)
    assert len(rows)==2
    best=best_visual_frame(manifest)
    assert best["path"] in (str(a),str(b))
    assert "visual_quality" in best and "action_score" in best

print("V144 Visual Scoring: PASS")
