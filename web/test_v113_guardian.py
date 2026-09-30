from pathlib import Path
import json
import tempfile
import sys

sys.path.insert(0,"/app/web")
from guardian_v113 import inspect_and_repair_local, source_restore_plan

def write_json(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload),encoding="utf-8")

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);media=root/"media";media.mkdir(parents=True)
    (media/"gaming_short_finale_share.mp4").write_bytes(b"x"*4096)
    write_json(root/"render_job.json",{"status":"running","started_at":100.0,"pid":123})
    result=inspect_and_repair_local(root,now=120.0)
    healed=json.loads((root/"render_job.json").read_text())
    assert result["status"]=="ready" and healed["status"]=="ready"
    assert "job_from_final" in result["repairs"]

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);(root/"media").mkdir(parents=True)
    write_json(root/"render_job.json",{"status":"running","started_at":100.0,"pid":456})
    result=inspect_and_repair_local(root,now=1200.0,stale_after=900)
    assert result["status"]=="stale" and "render_stale" in result["repairs"]

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);(root/"media").mkdir(parents=True)
    write_json(root/"render_job.json",{"status":"ready","started_at":100.0})
    result=inspect_and_repair_local(root,now=200.0)
    assert result["needs_final_restore"] is True

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);media=root/"media";media.mkdir(parents=True)
    write_json(media/".direct_upload_ready.json",{
        "path":str(media/"missing_source.mp4"),
        "bucket_key":"uploads/session/upload/source.mp4",
    })
    result=inspect_and_repair_local(root,now=200.0)
    assert result["needs_source_restore"] is True

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);media=root/"media";media.mkdir(parents=True)
    marker=media/".direct_upload_ready.json"
    missing=media/"source_bucket_game_1234567890abcdef1234.mp4"
    write_json(marker,{
        "path":str(missing),
        "name":"game.mp4",
        "size":4096,
        "upload_id":"1234567890abcdef1234",
        "bucket_key":"uploads/session/1234567890abcdef1234/game.mp4",
        "analysis_key":"analysis/session/1234567890abcdef1234/v52-keyframe-turbo.json",
    })
    plan=source_restore_plan(root)
    assert plan["bucket_key"].endswith("/game.mp4")
    assert plan["upload_id"]=="1234567890abcdef1234"
    assert plan["size"]==4096
    missing.write_bytes(b"x"*4096)
    assert source_restore_plan(root)=={}

server=Path("/app/web/direct_upload_server.py").read_text(encoding="utf-8")
app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V113_GUARDIAN.py").read_text(encoding="utf-8")
for marker in (
    "from guardian_v113 import inspect_and_repair_local as _guardian_local",
    "def _guardian_tick(",
    'clean=="/guardian/status"',
    "_guardian_tick(sid)",
    "GSF_GUARDIAN_REPAIR",
    "final_from_bucket",
    "_guardian_restore_source_from_marker",
    "_guardian_source_plan",
    "source_from_bucket",
    "GSF_GUARDIAN_SOURCE_RESTORED",
):
    assert marker in server, marker
for marker in ("GSF_V113_GUARDIAN=True","V113 GSF GUARDIAN"):
    assert marker in app, marker
compile(server,"<direct_upload_server>","exec")
compile(app,"<v113>","exec")
print("V113 Guardian self-healing contract: PASS")
