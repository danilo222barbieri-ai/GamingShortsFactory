#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v323MobileEditorPlayerActions'
ACTION_ID='v323EditorActions'
SHELL_MARK='V323_EDITOR_ACTION_BRIDGE'

STYLE=r'''<style id="v323MobileEditorPlayerActions">
/* V323: mobile Game Editor = player-first. Desktop geometry is untouched. */
#ng27 .v323EditorActions{display:none}
@media(max-width:760px){
  #ng27{
    height:100dvh!important;min-height:0!important;max-height:none!important;
    padding:4px 6px 2px!important;overflow:hidden!important;border-radius:0!important;
  }
  #ng27 .shell{
    width:100%!important;height:100%!important;min-height:0!important;
    padding:0!important;justify-content:flex-start!important;overflow:visible!important;
  }
  /* Outer app shell already owns the Game Editor title. Keep only FULL inside the player. */
  #ng27 .topline{display:none!important}
  #ng27 .gsfGuide,#ng27 .footNote{display:none!important}
  #ng27 .cockpit,#ng27.expanded .cockpit{
    display:block!important;position:relative!important;
    width:min(100%,clamp(250px,calc((100dvh - 96px)*.5625),340px))!important;
    min-height:0!important;margin:0 auto!important;
  }
  #ng27 .stageWrap{
    position:relative!important;width:100%!important;min-width:0!important;
    margin:0 auto!important;overflow:visible!important;
  }
  #ng27 .stage.r916,#ng27.expanded .stage.r916{
    width:100%!important;max-width:none!important;aspect-ratio:9/16!important;
    margin:0!important;border-radius:21px!important;overflow:hidden!important;
    box-shadow:0 14px 36px rgba(28,52,70,.15)!important;
  }

  /* Existing real controls become glass overlays INSIDE the player. */
  #ng27 .cockpit>.rail{
    position:absolute!important;top:50%!important;z-index:64!important;
    display:flex!important;flex-direction:column!important;justify-content:center!important;
    gap:7px!important;transform:translateY(-50%)!important;pointer-events:none!important;
  }
  #ng27 .cockpit>.rail:first-child{left:7px!important}
  #ng27 .cockpit>.rail:last-child{right:7px!important}
  #ng27 .cockpit>.rail .railBtn{
    pointer-events:auto!important;width:48px!important;height:48px!important;
    min-width:48px!important;min-height:48px!important;padding:0!important;
    border-radius:14px!important;border:1px solid rgba(255,255,255,.64)!important;
    background:linear-gradient(145deg,rgba(18,42,69,.54),rgba(30,55,88,.37))!important;
    -webkit-backdrop-filter:blur(14px) saturate(1.12)!important;backdrop-filter:blur(14px) saturate(1.12)!important;
    box-shadow:0 7px 20px rgba(8,24,39,.18),inset 0 1px 0 rgba(255,255,255,.24)!important;
    color:#fff!important;gap:2px!important;
  }
  #ng27 .cockpit>.rail .railBtn .ico{width:19px!important;height:19px!important;color:#fff!important;stroke:currentColor!important}
  #ng27 .cockpit>.rail .railBtn span{font-size:7.2px!important;line-height:1!important;letter-spacing:.025em!important;color:#fff!important;text-shadow:0 1px 4px rgba(0,0,0,.30)!important}
  #ng27 .cockpit>.rail .railBtn.active{background:linear-gradient(145deg,rgba(65,164,235,.82),rgba(61,119,211,.70))!important;border-color:rgba(199,237,255,.88)!important}

  /* Mobile primary toolset. COVER/HUD remain available in desktop; undo/redo/done are replaced by explicit mobile workflow actions. */
  #ng27 .railBtn[data-panel="cover"],
  #ng27 .railBtn[data-panel="hud"],
  #ng27 #undoBtn,
  #ng27 #redoBtn,
  #ng27 #doneBtn{display:none!important}
  #ng27 .cockpit>.rail:first-child .railBtn[data-panel="frame"]{order:1}
  #ng27 .cockpit>.rail:first-child .railBtn[data-panel="caption"]{order:2}
  #ng27 .cockpit>.rail:first-child .railBtn[data-panel="look"]{order:3}
  #ng27 .cockpit>.rail:first-child .railBtn[data-panel="audio"]{order:4}
  #ng27 .cockpit>.rail:last-child #playBtn{order:1}
  #ng27 .cockpit>.rail:last-child .railBtn[data-panel="vision"]{order:2}
  #ng27 .cockpit>.rail:last-child .railBtn[data-panel="vision"] span{font-size:0!important}
  #ng27 .cockpit>.rail:last-child .railBtn[data-panel="vision"] span:after{content:"AI";font-size:7.2px!important}

  /* FULL is physically moved into #stage by V323 JS. */
  #ng27 #zoomEditorBtn.v323InsidePlayer{
    display:flex!important;position:absolute!important;top:8px!important;right:8px!important;z-index:82!important;
    min-width:54px!important;height:38px!important;padding:0 9px!important;border-radius:12px!important;
    border:1px solid rgba(255,255,255,.65)!important;background:rgba(18,42,69,.52)!important;
    color:#fff!important;box-shadow:0 7px 18px rgba(8,24,39,.16)!important;
    -webkit-backdrop-filter:blur(14px)!important;backdrop-filter:blur(14px)!important;
  }
  #ng27 #zoomEditorBtn.v323InsidePlayer span{font-size:7.6px!important;color:#fff!important}
  #ng27 #zoomEditorBtn.v323InsidePlayer .ico{width:17px!important;height:17px!important;color:#fff!important}

  /* Timeline stays at the bottom of the frame; workflow actions sit immediately BELOW it. */
  #ng27 .timeline,#ng27.expanded .timeline{
    position:absolute!important;left:50%!important;bottom:8px!important;z-index:58!important;
    width:calc(100% - 16px)!important;margin:0!important;padding:6px 8px 7px!important;
    transform:translateX(-50%)!important;border-radius:13px!important;
    background:rgba(8,19,28,.70)!important;border:1px solid rgba(255,255,255,.15)!important;
    -webkit-backdrop-filter:blur(16px)!important;backdrop-filter:blur(16px)!important;
    box-shadow:0 8px 20px rgba(4,12,18,.20)!important;
  }
  #ng27 .timeline .tlMeta,#ng27 .timeline .trimRow{color:#eef7fb!important}
  #ng27 .v323EditorActions{
    display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;
    gap:7px!important;width:100%!important;margin:8px 0 0!important;padding:0!important;
  }
  #ng27 .v323EditorAction{
    min-width:0!important;min-height:48px!important;border-radius:15px!important;
    border:1px solid rgba(143,181,216,.24)!important;padding:8px 9px!important;
    font:inherit!important;font-size:10px!important;font-weight:950!important;line-height:1.05!important;
    cursor:pointer!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important;
    box-shadow:0 8px 20px rgba(61,104,145,.08)!important;
  }
  #ng27 .v323EditorAction.primary{background:linear-gradient(135deg,#72D0FA,#4F9EF0)!important;color:#fff!important;border-color:rgba(78,164,234,.34)!important}
  #ng27 .v323EditorAction.secondary{background:rgba(255,255,255,.90)!important;color:#244C86!important}
  #ng27 .v323EditorAction:active{transform:scale(.98)!important}

  /* Fullscreen carries the same real tools inside the player; final actions stay outside fullscreen. */
  #ng27.gsfFullscreen .cockpit,
  #ng27:fullscreen .cockpit,
  #ng27:-webkit-full-screen .cockpit{width:100vw!important;height:100dvh!important;margin:0!important}
  #ng27.gsfFullscreen .stageWrap,
  #ng27:fullscreen .stageWrap,
  #ng27:-webkit-full-screen .stageWrap{width:100vw!important;height:100dvh!important;display:flex!important;align-items:center!important;justify-content:center!important}
  #ng27.gsfFullscreen .stage.r916,
  #ng27:fullscreen .stage.r916,
  #ng27:-webkit-full-screen .stage.r916{width:min(100vw,calc(100dvh * 9 / 16))!important;height:min(100dvh,calc(100vw * 16 / 9))!important;max-width:none!important;border-radius:0!important}
  #ng27.gsfFullscreen .v323EditorActions,
  #ng27:fullscreen .v323EditorActions,
  #ng27:-webkit-full-screen .v323EditorActions{display:none!important}
  #ng27.gsfFullscreen .cockpit>.rail:first-child,
  #ng27:fullscreen .cockpit>.rail:first-child,
  #ng27:-webkit-full-screen .cockpit>.rail:first-child{left:max(8px,env(safe-area-inset-left))!important}
  #ng27.gsfFullscreen .cockpit>.rail:last-child,
  #ng27:fullscreen .cockpit>.rail:last-child,
  #ng27:-webkit-full-screen .cockpit>.rail:last-child{right:max(8px,env(safe-area-inset-right))!important}
  #ng27.gsfFullscreen #zoomEditorBtn.v323InsidePlayer,
  #ng27:fullscreen #zoomEditorBtn.v323InsidePlayer,
  #ng27:-webkit-full-screen #zoomEditorBtn.v323InsidePlayer{top:max(10px,env(safe-area-inset-top))!important;right:max(10px,env(safe-area-inset-right))!important}
}
@media(max-width:390px) and (max-height:760px){
  #ng27 .cockpit,#ng27.expanded .cockpit{width:min(100%,clamp(238px,calc((100dvh - 92px)*.5625),308px))!important}
  #ng27 .cockpit>.rail .railBtn{width:44px!important;height:44px!important;min-width:44px!important;min-height:44px!important;border-radius:13px!important}
  #ng27 .cockpit>.rail:first-child{left:5px!important}#ng27 .cockpit>.rail:last-child{right:5px!important}
  #ng27 .v323EditorAction{min-height:44px!important;font-size:9.2px!important}
}
</style>'''

ACTIONS='''<div class="v323EditorActions" id="v323EditorActions" aria-label="Azioni progetto"><button type="button" class="v323EditorAction primary" id="v323CreateShort">▶ CREA SHORT</button><button type="button" class="v323EditorAction secondary" id="v323SaveDraft">▣ SALVA LA TUA BOZZA</button></div>'''

EDITOR_JS=r'''
 /* V323 MOBILE EDITOR PLAYER ACTIONS */
 const v323CreateShort=root.querySelector('#v323CreateShort');
 const v323SaveDraft=root.querySelector('#v323SaveDraft');
 const v323FullscreenHome=zoomEditorBtn?zoomEditorBtn.parentElement:null;
 const v323FullscreenNext=zoomEditorBtn?zoomEditorBtn.nextSibling:null;
 function v323PlaceFullscreen(){
   if(!zoomEditorBtn||!stage)return;
   if(window.matchMedia('(max-width:760px)').matches){
     if(zoomEditorBtn.parentElement!==stage)stage.appendChild(zoomEditorBtn);
     zoomEditorBtn.classList.add('v323InsidePlayer');
   }else{
     zoomEditorBtn.classList.remove('v323InsidePlayer');
     if(v323FullscreenHome&&zoomEditorBtn.parentElement!==v323FullscreenHome){
       if(v323FullscreenNext&&v323FullscreenNext.parentNode===v323FullscreenHome)v323FullscreenHome.insertBefore(zoomEditorBtn,v323FullscreenNext);
       else v323FullscreenHome.appendChild(zoomEditorBtn);
     }
   }
 }
 function v323BasePayload(){
   commit();
   const payload=cloneState();
   payload.editorVersion='2027.6';
   payload.sourceDuration=duration;
   payload.editorActionNonce=String(Date.now())+'-'+Math.random().toString(36).slice(2,8);
   return payload;
 }
 function v323CreateShortAction(){
   const payload=v323BasePayload();
   payload.editorAction="create_short";
   sendStateToPython(payload);
   persistLocalState();
   flash('CREAZIONE SHORT…');
 }
 function v323SaveDraftAction(){
   const payload=v323BasePayload();
   payload.editorAction="save_draft";
   sendStateToPython(payload);
   persistLocalState();
   flash('SALVATAGGIO BOZZA…');
 }
 if(v323CreateShort)v323CreateShort.onclick=v323CreateShortAction;
 if(v323SaveDraft)v323SaveDraft.onclick=v323SaveDraftAction;
 v323PlaceFullscreen();
 window.addEventListener('resize',()=>{clearTimeout(v323PlaceFullscreen.t);v323PlaceFullscreen.t=setTimeout(v323PlaceFullscreen,80)});
'''

SHELL_BLOCK=r'''if(e.source===frame.contentWindow&&e.data&&e.data.type==='streamlit:setComponentValue'){
          /* V323_EDITOR_ACTION_BRIDGE */
          const state=e.data.value;
          if(state&&typeof state==='object'){
            const action=String(state.editorAction||'');
            const cleanState={...state};
            delete cleanState.editorAction;delete cleanState.editorActionNonce;
            editorMeta.initial_state=cleanState;
            const notify=(title,msg='',kind='success')=>{try{window.GSFNotify&&window.GSFNotify.show(title,msg,kind)}catch(_e){}};
            const saveState=fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:cleanState})}).then(r=>{if(!r.ok)throw new Error('Stato Editor non salvato');return r});
            if(action==='save_draft'){
              saveState.then(()=>fetch('/creator-hub/project/save-draft',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}))
                .then(async r=>{let j={};try{j=await r.json()}catch(_e){};if(!r.ok||!j.ok)throw new Error(j.error||'Bozza non salvata');notify('Bozza salvata',String((j.draft||{}).title||''),'success')})
                .catch(err=>notify('Bozza non salvata',String(err&&err.message||err),'error'));
              guide('done');
              return;
            }
            if(action==='create_short'){
              saveState.then(()=>{
                close();
                try{sessionStorage.setItem(KEY,'0')}catch(_e){}
                const target=document.querySelector('.st-key-gsf-major-create-short button,.st-key-create_final_short_v54 button');
                if(target){target.click();return;}
                const fallback=[...document.querySelectorAll('button')].find(b=>/crea\s+short/i.test(String(b.innerText||b.textContent||'')));
                if(fallback){fallback.click();return;}
                notify('Crea Short non disponibile','Riapri il progetto e riprova.','error');
              }).catch(err=>notify('Crea Short non avviato',String(err&&err.message||err),'error'));
              guide('done');
              return;
            }
            saveState.catch(()=>{});
            guide('done');
          }
          return;
        }'''


def _find_matching_div_end(text:str,start:int)->int:
    token=re.compile(r'<div\b[^>]*>|</div\s*>',re.IGNORECASE)
    depth=0
    for match in token.finditer(text,start):
        if match.group(0).lower().startswith('</div'):
            depth-=1
            if depth==0:return match.end()
        else:
            depth+=1
    raise RuntimeError('V323 timeline closing div missing')


def _find_matching_brace(text:str,start:int)->int:
    first=text.find('{',start)
    if first<0:raise RuntimeError('V323 shell bridge opening brace missing')
    depth=0
    quote='';escape=False
    for i in range(first,len(text)):
        ch=text[i]
        if quote:
            if escape:escape=False
            elif ch=='\\':escape=True
            elif ch==quote:quote=''
            continue
        if ch in ('\"',"'",'`'):
            quote=ch;continue
        if ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:return i+1
    raise RuntimeError('V323 shell bridge closing brace missing')


def _clean_editor(text:str)->str:
    text=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)
    text=re.sub(r'\s*<div class="v323EditorActions" id="v323EditorActions".*?</div>','',text,count=1,flags=re.DOTALL)
    text=re.sub(r'\n?\s*/\* V323 MOBILE EDITOR PLAYER ACTIONS \*/.*?window\.addEventListener\(\'resize\'.*?\);\n?','',text,count=1,flags=re.DOTALL)
    return text


def patch_editor_text(text:str)->str:
    complete=(f'id="{STYLE_ID}"' in text and f'id="{ACTION_ID}"' in text and 'V323 MOBILE EDITOR PLAYER ACTIONS' in text and 'editorAction="create_short"' in text and 'editorAction="save_draft"' in text)
    if complete:return text
    for marker in ('id="ng27"','id="stage"','id="zoomEditorBtn"','id="playBtn"','id="doneBtn"','data-panel="frame"','data-panel="caption"','data-panel="audio"','data-panel="vision"'):
        if marker not in text:raise RuntimeError('V323 editor anchor missing: '+marker)
    out=_clean_editor(text)
    if '</head>' not in out:raise RuntimeError('V323 editor </head> missing')
    out=out.replace('</head>',STYLE+'\n</head>',1)
    timeline=out.find('<div class="timeline"')
    if timeline<0:raise RuntimeError('V323 timeline anchor missing')
    timeline_end=_find_matching_div_end(out,timeline)
    out=out[:timeline_end]+'\n      '+ACTIONS+out[timeline_end:]
    js_anchor=" root.querySelector('#doneBtn').onclick=()=>{"
    if js_anchor not in out:raise RuntimeError('V323 done handler anchor missing')
    out=out.replace(js_anchor,EDITOR_JS+'\n'+js_anchor,1)
    return out


def patch_shell_text(text:str)->str:
    if SHELL_MARK in text:return text
    anchor="if(e.source===frame.contentWindow&&e.data&&e.data.type==='streamlit:setComponentValue'){"
    start=text.find(anchor)
    if start<0:raise RuntimeError('V323 shell editor component-value bridge missing')
    end=_find_matching_brace(text,start)
    return text[:start]+SHELL_BLOCK+text[end:]


def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    app=root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    if not editor.is_file():raise SystemExit('V323 editor target missing: '+str(editor))
    if not app.is_file():raise SystemExit('V323 shell target missing: '+str(app))
    before=editor.read_text(encoding='utf-8');after=patch_editor_text(before);editor.write_text(after,encoding='utf-8')
    print('V323 mobile editor UI applied changed=',before!=after,flush=True)
    before_app=app.read_text(encoding='utf-8');after_app=patch_shell_text(before_app);app.write_text(after_app,encoding='utf-8')
    print('V323 editor action bridge applied changed=',before_app!=after_app,flush=True)

if __name__=='__main__':
    main()
