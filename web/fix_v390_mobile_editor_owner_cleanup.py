#!/usr/bin/env python3
from pathlib import Path
import re,sys

MARK='V390_MOBILE_EDITOR_OWNER_CLEANUP'
STYLE_IDS=[
 'v323MobileEditorPlayerActions','v325MobileEditorViewportFit','v326MobileEditorExact',
 'v360MobileEditorReference','v376MobileEditorReference','v378MobileEditorStack',
 'v379MobileEditorFinalCompose'
]
SCRIPT_IDS=[
 'v324EditorActionPlacement','v325MobileEditorReferenceLayout','v326MobileEditorRuntime',
 'v376MobileEditorReferenceRuntime','v379MobileEditorFinalComposeRuntime'
]
TOKENS=[
 'id="v323MobileEditorPlayerActions"','id="v324EditorActionPlacement"',
 'id="v325MobileEditorViewportFit"','id="v325MobileEditorReferenceLayout"',
 'id="v326MobileEditorExact"','id="v326MobileEditorRuntime"',
 'id="v360MobileEditorReference"','id="v376MobileEditorReference"',
 'id="v376MobileEditorReferenceRuntime"','id="v378MobileEditorStack"',
 'id="v379MobileEditorFinalCompose"','id="v379MobileEditorFinalComposeRuntime"',
 'V323 MOBILE EDITOR PLAYER ACTIONS','v323PlaceFullscreen'
]

def strip_tag(text:str,tag:str,sid:str)->str:
    pat=(r'\s*<'+tag+r'\b(?=[^>]*\bid\s*=\s*["\']'+re.escape(sid)+
         r'["\'])[^>]*>.*?</'+tag+r'>\s*')
    return re.sub(pat,'\n',text,flags=re.S|re.I)

def clean(text:str)->str:
    for sid in STYLE_IDS:text=strip_tag(text,'style',sid)
    for sid in SCRIPT_IDS:text=strip_tag(text,'script',sid)
    text=re.sub(r'\s*<div\b(?=[^>]*\bid\s*=\s*["\']v323EditorActions["\'])[^>]*>.*?</div>\s*','\n',text,count=1,flags=re.S|re.I)
    # V323 is injected directly into the base Editor script, so it has no script id.
    # Remove it by its stable marker and the original Done-handler boundary instead
    # of depending on its resize line, which later migrations can rewrite.
    text=re.sub(
        r'\s*/\*\s*V323 MOBILE EDITOR PLAYER ACTIONS\s*\*/.*?(?=\s*root\.querySelector\(["\']#doneBtn["\']\)\.onclick)',
        '\n',text,count=1,flags=re.S|re.I)
    # Recovery for a previously partially-cleaned V323 block where the marker was
    # removed but the function survived.
    if 'v323PlaceFullscreen' in text:
        text=re.sub(
            r'\s*const\s+v323CreateShort\s*=.*?(?=\s*root\.querySelector\(["\']#doneBtn["\']\)\.onclick)',
            '\n',text,count=1,flags=re.S|re.I)
    return text

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    path=root/'web'/'editor_2027_component'/'index.html'
    if not path.is_file():raise SystemExit('V390 Editor target missing: '+str(path))
    before=path.read_text(encoding='utf-8');after=clean(before)
    leftovers=[x for x in TOKENS if x in after]
    if leftovers:raise RuntimeError('V390 residual legacy Editor owners: '+', '.join(leftovers))
    if 'V389_MOBILE_EDITOR_BOUNDED_RESET' not in after:raise RuntimeError('V390 requires V389 Editor owner first')
    if MARK not in after:
        after=after.replace('</body>','<!-- '+MARK+' -->\n</body>',1)
    path.write_text(after,encoding='utf-8')
    print('V390 residual mobile Editor owners retired changed=',before!=after,flush=True)

if __name__=='__main__':main()
