#!/usr/bin/env python3
from pathlib import Path
import sys

home = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/home_v154_component/index.html")
embed = Path(sys.argv[2] if len(sys.argv) > 2 else "/app/web/home_v154_embed.py")


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


src = home.read_text(encoding="utf-8")
emb = embed.read_text(encoding="utf-8")
start = src.rfind("/* V294 HOME DESKTOP REALIGN */")
need(start >= 0, "V294 desktop realign marker exists")
end = src.find("/* END V294 HOME DESKTOP REALIGN */", start)
need(end > start, "V294 desktop realign block closes")
block = src[start:end]

need("@media (min-width:761px)" in block, "V294 is desktop-only")
need("max-width:760px" not in block and "max-width: 760px" not in block, "V294 does not touch mobile")
need("--gsf-desk-ring:clamp(204px,min(18.5vw,27vh),282px)!important" in block, "desktop uploader returns to compact calibrated size")
need("--gsf-desk-content:clamp(620px,59vw,790px)!important" in block, "desktop CTA row returns to balanced width")
need("--gsf-desk-card-h:clamp(110px,13.8vh,126px)!important" in block, "desktop CTA height returns to calibrated scale")
need("top:-9px!important" in block, "desktop uploader keeps V270 vertical calibration")
need("transform:translateY(-8px)!important" in block, "desktop CTA row remains lifted")
need("justify-content:center!important" in block, "CTA content is vertically centered again")
need("max-width:190px!important" in block, "CTA copy width is restored")
need("height:clamp(220px,35vh,310px)!important" in block, "desktop side ads return to balanced height")
need("width:clamp(190px,15.5vw,260px)!important" in block, "upper desktop murals return to balanced width")
need("font-size:clamp(20px,1.7vw,28px)!important" in block, "upper desktop murals return to balanced type scale")
need("width:clamp(235px,20vw,315px)!important" in block, "center desktop mural returns to balanced width")
need("gsf_home_v154_live_294" in emb, "Home component cache key is bumped to V294")
need("V279 DESKTOP MURALS + TALLER ADS" in src, "legacy V279 layer stays intact underneath the final V294 override")
print("V294 Home desktop realign: PASS")
