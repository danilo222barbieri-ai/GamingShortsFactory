from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
 "Fluid responsive override exists":"V165 FLUID RESPONSIVE HOME" in home,
 "Desktop Home fills full width":"width:100%;height:100dvh" in home and "max-width:none;max-height:none;aspect-ratio:auto" in home,
 "Centered 16:9 artboard is neutralized":"body{display:block" in home and "transform:none" in home,
 "Hero is a responsive three-column grid":'grid-template-areas:"left center right"' in home,
 "Handwritten notes participate in the grid":".scribble.left{grid-area:left" in home and ".scribble.right{grid-area:right" in home,
 "Primary sections use fluid desktop width":"width:min(100%,1400px)" in home,
 "Desktop frame uses available height":"const target=Math.max(430,Math.floor(available))" in home,
 "Short-height desktop rules remain adaptive":"grid-template-rows:minmax(175px,1fr) 80px 20px 54px 42px 16px" in home,
 "Parent iframe has no desktop width cap":"V165 FLUID HOME SHELL" in apply and "max-width:none !important" in apply,
 "Approved visual reference remains":"V164 APPROVED HOME REFERENCE" in home and "#d9efff" in home and "#dcf8e9" in home and "#fff1b6" in home,
 "Mobile layout remains separate":"@media(max-width:760px)" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V165 fluid responsive Home failed: "+", ".join(bad))
print("V165 fluid responsive Home contract: PASS")
