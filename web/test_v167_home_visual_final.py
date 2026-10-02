from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Visual final override exists":"V167 HOME VISUAL FINAL" in home,
 "Reference vivid palette present":"#2370E2" in home and "#C9F5DC" in home and "#FFEDAF" in home and "#79EAC8" in home,
 "Uploader keeps animated pulse":"@keyframes gsfMintPulse" in home and ".rings.uploading{animation:gsfMintPulse" in home,
 "Uploader becomes blue mint":"conic-gradient(from 210deg" in home and "--v167-ring-blue:#72D8FF" in home and "--v167-ring-mint:#79EAC8" in home,
 "Format helper visually removed":".circle small{display:none!important}" in home,
 "Projects visually removed without deleting DOM":".sectionHead,.projects{display:none!important}" in home and '<div class="projects">' in home,
 "Three CTA cards are tall centered cards":"width:min(72vw,760px)!important" in home and "grid-template-columns:repeat(3,minmax(180px,1fr))!important" in home,
 "AI card uses reference blue":"--v167-blue-bg:#D7E9FF" in home,
 "Editor card uses reference mint":"--v167-mint-bg:#C9F5DC" in home,
 "Short card uses reference yellow":"--v167-gold-bg:#FFEDAF" in home,
 "Short icon is play triangle":'M17 12.5 35 24 17 35.5Z' in home,
 "Bottom nav reference glass":"width:min(86%,980px)!important" in home and "border-radius:999px!important" in home,
 "V166 responsive structure retained":"V166 MEGA RESPONSIVE HOME" in home and 'grid-template-areas:"left center right"!important' in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V167 visual final failed: "+", ".join(bad))
print("V167 Home visual final contract: PASS")
