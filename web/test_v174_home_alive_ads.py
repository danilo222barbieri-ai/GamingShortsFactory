from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "V174 alive layer exists":"V174 HOME ALIVE + TALLER ADS" in home,
 "Legacy V154 marker preserved":"CARICA IL TUO GAMEPLAY" in home,
 "V172 visible uploader markup restored":'<strong id="uploadLabel">CARICA<br>IL TUO GAMEPLAY</strong>' in home,
 "Uploader breathes at idle":"@keyframes gsfUploaderBreathe" in home and ".rings:not(.uploading):not(.uploaded)" in home,
 "Outer rings breathe":"@keyframes gsfOuterRingAlive" in home,
 "Cloud floats":"@keyframes gsfCloudAlive" in home and ".circle:not(.loaded) .icon" in home,
 "CTA icons have staggered life":"@keyframes gsfIconAlive" in home and "animation-delay:-1.8s" in home and "animation-delay:-3.6s" in home,
 "CTA hover is interactive":".feature:hover,.feature:focus-visible" in home and "translateY(-5px)" in home,
 "Active nav breathes":"@keyframes gsfActiveNavAlive" in home,
 "Ads are taller":"height:clamp(275px,42vh,410px)!important" in home,
 "Ads are wider":"width:clamp(104px,8.4vw,136px)!important" in home,
 "Large desktops get larger ad rails":"min-width:1600px" in home and "height:clamp(340px,44vh,455px)!important" in home,
 "Reduced motion is respected":"prefers-reduced-motion:reduce" in home and "animation:none!important" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V174 Home alive/ads failed: "+", ".join(bad))
print("V174 Home alive + taller ads: PASS")
