from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
 "Home computes exact remaining viewport":"getBoundingClientRect().top" in home and "const available=Math.max(430" in home and "window.parent.innerHeight" in home,
 "Home desktop document is overflow hidden":"overflow:hidden;scrollbar-width:none" in home,
 "Parent shell has zero-scroll contract":"V161.1 ZERO-SCROLL CONTRACT" in apply,
 "Streamlit main locked to 100dvh":"height:100dvh !important" in apply and "overflow:hidden !important" in apply,
 "Streamlit status chrome removed":'[data-testid="stStatusWidget"]' in apply,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V161.1 zero-scroll contract failed: "+", ".join(bad))
print("V161.1 desktop zero-scroll contract: PASS")
