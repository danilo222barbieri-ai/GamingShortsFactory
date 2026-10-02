from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
embed=(root/"web/home_v154_embed.py").read_text(encoding="utf-8")
checks={
 "V179 mobile reset exists":"V179 MOBILE HARD RESET" in home,
 "Legacy <=430 note hiding is overridden":".scribble.left,\n .scribble.right{\n   display:block!important" in home,
 "Old project shelf hidden on mobile":".sectionHead,.projects,.momentShelf{display:none!important}" in home,
 "Mobile notes are visibly positioned":"top:92px!important" in home and "top:102px!important" in home,
 "Mobile arrows point inward":"right:-46px!important" in home and "left:-46px!important" in home,
 "Mobile gamebar is explicit":"height:62px!important" in home and "grid-template-columns:repeat(5,1fr)!important" in home,
 "Mobile footer is explicit":"min-height:86px!important" in home,
 "Mobile social SVGs are styled":".footerSocialLink svg{" in home,
 "Fresh mobile component":"gsf_home_v154_live_179" in embed,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V179 mobile hard reset failed: "+", ".join(bad))
print("V179 mobile hard reset: PASS")
