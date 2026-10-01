from pathlib import Path
import importlib.util

p=Path("/app/web/frame_vision_v135.py")
assert p.exists()
spec=importlib.util.spec_from_file_location("frame_vision_v135",p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
times=m.sample_times(10,[{"start":5}],interval=2,max_frames=20)
assert 5.0 in times and 4.3 in times and 5.7 in times
assert times==sorted(times)
src=p.read_text(encoding="utf-8")
for marker in ("extract_frames","build_frame_manifest","ffmpeg","game_recognition","cover_selection","privacy_ocr"):
    assert marker in src, marker
print("V135 Frame Vision contracts: PASS")
