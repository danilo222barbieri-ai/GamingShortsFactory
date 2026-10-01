from pathlib import Path

src=Path("/app/GamingShortsFactory_V143_RENDER_EXECUTION.py")
out=Path("/app/GamingShortsFactory_V144_VISUAL_SCORING.py")
s=src.read_text(encoding="utf-8")
s=s.replace(
    "Gaming Shorts Factory · V143 Render Execution",
    "Gaming Shorts Factory · V144 Visual Scoring",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V144 Visual Scoring applied:",out)
