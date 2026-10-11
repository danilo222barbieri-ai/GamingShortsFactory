#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V379_MOBILE_EDITOR_FINAL_COMPOSE'

EDITOR_PATCH=r'''
<!-- V379_MOBILE_EDITOR_FINAL_COMPOSE -->
<style id="v379MobileEditorFinalCompose">
.v379EditorTitle{display:none}
@media(max-width:760px){
  #ng27.v326Mobile{
    --v376-player-w:clamp(180px,50vw,200px)!important;
  }
  #ng27.v326Mobile .topline{
    display:flex!important;position:relative!important;box-sizing:border-box!important;
    width:calc(100% - 8px)!important;min-height:56px!important;height:56px!important;
    margin:0 auto 7px!important;padding:7px 8px 7px 12px!important;
    align-items:center!important;justify-content:space-between!important;gap:8px!important;
    border-radius:18px!important;background:rgba(255,255,255,.98)!important;
    border:1px solid rgba(166,203,226,.34)!important;
    box-shadow:0 7px 20px rgba(65,110,151,.08)!important;
    overflow:hidden!important;z-index:120!important;
    -webkit-backdrop-filter:none!important;backdrop-filter:none!important;
    transition:none!important;animation:none!important;
  }
  #ng27.v326Mobile .v379EditorTitle{
    display:flex!important;min-width:0!important;flex:1 1 auto!important;
    flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;
    color:#103A79!important;text-align:left!important;line-height:1!important;
  }
  #ng27.v326Mobile .v379EditorTitle strong{
    display:block!important;font-size:17px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important;
  }
  #ng27.v326Mobile .v379EditorTitle span{
    display:block!important;max-width:250px!important;margin-top:4px!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
    font-size:8px!important;line-height:1.05!important;font-weight:750!important;color:#7183A3!important;
  }
  #ng27.v326Mobile .topline #zoomEditorBtn{
    position:relative!important;top:auto!important;right:auto!important;left:auto!important;bottom:auto!important;
    flex:0 0 auto!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:5px!important;
    width:66px!important;min-width:66px!important;height:39px!important;min-height:39px!important;padding:0 8px!important;
    border-radius:13px!important;background:#F7FBFF!important;color:#2B4F86!important;
    border:1px solid rgba(154,190,219,.34)!important;box-shadow:0 5px 14px rgba(64,104,143,.08)!important;
    transition:none!important;animation:none!important;
  }
  #ng27.v326Mobile .topline #zoomEditorBtn .mobileHide{display:inline!important;font-size:8px!important;font-weight:900!important}
  #ng27.v326Mobile .topline #zoomEditorBtn .ico{width:15px!important;height:15px!important}
  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    grid-template-rows:auto 48px 92px!important;gap:7px!important;align-content:start!important;
  }
  #ng27.v326Mobile .cockpit>.timeline{
    overflow:visible!important;position:relative!important;z-index:5!important;
  }
  #ng27.v326Mobile .cockpit>.timeline .trimRow{position:relative!important;z-index:7!important;overflow:visible!important}
  #ng27.v326Mobile .cockpit>.timeline input[type="range"]{position:relative!important;z-index:8!important}
}
</style>
<script id="v379MobileEditorFinalComposeRuntime">
(()=>{
  const root=document.getElementById('ng27');
  if(!root)return;
  const top=root.querySelector('.topline');
  if(!top)return;
  if(!top.querySelector('.v379EditorTitle')){
    const title=document.createElement('div');
    title.className='v379EditorTitle';
    title.innerHTML='<strong>Game Editor</strong><span>Il tuo gameplay resta nel progetto mentre modifichi.</span>';
    top.insertBefore(title,top.firstChild);
  }
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v379EditorParentCleanup">
@media(max-width:760px){
  #gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}
}
</style>
<script id="V379_HIDE_DUPLICATE_FINAL_CTA">
(()=>{
  const root=document.getElementById('gsf-editor-overlay-v220');
  if(!root)return;
  const clean=()=>{
    root.querySelectorAll('button,a,[role="button"]').forEach((el)=>{
      const t=String(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();
      if(t.includes('HAI FINITO')&&t.includes('CREA IL TUO SHORT')){
        el.style.setProperty('display','none','important');
        el.setAttribute('data-v379-hidden-final-cta','1');
      }
    });
  };
  clean();
  try{new MutationObserver(clean).observe(root,{childList:true,subtree:true});}catch(_e){}
})();
</script>
'''

def patch_editor(text:str)->str:
    if MARK in text:return text
    if 'V378_MOBILE_EDITOR_STACK' not in text:
        raise RuntimeError('V379 requires V378 Editor stack first')
    if '</body>' not in text:
        raise RuntimeError('V379 editor body anchor missing')
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    if 'V379_HIDE_DUPLICATE_FINAL_CTA' in text:return text
    if 'v376EditorTitleCard' not in text:
        raise RuntimeError('V379 requires V376 parent Editor shell first')
    marker='<style id="gsf-v220-editor-shell">'
    if marker not in text:
        raise RuntimeError('V379 parent Editor shell anchor missing')
    out=text.replace(marker,SHELL_PATCH+'\n'+marker,1)
    compile(out,'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py','exec')
    return out

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():
        raise SystemExit('V379 runtime files missing')
    eb=editor.read_text(encoding='utf-8'); ea=patch_editor(eb); editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8'); sa=patch_shell(sb); shell.write_text(sa,encoding='utf-8')
    print('V379 mobile Editor final compose applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__': main()
