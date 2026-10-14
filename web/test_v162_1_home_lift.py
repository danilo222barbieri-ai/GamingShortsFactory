from pathlib import Path

root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")

# V162.1 originally protected a raised, zero-scroll desktop Home. The exact
# historical pixel values and version comments were superseded/normalized by
# later adaptive passes. Keep testing the final behavior, not retired labels.
checks={
 "Desktop Home remains viewport bounded":"height:100dvh" in home and "overflow:hidden" in home,
 "Modern adaptive top spacing active":"padding:clamp(12px,1.5vh,20px)" in home,
 "Topbar remains compact flex shell":".topbar{display:flex;align-items:center;justify-content:space-between" in home,
 "Upload stage remains centered":".stage{position:relative;min-height:260px;display:flex;align-items:center;justify-content:center}" in home,
 "Feature row remains raised/compact":".features{flex:0 0 auto;display:grid" in home and "margin:-2px 4px" in home,
 "Navigation stack remains compact":".bottomNav{flex:0 0 auto;display:grid" in home,
 "Responsive Home fallback retained":"@media(max-width:760px)" in home and "min-height:100dvh" in home,
 "Parent iframe container lifted":"V162.1 HOME LIFT" in apply and "margin-top:-8px" in apply,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V162.1 modern Home lift failed: "+", ".join(bad))
print("V162.1 modern raised desktop Home contract: PASS")
