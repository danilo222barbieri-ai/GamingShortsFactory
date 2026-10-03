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
checks={
 "V268.1 on all five surfaces":all("V268.1 DESKTOP MASTER -> MOBILE PARITY" in x for x in b.values()),
 "Mobile parity contract":all("@media (max-width:760px)" in x for x in b.values()),
 "Home desktop material copied":"rgba(255,255,255,.93)" in b["home"] and "rgba(150,184,214,.23)" in b["home"],
 "Mobile Home fonts increased":"font-size:clamp(11.3px,3.05vw,12.2px)!important" in b["home"],
 "Mobile murals untouched":".scribble" not in b["home"] and "muralAmbient" not in b["home"],
 "Mobile ad policy untouched":".sideAd" not in b["home"],
 "Share murals untouched":"#mural" not in b["share"] and ".mural" not in b["share"],
 "No font family replacement":all("font-family" not in x for x in b.values()),
}
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V268.1 failed: "+", ".join(bad))
print("V268.1 desktop master to mobile parity: PASS")
