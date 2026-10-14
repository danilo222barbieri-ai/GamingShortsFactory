from pathlib import Path
root=Path("/app")/"web"
files={
 "home":(root/"home_v154_component/index.html").read_text(encoding="utf-8"),
 "ai":(root/"ai_v221_component/index.html").read_text(encoding="utf-8"),
 "hub":(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
 "editor":(root/"editor_2027_component/index.html").read_text(encoding="utf-8"),
 "share":(root/"share_v156_component/index.html").read_text(encoding="utf-8"),
}

def v268_block(content):
    start=content.rfind("/* V268 DESKTOP AESTHETIC CALIBRATION")
    if start < 0:
        return ""
    end=content.find("/* END V268 DESKTOP AESTHETIC CALIBRATION */",start)
    if end < 0:
        return content[start:]
    return content[start:end+len("/* END V268 DESKTOP AESTHETIC CALIBRATION */")]

blocks={name:v268_block(content) for name,content in files.items()}
ai_v404 = '<main id="ai404">' in files["ai"]
legacy_blocks = {name: block for name, block in blocks.items() if name != "ai" or not ai_v404}
home=blocks["home"]

checks={
 "V268 present on legacy surfaces":all("V268 DESKTOP AESTHETIC CALIBRATION" in x for x in legacy_blocks.values()),
 "Desktop circle reduced":"--gsf-desk-ring:clamp(204px,min(18.5vw,27vh),282px)!important" in home,
 "Desktop cards taller":"--gsf-desk-card-h:clamp(110px,13.8vh,126px)!important" in home,
 "Desktop cards lifted":"transform:translateY(-8px)!important" in home,
 "Circle palette untouched by V268":".rings{" not in home,
 "Logo untouched":"brandOnly" not in home,
 "Login untouched":"accountEntry" not in home,
}
if ai_v404:
    checks["V404 fluid AI typography"] = "font-size:clamp(29px,4vw,48px)" in files["ai"] and "font-size:clamp(13px,1.5vw,16px)" in files["ai"]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V268 failed: "+", ".join(bad))
print("V268 desktop aesthetic calibration: PASS")
