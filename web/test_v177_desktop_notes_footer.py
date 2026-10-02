from pathlib import Path
import re
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
embed=(root/"web/home_v154_embed.py").read_text(encoding="utf-8")
m=re.search(r"gsf_home_v154_live_([0-9]+)",embed)
version=int(m.group(1)) if m else 0
checks={
 "V177 layer exists":"V177 DESKTOP TARGETED NOTES + TRUE FOOTER" in home,
 "Desktop grid has explicit nav/footer tracks":"grid-template-rows:minmax(0,47fr) minmax(0,34fr) minmax(58px,13fr) minmax(32px,6fr)" in home,
 "Gamebar explicitly row 3":"grid-row:3!important" in home,
 "Footer explicitly row 4":"grid-row:4!important" in home,
 "Footer separated by border":"border-top:1px solid rgba(146,183,214,.24)!important" in home,
 "Footer social centered":"justify-self:center!important" in home and ".footerSocial{" in home,
 "Left note anchors toward uploader":"grid-area:left!important" in home and "justify-self:end!important" in home,
 "Right note anchors toward uploader":"grid-area:right!important" in home and "justify-self:start!important" in home,
 "Arrows are pinned to inner note edges":"right:clamp(-58px,-3.5vw,-38px)!important" in home and "left:clamp(-58px,-3.5vw,-38px)!important" in home,
 "Notes can expand outward":"width:clamp(230px,22vw,360px)!important" in home,
 "Fresh component cache bust":version>=177,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V177 desktop notes/footer failed: "+", ".join(bad))
print("V177 desktop targeted notes + true footer: PASS")
