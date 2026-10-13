#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V394_MOBILE_EDITOR_FOOTER_RESTORE'

EDITOR_PATCH=r'''
<!-- V394_MOBILE_EDITOR_FOOTER_RESTORE -->
<style id="v394MobileEditorFooterGap">
@media(max-width:760px){
  /* Keep the Editor composition, with an unmistakable gap above the global Game Bar. */
  #ng27 .v391EditorActions{margin-top:6px!important}
  #ng27 .v393ChangeShort{
    height:27px!important;min-height:27px!important;
    margin:5px auto 14px!important;
  }
}
</style>
'''

SHELL_PATCH=r'''
<style id="v394EditorFooterRestore">
@media(max-width:760px){
  html.v394EditorActive #gsf-global-footer{
    display:block!important;
    visibility:visible!important;
    opacity:1!important;
    pointer-events:auto!important;
  }
}
</style>
<script id="v394EditorFooterRestoreRuntime">
(()=>{
  const P=window.parent,D=P.document;if(!D||P.__GSF_V394_EDITOR_FOOTER_RESTORE)return;
  P.__GSF_V394_EDITOR_FOOTER_RESTORE=true;
  const host=()=>D.getElementById('gsf-editor-overlay-v220');
  const sync=()=>{
    const h=host();
    const active=!!(P.innerWidth<=760&&h&&h.classList.contains('is-open')&&h.getAttribute('aria-hidden')!=='true');
    D.documentElement.classList.toggle('v394EditorActive',active);
  };
  sync();
  [60,180,420,900,1600].forEach(ms=>P.setTimeout(sync,ms));
  const h=host();
  if(h){
    try{new MutationObserver(sync).observe(h,{attributes:true,attributeFilter:['class','aria-hidden'],childList:true,subtree:true})}catch(_e){}
  }
})();
</script>
'''

def patch_editor(text:str)->str:
    if MARK in text:return text
    for anchor in ('V393_MOBILE_EDITOR_CLEAN_TRANSPORT','v393ChangeShort','</body>'):
        if anchor not in text:raise RuntimeError('V394 Editor anchor missing: '+anchor)
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    if 'id="v394EditorFooterRestore"' in text:return text
    for anchor in ('gsf-global-footer','gsf-editor-overlay-v220','<style id="gsf-v220-editor-shell">'):
        if anchor not in text:raise RuntimeError('V394 shell anchor missing: '+anchor)
    anchor='<style id="gsf-v220-editor-shell">'
    return text.replace(anchor,SHELL_PATCH+'\n'+anchor,1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():raise SystemExit('V394 runtime files missing')
    eb=editor.read_text(encoding='utf-8');ea=patch_editor(eb);editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8');sa=patch_shell(sb);compile(sa,str(shell),'exec');shell.write_text(sa,encoding='utf-8')
    print('V394 mobile Editor footer visibility + Change Short gap applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__':main()
