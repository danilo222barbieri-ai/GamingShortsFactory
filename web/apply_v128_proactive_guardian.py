from pathlib import Path

src=Path("/app/GamingShortsFactory_V127_LEARNING_RANKER.py")
out=Path("/app/GamingShortsFactory_V128_PROACTIVE_GUARDIAN.py")
s=src.read_text(encoding="utf-8")

s=s.replace(
    "Gaming Shorts Factory · V127 Learning Ranker",
    "Gaming Shorts Factory · V128 Proactive Guardian",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V128 Proactive Guardian applied:",out)
