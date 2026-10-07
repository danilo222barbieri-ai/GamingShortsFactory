#!/usr/bin/env python3
from pathlib import Path
import sys

DEFAULT_AI = Path('/app/web/ai_v221_component/index.html')

CSS = r'''
/* V309 MOBILE AI FLOW */
#ai221 .momentFullscreen{
  display:none;
  position:fixed;
  inset:0;
  z-index:10000;
  background:#02070D;
  color:#fff;
  align-items:stretch;
  justify-content:center;
  flex-direction:column;
  padding:max(10px,env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) max(12px,env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));
}
#ai221 .momentFullscreen.open{display:flex}
#ai221 .momentFullscreenTop{
  flex:0 0 auto;
  min-height:48px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  padding:2px 2px 9px;
}
#ai221 .momentFullscreenBack{
  min-height:42px;
  border:1px solid rgba(255,255,255,.18);
  border-radius:14px;
  padding:8px 12px;
  background:rgba(255,255,255,.10);
  color:#fff;
  font-size:12px;
  font-weight:900;
  cursor:pointer;
  -webkit-tap-highlight-color:transparent;
}
#ai221 .momentFullscreenLabel{font-size:11px;font-weight:850;color:rgba(255,255,255,.76);text-align:right}
#ai221 .momentFullscreenStage{
  min-height:0;
  flex:1 1 auto;
  display:grid;
  place-items:center;
  overflow:hidden;
}
#ai221 .momentFullscreenVideo{
  display:block;
  width:100%;
  height:100%;
  max-width:100%;
  max-height:100%;
  object-fit:contain;
  background:#000;
  border-radius:16px;
}

@media(max-width:760px){
  #ai221{
    height:100dvh!important;
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    overscroll-behavior-y:contain!important;
    -webkit-overflow-scrolling:touch!important;
    scroll-behavior:smooth;
  }
  #ai221 .journeySteps{display:none!important}
  #ai221 .top{
    display:grid!important;
    grid-template-columns:minmax(0,1fr) auto!important;
    align-items:start!important;
    gap:8px!important;
    margin-bottom:8px!important;
  }
  #ai221 .title{min-width:0!important;align-items:flex-start!important}
  #ai221 .titleIcon{flex:0 0 auto!important}
  #ai221 h1{line-height:1.02!important}
  #ai221 .duration{align-self:start!important}
  #ai221 .panel{overflow:visible!important}
  #ai221 .moments{
    grid-template-columns:1fr!important;
    gap:8px!important;
  }
  #ai221 .moment{
    width:100%!important;
    min-height:88px!important;
    display:grid!important;
    grid-template-columns:116px minmax(0,1fr)!important;
    align-items:center!important;
    gap:10px!important;
    padding:6px!important;
    text-align:left!important;
  }
  #ai221 .thumb{
    width:116px!important;
    height:76px!important;
    border-radius:13px!important;
  }
  #ai221 .moment b{
    margin:0!important;
    padding-right:8px!important;
    font-size:11px!important;
    line-height:1.15!important;
  }
  #ai221 .moment .play{width:34px!important;height:34px!important;font-size:12px!important}
  #ai221 .momentNextActions{
    scroll-margin:14px 0 90px!important;
    margin-top:9px!important;
  }
  #ai221 .momentChoiceTitle{align-items:flex-start!important}
}
/* END V309 MOBILE AI FLOW */
'''

OVERLAY = r'''
 <section class="momentFullscreen" id="momentFullscreen" aria-hidden="true" aria-label="Anteprima momento a schermo intero">
  <div class="momentFullscreenTop">
   <button class="momentFullscreenBack" id="closeMomentFullscreen" type="button">← Torna ai 3 momenti</button>
   <div class="momentFullscreenLabel" id="momentFullscreenLabel">Anteprima</div>
  </div>
  <div class="momentFullscreenStage">
   <video class="momentFullscreenVideo" id="momentFullscreenVideo" controls playsinline preload="metadata"></video>
  </div>
 </section>
'''

JS = r'''
 let momentPreviewScroll=0;
 function selectedActions(){return document.getElementById("momentNextActions")}
 function scrollToSelectedActions(){
  const actions=selectedActions();
  if(actions&&!actions.hidden){
   requestAnimationFrame(()=>actions.scrollIntoView({behavior:"smooth",block:"nearest"}));
  }
 }
 function closeMomentPreview(scrollToActions=true){
  const overlay=document.getElementById("momentFullscreen"),video=document.getElementById("momentFullscreenVideo");
  if(!overlay||!video)return;
  try{video.pause()}catch(_e){}
  overlay.classList.remove("open");
  overlay.setAttribute("aria-hidden","true");
  document.body.classList.remove("moment-fullscreen-open");
  const root=document.getElementById("ai221");
  if(root&&Number.isFinite(momentPreviewScroll))root.scrollTop=momentPreviewScroll;
  if(scrollToActions)scrollToSelectedActions();
 }
 function openMomentPreview(index){
  if(!window.matchMedia("(max-width:760px)").matches)return;
  const rows=Array.isArray(state.previews)?state.previews.slice(0,3):[];
  const i=Math.max(0,Math.min(2,Number(index)||0)),d=rows[i]||{};
  if(!d.video)return;
  const overlay=document.getElementById("momentFullscreen"),video=document.getElementById("momentFullscreenVideo"),label=document.getElementById("momentFullscreenLabel");
  if(!overlay||!video)return;
  const root=document.getElementById("ai221");
  momentPreviewScroll=root?root.scrollTop:0;
  document.querySelectorAll(".moment .thumb video").forEach(v=>{try{v.pause()}catch(_e){};v.remove()});
  video.poster=d.cover||"";
  if(video.src!==d.video){video.src=d.video;video.load()}
  if(label)label.textContent="Momento "+(i+1)+" · anteprima";
  overlay.classList.add("open");
  overlay.setAttribute("aria-hidden","false");
  document.body.classList.add("moment-fullscreen-open");
  const play=video.play();if(play&&play.catch)play.catch(()=>{});
  try{
   const request=overlay.requestFullscreen?overlay.requestFullscreen():null;
   if(request&&request.catch)request.catch(()=>{
    try{if(video.webkitEnterFullscreen)video.webkitEnterFullscreen()}catch(_e){}
   });
   else if(!overlay.requestFullscreen&&video.webkitEnterFullscreen)video.webkitEnterFullscreen();
  }catch(_e){try{if(video.webkitEnterFullscreen)video.webkitEnterFullscreen()}catch(_e2){}}
 }
'''

MOBILE_CLICK = r'''document.querySelectorAll(".moment").forEach(card=>card.addEventListener("click",()=>{
  const index=Number(card.dataset.index)||0;
  if(window.matchMedia("(max-width:760px)").matches){
   if(typeof selectMoment==="function")selectMoment(index,true);else send("preview",{index});
   openMomentPreview(index);
   return;
  }
  if(typeof selectMoment==="function")selectMoment(index,true);else send("preview",{index});
 }));'''

CLOSE_BINDINGS = r'''
 const closeMomentFullscreen=document.getElementById("closeMomentFullscreen");
 if(closeMomentFullscreen)closeMomentFullscreen.addEventListener("click",async()=>{
  try{if(document.fullscreenElement&&document.exitFullscreen)await document.exitFullscreen()}catch(_e){}
  closeMomentPreview(true);
 });
 const fullscreenVideo=document.getElementById("momentFullscreenVideo");
 if(fullscreenVideo)fullscreenVideo.addEventListener("webkitendfullscreen",()=>closeMomentPreview(true));
 document.addEventListener("fullscreenchange",()=>{
  const overlay=document.getElementById("momentFullscreen");
  if(overlay&&overlay.classList.contains("open")&&!document.fullscreenElement)closeMomentPreview(true);
 });
 document.addEventListener("keydown",e=>{if(e.key==="Escape")closeMomentPreview(true)});
'''

BASE_CLICK = 'document.querySelectorAll(".moment").forEach(card=>card.addEventListener("click",()=>send("preview",{index:Number(card.dataset.index)||0})));'
V288_CLICK = 'document.querySelectorAll(".moment").forEach(card=>card.addEventListener("click",()=>selectMoment(Number(card.dataset.index)||0,true)));'


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f'V309 anchor missing: {label}')
    return text.replace(old, new, 1)


def patch_ai_text(text):
    if 'V309 MOBILE AI FLOW' in text:
        return text

    text = replace_once(text, '</style>', CSS + '\n</style>', 'style end')
    text = replace_once(text, '</main>\n<script>', OVERLAY + '\n</main>\n<script>', 'main end')
    text = replace_once(text, ' function sync(){', JS + '\n function sync(){', 'sync helper')

    if V288_CLICK in text:
        text = text.replace(V288_CLICK, MOBILE_CLICK, 1)
    elif BASE_CLICK in text:
        text = text.replace(BASE_CLICK, MOBILE_CLICK, 1)
    else:
        raise RuntimeError('V309 anchor missing: moment click handler')

    anchor = 'create.addEventListener("click",()=>{if(!state.loaded)return;guide("creating");status.textContent="L’IA sta cercando i momenti migliori…";send("create",{engine:state.engine,duration:state.duration})});'
    text = replace_once(text, anchor, anchor + '\n' + CLOSE_BINDINGS, 'create handler')
    return text


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_AI
    if not target.exists():
        raise SystemExit(f'V309 target missing: {target}')
    before = target.read_text(encoding='utf-8')
    after = patch_ai_text(before)
    target.write_text(after, encoding='utf-8')
    print('V309 mobile AI flow applied:', target, 'changed=', after != before, flush=True)


if __name__ == '__main__':
    main()
