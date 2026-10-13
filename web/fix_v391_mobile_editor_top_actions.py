#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V391_MOBILE_EDITOR_TOP_ACTIONS'
STYLE=r'''
<!-- V391_MOBILE_EDITOR_TOP_ACTIONS -->
<style id="v391MobileEditorTopActions">
@media(max-width:760px){
  /* V391: normal mobile mode starts close to the global header instead of vertical centering. */
  #ng27 .shell{align-items:center!important;justify-content:flex-start!important;padding-top:18px!important}
  #ng27 .cockpit,#ng27.expanded .cockpit{flex-direction:column!important;align-items:center!important;justify-content:flex-start!important;gap:10px!important;padding-top:0!important}
  #ng27 .stageWrap{margin:0 auto!important;flex:0 0 auto!important}
  #ng27 .v391EditorActions{position:relative!important;z-index:176!important;width:var(--v389-player-w)!important;max-width:calc(100% - 20px)!important;margin:10px auto 0!important;padding:0!important;display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:8px!important;flex:0 0 auto!important}
  #ng27 .v391EditorAction{width:100%!important;min-width:0!important;height:44px!important;min-height:44px!important;margin:0!important;padding:0 8px!important;border-radius:15px!important;border:1px solid rgba(122,174,220,.30)!important;font-size:8.6px!important;line-height:1!important;font-weight:950!important;letter-spacing:.01em!important;white-space:nowrap!important;box-shadow:0 7px 17px rgba(49,91,132,.10)!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important}
  #ng27 .v391EditorAction.save{background:rgba(255,255,255,.94)!important;color:#214c83!important}
  #ng27 .v391EditorAction.create{background:linear-gradient(135deg,#66c8f6,#3b8eef)!important;color:#fff!important;border-color:rgba(63,145,229,.34)!important}
  #ng27 .v391EditorAction:active{transform:scale(.98)!important}
  #ng27.gsfFullscreen .v391EditorActions,#ng27.gsfFullscreenFallback .v391EditorActions,#ng27:fullscreen .v391EditorActions,#ng27:-webkit-full-screen .v391EditorActions{display:none!important}
}
</style>
'''

RUNTIME=r'''
 /* V391_EDITOR_ACTION_RUNTIME */
 let v391Actions=root.querySelector('#v391EditorActions');
 if(!v391Actions){
   v391Actions=document.createElement('div');
   v391Actions.id='v391EditorActions';
   v391Actions.className='v391EditorActions';
   v391Actions.setAttribute('aria-label','Azioni progetto');
   v391Actions.innerHTML='<button type="button" class="v391EditorAction save" id="v391SaveDraft">SALVA BOZZA</button><button type="button" class="v391EditorAction create" id="v391CreateShort">CREA SHORT</button>';
   const v391StageWrap=root.querySelector('.stageWrap');
   if(v391StageWrap)v391StageWrap.insertAdjacentElement('afterend',v391Actions);
 }
 function v391FinalAction(action){
   commit();
   const payload=cloneState();
   payload.editorVersion='2027.6';
   payload.sourceDuration=duration;
   payload.editorAction=action;
   payload.editorActionNonce=String(Date.now())+'-'+Math.random().toString(36).slice(2,8);
   sendStateToPython(payload);
   persistLocalState();
   flash(action==='create_short'?'CREAZIONE SHORT…':'SALVATAGGIO BOZZA…');
 }
 const v391SaveDraft=root.querySelector('#v391SaveDraft');
 const v391CreateShort=root.querySelector('#v391CreateShort');
 if(v391SaveDraft)v391SaveDraft.onclick=()=>v391FinalAction('save_draft');
 if(v391CreateShort)v391CreateShort.onclick=()=>v391FinalAction('create_short');
'''

def patch_text(text:str)->str:
    if MARK in text:return text
    for anchor in ('V389_MOBILE_EDITOR_BOUNDED_RESET','id="ng27"','class="stageWrap"','id="doneBtn"','</body>'):
        if anchor not in text:raise RuntimeError('V391 Editor anchor missing: '+anchor)
    done_anchor=" root.querySelector('#doneBtn').onclick=()=>{"
    if done_anchor not in text:raise RuntimeError('V391 Done-handler anchor missing')
    text=text.replace(done_anchor,RUNTIME+'\n'+done_anchor,1)
    return text.replace('</body>',STYLE+'\n</body>',1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    path=root/'web'/'editor_2027_component'/'index.html'
    if not path.is_file():raise SystemExit('V391 Editor target missing: '+str(path))
    before=path.read_text(encoding='utf-8');after=patch_text(before);path.write_text(after,encoding='utf-8')
    print('V391 mobile Editor raised + project actions restored changed=',before!=after,flush=True)

if __name__=='__main__':main()
