from pathlib import Path
import re

AI = Path('/app/web/ai_v221_component/index.html')
HOME = Path('/app/web/home_v154_component/index.html')
EDITOR = Path('/app/web/editor_2027_component/index.html')
APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')


AI_CSS = r'''
/* V288 AI JOURNEY */
#ai221 .journeySteps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;margin:0 2px 10px;padding:6px;border:1px solid rgba(143,181,216,.22);border-radius:16px;background:rgba(255,255,255,.66)}
#ai221 .journeyStep{min-width:0;padding:7px 5px;border-radius:11px;text-align:center;color:#8294AA;font-size:8.5px;font-weight:850;white-space:nowrap}
#ai221 .journeyStep.active{background:linear-gradient(145deg,#E4F4FF,#E4F8EF);color:#3479AD;box-shadow:inset 0 0 0 1px rgba(118,190,226,.16)}
#ai221 .moment{border:1px solid rgba(143,181,216,.23);transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease}
#ai221 .moment.selected{border-color:#65BDF1!important;box-shadow:0 0 0 3px rgba(92,190,240,.15),0 12px 28px rgba(65,105,145,.10)!important;transform:translateY(-2px)}
#ai221 .moment .thumb video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#0D1F35;z-index:1}
#ai221 .momentNextActions{margin-top:10px;padding:11px;border:1px solid rgba(143,181,216,.22);border-radius:19px;background:linear-gradient(145deg,rgba(247,252,255,.98),rgba(239,250,246,.95));box-shadow:0 10px 26px rgba(65,105,145,.06)}
#ai221 .momentNextActions[hidden]{display:none!important}
#ai221 .momentChoiceTitle{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:9px;color:#0D2A66;font-size:11px;font-weight:900}
#ai221 .momentChoiceTitle small{color:#7D91A8;font-size:8.5px;font-weight:750}
#ai221 .momentActionGrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
#ai221 .momentAction{min-height:48px;border:0;border-radius:15px;padding:10px 13px;font-size:10px;font-weight:900;cursor:pointer;box-shadow:0 9px 20px rgba(65,105,145,.08)}
#ai221 .momentAction.editor{background:linear-gradient(145deg,#DDF6EA,#CFF0DD);color:#24765B}
#ai221 .momentAction.short{background:linear-gradient(135deg,#77D3FB,#4EA7F3);color:white}
@media(max-width:520px){
 #ai221 .journeySteps{gap:3px;padding:4px;margin-bottom:7px}
 #ai221 .journeyStep{font-size:7px;padding:6px 2px}
 #ai221 .momentActionGrid{grid-template-columns:1fr}
 #ai221 .momentAction{min-height:46px;font-size:10px}
 #ai221 .momentChoiceTitle{font-size:10.5px}
}
/* END V288 AI JOURNEY */
'''

AI_STEPS = '''
 <div class="journeySteps" aria-label="Percorso creazione Short">
  <div class="journeyStep active">1 Motore</div><div class="journeyStep">2 Momento</div><div class="journeyStep">3 Editor</div><div class="journeyStep">4 Crea Short</div><div class="journeyStep">5 Pronto</div>
 </div>
'''

AI_ACTIONS = '''
 <section class="momentNextActions" id="momentNextActions" hidden aria-live="polite">
  <div class="momentChoiceTitle"><span id="selectedMomentLabel">Momento selezionato</span><small>Scegli come continuare</small></div>
  <div class="momentActionGrid">
   <button class="momentAction editor" id="editSelectedMoment" type="button">MODIFICA CON GAME EDITOR →</button>
   <button class="momentAction short" id="createSelectedMoment" type="button">CREA SHORT SENZA MODIFICHE →</button>
  </div>
 </section>
'''

AI_JS = r'''
 function selectMoment(index,emit=true){
  const rows=Array.isArray(state.previews)?state.previews.slice(0,3):[];
  const i=Number(index);
  if(!Number.isInteger(i)||i<0||i>=rows.length)return;
  state.selectedMoment=i;
  document.querySelectorAll(".moment").forEach((card,n)=>card.classList.toggle("selected",n===i));
  const actions=document.getElementById("momentNextActions"),label=document.getElementById("selectedMomentLabel");
  if(actions)actions.hidden=false;
  if(label)label.textContent="Momento "+(i+1)+" selezionato";
  const card=document.querySelector('.moment[data-index="'+i+'"]'),d=rows[i]||{};
  if(card&&d.video){
   const thumb=card.querySelector(".thumb");
   if(thumb&&!thumb.querySelector("video")){
    document.querySelectorAll(".moment .thumb video").forEach(v=>v.remove());
    const v=document.createElement("video");v.src=d.video;v.controls=true;v.autoplay=true;v.playsInline=true;v.muted=false;thumb.prepend(v);
   }
  }
  document.querySelectorAll(".journeyStep").forEach((step,n)=>step.classList.toggle("active",n<=1));
  if(emit)send("select_moment",{index:i,duration:state.duration,engine:state.engine});
 }
'''

HOME_BRIDGE = r'''
   /* V288 AI JOURNEY BRIDGE */
   if(action==="select_moment"){
     const idx=Math.max(0,Math.min(2,Number(e.data.index)||0));
     try{sessionStorage.setItem("gsf_ai_selected_moment_v288",String(idx))}catch(_e){}
     value({event:"preview_moment",index:idx,duration,engine});
     return;
   }
   if(action==="open_editor"){
     let idx=Number(e.data.index);
     if(!Number.isFinite(idx)){try{idx=Number(sessionStorage.getItem("gsf_ai_selected_moment_v288"))}catch(_e){idx=0}}
     idx=Math.max(0,Math.min(2,Number.isFinite(idx)?idx:0));
     const selectedPreview=(Array.isArray(previewData)?previewData[idx]:null)||{};
     shellNav("editor",{momentIndex:idx,video_url:String(selectedPreview.video||""),cover:String(selectedPreview.cover||""),duration:Number(duration)||15,engine:String(engine||"")});
     value({event:"open_editor",duration,engine,index:idx});
     return;
   }
   if(action==="create_short"){
     let idx=Number(e.data.index);
     if(!Number.isFinite(idx)){try{idx=Number(sessionStorage.getItem("gsf_ai_selected_moment_v288"))}catch(_e){idx=0}}
     idx=Math.max(0,Math.min(2,Number.isFinite(idx)?idx:0));
     const selectedPreview=(Array.isArray(previewData)?previewData[idx]:null)||{};
     parentClick(["crea short","crea short finale","crea il tuo short"]);
     value({event:"create_short",duration,engine,index:idx,video:String(selectedPreview.video||"")});
     return;
   }
'''

EDITOR_CSS = r'''
/* V288 EDITOR TO SHORT */
#ng27 .createShortJourney{position:relative;z-index:4;width:min(100%,520px);margin:8px auto 3px;padding:6px}
#ng27 .createShortJourneyBtn{width:100%;min-height:48px;border:1px solid rgba(112,190,231,.28);border-radius:16px;background:linear-gradient(135deg,#77D3FB,#4EA7F3);color:#fff;box-shadow:0 10px 24px rgba(69,157,223,.20);font-weight:900;font-size:10px;letter-spacing:.035em;display:flex;align-items:center;justify-content:center;gap:7px}
#ng27 .createShortJourneyBtn small{font-size:8px;font-weight:800;opacity:.88;letter-spacing:.02em}
#ng27 .createShortJourneyBtn:active{transform:scale(.985)}
@media(max-width:820px) and (any-pointer:coarse){
 #ng27 .createShortJourney{width:calc(100% - 10px);margin:7px auto 2px;padding:4px}
 #ng27 .createShortJourneyBtn{min-height:50px;border-radius:15px;font-size:10.5px}
}
/* END V288 EDITOR TO SHORT */
'''

EDITOR_CTA = '''
  <div class="createShortJourney">
   <button class="createShortJourneyBtn" id="createShortFromEditor" type="button"><small>HAI FINITO?</small> CREA IL TUO SHORT →</button>
  </div>
'''

EDITOR_HANDLER = r'''
 const createShortFromEditor=root.querySelector('#createShortFromEditor');
 if(createShortFromEditor)createShortFromEditor.onclick=()=>{
   commit();
   const payload=cloneState();
   payload.editorVersion='2027.6';
   payload.sourceDuration=duration;
   payload.nextAction='create_short';
   sendStateToPython(payload);
   clearLocalState();
   flash('PRONTO PER LO SHORT');
 };
'''

APP_SELECTION_DECL = "      let pendingSelection=null;\n"

APP_SELECTION_OPEN = r'''
        const selection=pendingSelection;pendingSelection=null;
'''

APP_SELECTION_RENDER = r'''
        if(selection&&selection.video_url){
          const selectedDuration=Math.max(.5,Number(selection.duration)||15);
          editorMeta.video_url=String(selection.video_url);
          editorMeta.initial_state=Object.assign({},editorMeta.initial_state||{}, {inPoint:0,outPoint:selectedDuration,sourceDuration:selectedDuration,momentIndex:Number(selection.momentIndex)||0});
          setTimeout(sendRender,18);
          return;
        }
'''

APP_TRIGGER_HELPER = r'''
      /* V288 EDITOR JOURNEY BRIDGE */
      const triggerCreateShort=()=>{
        const nodes=[...document.querySelectorAll('button,a,[role=button]')].filter(x=>!x.closest('#gsf-editor-overlay-v220'));
        const wanted=['crea short finale','crea il tuo short','crea short'];
        const el=nodes.find(x=>wanted.some(w=>(x.innerText||x.textContent||'').trim().toLowerCase().includes(w)));
        if(el){close();el.click();return true}
        return false;
      };
'''


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f'V288 anchor missing: {label}')
    return text.replace(old, new, 1)


def patch_ai():
    text=AI.read_text(encoding='utf-8');before=text
    if 'V288 AI JOURNEY' not in text:
        text=replace_once(text,'</style>',AI_CSS+'\n</style>','AI CSS')
        text=replace_once(text,'<main id="ai221">','<main id="ai221">'+AI_STEPS,'AI journey steps')
        text=replace_once(text,'<button class="create" id="createAi" disabled>Crea con IA</button>','<button class="create" id="createAi" disabled>TROVA I 3 MOMENTI MIGLIORI →</button>','AI CTA copy')
        text=replace_once(text,'</main>\n<script>',' '+AI_ACTIONS+'\n</main>\n<script>','AI moment actions')
        text=replace_once(text,'let state={loaded:false,duration:15,engine:"auto",previews:[]},seq=0;','let state={loaded:false,duration:15,engine:"auto",previews:[],selectedMoment:-1},seq=0;','AI state')
        text=replace_once(text,' function sync(){',AI_JS+'\n function sync(){','AI selectMoment helper')
        old='document.querySelectorAll(".moment").forEach(card=>card.addEventListener("click",()=>send("preview",{index:Number(card.dataset.index)||0})));'
        new='document.querySelectorAll(".moment").forEach(card=>card.addEventListener("click",()=>selectMoment(Number(card.dataset.index)||0,true)));'
        text=replace_once(text,old,new,'AI moment selection')
        anchor='create.addEventListener("click",()=>{if(!state.loaded)return;guide("creating");status.textContent="L’IA sta cercando i momenti migliori…";send("create",{engine:state.engine,duration:state.duration})});'
        handlers=anchor+'\n document.getElementById("editSelectedMoment").addEventListener("click",()=>{if(state.selectedMoment<0)return;send("open_editor",{index:state.selectedMoment,duration:state.duration,engine:state.engine})});\n document.getElementById("createSelectedMoment").addEventListener("click",()=>{if(state.selectedMoment<0)return;send("create_short",{index:state.selectedMoment,duration:state.duration,engine:state.engine})});'
        text=replace_once(text,anchor,handlers,'AI next-step handlers')
    AI.write_text(text,encoding='utf-8')
    print('V288 AI journey applied:',AI,'changed=',text!=before,flush=True)


def patch_home():
    text=HOME.read_text(encoding='utf-8');before=text
    if 'V288 AI JOURNEY BRIDGE' not in text:
        anchor='   if(action==="open_editor"){shellNav("editor");return;}\n'
        text=replace_once(text,anchor,HOME_BRIDGE,'Home AI command bridge')
    HOME.write_text(text,encoding='utf-8')
    print('V288 Home AI bridge applied:',HOME,'changed=',text!=before,flush=True)


def patch_editor():
    text=EDITOR.read_text(encoding='utf-8');before=text
    if 'V288 EDITOR TO SHORT' not in text:
        text=replace_once(text,'</style>',EDITOR_CSS+'\n</style>','Editor CSS')
        foot='<div class="footNote">GAME EDITOR LIVE · FRAME / COVER / LOOK / HUD / CAPTION / AUDIO / IN-OUT / UNDO-REDO</div>'
        text=replace_once(text,foot,EDITOR_CTA+foot,'Editor Create Short CTA')
        anchor=" const playBtn=root.querySelector('#playBtn');"
        text=replace_once(text,anchor,EDITOR_HANDLER+'\n'+anchor,'Editor Create Short handler')
    EDITOR.write_text(text,encoding='utf-8')
    print('V288 Editor CTA applied:',EDITOR,'changed=',text!=before,flush=True)


def patch_app():
    text=APP.read_text(encoding='utf-8');before=text
    if 'V288 EDITOR JOURNEY BRIDGE' not in text:
        text=replace_once(text,'      const sendRender=()=>{',APP_SELECTION_DECL+'      const sendRender=()=>{','Editor selection declaration')
        text=replace_once(text,'      const open=(remember=true)=>{\n', '      const open=(remember=true)=>{\n'+APP_SELECTION_OPEN,'Editor selection open')
        load_anchor="        fetch('/editor/state',{cache:'no-store',credentials:'same-origin'})\n"
        text=replace_once(text,load_anchor,APP_SELECTION_RENDER+load_anchor,'Editor selected video render')
        close_anchor="      const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true');try{sessionStorage.setItem(KEY,'0')}catch(e){}};\n"
        text=replace_once(text,close_anchor,close_anchor+APP_TRIGGER_HELPER,'Editor final Short helper')
        old="            fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state})}).catch(()=>{});\n            guide('done');"
        new="            const saveEditorState=fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state})}).catch(()=>{});\n            if(state.nextAction==='create_short')saveEditorState.finally(()=>setTimeout(triggerCreateShort,60));\n            guide('done');"
        text=replace_once(text,old,new,'Editor Create Short state consumer')
        old_nav="        if(t==='editor'){open();return}"
        new_nav="        if(t==='editor'){pendingSelection={video_url:String(e.data.video_url||''),duration:Number(e.data.duration)||15,momentIndex:Number(e.data.momentIndex)||0};open();return}"
        text=replace_once(text,old_nav,new_nav,'Editor selected moment navigation')
    APP.write_text(text,encoding='utf-8')
    print('V288 Editor shell bridge applied:',APP,'changed=',text!=before,flush=True)


if __name__=='__main__':
    for path in (AI,HOME,EDITOR,APP):
        if not path.is_file():
            raise RuntimeError('V288 required file missing: '+str(path))
    patch_ai();patch_home();patch_editor();patch_app()
