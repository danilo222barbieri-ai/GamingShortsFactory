from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
hub=(root/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
  "Home targets guaranteed Hub overlay":"gsf-creator-hub-live-v160" in home,
  "Hub can close guaranteed overlay":"gsf-creator-hub-live-v160" in hub,
  "Production shell owns guaranteed Hub":"gsf-creator-hub-live-v160" in apply,
  "Hub iframe is current V156 surface":'/creator-hub-v156/' in apply,
  "Hub has dissolve/scale shell":'transform:scale(.985)' in apply and '.is-open' in apply,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V160 Hub shell failed: "+", ".join(bad))
print("V160 guaranteed Creator Hub overlay: PASS")
