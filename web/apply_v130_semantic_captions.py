from pathlib import Path

src=Path("/app/GamingShortsFactory_V129_AUTO_HIGHLIGHTS.py")
out=Path("/app/GamingShortsFactory_V130_SEMANTIC_CAPTIONS.py")
s=src.read_text(encoding="utf-8")

s=s.replace(
    "Gaming Shorts Factory · V129 Auto Highlights",
    "Gaming Shorts Factory · V130 Semantic Captions",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V130 Semantic Captions applied:",out)
