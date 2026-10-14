from pathlib import Path
import subprocess
import sys

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
ai_v404='id="ai404"' in files["ai"]
legacy_surfaces=("home","hub","editor","share") if ai_v404 else tuple(files)

if ai_v404:
    subprocess.run([sys.executable, str(root/"test_v404_crea_con_ia_simple.py")], check=True)

checks={
 "V268.1 on active legacy surfaces":all("V268.1 DESKTOP MASTER -> MOBILE PARITY" in b[name] for name in legacy_surfaces),
 "Mobile parity legacy contract":all("@media (max-width:760px)" in b[name] for name in legacy_surfaces),
 "Home desktop material copied":"rgba(255,255,255,.93)" in b["home"] and "rgba(150,184,214,.23)" in b["home"],
 "Mobile Home fonts increased":"font-size:clamp(11.3px,3.05vw,12.2px)!important" in b["home"],
 "Mobile murals untouched":".scribble" not in b["home"] and "muralAmbient" not in b["home"],
 "Mobile ad policy untouched":".sideAd" not in b["home"],
 "Share murals untouched":"#mural" not in b["share"] and ".mural" not in b["share"],
 "No font family replacement":all("font-family" not in b[name] for name in legacy_surfaces),
 "AI V404 responsive replacement":(("@media(max-width:700px)" in files["ai"] and "prefers-reduced-motion:reduce" in files["ai"]) if ai_v404 else ("V268.1 DESKTOP MASTER -> MOBILE PARITY" in b["ai"])),
}
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V268.1 failed: "+", ".join(bad))
print("V268.1 desktop master to mobile parity: PASS")
