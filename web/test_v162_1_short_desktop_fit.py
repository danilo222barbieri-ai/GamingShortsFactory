from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Desktop has no 600px floor":"min-height:600px" not in home.split("@media(max-width:760px)")[0],
 "Viewport JS can fit short laptops":"Math.max(430" in home and "available=Math.max(430" in home,
 "Short desktop fit exists":"V162.1 SHORT DESKTOP FIT" in home,
 "Short desktop threshold exists":"max-height:720px" in home,
 "Projects shrink on short screens":"grid-template-columns:78px 1fr" in home,
 "Bottom nav shrinks on short screens":".navItem svg{width:16px;height:16px}" in home,
 "Creator Hub crown removed":'content:"♛"' not in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V162.1 short desktop fit failed: "+", ".join(bad))
print("V162.1 short desktop fit contract: PASS")
