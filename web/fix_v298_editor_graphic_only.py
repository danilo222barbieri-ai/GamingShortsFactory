#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
EDITOR = ROOT / 'web' / 'editor_2027_component' / 'index.html'
EMBED = ROOT / 'web' / 'editor_2027_embed.py'

CSS = r'''
/* V298 EDITOR GRAPHIC ONLY */
@media (min-width:1024px){
  #ng27[data-v298-layout="graphic-only"]{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    overflow:hidden!important;
    background:
      radial-gradient(circle at 50% 35%,rgba(183,228,255,.34),transparent 46%),
      radial-gradient(circle at 12% 50%,rgba(210,244,255,.26),transparent 34%),
      radial-gradient(circle at 88% 48%,rgba(205,241,255,.26),transparent 34%),
      linear-gradient(180deg,#FBFDFF 0%,#F4FAFF 100%)!important;
  }
  #ng27[data-v298-layout="graphic-only"] .shell{
    width:100%!important;
    max-width:1680px!important;
    height:100%!important;
    min-height:0!important;
    margin:0 auto!important;
    padding:8px 14px 8px!important;
    border-radius:0!important;
    background:transparent!important;
    overflow:hidden!important;
    display:flex!important;
    flex-direction:column!important;
    justify-content:flex-start!important;
  }
  #ng27[data-v298-layout="graphic-only"] .topline{
    flex:0 0 40px!important;
    min-height:40px!important;
    padding:0 4px 4px!important;
  }
  #ng27[data-v298-layout="graphic-only"] .topline:before{
    content:"MODIFICA IL TUO GAMEPLAY"!important;
    font-size:12px!important;
    letter-spacing:.18em!important;
    color:#6484A8!important;
    font-weight:900!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v297EditorGrid,
  #ng27[data-v298-layout="graphic-only"] .v297EditorSidebar{
    display:none!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorWorkspace{
    flex:1 1 auto;
    min-height:0;
    width:100%;
    display:grid;
    grid-template-columns:clamp(76px,6vw,108px) clamp(92px,7.5vw,132px) minmax(0,1fr) clamp(92px,7.5vw,132px) clamp(76px,6vw,108px);
    gap:clamp(8px,.9vw,14px);
    align-items:center;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorCore{
    min-width:0;
    min-height:0;
    height:100%;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    gap:7px;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorTop{
    width:100%;
    min-width:0;
    min-height:0;
    display:grid;
    grid-template-columns:minmax(260px,1fr) minmax(220px,292px);
    gap:14px;
    align-items:center;
  }
  #ng27[data-v298-layout="graphic-only"] .v297EditorCenter{
    min-width:0!important;
    min-height:0!important;
    width:100%!important;
    height:auto!important;
    display:grid!important;
    place-items:center!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v297EditorCenter .stageWrap{
    width:100%!important;
    height:auto!important;
    display:grid!important;
    place-items:center!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v297EditorCenter .stage.r916{
    width:clamp(250px,calc(58vh * .5625),350px)!important;
    max-width:100%!important;
    max-height:58vh!important;
    border-radius:27px!important;
    box-shadow:0 24px 58px rgba(42,101,145,.18),0 0 0 1px rgba(112,191,235,.14)!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMoments{
    align-self:center!important;
    width:100%!important;
    display:grid!important;
    grid-template-columns:1fr!important;
    gap:9px!important;
    padding:12px!important;
    border:1px solid rgba(143,181,216,.24)!important;
    border-radius:25px!important;
    background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(240,249,255,.88))!important;
    box-shadow:0 16px 38px rgba(61,104,145,.09),inset 0 1px 0 #fff!important;
    backdrop-filter:blur(16px)!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMoments h3{
    margin:0!important;
    font-size:16px!important;
    color:#173F73!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMoments>p{
    margin:-3px 0 2px!important;
    font-size:8.5px!important;
    color:#7B91AA!important;
    font-weight:750!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v297MomentCard{
    position:relative!important;
    min-height:76px!important;
    padding:9px 9px 9px 78px!important;
    border-radius:17px!important;
    background:linear-gradient(145deg,#FFFFFF,#F1F8FF)!important;
    border:1px solid rgba(143,181,216,.24)!important;
    overflow:hidden!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v297MomentCard.active{
    border-color:#69C8F5!important;
    box-shadow:0 0 0 3px rgba(91,188,241,.12)!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298MomentThumb{
    position:absolute;
    left:8px;
    top:8px;
    bottom:8px;
    width:60px;
    border-radius:12px;
    background:
      linear-gradient(135deg,rgba(54,137,197,.14),rgba(80,190,243,.28)),
      radial-gradient(circle at 65% 35%,rgba(255,255,255,.92),transparent 24%),
      linear-gradient(160deg,#B9DCF2,#EAF7FF 48%,#B6E4F7);
    box-shadow:inset 0 0 0 1px rgba(113,181,222,.18);
  }
  #ng27[data-v298-layout="graphic-only"] .v298MomentThumb:after{
    content:attr(data-rank);
    position:absolute;
    right:5px;
    bottom:4px;
    width:18px;
    height:18px;
    display:grid;
    place-items:center;
    border-radius:50%;
    background:rgba(255,255,255,.88);
    color:#2B75B8;
    font-size:8px;
    font-weight:950;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorTimeline{
    width:min(100%,820px)!important;
    height:auto!important;
    min-height:70px!important;
    margin:0 auto!important;
    display:grid!important;
    place-items:center!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorTimeline .timeline{
    width:100%!important;
    margin:0!important;
    border-radius:17px!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorToolbar{
    width:min(100%,860px);
    min-height:58px;
    display:flex;
    align-items:center;
    justify-content:center;
    gap:5px;
    padding:6px 7px;
    border:1px solid rgba(143,181,216,.24);
    border-radius:20px;
    background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(238,248,255,.90));
    box-shadow:0 12px 28px rgba(61,104,145,.08),inset 0 1px 0 #fff;
    backdrop-filter:blur(16px);
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorToolbar .railBtn{
    flex:1 1 0!important;
    width:auto!important;
    min-width:42px!important;
    max-width:72px!important;
    height:48px!important;
    min-height:48px!important;
    border-radius:13px!important;
    padding:5px 3px!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorToolbar .railBtn .ico{
    width:20px!important;
    height:20px!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorToolbar .railBtn span{
    font-size:7.2px!important;
    line-height:1!important;
  }
  #ng27[data-v298-layout="graphic-only"] .createShortJourney{
    width:min(100%,420px)!important;
    margin:0 auto!important;
  }
  #ng27[data-v298-layout="graphic-only"] .createShortJourneyBtn{
    min-height:44px!important;
    border-radius:17px!important;
    font-size:10px!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorAd{
    height:clamp(330px,56vh,520px);
    border:1px solid rgba(143,181,216,.20);
    border-radius:28px;
    background:linear-gradient(180deg,rgba(255,255,255,.86),rgba(233,247,255,.70));
    box-shadow:0 16px 38px rgba(64,108,148,.07),inset 0 1px 0 rgba(255,255,255,.95);
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    gap:16px;
    overflow:hidden;
    color:#8AA0B8;
    backdrop-filter:blur(14px);
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorAd small{
    font-size:7px;
    font-weight:900;
    letter-spacing:.16em;
    text-transform:uppercase;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorAd b{
    writing-mode:vertical-rl;
    transform:rotate(180deg);
    font-size:18px;
    letter-spacing:.24em;
    color:#B3C8DA;
    font-weight:900;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMuralSlot{
    min-height:330px;
    height:56vh;
    max-height:520px;
    display:flex;
    align-items:center;
    justify-content:center;
    overflow:visible;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMural,
  #ng27[data-v298-layout="graphic-only"] .v298EditorMuralSlot .gsfGuide{
    position:static!important;
    inset:auto!important;
    display:block!important;
    width:100%!important;
    color:#6587AD!important;
    font-family:"Comic Sans MS","Bradley Hand",cursive!important;
    font-size:clamp(14px,1.15vw,18px)!important;
    font-weight:700!important;
    line-height:1.15!important;
    text-align:center!important;
    transform:rotate(-4deg)!important;
    pointer-events:none!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMuralRight{
    transform:rotate(4deg)!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v298EditorMural .arr,
  #ng27[data-v298-layout="graphic-only"] .v298EditorMuralSlot .gsfGuide .arr{
    display:block!important;
    margin-top:7px!important;
    font-size:30px!important;
    line-height:.8!important;
    color:#78A7D4!important;
  }
  #ng27[data-v298-layout="graphic-only"] .footNote{
    display:none!important;
  }
}
@media (min-width:1024px) and (max-height:800px){
  #ng27[data-v298-layout="graphic-only"] .v297EditorCenter .stage.r916{
    width:clamp(238px,calc(54vh * .5625),305px)!important;
    max-height:54vh!important;
  }
  #ng27[data-v298-layout="graphic-only"] .v297MomentCard{min-height:66px!important}
  #ng27[data-v298-layout="graphic-only"] .v298EditorAd,
  #ng27[data-v298-layout="graphic-only"] .v298EditorMuralSlot{height:52vh!important}
}
/* END V298 EDITOR GRAPHIC ONLY */
'''

JS = r'''
<script id="v298EditorGraphicOnly">
(()=>{
  if(!window.matchMedia('(min-width:1024px)').matches)return;
  const root=document.getElementById('ng27');
  const shell=root&&root.querySelector('.shell');
  const grid=root&&root.querySelector('.v297EditorGrid');
  if(!root||!shell||!grid||root.querySelector('.v298EditorWorkspace'))return;

  const side=grid.querySelector('.v297EditorSidebar');
  const center=grid.querySelector('.v297EditorCenter');
  const moments=grid.querySelector('.v297EditorMoments');
  const timeline=shell.querySelector('.v297EditorTimeline');
  const cta=shell.querySelector('.createShortJourney');
  if(!side||!center||!moments||!timeline)return;

  const workspace=document.createElement('section');
  workspace.className='v298EditorWorkspace';

  const adLeft=document.createElement('aside');
  adLeft.className='v298EditorAd v298EditorAdLeft';
  adLeft.innerHTML='<small>Pubblicità</small><b>PUB</b>';

  const leftMuralSlot=document.createElement('div');
  leftMuralSlot.className='v298EditorMuralSlot v298EditorMuralLeft';
  const guide=shell.querySelector('.gsfGuide');
  if(guide){leftMuralSlot.append(guide)}
  else{leftMuralSlot.innerHTML='<div class="v298EditorMural">Tocca il video e personalizzalo<span class="arr">↝</span></div>'}

  const core=document.createElement('section');
  core.className='v298EditorCore';
  const top=document.createElement('div');
  top.className='v298EditorTop';
  core.append(top);
  top.append(center,moments);

  moments.classList.add('v298EditorMoments');
  const momentsTitle=moments.querySelector('h3');
  const momentsCopy=moments.querySelector('p');
  if(momentsTitle)momentsTitle.textContent='I 3 MIGLIORI';
  if(momentsCopy)momentsCopy.textContent='I momenti più forti del tuo gameplay';
  [...moments.querySelectorAll('.v297MomentCard')].slice(0,3).forEach((card,index)=>{
    card.dataset.v298Moment=String(index+1);
    if(!card.querySelector('.v298MomentThumb')){
      const thumb=document.createElement('span');
      thumb.className='v298MomentThumb';
      thumb.dataset.rank=String(index+1);
      card.prepend(thumb);
    }
  });

  timeline.classList.add('v298EditorTimeline');
  core.append(timeline);

  const toolbar=document.createElement('nav');
  toolbar.className='v298EditorToolbar';
  toolbar.setAttribute('aria-label','Strumenti Game Editor');
  const desired=[
    '[data-panel="frame"]','[data-panel="caption"]','[data-panel="look"]','[data-panel="audio"]','[data-panel="vision"]',
    '[data-panel="cover"]','[data-panel="hud"]','#playBtn','#undoBtn','#redoBtn','#doneBtn'
  ];
  const all=[...side.querySelectorAll('.railBtn')];
  desired.forEach(selector=>{const btn=side.querySelector(selector);if(btn)toolbar.append(btn)});
  all.forEach(btn=>{if(!toolbar.contains(btn))toolbar.append(btn)});
  const aiLabel=toolbar.querySelector('[data-panel="vision"] span');
  if(aiLabel)aiLabel.textContent='AI';
  core.append(toolbar);
  if(cta)core.append(cta);

  const rightMuralSlot=document.createElement('div');
  rightMuralSlot.className='v298EditorMuralSlot';
  rightMuralSlot.innerHTML='<div class="v298EditorMural v298EditorMuralRight">I tuoi 3 momenti migliori sono qui<span class="arr">↜</span></div>';

  const adRight=document.createElement('aside');
  adRight.className='v298EditorAd v298EditorAdRight';
  adRight.innerHTML='<small>Pubblicità</small><b>PUB</b>';

  grid.insertAdjacentElement('beforebegin',workspace);
  workspace.append(adLeft,leftMuralSlot,core,rightMuralSlot,adRight);
  grid.remove();
})();
</script>
'''


def patch_editor_text(text: str) -> str:
    if 'V298 EDITOR GRAPHIC ONLY' in text:
        return text
    if 'V297 DESK REBUILD — EDITOR' not in text or 'v297EditorRuntime' not in text:
        raise RuntimeError('V298 requires the V297 desktop Editor structure first')

    m = re.search(r'<div id="ng27"[^>]*>', text)
    if not m:
        raise RuntimeError('V298 editor root anchor missing')
    tag = m.group(0)
    if 'data-v298-layout=' not in tag:
        new_tag = tag[:-1] + ' data-v298-layout="graphic-only">'
        text = text.replace(tag, new_tag, 1)

    style_pos = text.rfind('</style>')
    if style_pos < 0:
        raise RuntimeError('V298 editor style anchor missing')
    text = text[:style_pos] + CSS + '\n' + text[style_pos:]

    if '</body>' not in text:
        raise RuntimeError('V298 editor body anchor missing')
    text = text.replace('</body>', JS + '\n</body>', 1)
    return text


def patch_embed_text(text: str) -> str:
    if '"gsf_editor_2027_v298"' in text:
        return text
    patched, count = re.subn(r'"gsf_editor_2027_v\d+"', '"gsf_editor_2027_v298"', text, count=1)
    if count != 1:
        raise RuntimeError('V298 editor cache key anchor missing')
    return patched


def main() -> None:
    if not EDITOR.is_file() or not EMBED.is_file():
        raise RuntimeError('V298 required Editor files missing')
    before = EDITOR.read_text(encoding='utf-8')
    after = patch_editor_text(before)
    EDITOR.write_text(after, encoding='utf-8')

    embed_before = EMBED.read_text(encoding='utf-8')
    embed_after = patch_embed_text(embed_before)
    EMBED.write_text(embed_after, encoding='utf-8')

    print('V298 graphic-only Editor applied:', EDITOR, 'changed=', after != before, flush=True)
    print('V298 Editor cache key:', 'changed=' + str(embed_after != embed_before), flush=True)


if __name__ == '__main__':
    main()
