from pathlib import Path
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V175 geometry exists":"V175 BALANCED ADAPTIVE GEOMETRY" in home,
 "Hero and cards have balanced rows":"49fr" in home and "33fr" in home,
 "Uploader remains adaptive":"--v175-ring:clamp(230px,min(23vw,38vh),340px)" in home,
 "Notes use outer margins":"justify-self:start!important" in home and "justify-self:end!important" in home,
 "Notes expand outward":"margin-left:clamp(10px,4.2vw,82px)" in home and "margin-right:clamp(10px,4.2vw,82px)" in home,
 "Cards regain vertical space":"height:88%!important" in home and "width:min(58vw,820px)!important" in home,
 "Short laptop has dedicated geometry":"max-height:650px" in home and "--v175-ring:clamp(205px" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V175 adaptive geometry failed: "+", ".join(bad))
print("V175 balanced adaptive geometry: PASS")
