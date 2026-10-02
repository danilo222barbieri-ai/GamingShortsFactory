from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
 "Mega responsive override exists":"V166 MEGA RESPONSIVE HOME" in home,
 "Home is full viewport not 16:9 poster":"aspect-ratio:auto!important" in home and "width:100%!important;height:100%!important" in home,
 "Canonical parent shell fills browser":"V166 CANONICAL FLUID HOME SHELL" in apply and "width:100vw !important" in apply and "height:100dvh !important" in apply,
 "Production Streamlit gap cleanup exists":"V166.1 REAL VIEWPORT CLEANUP" in apply and "row-gap:0 !important" in apply,
 "Runtime collapses dead parent spacers":"normalizeParentHomeShell" in home and "safeToCollapse" in home and "previousElementSibling" in home,
 "Runtime rechecks parent spacers":"collapseParentHomeSpacers" in home,
 "No top lift survives final shell":"transform:none !important" in apply and "margin:0 !important" in apply,
 "Hero is real responsive grid":'grid-template-areas:"left center right"!important' in home,
 "Hero has readable adaptive uploader":"--gsf-hero-size:clamp(250px,min(28vw,40vh),390px)" in home,
 "CTA row gets substantial responsive height":"grid-template-rows:42% 26% 4% 12% 9% 3%!important" in home,
 "CTA cards are fluid thirds":"grid-template-columns:repeat(3,minmax(0,1fr))!important" in home,
 "Projects remain visible and fluid":".projects{" in home and "display:grid!important;width:100%!important;height:100%!important" in home,
 "Navigation uses active dot":".navItem.active:after" in home,
 "Navigation remains five-item":"<nav class=\"bottomNav\"" in home and home.count('class=\"navItem') >= 5,
 "Reference project metadata present":"3 short · 12 min fa" in home and "1 short · 1 giorno fa" in home and "2 short · 2 giorni fa" in home,
 "Runtime follows real viewport":"visualViewport.addEventListener" in home and "window.parent.addEventListener" in home,
 "Exact available height drives iframe":"const target=Math.max(430,Math.floor(available))" in home and 'shell.frame.style.setProperty("height",target+"px","important")' in home,
 "Approved V164 palette retained":"#d9efff" in home and "#dcf8e9" in home and "#fff1b6" in home,
 "Mobile remains independent":"@media(max-width:760px)" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V166 mega responsive Home failed: "+", ".join(bad))
print("V166 mega responsive Home contract: PASS")
