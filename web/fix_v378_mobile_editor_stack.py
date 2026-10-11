#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V378_MOBILE_EDITOR_STACK'

PATCH=r'''
<!-- V378_MOBILE_EDITOR_STACK -->
<style id="v378MobileEditorStack">
@media(max-width:760px){
  /* Do not let the first cockpit row absorb all remaining viewport height.
     Keep the approved order tight: player -> actions -> timeline. */
  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    height:auto!important;min-height:0!important;
    grid-template-rows:auto 48px 92px!important;
    align-content:start!important;
  }
  #ng27.v326Mobile .stageWrap{align-self:start!important}
}
</style>
'''

def patch_text(text:str)->str:
    if MARK in text:
        return text
    if 'V376_MOBILE_EDITOR_REFERENCE' not in text:
        raise RuntimeError('V378 requires V376 mobile Editor reference')
    if 'V377_IOS_FLICKER_GUARD' not in text:
        raise RuntimeError('V378 requires V377 iOS flicker guard')
    if '</body>' not in text:
        raise RuntimeError('V378 Editor body anchor missing')
    return text.replace('</body>',PATCH+'\n</body>',1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    if not editor.is_file():
        raise SystemExit('V378 Editor target missing: '+str(editor))
    before=editor.read_text(encoding='utf-8')
    after=patch_text(before)
    editor.write_text(after,encoding='utf-8')
    print('V378 mobile Editor stack applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
