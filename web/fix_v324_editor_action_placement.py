#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V324_EDITOR_ACTION_PLACEMENT'
SCRIPT=r'''<script id="v324EditorActionPlacement">
/* V324_EDITOR_ACTION_PLACEMENT */
(function(){
  function place(){
    const root=document.getElementById('ng27');
    const stageWrap=root&&root.querySelector('.stageWrap');
    const actions=root&&root.querySelector('#v323EditorActions');
    if(!root||!stageWrap||!actions)return;
    if(actions.parentElement===stageWrap){
      stageWrap.insertAdjacentElement('afterend',actions);
    }
  }
  place();
  window.addEventListener('resize',place,{passive:true});
})();
</script>'''

def patch_text(text:str)->str:
    if MARK in text:
        return text
    for marker in ('id="ng27"','class="stageWrap"','id="v323EditorActions"'):
        if marker not in text:
            raise RuntimeError('V324 editor anchor missing: '+marker)
    if '</body>' not in text:
        raise RuntimeError('V324 editor </body> missing')
    return text.replace('</body>',SCRIPT+'\n</body>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/editor_2027_component/index.html')
    if not path.is_file():
        raise SystemExit('V324 editor target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V324 editor action placement applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
