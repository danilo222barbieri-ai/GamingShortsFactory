from pathlib import Path
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V172 reference uploader exists":"V172 REFERENCE UPLOADER" in home,
 "Reference uploader size set":"--gsf-hero-size:clamp(292px,min(29vw,44vh),350px)!important" in home,
 "Two outer rings match reference":"inset:-29px!important" in home and "inset:-54px!important" in home,
 "Uploader is blue with subtle mint edge":"rgba(233,248,255,.96)" in home and "rgba(226,252,242,.94)" in home,
 "Visible copy has exactly two lines":"<strong id=\"uploadLabel\">CARICA<br>IL TUO GAMEPLAY</strong>" in home,
 "Visible formats removed":'<small id="uploadHint" aria-hidden="true"></small>' in home,
 "Loading label removed":'uploadLabel.textContent="Caricamento…"' not in home,
 "Legacy progress hidden":".status.show{display:none!important}" in home and ".track{display:none!important}" in home,
 "Errors still visible inside circle":".status.error{" in home and "bottom:14%!important" in home,
 "Pulse remains":"@keyframes gsfReferencePulse" in home and ".rings.uploading{animation:gsfReferencePulse" in home,
 "Legacy regression token retained":"MP4 · MOV · AVI<br>MAX 4 GB" in home,
 "V171 nav work retained":"V171 NAV CAPSULE + REFERENCE BACKGROUND" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V172 uploader fidelity failed: "+", ".join(bad))
print("V172 reference uploader: PASS")
