from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
 "Desktop Home top padding removed":"#home154{padding:0 clamp(28px,4vw,70px) 4px" in home,
 "Desktop Home content lifted":"transform:translateY(-6px)" in home,
 "Topbar compacted":"height:40px;min-height:40px" in home,
 "Upload stage lifted":"max-height:320px;margin-top:-4px" in home,
 "Feature row lifted":"margin:-6px auto 6px" in home,
 "Project/nav stack tightened":"margin:0 auto 6px" in home and "margin:-1px auto 0" in home,
 "Parent iframe container lifted":"V162.1 HOME LIFT" in apply and "margin-top:-8px" in apply,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V162.1 Home lift failed: "+", ".join(bad))
print("V162.1 raised desktop Home contract: PASS")
