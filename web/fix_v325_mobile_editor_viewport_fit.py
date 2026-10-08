#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v325MobileEditorViewportFit'
SCRIPT_ID='v325MobileEditorReferenceLayout'
OLD_MOBILE_HEIGHT='if(pw<=820){setFrameHeight(Math.max(720,Math.ceil(document.documentElement.scrollHeight||720)));return}'
NEW_MOBILE_HEIGHT='if(pw<=820){const ph=Math.max(560,Number(window.parent.innerHeight||window.innerHeight||760));setFrameHeight(Math.max(500,Math.min(710,Math.floor(ph-145))));return}'

STYLE=r'''<style id="v325MobileEditorViewportFit">
/* V325 approved mobile reference: PLAYER -> ACTIONS -> TIMELINE. Desktop untouched. */
@media(max-width:760px){
  #ng27{
    width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
    overflow:hidden!important;padding:0 7px 2px!important;border-radius:0!important;
    background:radial-gradient(circle at 50% 8%,rgba(198,233,249,.92),transparent 37%),linear-gradient(180deg,#F8FDFF 0%,#EEF7FC 100%)!important;
  }
  #ng27 .shell{
    width:100%!important;height:100%!important;min-height:0!important;max-width:none!important;
    margin:0!important;padding:0!important;display:flex!important;flex-direction:column!important;
    justify-content:flex-start!important;align-items:stretch!important;overflow:hidden!important;
  }
  #ng27 .topline,#ng27 .gsfGuide,#ng27 .footNote{display:none!important}

  #ng27 .cockpit,#ng27.expanded .cockpit{
    position:relative!important;width:100%!important;max-width:430px!important;height:auto!important;min-height:0!important;
    margin:0 auto!important;padding:0 1px 2px!important;
    display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:auto auto auto!important;
    gap:8px!important;align-items:start!important;align-content:start!important;justify-items:stretch!important;
    overflow:visible!important;
  }

  /* Player: compact enough to leave room for the real workflow and timeline. */
  #ng27 .stageWrap{
    grid-column:1!important;grid-row:1!important;justify-self:center!important;
    position:relative!important;width:min(calc(100% - 18px),292px,calc((100dvh - 150px)*.5625))!important;
    height:auto!important;min-height:0!important;max-height:none!important;
    margin:0 auto!important;padding:0!important;display:block!important;overflow:visible!important;
  }
  #ng27 .stage.r916,#ng27.expanded .stage.r916{
    position:relative!important;display:block!important;width:100%!important;max-width:none!important;height:auto!important;
    aspect-ratio:9/16!important;margin:0!important;border-radius:22px!important;overflow:hidden!important;
    border:1px solid rgba(137,210,240,.46)!important;
    box-shadow:0 13px 32px rgba(44,102,139,.16),0 0 0 6px rgba(255,255,255,.38)!important;
  }

  /* Actual editor controls are moved into #stage by V325 JS. */
  #ng27 .stage>.rail.v325Rail{
    position:absolute!important;top:50%!important;z-index:86!important;width:auto!important;height:auto!important;
    margin:0!important;padding:0!important;display:flex!important;flex-direction:column!important;gap:8px!important;
    transform:translateY(-50%)!important;pointer-events:none!important;
  }
  #ng27 .stage>.rail.v325LeftRail{left:8px!important}
  #ng27 .stage>.rail.v325RightRail{right:8px!important}
  #ng27 .stage>.rail.v325Rail .railBtn{
    pointer-events:auto!important;display:flex!important;width:48px!important;height:58px!important;min-width:48px!important;min-height:58px!important;
    padding:0!important;border-radius:17px!important;border:1px solid rgba(255,255,255,.64)!important;
    background:linear-gradient(145deg,rgba(25,49,77,.66),rgba(36,63,94,.48))!important;
    color:#fff!important;box-shadow:0 7px 19px rgba(8,24,39,.20),inset 0 1px 0 rgba(255,255,255,.24)!important;
    -webkit-backdrop-filter:blur(14px) saturate(1.12)!important;backdrop-filter:blur(14px) saturate(1.12)!important;
  }
  #ng27 .stage>.rail.v325Rail .railBtn .ico{width:21px!important;height:21px!important;color:#fff!important}
  #ng27 .stage>.rail.v325Rail .railBtn span{font-size:7.4px!important;line-height:1!important;color:#fff!important;text-shadow:0 1px 4px rgba(0,0,0,.3)!important}
  #ng27 .stage>.rail.v325Rail .railBtn.active{background:linear-gradient(145deg,rgba(72,168,236,.88),rgba(61,119,211,.78))!important}

  /* Central playback dock lives inside the player, like the approved reference. */
  #ng27 .v325PlaybackDock{
    position:absolute!important;left:50%!important;bottom:27px!important;z-index:91!important;
    transform:translateX(-50%)!important;display:flex!important;align-items:center!important;gap:12px!important;
  }
  #ng27 .v325Skip{
    width:28px!important;height:34px!important;border:0!important;background:transparent!important;color:#fff!important;
    font-size:23px!important;font-weight:900!important;text-shadow:0 2px 8px rgba(0,0,0,.45)!important;padding:0!important;
  }
  #ng27 #playBtn.v325PlayerPlay{
    display:grid!important;place-items:center!important;position:relative!important;width:58px!important;height:58px!important;
    min-width:58px!important;min-height:58px!important;border-radius:50%!important;padding:0!important;
    border:1px solid rgba(255,255,255,.78)!important;background:linear-gradient(145deg,rgba(67,164,240,.96),rgba(55,111,218,.94))!important;
    color:#fff!important;box-shadow:0 9px 24px rgba(17,50,94,.32),inset 0 1px 0 rgba(255,255,255,.35)!important;
  }
  #ng27 #playBtn.v325PlayerPlay .ico{width:27px!important;height:27px!important;color:#fff!important}
  #ng27 #playBtn.v325PlayerPlay span{display:none!important}

  #ng27 .v325PlayerMeta{position:absolute!important;top:10px!important;left:10px!important;right:10px!important;z-index:89!important;display:flex!important;align-items:center!important;pointer-events:none!important}
  #ng27 .v325TimeChip,#ng27 .v325RatioChip{
    height:29px!important;display:flex!important;align-items:center!important;padding:0 9px!important;border-radius:12px!important;
    color:#fff!important;background:rgba(20,42,68,.60)!important;border:1px solid rgba(255,255,255,.32)!important;
    -webkit-backdrop-filter:blur(13px)!important;backdrop-filter:blur(13px)!important;box-shadow:0 5px 12px rgba(6,20,34,.14)!important;
    font-size:8.6px!important;font-weight:900!important;letter-spacing:.02em!important;
  }
  #ng27 .v325RatioChip{margin-left:auto!important;margin-right:46px!important}
  #ng27 #zoomEditorBtn.v323InsidePlayer{
    display:flex!important;position:absolute!important;top:10px!important;right:10px!important;z-index:93!important;
    width:38px!important;min-width:38px!important;height:38px!important;padding:0!important;border-radius:12px!important;
    border:1px solid rgba(255,255,255,.66)!important;background:rgba(20,42,68,.60)!important;color:#fff!important;
  }
  #ng27 #zoomEditorBtn.v323InsidePlayer span{display:none!important}
  #ng27 #zoomEditorBtn.v323InsidePlayer .ico{width:19px!important;height:19px!important;color:#fff!important;margin:auto!important}
  #ng27 .captionPreview.v325DefaultCaption{display:none!important}

  /* Two real project actions directly under the player. */
  #ng27 .cockpit>.v323EditorActions{
    grid-column:1!important;grid-row:2!important;position:relative!important;z-index:80!important;
    width:100%!important;max-width:430px!important;min-width:0!important;margin:0!important;padding:0!important;
    display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:8px!important;
  }
  #ng27 .cockpit>.v323EditorActions .v323EditorAction{
    width:100%!important;min-width:0!important;min-height:48px!important;padding:8px 8px!important;border-radius:16px!important;
    font-size:9.4px!important;line-height:1.05!important;white-space:normal!important;font-weight:950!important;
  }

  /* Timeline is a real third row below actions, never detached at the phone bottom. */
  #ng27 .cockpit>.timeline.v325DetachedTimeline{
    grid-column:1!important;grid-row:3!important;position:relative!important;left:auto!important;right:auto!important;bottom:auto!important;top:auto!important;
    z-index:70!important;width:100%!important;max-width:430px!important;height:auto!important;margin:0!important;padding:9px 10px 8px!important;
    transform:none!important;border-radius:18px!important;border:1px solid rgba(151,187,216,.25)!important;
    background:rgba(255,255,255,.72)!important;box-shadow:0 8px 20px rgba(79,118,157,.08),inset 0 1px 0 rgba(255,255,255,.82)!important;
    -webkit-backdrop-filter:blur(14px)!important;backdrop-filter:blur(14px)!important;
  }
  #ng27 .cockpit>.timeline.v325DetachedTimeline .tlMeta{margin:0 2px 7px!important;color:#6c81a1!important;font-size:8.2px!important}
  #ng27 .cockpit>.timeline.v325DetachedTimeline .tlMeta span:nth-child(2){
    display:flex!important;align-items:center!important;justify-content:center!important;min-height:26px!important;padding:0 9px!important;
    border-radius:13px!important;background:rgba(191,244,229,.58)!important;color:#277a72!important;font-size:0!important;letter-spacing:0!important;
  }
  #ng27 .cockpit>.timeline.v325DetachedTimeline .tlMeta span:nth-child(2):after{content:"CC  Caption AUTO ✓";font-size:8.1px!important;font-weight:900!important}
  #ng27 .cockpit>.timeline.v325DetachedTimeline .track{
    height:48px!important;border-radius:11px!important;border:1px solid rgba(82,160,221,.36)!important;overflow:hidden!important;
    background:
      linear-gradient(180deg,rgba(98,186,239,.18),rgba(78,145,211,.10)),
      repeating-linear-gradient(90deg,rgba(77,150,210,.14) 0 34px,rgba(255,255,255,.40) 34px 36px)!important;
  }
  #ng27 .cockpit>.timeline.v325DetachedTimeline .track:after{
    content:""!important;position:absolute!important;left:4px!important;right:4px!important;bottom:4px!important;height:9px!important;opacity:.60!important;pointer-events:none!important;
    background:repeating-linear-gradient(90deg,rgba(79,169,225,.66) 0 2px,transparent 2px 5px)!important;
    clip-path:polygon(0 60%,4% 30%,8% 70%,12% 25%,16% 75%,20% 42%,24% 66%,28% 20%,32% 78%,36% 36%,40% 68%,44% 28%,48% 76%,52% 35%,56% 64%,60% 22%,64% 73%,68% 31%,72% 69%,76% 27%,80% 72%,84% 40%,88% 64%,92% 32%,96% 68%,100% 50%,100% 100%,0 100%)!important;
  }
  #ng27 .cockpit>.timeline.v325DetachedTimeline .trimRow{margin-top:6px!important;color:#69819d!important;font-size:7.7px!important;gap:3px!important}

  /* Fullscreen keeps the editing controls with the video. */
  #ng27.gsfFullscreen .stage>.rail.v325Rail,#ng27:fullscreen .stage>.rail.v325Rail,#ng27:-webkit-full-screen .stage>.rail.v325Rail{position:absolute!important}
  #ng27.gsfFullscreen .v325PlaybackDock,#ng27:fullscreen .v325PlaybackDock,#ng27:-webkit-full-screen .v325PlaybackDock{bottom:max(28px,env(safe-area-inset-bottom))!important}
}

@media(max-width:390px) and (max-height:700px){
  #ng27{padding-left:5px!important;padding-right:5px!important}
  #ng27 .cockpit,#ng27.expanded .cockpit{gap:6px!important}
  #ng27 .stageWrap{width:min(calc(100% - 20px),252px,calc((100dvh - 132px)*.5625))!important}
  #ng27 .stage>.rail.v325Rail{gap:5px!important}
  #ng27 .stage>.rail.v325Rail .railBtn{width:42px!important;height:48px!important;min-width:42px!important;min-height:48px!important;border-radius:14px!important}
  #ng27 .stage>.rail.v325Rail .railBtn .ico{width:18px!important;height:18px!important}
  #ng27 .v325PlaybackDock{bottom:22px!important;gap:9px!important}
  #ng27 #playBtn.v325PlayerPlay{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important}
  #ng27 .cockpit>.v323EditorActions{gap:6px!important}
  #ng27 .cockpit>.v323EditorActions .v323EditorAction{min-height:43px!important;font-size:8.3px!important}
  #ng27 .cockpit>.timeline.v325DetachedTimeline{padding:7px 8px 6px!important;border-radius:15px!important}
  #ng27 .cockpit>.timeline.v325DetachedTimeline .track{height:38px!important}
  #ng27 .cockpit>.timeline.v325DetachedTimeline .trimRow{display:none!important}
}
</style>'''

SCRIPT=r'''<script id="v325MobileEditorReferenceLayout">
/* V325 approved-reference mobile DOM placement. Existing handlers are preserved. */
(function(){
  const root=document.getElementById('ng27');
  if(!root)return;
  const cockpit=root.querySelector('.cockpit');
  const stageWrap=root.querySelector('.stageWrap');
  const stage=root.querySelector('#stage');
  const timeline=root.querySelector('.timeline');
  const actions=root.querySelector('#v323EditorActions');
  const video=root.querySelector('#video');
  const playBtn=root.querySelector('#playBtn');
  const caption=root.querySelector('#captionPreview');
  if(!cockpit||!stageWrap||!stage||!timeline||!actions||!playBtn)return;

  const directRails=Array.from(cockpit.children).filter(n=>n&&n.classList&&n.classList.contains('rail'));
  const leftRail=directRails[0]||root.querySelector('.rail');
  const rightRail=directRails[directRails.length-1]||null;
  if(!leftRail||!rightRail)return;
  const audioBtn=leftRail.querySelector('[data-panel="audio"]');

  const homes={
    left:{parent:leftRail.parentNode,next:leftRail.nextSibling},
    right:{parent:rightRail.parentNode,next:rightRail.nextSibling},
    audio:audioBtn?{parent:audioBtn.parentNode,next:audioBtn.nextSibling}:null,
    play:{parent:playBtn.parentNode,next:playBtn.nextSibling},
    timeline:{parent:timeline.parentNode,next:timeline.nextSibling}
  };
  function restore(node,home){
    if(!node||!home||!home.parent)return;
    if(home.next&&home.next.parentNode===home.parent)home.parent.insertBefore(node,home.next);else home.parent.appendChild(node);
  }
  function fmt(sec){sec=Math.max(0,Number(sec)||0);const m=Math.floor(sec/60),s=Math.floor(sec%60);return String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')}
  function ensureMeta(){
    let meta=stage.querySelector('.v325PlayerMeta');
    if(!meta){meta=document.createElement('div');meta.className='v325PlayerMeta';meta.innerHTML='<span class="v325TimeChip" id="v325TimeChip">00:00 / 00:15</span><span class="v325RatioChip">9:16</span>';stage.appendChild(meta)}
    return meta;
  }
  function ensureDock(){
    let dock=stage.querySelector('.v325PlaybackDock');
    if(!dock){
      dock=document.createElement('div');dock.className='v325PlaybackDock';dock.id='v325PlaybackDock';
      const prev=document.createElement('button');prev.type='button';prev.className='v325Skip';prev.setAttribute('aria-label','Indietro');prev.textContent='‹';
      const next=document.createElement('button');next.type='button';next.className='v325Skip';next.setAttribute('aria-label','Avanti');next.textContent='›';
      prev.onclick=()=>{if(video){const min=Number((root.querySelector('#inRange')||{}).value||0);video.currentTime=Math.max(min,(video.currentTime||0)-2)}};
      next.onclick=()=>{if(video){const out=Number((root.querySelector('#outRange')||{}).value||video.duration||15);video.currentTime=Math.min(out,(video.currentTime||0)+2)}};
      dock.appendChild(prev);dock.appendChild(playBtn);dock.appendChild(next);stage.appendChild(dock);
    }else if(playBtn.parentElement!==dock){dock.insertBefore(playBtn,dock.children[1]||null)}
    playBtn.classList.add('v325PlayerPlay');
    return dock;
  }
  function updateTime(){
    const chip=root.querySelector('#v325TimeChip');if(!chip)return;
    const out=Number((root.querySelector('#outRange')||{}).value||video&&video.duration||15);
    chip.textContent=fmt(video&&video.currentTime||0)+' / '+fmt(out);
  }
  function updateDefaultCaption(){
    if(!caption)return;
    const text=String(caption.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();
    caption.classList.toggle('v325DefaultCaption',text==='CAPTION AUTO');
  }
  function mobile(){return window.matchMedia('(max-width:760px)').matches}
  function place(){
    if(!mobile()){
      restore(playBtn,homes.play);playBtn.classList.remove('v325PlayerPlay');
      if(audioBtn)restore(audioBtn,homes.audio);
      leftRail.classList.remove('v325Rail','v325LeftRail');rightRail.classList.remove('v325Rail','v325RightRail');
      restore(leftRail,homes.left);restore(rightRail,homes.right);restore(timeline,homes.timeline);
      timeline.classList.remove('v325DetachedTimeline');
      const meta=stage.querySelector('.v325PlayerMeta');if(meta)meta.style.display='none';
      const dock=stage.querySelector('.v325PlaybackDock');if(dock)dock.style.display='none';
      return;
    }
    stage.appendChild(leftRail);stage.appendChild(rightRail);
    leftRail.classList.add('v325Rail','v325LeftRail');rightRail.classList.add('v325Rail','v325RightRail');
    if(audioBtn&&audioBtn.parentElement!==rightRail)rightRail.insertBefore(audioBtn,rightRail.firstChild);
    const dock=ensureDock();dock.style.display='flex';
    const meta=ensureMeta();meta.style.display='flex';
    if(timeline.parentElement!==cockpit)actions.insertAdjacentElement('afterend',timeline);
    else if(timeline.previousElementSibling!==actions)actions.insertAdjacentElement('afterend',timeline);
    timeline.classList.add('v325DetachedTimeline');
    updateTime();updateDefaultCaption();
    setTimeout(()=>window.dispatchEvent(new Event('resize')),20);
  }
  if(video){video.addEventListener('timeupdate',updateTime,{passive:true});video.addEventListener('loadedmetadata',updateTime,{passive:true})}
  const inR=root.querySelector('#inRange'),outR=root.querySelector('#outRange');
  if(inR)inR.addEventListener('input',updateTime,{passive:true});if(outR)outR.addEventListener('input',updateTime,{passive:true});
  if(caption)new MutationObserver(updateDefaultCaption).observe(caption,{childList:true,subtree:true,characterData:true});
  place();
  window.addEventListener('resize',()=>{clearTimeout(place.t);place.t=setTimeout(place,90)},{passive:true});
})();
</script>'''

def _clean(text:str)->str:
    text=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)
    text=re.sub(r'<script id="'+re.escape(SCRIPT_ID)+r'">.*?</script>\n?','',text,count=1,flags=re.DOTALL)
    return text

def patch_text(text:str)->str:
    if f'id="{STYLE_ID}"' in text and f'id="{SCRIPT_ID}"' in text and NEW_MOBILE_HEIGHT in text:
        return text
    for marker in ('id="ng27"','class="stageWrap"','class="timeline"','id="v323EditorActions"','id="playBtn"','data-panel="audio"','V324_EDITOR_ACTION_PLACEMENT'):
        if marker not in text:
            raise RuntimeError('V325 editor anchor missing: '+marker)
    out=_clean(text)
    if OLD_MOBILE_HEIGHT in out:
        out=out.replace(OLD_MOBILE_HEIGHT,NEW_MOBILE_HEIGHT,1)
    elif NEW_MOBILE_HEIGHT not in out:
        raise RuntimeError('V325 mobile frame-height anchor missing')
    if '</head>' not in out or '</body>' not in out:
        raise RuntimeError('V325 editor document anchors missing')
    out=out.replace('</head>',STYLE+'\n</head>',1)
    out=out.replace('</body>',SCRIPT+'\n</body>',1)
    return out

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/editor_2027_component/index.html')
    if not path.is_file(): raise SystemExit('V325 editor target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V325 approved mobile editor reference applied changed=',before!=after,flush=True)

if __name__=='__main__': main()
