from pathlib import Path
root=Path("/app")/"web"
files={
 "home":(root/"home_v154_component/index.html").read_text(encoding="utf-8"),
 "ai":(root/"ai_v221_component/index.html").read_text(encoding="utf-8"),
 "editor":(root/"editor_2027_component/index.html").read_text(encoding="utf-8"),
 "share":(root/"share_v156_component/index.html").read_text(encoding="utf-8"),
 "hub":(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
}
checks={
 "V267 present on all five surfaces":all("V267 GLOBAL DESKTOP POLISH" in v for v in files.values()),
 "Desktop-only contract":all("@media (min-width:761px)" in v[v.rfind("V267 GLOBAL DESKTOP POLISH")-80:] for v in files.values()),
 "Home mobile-proportion circle":'--gsf-desk-ring:clamp(228px,min(22vw,31vh),320px)!important' in files["home"],
 "Home short-laptop circle protection":'--gsf-desk-ring:clamp(212px,min(21vw,29vh),248px)!important' in files["home"],
 "Home circle colors untouched by V267":".rings{" not in files["home"][files["home"].rfind("/* V267 GLOBAL DESKTOP POLISH"):],
 "Home logo untouched":"brandOnly" not in files["home"][files["home"].rfind("/* V267 GLOBAL DESKTOP POLISH"):],
 "Home login untouched":"accountEntry" not in files["home"][files["home"].rfind("/* V267 GLOBAL DESKTOP POLISH"):],
 "AI desktop no page scroll":"#ai221{\n    overflow:hidden!important;" in files["ai"],
 "Share desktop no page scroll":"#share{\n    overflow:hidden!important;" in files["share"],
 "Hub desktop no page scroll":"#hub{\n    overflow:hidden!important;" in files["hub"],
 "Editor desktop no page scroll":"#ng27{\n    overflow:hidden!important;" in files["editor"],
 "Premium card motion":"cubic-bezier(.2,.8,.2,1)" in files["home"] and "cubic-bezier(.2,.8,.2,1)" in files["ai"] and "cubic-bezier(.2,.8,.2,1)" in files["share"],
 "Reduced motion protected":all("prefers-reduced-motion:reduce" in v[v.rfind("/* V267 GLOBAL DESKTOP POLISH"):] for v in files.values()),
}
for name,v in checks.items(): print(("PASS" if v else "FAIL")+": "+name)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V267 global desktop polish failed: "+", ".join(bad))

# User requested font unchanged: the additive V267 blocks must not introduce font-family.
for name,c in files.items():
    block=c[c.rfind("/* V267 GLOBAL DESKTOP POLISH"):]
    if "font-family" in block:
        raise SystemExit("V267 changed typography in "+name)
print("PASS: V267 typography untouched")
print("V267 global desktop polish: PASS")
