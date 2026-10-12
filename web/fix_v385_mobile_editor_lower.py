#!/usr/bin/env python3
from pathlib import Path
import re,sys
MARK='V385_MOBILE_EDITOR_LOWER'
PATCH=r'''
<!-- V385_MOBILE_EDITOR_LOWER -->
<style id="v385MobileEditorLower">
@media(max-width:760px){
/* Lower the complete compact Editor composition as one block, closer to the Game Bar. */
#ng27.v326Mobile .shell{align-items:flex-end!important;padding-bottom:8px!important;box-sizing:border-box!important}
#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{align-content:end!important;margin-top:auto!important;margin-bottom:0!important}
}
</style>
'''
def strip(t):return re.sub(r'\s*<!-- V385_MOBILE_EDITOR_LOWER -->.*?</style>\s*','\n',t,flags=re.S)
def main():
 root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app');p=root/'web'/'editor_2027_component'/'index.html';t=strip(p.read_text(encoding='utf-8'))
 if 'V384_MOBILE_EDITOR_NO_SCROLL' not in t:raise RuntimeError('V385 requires V384')
 p.write_text(t.replace('</body>',PATCH+'\n</body>',1),encoding='utf-8');print('V385 mobile Editor lowered toward Game Bar',flush=True)
if __name__=='__main__':main()
