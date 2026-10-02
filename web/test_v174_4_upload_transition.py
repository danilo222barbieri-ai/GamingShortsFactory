from pathlib import Path
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Transition layer exists":"V174.4 UPLOAD LABEL TRANSITION" in home,
 "Initial upload copy remains":'CARICA<br>IL TUO GAMEPLAY' in home,
 "Upload shows CARICAMENTO":'uploadLabel.textContent="CARICAMENTO"' in home,
 "Loaded state clears text":'uploadLabel.innerHTML=""' in home,
 "Loaded state keeps hand-drawn check":'class="gsfLoadedCheckSvg"' in home,
 "Loaded label hidden":".circle.loaded strong{display:none!important}" in home,
 "Loading word breathes":"@keyframes gsfLoadingWord" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V174.4 upload transition failed: "+", ".join(bad))
print("V174.4 upload label transition: PASS")
