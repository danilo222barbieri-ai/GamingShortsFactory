from pathlib import Path
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V177.2 social footer layer exists":"V177.2 VISIBLE SOCIAL FOOTER" in home,
 "Footer social cluster is absolutely centered":"left:50%!important" in home and "transform:translate(-50%,-50%)!important" in home,
 "Social buttons are visibly sized":"width:28px!important;height:28px!important" in home,
 "Facebook uses SVG":'aria-label="Facebook" title="Facebook"><svg' in home,
 "Instagram uses SVG":'aria-label="Instagram" title="Instagram"><svg' in home,
 "YouTube uses SVG":'aria-label="YouTube" title="YouTube"><svg' in home,
 "TikTok uses SVG":'aria-label="TikTok" title="TikTok"><svg' in home,
 "Twitch uses SVG":'aria-label="Twitch" title="Twitch"><svg' in home,
 "Footer remains its own track":"minmax(42px,7fr)" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V177.2 visible social footer failed: "+", ".join(bad))
print("V177.2 visible social footer: PASS")
