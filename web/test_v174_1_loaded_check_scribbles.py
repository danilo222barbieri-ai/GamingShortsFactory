from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V174.1 layer exists":"V174.1 HAND-DRAWN CHECK + WIDER SCRIBBLES" in home,
 "Rigid text tick removed":'uploadIcon.textContent="✓"' not in home,
 "Loaded tick is SVG":'class="gsfLoadedCheckSvg"' in home,
 "Organic double stroke exists":"gsfCheckMain" in home and "gsfCheckGhost" in home,
 "Loaded mark is tilted":"rotate(-8deg)" in home,
 "Loaded mark draws on":"@keyframes gsfDrawLoadedCheck" in home,
 "Cloud returns on reset":'uploadIcon.classList.remove("loadedCheck")' in home,
 "Side notes are wider":"width:clamp(210px,23vw,340px)!important" in home,
 "Side notes use screen margins":"left:clamp(18px,2.3vw,44px)!important" in home and "right:clamp(18px,2.3vw,44px)!important" in home,
 "Side arrows enlarged":"width:clamp(78px,7.5vw,112px)!important" in home,
 "Pad sketch enlarged":"width:clamp(52px,5.4vw,76px)!important" in home,
 "Reduced motion respected":"prefers-reduced-motion:reduce" in home and "stroke-dashoffset:0!important" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V174.1 failed: "+", ".join(bad))
print("V174.1 hand-drawn check + wider scribbles: PASS")
