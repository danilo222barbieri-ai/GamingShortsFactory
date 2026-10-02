from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Two-ring reference layer exists":"V174.2 TWO-RING REFERENCE UPLOADER" in home,
 "Inner circle uses faded blue mint gradient":"rgba(111,196,244,.72)" in home and "rgba(119,226,194,.44)" in home,
 "Only one outer ring remains":".rings:after{" in home and "content:none!important" in home and "display:none!important" in home,
 "Outer ring is very soft":"rgba(111,206,249,.34)" in home and "rgba(111,232,193,.26)" in home,
 "Outer ring sits around main circle":"inset:-54px!important" in home,
 "Idle animation keeps outer ring alive":"gsfOuterRingAlive 5.8s" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V174.2 two-ring uploader failed: "+", ".join(bad))
print("V174.2 two-ring reference uploader: PASS")
