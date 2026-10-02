from pathlib import Path
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Mobile parity layer exists":"V176 MOBILE VISUAL PARITY" in home,
 "Mobile gets soft three rings":"width:clamp(224px,64vw,248px)!important" in home and "inset:-22px!important" in home and "inset:-40px!important" in home,
 "Mobile uploader breathes":"gsfUploaderBreathe 5.4s" in home and "gsfCloudAlive 4.4s" in home,
 "Mobile upload transition remains":"gsfLoadingWord 1.35s" in home and "circle.loaded strong" in home,
 "Mobile side notes are enlarged":"width:clamp(112px,32vw,138px)!important" in home,
 "Mobile notes point inward":"translateX(38px)" in home and "translateX(-38px)" in home,
 "Mobile cards use desktop palette":"#D8E9FF" in home and "#CFF4DD" in home and "#FFE9A8" in home,
 "Mobile gamebar is separate":"margin:4px 0 16px!important" in home,
 "Mobile footer is separate":"padding:14px 2px 4px!important" in home and "border-top:1px solid rgba(150,184,214,.22)!important" in home,
 "Mobile footer social links are visible":"width:28px!important" in home and ".footerSocialLink" in home,
 "Small phones are covered":"@media (max-width:380px)" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V176 mobile parity failed: "+", ".join(bad))
print("V176 mobile visual parity: PASS")
