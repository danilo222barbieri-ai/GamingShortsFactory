from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
hub=(root/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8")
share=(root/"web/share_v156_component/index.html").read_text(encoding="utf-8")
editor=(root/"web/editor_2027_component/index.html").read_text(encoding="utf-8")
embed=(root/"web/home_v154_embed.py").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
 "Home targets 1920 desktop":"max-width:1920px" in home,
 "Home fills dynamic viewport":"height:100dvh" in home,
 "Home no 650/690 frame switch":"height(loaded?690:650)" not in home,
 "Home requests parent viewport":"function fitViewport()" in home and "window.parent.innerHeight" in home,
 "Hub fills viewport":"#hub{width:100%;height:100dvh" in hub and "max-width:1920px" in hub,
 "Hub old 650 removed":"#hub{height:650px" not in hub,
 "Share fills viewport":"#share{width:100%;height:100dvh" in share and "max-width:1920px" in share,
 "Share old 650 removed":"#share{height:650px" not in share,
 "Editor fills viewport":"height:100dvh" in editor and "max-width:1920px" in editor,
 "Editor requests parent viewport":"function fitEditorViewport()" in editor,
 "Home default iframe raised":"height=900" in embed,
 "Parent shell has V161 viewport contract":"V161 VIEWPORT CONTRACT" in apply,
 "Production Home no fixed 650/690":"height=690 if video is not None else 650" not in apply,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V161 viewport contract failed: "+", ".join(bad))
print("V161 1920x1080 adaptive viewport contract: PASS")
