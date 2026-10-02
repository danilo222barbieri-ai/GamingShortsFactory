from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V169 reference pass exists":"V169 REFERENCE FIDELITY" in home,
 "Uploader is explicit half blue half mint":"#5CCBFF" in home and "#54DDA9" in home and "49.5%" in home and "50.5%" in home,
 "Pulse is preserved":".rings.uploading" in home and "gsfMintPulse" in home,
 "Reference CTA colors are explicit":"#1674E8" in home and "#079A67" in home and "#D98200" in home,
 "Gamebar is prominent":"min-height:clamp(78px,10.5vh,96px)!important" in home and "0 0 0 7px rgba(224,242,255,.48)" in home,
 "Gamebar icons are circular":".navItem svg{" in home and "border-radius:50%!important" in home and "box-sizing:content-box!important" in home,
 "Active destination pops out":"transform:translateY(-3px) scale(1.14)!important" in home,
 "Footer is below gamebar":"grid-template-rows:42% 39% 0 0 14% 5%!important" in home and ".siteFooter{" in home and "z-index:1!important" in home,
 "Ads show on standard desktop":"@media (min-width:1180px) and (min-height:600px)" in home and ".sideAd{display:flex!important}" in home,
 "Both ad rails still exist":'id="gsfSideAdLeft"' in home and 'id="gsfSideAdRight"' in home,
 "Header remains text only":".hubLegacy{display:none!important}" in home and "GAMING SHORTS FACTORY" in home,
 "Responsive foundation retained":"V166 MEGA RESPONSIVE HOME" in home,
 "V167 visual layer retained":"V167 HOME VISUAL FINAL" in home,
 "V168 nav layer retained":"V168 HOME NAV + SIDE ADS" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V169 reference fidelity failed: "+", ".join(bad))
print("V169 reference fidelity contract: PASS")
