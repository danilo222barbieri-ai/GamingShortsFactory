from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V174.3 three-ring layer exists":"V174.3 THREE SOFT LIVING RINGS" in home,
 "Middle ring is restored":".rings:before{" in home and "inset:-30px!important" in home,
 "Outer third ring is restored":"content:\"\"!important" in home and "inset:-55px!important" in home,
 "Both outer rings are visible":"display:block!important" in home,
 "Blue mint palette remains soft":"rgba(109,195,244,.68)" in home and "rgba(113,229,192,.42)" in home,
 "Third ring is more faded":"rgba(110,205,249,.24)" in home and "rgba(106,231,191,.22)" in home,
 "Three-ring motion is independent":"@keyframes gsfSecondRingAlive" in home and "@keyframes gsfThirdRingAlive" in home,
 "Upload keeps third ring alive":".rings.uploading:after{" in home and "opacity:.86!important" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V174.3 three-ring uploader failed: "+", ".join(bad))
print("V174.3 three soft living rings: PASS")
