from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
embed=(root/"web/home_v154_embed.py").read_text(encoding="utf-8")
checks={
 "V178 geometry exists":"V178 REFERENCE-LOCKED NOTES + BOTTOM FOOTER" in home,
 "Notes are keyed to uploader diameter":"var(--gsf-hero-size) / 2" in home,
 "Left note hugs uploader":"right:calc(50% + (var(--gsf-hero-size) / 2)" in home,
 "Right note hugs uploader":"left:calc(50% + (var(--gsf-hero-size) / 2)" in home,
 "Arrows are long enough to touch ring":"width:clamp(92px,7vw,126px)!important" in home,
 "Gamebar is pinned above footer":"bottom:54px!important" in home,
 "Footer is pinned to bottom":"bottom:0!important" in home and "height:44px!important" in home,
 "Footer socials remain visible":"footerSocialLink" in home and "width:26px!important" in home,
 "Fresh component name":("gsf_home_v154_live_178" in embed or "gsf_home_v154_live_179" in embed),
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V178 reference geometry failed: "+", ".join(bad))
print("V178 reference-locked notes + true bottom footer: PASS")
