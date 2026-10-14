from pathlib import Path
root=Path("/app")/"web"
files={
 "home":(root/"home_v154_component/index.html").read_text(encoding="utf-8"),
 "ai":(root/"ai_v221_component/index.html").read_text(encoding="utf-8"),
 "editor":(root/"editor_2027_component/index.html").read_text(encoding="utf-8"),
 "share":(root/"share_v156_component/index.html").read_text(encoding="utf-8"),
 "hub":(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
}

def v267_block(content):
    start=content.rfind("/* V267 GLOBAL DESKTOP POLISH")
    if start < 0:
        return ""
    end=content.find("/* END V267 GLOBAL DESKTOP POLISH */", start)
    if end < 0:
        return content[start:]
    return content[start:end+len("/* END V267 GLOBAL DESKTOP POLISH */")]

blocks={name:v267_block(content) for name,content in files.items()}

# V404 replaces the AI selectors and uses a scrollable two-step flow.
# Legacy surfaces retain their original V267 regression coverage.
ai_v404 = '<main id="ai404">' in files["ai"]
legacy_blocks = {name: block for name, block in blocks.items() if name != "ai" or not ai_v404}
ai_style = files["ai"] if ai_v404 else blocks["ai"]
if ai_v404:
    import runpy
    runpy.run_path(str(root / "test_v404_crea_con_ia_simple.py"), run_name="__main__")

checks={
 "V267 present on legacy surfaces":all("V267 GLOBAL DESKTOP POLISH" in v for v in legacy_blocks.values()),
 "Desktop-only contract":all("@media (min-width:761px)" in v for v in legacy_blocks.values()),
 "Home mobile-proportion circle":'--gsf-desk-ring:clamp(228px,min(22vw,31vh),320px)!important' in blocks["home"],
 "Home short-laptop circle protection":'--gsf-desk-ring:clamp(212px,min(21vw,29vh),248px)!important' in blocks["home"],
 "Home circle colors untouched by V267":".rings{" not in blocks["home"],
 "Home logo untouched":"brandOnly" not in blocks["home"],
 "Home login untouched":"accountEntry" not in blocks["home"],
 "AI viewport contract": ('#ai404{width:100%;min-height:100vh' in ai_style and '.action-dock{position:fixed;' in ai_style) if ai_v404 else "#ai221{\n    overflow:hidden!important;" in blocks["ai"],
 "Share desktop no page scroll":"#share{\n    overflow:hidden!important;" in blocks["share"],
 "Hub desktop no page scroll":"#hub{\n    overflow:hidden!important;" in blocks["hub"],
 "Editor desktop no page scroll":"#ng27{\n    overflow:hidden!important;" in blocks["editor"],
 "Premium card motion":"cubic-bezier(.2,.8,.2,1)" in blocks["home"] and "cubic-bezier(.2,.8,.2,1)" in ai_style and "cubic-bezier(.2,.8,.2,1)" in blocks["share"],
 "Reduced motion protected":all("prefers-reduced-motion:reduce" in v for v in legacy_blocks.values()) and "prefers-reduced-motion:reduce" in ai_style,
}
for name,v in checks.items(): print(("PASS" if v else "FAIL")+": "+name)
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("V267 global desktop polish failed: "+", ".join(bad))

# User requested font unchanged: the additive V267 blocks must not introduce font-family.
for name,block in blocks.items():
    if "font-family" in block:
        raise SystemExit("V267 changed typography in "+name)
print("PASS: V267 typography untouched")
print("V267 global desktop polish: PASS")
