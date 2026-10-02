from pathlib import Path
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Outer rebalance layer exists":"V174.5 OUTER PROPORTION REBALANCE" in home,
 "Hero/cards are balanced":"47fr" in home and "34fr" in home,
 "Uploader outer size reduced":"--gsf-hero-size:clamp(260px,min(26vw,37vh),325px)!important" in home,
 "Three rings retained":"inset:-25px!important" in home and "inset:-46px!important" in home,
 "Internal loaded check retained":"gsfLoadedCheckSvg" in home,
 "Internal upload label transition retained":'uploadLabel.textContent="CARICAMENTO"' in home,
 "Short screens remain balanced":"--gsf-hero-size:clamp(235px,min(25vw,35vh),285px)!important" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V174.5 outer proportion rebalance failed: "+", ".join(bad))
print("V174.5 outer proportion rebalance: PASS")
