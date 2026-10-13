#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


MARKER = "__GSF_AI_MONUMENT_V397"

INJECTION = r'''
<!-- __GSF_AI_MONUMENT_V397 -->
<style id="gsfAiMonumentV397Style">
  #ng27 #stage{position:relative;touch-action:none}
  #ng27 #aiMonumentV397{
    position:absolute;right:12px;top:12px;z-index:48;width:52px;height:52px;
    border:1px solid rgba(255,255,255,.72);border-radius:999px;padding:0;
    background:radial-gradient(circle at 34% 28%,rgba(255,255,255,.96),rgba(187,229,255,.92) 46%,rgba(154,210,255,.82) 72%,rgba(255,221,116,.82));
    box-shadow:0 10px 30px rgba(72,151,207,.22),inset 0 0 0 5px rgba(255,255,255,.24);
    color:#173449;font:800 12px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    letter-spacing:.04em;display:grid;place-items:center;cursor:pointer;-webkit-tap-highlight-color:transparent;
    transition:transform .18s ease,box-shadow .18s ease,opacity .18s ease;
  }
  #ng27 #aiMonumentV397:active{transform:scale(.92)}
  #ng27 #aiMonumentV397.ai-live{box-shadow:0 0 0 5px rgba(143,219,255,.18),0 12px 34px rgba(72,151,207,.28);animation:gsfAiPulseV397 2.4s ease-in-out infinite}
  #ng27 #aiMonumentV397::after{content:"AI"}
  #ng27 .railBtn span{font-size:max(10px,.68rem);font-weight:750;letter-spacing:.045em}
  #ng27 .panelNote,#ng27 .range span,#ng27 .strip .pill{font-size:max(11px,.72rem)}
  @keyframes gsfAiPulseV397{0%,100%{transform:scale(1)}50%{transform:scale(1.055)}}
  @media (prefers-reduced-motion:reduce){#ng27 #aiMonumentV397.ai-live{animation:none}}
</style>
<script id="gsfAiMonumentV397Script">
(() => {
  const pinch = {active:false,startDistance:0,startZoom:1};
  const doubleTap = {last:0};
  let pan = null;

  const clamp = (v,a,b) => Math.max(a,Math.min(b,v));
  const stageEl = () => document.getElementById('stage');
  const safeApply = () => { if(typeof applyState === 'function') applyState(); };
  const safeCommit = () => { if(typeof commit === 'function') commit(); };
  const safeFlash = (msg) => { if(typeof flash === 'function') flash(msg); };

  function setAiVisual(){
    const orb=document.getElementById('aiMonumentV397');
    if(!orb || typeof state === 'undefined')return;
    orb.classList.toggle('ai-live',String(state.aiMode||'Off')!=='Off');
    orb.setAttribute('aria-pressed',String(String(state.aiMode||'Off')!=='Off'));
    orb.title=String(state.aiMode||'Off')==='Off'?'Attiva AI Auto Gaming':'AI attiva · '+String(state.aiMode||'Auto Gaming');
  }

  function activateAiFraming(){
    if(typeof state === 'undefined')return;
    state.aiMode='Auto Gaming';
    state.visionEnabled=true;
    state.hudMode='Smart Safe';
    state.audioMode='Game Boost';
    state.muted=false;
    state.framePreset='gameplay';
    state.zoom=Math.max(1.08,Math.min(1.34,Number(state.zoom)||1.12));
    if(typeof visionPrimary !== 'undefined' && visionPrimary && Number(visionPrimary.confidence)>=.18){
      state.panX=clamp((Number(visionPrimary.x)-50)*.34,-18,18);
      state.panY=clamp((Number(visionPrimary.y)-46)*.30,-16,16);
    }
    safeApply();safeCommit();setAiVisual();safeFlash('AI · INQUADRATURA GAMING');
  }

  function distance(a,b){
    const dx=a.clientX-b.clientX,dy=a.clientY-b.clientY;
    return Math.sqrt(dx*dx+dy*dy);
  }

  function install(){
    const stage=stageEl();
    if(!stage || stage.dataset.aiMonumentV397==='1')return;
    stage.dataset.aiMonumentV397='1';

    const orb=document.createElement('button');
    orb.id='aiMonumentV397';
    orb.type='button';
    orb.setAttribute('aria-label','Assistente AI Auto Gaming');
    orb.onclick=(ev)=>{ev.preventDefault();ev.stopPropagation();activateAiFraming();};
    stage.appendChild(orb);
    setAiVisual();

    stage.addEventListener('touchstart',(ev)=>{
      if(ev.target && ev.target.closest && ev.target.closest('button,input,select,textarea'))return;
      if(typeof state === 'undefined')return;
      if(ev.touches.length===2){
        pinch.active=true;
        pinch.startDistance=Math.max(1,distance(ev.touches[0],ev.touches[1]));
        pinch.startZoom=Number(state.zoom)||1;
        pan=null;
        ev.preventDefault();
        return;
      }
      if(ev.touches.length===1){
        const now=Date.now();
        if(now-doubleTap.last<300){
          doubleTap.last=0;
          activateAiFraming();
          ev.preventDefault();
          return;
        }
        doubleTap.last=now;
        const t=ev.touches[0];
        pan={x:t.clientX,y:t.clientY,panX:Number(state.panX)||0,panY:Number(state.panY)||0,moved:false};
      }
    },{passive:false});

    stage.addEventListener('touchmove',(ev)=>{
      if(typeof state === 'undefined')return;
      if(pinch.active && ev.touches.length===2){
        const d=Math.max(1,distance(ev.touches[0],ev.touches[1]));
        state.zoom=clamp(pinch.startZoom*(d/pinch.startDistance),.8,2);
        safeApply();
        ev.preventDefault();
        return;
      }
      if(pan && ev.touches.length===1){
        const rect=stage.getBoundingClientRect();
        const t=ev.touches[0];
        const dx=t.clientX-pan.x,dy=t.clientY-pan.y;
        if(Math.abs(dx)+Math.abs(dy)>3)pan.moved=true;
        state.panX=clamp(pan.panX+(dx/Math.max(1,rect.width))*100,-25,25);
        state.panY=clamp(pan.panY+(dy/Math.max(1,rect.height))*100,-25,25);
        state.framePreset='free';
        safeApply();
        ev.preventDefault();
      }
    },{passive:false});

    stage.addEventListener('touchend',(ev)=>{
      if(pinch.active && ev.touches.length<2){pinch.active=false;safeCommit();safeFlash('PINCH · ZOOM SALVATO');}
      if(pan && ev.touches.length===0){if(pan.moved){safeCommit();safeFlash('TOUCH · FRAME SALVATO');}pan=null;}
      setAiVisual();
    },{passive:true});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
  else install();
  setTimeout(install,120);
})();
</script>
'''


def resolve_target(argv) -> Path:
    if len(argv) > 1:
        return Path(argv[1])
    app = Path("/app/web/editor_2027_component/index.html")
    if app.is_file():
        return app
    return Path(__file__).resolve().parent / "editor_2027_component" / "index.html"


def main(argv=None):
    argv=list(sys.argv if argv is None else argv)
    path=resolve_target(argv)
    text=path.read_text(encoding="utf-8")
    if MARKER in text:
        print("V397 AI monument restart-safe: already installed", path)
        return 0
    anchor="</body>"
    if anchor not in text:
        raise RuntimeError("V397 editor body anchor missing")
    text=text.replace(anchor,INJECTION+"\n"+anchor,1)
    path.write_text(text,encoding="utf-8")
    print("V397 AI monument installed:",path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
