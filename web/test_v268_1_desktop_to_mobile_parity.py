from pathlib import Path
root=Path("/app")/"web"
files={
 "home":(root/"home_v154_component/index.html").read_text(encoding="utf-8"),
 "ai":(root/"ai_v221_component/index.html").read_text(encoding="utf-8"),
 "hub":(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
 "editor":(root/"editor_2027_component/index.html").read_text(encoding="utf-8"),
 "share":(root/"share_v156_component/index.html").read_text(encoding="utf-8"),
}
def block(x):
    s=x.rfind("/* V268.1 DESKTOP MASTER -> MOBILE PARITY")
    if s<0:return ""
    e=x.find("/* END V268.1 DESKTOP MASTER -> MOBILE PARITY */",s)
    return x[s:e+len("/* END V268.1 DESKTOP MASTER -> MOBILE PARITY */")] if e>=0 else x[s:]
b={k:block(v) for k,v in files.items()}
ai_v404 = '<main id="ai404">' in files["ai"]
legacy_blocks = {name: value for name, value in b.items() if name != "ai" or not ai_v404}
checks={
 "V268.1 on legacy surfaces":all("V268.1 DESKTOP MASTER -> MOBILE PARITY" in x for x in legacy_blocks.values()),
 "Mobile parity contract":all("@media (max-width:760px)" in x for x in legacy_blocks.values()),
 "Home desktop material copied":"rgba(255,255,255,.93)" in b["home"] and "rgba(150,184,214,.23)" in b["home"],
 "Mobile Home fonts increased":"font-size:clamp(11.3px,3.05vw,12.2px)!important" in b["home"],
 "Mobile murals untouched":".scribble" not in b["home"] and "muralAmbient" not in b["home"],
 "Mobile ad policy untouched":".sideAd" not in b["home"],
 "Share murals untouched":"#mural" not in b["share"] and ".mural" not in b["share"],
 "No font family replacement":all("font-family" not in x for x in legacy_blocks.values()),
}
if ai_v404:
    checks["V404 mobile AI layout"] = "@media(max-width:700px)" in files["ai"] and ".engine-grid{grid-template-columns:1fr;" in files["ai"] and ".moments-grid{grid-template-columns:1fr 1fr;" in files["ai"]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V268.1 failed: "+", ".join(bad))
print("V268.1 desktop master to mobile parity: PASS")
