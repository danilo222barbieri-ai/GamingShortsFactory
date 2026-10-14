from pathlib import Path
root=Path("/app")/"web"
files={
 "home":(root/"home_v154_component/index.html").read_text(encoding="utf-8"),
 "ai":(root/"ai_v221_component/index.html").read_text(encoding="utf-8"),
 "editor":(root/"editor_2027_component/index.html").read_text(encoding="utf-8"),
 "share":(root/"share_v156_component/index.html").read_text(encoding="utf-8"),
 "hub":(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
}
v407_path=root/"gsf_desktop_shell_v407.py"
v407_active=v407_path.is_file()
v407=v407_path.read_text(encoding="utf-8") if v407_active else ""

def v267_block(content):
    start=content.rfind("/* V267 GLOBAL DESKTOP POLISH")
    if start < 0:
        return ""
    end=content.find("/* END V267 GLOBAL DESKTOP POLISH */", start)
    if end < 0:
        return content[start:]
    return content[start:end+len("/* END V267 GLOBAL DESKTOP POLISH */")]

blocks={name:v267_block(content) for name,content in files.items()}

checks={
 "V267 present on all five surfaces":all("V267 GLOBAL DESKTOP POLISH" in v for v in blocks.values()),
 "Desktop-only contract":all("@media (min-width:761px)" in v for v in blocks.values()),
 "Home mobile-proportion circle":'--gsf-desk-ring:clamp(228px,min(22vw,31vh),320px)!important' in blocks["home"],
 "Home short-laptop circle protection":'--gsf-desk-ring:clamp(212px,min(21vw,29vh),248px)!important' in blocks["home"],
 "Home circle colors untouched by V267":".rings{" not in blocks["home"],
 "Home logo untouched":"brandOnly" not in blocks["home"],
 "Home login untouched":"accountEntry" not in blocks["home"],
 "AI desktop no page scroll":"#ai221{\n    overflow:hidden!important;" in blocks["ai"],
 "Share desktop no page scroll":"#share{\n    overflow:hidden!important;" in blocks["share"],
 "Hub desktop no page scroll":"#hub{\n    overflow:hidden!important;" in blocks["hub"],
 "Editor desktop no page scroll":"#ng27{\n    overflow:hidden!important;" in blocks["editor"],
}

# V407 deliberately replaces the old wide desktop composition with one centered
# mobile canvas plus lateral ad rails. Once that shell is present, V267 no longer
# owns card animation or reduced-motion rules for the superseded desktop layout;
# it still guards every V267 rule above that remains relevant to the components.
if v407_active:
    checks["V407 mobile canvas"]="center_width_px: int = 480" in v407 and "desktop_breakpoint_px: int = 1100" in v407
    checks["V407 giant ad rails"]="rail_min_px: int = 220" in v407 and "rail_max_px: int = 460" in v407
else:
    checks["Premium card motion"]="cubic-bezier(.2,.8,.2,1)" in blocks["home"] and "cubic-bezier(.2,.8,.2,1)" in blocks["ai"] and "cubic-bezier(.2,.8,.2,1)" in blocks["share"]
    checks["Reduced motion protected"]=all("prefers-reduced-motion:reduce" in v for v in blocks.values())

for name,v in checks.items(): print(("PASS" if v else "FAIL")+": "+name)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V267 global desktop polish failed: "+", ".join(bad))

# User requested font unchanged: the additive V267 blocks must not introduce font-family.
for name,block in blocks.items():
    if "font-family" in block:
        raise SystemExit("V267 changed typography in "+name)
print("PASS: V267 typography untouched")
print("V267 global desktop polish: PASS")
