from pathlib import Path
import subprocess,tempfile,sys

sys.path.insert(0,"/app/web")
from privacy_cleanup_v149 import cleanup_video,_mask_filters,scan_final_video

fake={
    "width":640,"height":360,"duration":3.0,
    "detections":[{"time":1.0,"boxes":[{
        "x":.10,"y":.12,"w":.42,"h":.12,
        "text":"test@example.com",
        "findings":[{"kind":"email","value":"test@example.com"}],
    }]}],
    "qr_frames":[],
    "publish_guard":"clear",
}
filters=_mask_filters(fake)
assert len(filters)==1 and "drawbox" in filters[0] and "between(t" in filters[0]

with tempfile.TemporaryDirectory() as td:
    td=Path(td); src=td/"src.mp4"; out=td/"clean.mp4"
    subprocess.run([
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=640x360:rate=24",
        "-f","lavfi","-i","sine=frequency=440:sample_rate=44100",
        "-t","3","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
        "-c:a","aac",str(src),
    ],check=True,timeout=60)
    result=cleanup_video(src,out,report=fake)
    assert result["ok"] and result["applied"] and result["mask_count"]==1
    assert out.is_file() and out.stat().st_size>1024
    report=scan_final_video(src,td/"scan")
    assert report["engine"]=="v149-privacy-cleanup"
    assert "publish_guard" in report and "mask_count" in report

if len(sys.argv)>1:
    app=Path(sys.argv[1]).read_text(encoding="utf-8")
    for marker in ("privacy_cleanup_v149","GSF_V149_PRIVACY","privacy_cleanup_v149.json"):
        assert marker in app,marker

print("V149 Privacy Cleanup: PASS")
