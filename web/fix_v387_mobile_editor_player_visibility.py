#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V387_MOBILE_EDITOR_PLAYER_VISIBILITY'

EDITOR_PATCH=r'''
<!-- V387_MOBILE_EDITOR_PLAYER_VISIBILITY -->
<style id="v387MobileEditorPlayerVisibility">
@media(max-width:760px){
  #ng27,#ng27.v326Mobile{
    --v387-player-w:min(60vw,236px);
    height:100%!important;min-height:0!important;
    padding:3px 10px 5px!important;overflow:hidden!important;
  }
  #ng27 .shell,#ng27.v326Mobile .shell{
    width:100%!important;height:100%!important;min-height:0!important;max-width:430px!important;
    margin:0 auto!important;padding:0!important;display:flex!important;flex-direction:column!important;
    align-items:stretch!important;justify-content:flex-start!important;overflow:hidden!important;
  }
  #ng27 .topline,#ng27.v326Mobile .topline{display:none!important}
  #ng27 .v387EditorTitleCard,#ng27.v326Mobile .v387EditorTitleCard{
    flex:0 0 58px!important;box-sizing:border-box!important;
    width:min(calc(100% - 66px),330px)!important;height:58px!important;min-height:58px!important;
    margin:0 auto 7px 10px!important;padding:9px 10px 9px 13px!important;
    display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;
    border-radius:18px!important;background:rgba(255,255,255,.97)!important;
    border:1px solid rgba(166,203,226,.34)!important;box-shadow:0 7px 20px rgba(65,110,151,.08)!important;
    color:#103A79!important;overflow:hidden!important;transition:none!important;animation:none!important;
  }
  #ng27 .v387EditorTitleText{min-width:0!important;display:flex!important;flex-direction:column!important;align-items:flex-start!important;justify-content:center!important}
  #ng27 .v387EditorTitleText strong{font-size:17px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important;color:#103A79!important}
  #ng27 .v387EditorTitleText span{display:block!important;max-width:218px!important;margin-top:4px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;font-size:7.8px!important;line-height:1.05!important;font-weight:750!important;color:#7183A3!important}
  #ng27 .v387HeaderFull{
    flex:0 0 auto!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:4px!important;
    width:62px!important;height:38px!important;min-width:62px!important;min-height:38px!important;padding:0 7px!important;
    border-radius:13px!important;border:1px solid rgba(154,190,219,.34)!important;background:#F7FBFF!important;color:#2B4F86!important;
    box-shadow:0 5px 14px rgba(64,104,143,.08)!important;font-size:8px!important;font-weight:950!important;
  }
  #ng27 .cockpit,#ng27.expanded .cockpit,#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    flex:0 0 auto!important;width:100%!important;height:auto!important;min-height:0!important;max-width:430px!important;
    margin:0 auto!important;padding:0!important;display:grid!important;grid-template-columns:1fr!important;
    grid-template-rows:auto 46px 94px!important;gap:8px!important;align-items:start!important;align-content:start!important;
    justify-items:center!important;overflow:visible!important;
  }
  /* V387_NONZERO_PLAYER_ROW: wrapper ratio sizes grid row from width; it can never become a zero-height flex remainder. */
  #ng27 .stageWrap,#ng27.v326Mobile .stageWrap{
    grid-row:1!important;grid-column:1!important;position:relative!important;
    width:var(--v387-player-w)!important;max-width:236px!important;height:auto!important;min-height:1px!important;aspect-ratio:9/16!important;
    margin:0!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important;
  }
  #ng27 .stage.r916,#ng27.expanded .stage.r916,#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{
    position:absolute!important;inset:0!important;width:100%!important;height:100%!important;min-height:100%!important;max-width:none!important;max-height:none!important;
    aspect-ratio:9/16!important;margin:0!important;border-radius:22px!important;overflow:hidden!important;
  }
  #ng27 .stage video,#ng27.v326Mobile .stage video{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;object-fit:cover!important}
  #ng27 .cockpit>.v323EditorActions,#ng27.v326Mobile .cockpit>.v323EditorActions{grid-row:2!important;grid-column:1!important}
  #ng27 .cockpit>.timeline,#ng27.v326Mobile .cockpit>.timeline{grid-row:3!important;grid-column:1!important}
  #ng27 .v387EditorTitleCard,#ng27 .stageWrap,#ng27 .stage,#ng27 video{transition:none!important;animation:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
}
</style>
<script id="v387MobileEditorPlayerVisibilityRuntime">
(()=>{
  const root=document.getElementById('ng27');if(!root)return;
  const shell=root.querySelector('.shell'),cockpit=root.querySelector('.cockpit');if(!shell||!cockpit)return;
  let card=shell.querySelector('.v387EditorTitleCard');
  if(!card){
    card=document.createElement('div');card.className='v387EditorTitleCard';
    card.innerHTML='<div class="v387EditorTitleText"><strong>Game Editor</strong><span>Il tuo gameplay resta nel progetto mentre modifichi.</span></div><button type="button" class="v387HeaderFull" aria-label="Schermo intero">↗ FULL</button>';
    shell.insertBefore(card,cockpit);
  }
  const headerFull=card.querySelector('.v387HeaderFull');
  if(headerFull&&!headerFull.dataset.wired){
    headerFull.dataset.wired='1';
    headerFull.addEventListener('click',()=>{const original=root.querySelector('#zoomEditorBtn');if(original)original.click()});
  }
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v387EditorIframeFill">
@media(max-width:760px){
  /* V387_EDITOR_IFRAME_FILL: this comes after the legacy V220 shell style so the iframe cannot collapse to CTA height. */
  body #gsf-editor-overlay-v220{flex-direction:column!important;overflow:hidden!important;min-height:0!important}
  body #gsf-editor-overlay-v220.is-open{display:flex!important}
  body #gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}
  body #gsf-editor-overlay-v220 iframe.gsf-editor-frame,
  body #gsf-editor-overlay-v220 iframe[title="Game Editor"]{
    display:block!important;position:relative!important;flex:1 1 0!important;
    width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
    margin:0!important;padding:0!important;border:0!important;background:transparent!important;
    transform:translateZ(0)!important;transition:none!important;animation:none!important;
  }
}
</style>
'''

def strip_editor(text:str)->str:
    return re.sub(r'\s*<!-- V387_MOBILE_EDITOR_PLAYER_VISIBILITY -->.*?<script id="v387MobileEditorPlayerVisibilityRuntime">.*?</script>\s*','\n',text,flags=re.S)

def strip_shell(text:str)->str:
    return re.sub(r'\s*<style id="v387EditorIframeFill">.*?</style>\s*','\n',text,flags=re.S)

def patch_editor(text:str)->str:
    text=strip_editor(text)
    if 'V386_MOBILE_EDITOR_REFERENCE_LOCK' not in text:
        raise RuntimeError('V387 requires V386 Editor reference lock first')
    if '</body>' not in text:
        raise RuntimeError('V387 Editor body anchor missing')
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    text=strip_shell(text)
    if 'V386_EDITOR_TITLE_CARD' not in text:
        raise RuntimeError('V387 requires V386 parent Editor shell first')
    pat=r'(<style id="gsf-v220-editor-shell">.*?</style>)'
    m=re.search(pat,text,flags=re.S)
    if not m:
        raise RuntimeError('V387 V220 shell style anchor missing')
    text=text[:m.end()]+SHELL_PATCH+text[m.end():]
    compile(text,'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py','exec')
    return text

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():
        raise SystemExit('V387 runtime files missing')
    eb=editor.read_text(encoding='utf-8');ea=patch_editor(eb);editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8');sa=patch_shell(sb);shell.write_text(sa,encoding='utf-8')
    print('V387 mobile Editor player visibility applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__':
    main()
