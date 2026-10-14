from pathlib import Path
import subprocess
import sys

root=Path("/app")/"web"
files={
 "home":(root/"home_v154_component/index.html").read_text(encoding="utf-8"),
 "ai":(root/"ai_v221_component/index.html").read_text(encoding="utf-8"),
 "editor":(root/"editor_2027_component/index.html").read_text(encoding="utf-8"),
 "share":(root/"share_v156_component/index.html").read_text(encoding="utf-8"),
 "hub":(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
}

def v267_block(content):
    start=content.rfind("/* V267 GLOBAL DESKTOP POLISH")
    if start < 0:
        return ""
    end=content.find("/* END V267 GLOBAL DESKTOP POLISH */", start)
    if end < 0:
        return content[start:]
    return content[start:end+len("/* END V267 GLOBAL DESKTOP POLISH */")]

blocks={name:v267_block(content) for name,content in files.items()}
ai_v404='id="ai404"' in files["ai"]
legacy_surfaces=("home","editor","share","hub") if ai_v404 else tuple(files)

if ai_v404:
    subprocess.run([sys.executable, str(root/"test_v404_crea_con_ia_simple.py")], check=True)

checks={
 "V267 present on active legacy surfaces":all("V267 GLOBAL DESKTOP POLISH" in blocks[name] for name in legacy_surfaces),
 "Desktop-only legacy contract":all("@media (min-width:761px)" in blocks[name] for name in legacy_surfaces),
 "Home mobile-proportion circle":'--gsf-desk-ring:clamp(228px,min(22vw,31vh),320px)!important' in blocks["home"],
 "Home short-laptop circle protection":'--gsf-desk-ring:clamp(212px,min(21vw,29vh),248px)!important' in blocks["home"],
 "Home circle colors untouched by V267":".rings{" not in blocks["home"],
 "Home logo untouched":"brandOnly" not in blocks["home"],
 "Home login untouched":"accountEntry" not in blocks["home"],
 "AI desktop no page scroll or V404 replacement contract":ai_v404 or "#ai221{\n    overflow:hidden!important;" in blocks["ai"],
 "Share desktop no page scroll":"#share{\n    overflow:hidden!important;" in blocks["share"],
 "Hub desktop no page scroll":"#hub{\n    overflow:hidden!important;" in blocks["hub"],
 "Editor desktop no page scroll":"#ng27{\n    overflow:hidden!important;" in blocks["editor"],
 "Premium card motion":("cubic-bezier(.2,.8,.2,1)" in blocks["home"] and "cubic-bezier(.2,.8,.2,1)" in blocks["share"] and (("cubic-bezier(.2,.8,.2,1)" in files["ai"]) if ai_v404 else ("cubic-bezier(.2,.8,.2,1)" in blocks["ai"]))),
 "Reduced motion protected":all("prefers-reduced-motion:reduce" in blocks[name] for name in legacy_surfaces) and (("prefers-reduced-motion:reduce" in files["ai"]) if ai_v404 else True),
}
for name,v in checks.items(): print(("PASS" if v else "FAIL")+": "+name)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V267 global desktop polish failed: "+", ".join(bad))

# User requested font unchanged: legacy V267 blocks must not introduce font-family.
for name in legacy_surfaces:
    if "font-family" in blocks[name]:
        raise SystemExit("V267 changed typography in "+name)
print("PASS: V267 typography untouched")
print("V267 global desktop polish: PASS")
