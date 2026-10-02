from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V168 refinement exists":"V168 HOME NAV + SIDE ADS" in home,
 "Header is text only":'class="hub hubLegacy"' in home and ".hubLegacy{display:none!important}" in home and "GAMING SHORTS FACTORY" in home,
 "No graphic logo added":"<img" not in home.split('<div class="topbar">',1)[1].split("</div>",1)[0],
 "Reference light background restored":"linear-gradient(180deg,#FBFDFF 0%,#F7FBFF 44%,#F3FAFF 100%)" in home,
 "Uploader has clear blue mint split":"linear-gradient(90deg,#79D9FF 0%,#79D9FF 47%,#8BEBD0 53%,#75E7C2 100%)" in home,
 "Handwritten notes and pad share color":".scribble .arrow,.scribble .padSketch{color:#687FA7!important}" in home,
 "Navigation has Hub":"data-nav=\"hub\"" in home and "<span>Hub</span>" in home,
 "Navigation has My Shorts":"data-nav=\"shorts\"" in home and "<span>I miei Short</span>" in home,
 "Old AI nav removed":'data-nav="ai"' not in home,
 "Old Editor nav removed":'data-nav="editor"' not in home,
 "Navigation is compact and centered":"width:min(64%,760px)!important" in home and "min-width:560px!important" in home,
 "Two desktop ad rails exist":'id="gsfSideAdLeft"' in home and 'id="gsfSideAdRight"' in home,
 "Ads only appear on wide desktop":"@media (min-width:1450px) and (min-height:700px)" in home and ".sideAd{display:flex}" in home,
 "Ads disappear on mobile":".sideAd{display:none!important}" in home,
 "Hub nav opens Creator Hub":'if(nav==="hub")shellNav("hub")' in home,
 "Responsive V166 remains":"V166 MEGA RESPONSIVE HOME" in home,
 "Visual V167 remains":"V167 HOME VISUAL FINAL" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V168 Home nav/ads failed: "+", ".join(bad))
print("V168 Home nav + side ads contract: PASS")
