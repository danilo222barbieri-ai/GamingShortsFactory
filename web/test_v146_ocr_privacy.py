from pathlib import Path
import tempfile,sys

sys.path.insert(0,"/app/web")
from ocr_privacy_v146 import classify_sensitive,scan_frame,merge_provider_results
from PIL import Image,ImageDraw

f=classify_sensitive("mail test@example.com discord.gg/abc123 192.168.1.5")
k={x["kind"] for x in f}
assert "email" in k and "discord_invite" in k and "ip" in k

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/"frame.png"
    img=Image.new("RGB",(900,300),"white")
    d=ImageDraw.Draw(img)
    d.text((40,120),"test@example.com",fill="black")
    img.save(p)
    r=scan_frame(p)
    assert r["engine"]=="v146-ocr-privacy"
    assert "privacy_findings" in r
    merged=merge_provider_results([{"path":str(p),"labels":["high_action"]}],{"frames":[r]})
    assert merged and merged[0]["path"]==str(p)

print("V146 OCR Privacy Engine: PASS")
