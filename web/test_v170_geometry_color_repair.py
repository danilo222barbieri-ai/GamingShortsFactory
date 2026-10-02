from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V170 restore exists":"V170 GEOMETRY RESTORE + HARD REFERENCE COLORS" in home,
 "Approved positions restored":"grid-template-rows:43% 41% 0 0 12% 3%!important" in home,
 "Stage no longer narrowed by ads":".stage{width:100%!important}" in home,
 "CTA row restored to V167 width":"width:min(72vw,760px)!important" in home,
 "Gamebar no longer grows layout":"min-height:0!important" in home and "height:100%!important" in home,
 "Gamebar prominence is visual":"box-sizing:content-box!important" in home and "border-radius:50%!important" in home,
 "Footer stays in its own row":"padding:0 8px!important" in home and "z-index:1!important" in home,
 "Uploader split is vivid":"#34B8FF" in home and "#2ED291" in home and "49.6%" in home and "50.4%" in home,
 "CTA icon colors are vivid":"#1875E6" in home and "#078F61" in home and "#D68000" in home,
 "Ad rails remain absolute":"top:47%!important" in home and "transform:translateY(-50%)!important" in home,
 "Ads do not change stage width on desktop":"@media (min-width:1180px) and (min-height:600px)" in home and ".stage{width:100%!important}" in home,
 "Prior responsive foundation retained":"V166 MEGA RESPONSIVE HOME" in home and "V167 HOME VISUAL FINAL" in home and "V168 HOME NAV + SIDE ADS" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V170 geometry/color repair failed: "+", ".join(bad))
print("V170 geometry + color repair: PASS")
