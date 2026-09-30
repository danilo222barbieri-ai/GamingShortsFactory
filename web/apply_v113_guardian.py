from pathlib import Path

src=Path("/app/GamingShortsFactory_V112_GAME_BRAIN.py")
out=Path("/app/GamingShortsFactory_V113_GUARDIAN.py")
s=src.read_text(encoding="utf-8")
marker=r"""
# ===== V113 GSF GUARDIAN =====
GSF_V113_GUARDIAN=True
# Operational self-healing runs in direct_upload_server.py.
# ===== /V113 GSF GUARDIAN =====
"""
s=s.rstrip()+"\n\n"+marker.lstrip()
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V113 Guardian app marker applied:",out)
