from pathlib import Path

src=Path("/app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py")
out=Path("/app/GamingShortsFactory_V127_LEARNING_RANKER.py")
s=src.read_text(encoding="utf-8")

s=s.replace(
    "Gaming Shorts Factory · V126 Creative Director",
    "Gaming Shorts Factory · V127 Learning Ranker",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V127 Learning Ranker applied:",out)
