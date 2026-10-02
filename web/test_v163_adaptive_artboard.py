from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Desktop artboard is 16:9":"aspect-ratio:16/9" in home,
 "Desktop artboard fits viewport":"width:min(100vw,calc(100dvh * 16 / 9))" in home and "height:min(100dvh,calc(100vw * 9 / 16))" in home,
 "No obsolete fixed desktop override":"min-height:600px" not in home.split("@media (max-width:760px)")[0],
 "Hero uses proportional grid":"grid-template-rows:45% 18% 18% 9% 6%" in home,
 "Three CTA cards stay proportional":".features{height:100%" in home,
 "Projects stay visible":"display:grid!important" in home and ".projects" in home,
 "Frame height derived from 16:9 artboard":"const artH=Math.min(vh,vw*9/16)" in home,
 "Desktop no forced 600 floor":"min-height:600px" not in home.split("@media (max-width:760px)")[0],
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V163 adaptive artboard failed: "+", ".join(bad))
print("V163 adaptive 16:9 desktop artboard: PASS")
