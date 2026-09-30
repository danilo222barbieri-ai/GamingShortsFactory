from pathlib import Path

src=Path("/app/GamingShortsFactory_V128_PROACTIVE_GUARDIAN.py")
out=Path("/app/GamingShortsFactory_V129_AUTO_HIGHLIGHTS.py")
s=src.read_text(encoding="utf-8")

s=s.replace(
    "Gaming Shorts Factory · V128 Proactive Guardian",
    "Gaming Shorts Factory · V129 Auto Highlights",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V129 Auto Highlights applied:",out)
