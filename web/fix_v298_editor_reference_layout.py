#!/usr/bin/env python3
from pathlib import Path
import re

EDITOR = Path("/app/web/editor_2027_component/index.html")
EMBED = Path("/app/web/editor_2027_embed.py")
MARKER = "V298 EDITOR REFERENCE LAYOUT"

CSS = r'''
/* V298 EDITOR REFERENCE LAYOUT */
@media (min-width:761px){
 #ng27[data-v297-layout="editor"]{overflow:hidden!important;padding:10px 14px 8px!important;background:radial-gradient(circle at 50% 38%,rgba(185,232,255,.40),transparent 46%),linear-gradient(180deg,#FCFEFF 0%,#F5FAFE 100%)!important}
 #ng27 .shell{width:100%!important;max-width:1580px!important;height:100%!important;margin:0 auto!important;padding:4px 8px 6px!important;display:grid!important;grid-template-rows:auto minmax(0,1fr) auto auto!important;gap:7px!important;align-items:stretch!important;overflow:hidden!important;background:transparent!important}
 #ng27 .topline{min-height:30px!important;padding:0 5px 3px!important}
 #ng27 .topline:before{font-size:11px!important;letter-spacing:.24em!important}
 #ng27 .v297EditorGrid{display:none!important}
 #ng27 .v297EditorSidebar{display:none!important}
 #ng27 .v297EditorTimeline{display:none!important}
 #ng27 .v298EditorWorkspace{min-width:0;min-height:0;display:grid;grid-template-columns:clamp(92px,9vw,150px) minmax(360px,560px) minmax(250px,320px) clamp(92px,9vw,150px);gap:clamp(10px,1.25vw,20px);align-items:center;justify-content:center;overflow:visible}
 #ng27 .v298EditorAd{height:min(52vh,470px);min-height:300px;border:1px solid rgba(148,185,216,.28);border-radius:24px;background:linear-gradient(180deg,rgba(255,255,255,.93),rgba(235,247,255,.76));box-shadow:0 14px 34px rgba(67,108,145,.08),inset 0 1px 0 #fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;color:#9AAEC1;text-align:center;overflow:hidden}
 #ng27 .v298EditorAd:before{content:"";width:34px;height:1px;background:rgba(112,155,192,.25)}
 #ng27 .v298EditorAd span{font-size:8px;font-weight:950;letter-spacing:.18em;text-transform:uppercase}.v298EditorAd small{font-size:7px;font-weight:750;letter-spacing:.05em;opacity:.72}
 #ng27 .v298EditorCenter{position:relative;min-width:0;min-height:0;height:100%;display:grid;grid-template-rows:minmax(0,1fr) auto;gap:8px;align-items:center;justify-items:center;overflow:visible}
 #ng27 .v298EditorPlayer{position:relative;min-width:0;min-height:0;width:100%;height:100%;display:grid;place-items:center;overflow:visible}
 #ng27 .v298EditorPlayer .stageWrap{width:100%!important;height:100%!important;display:grid!important;place-items:center!important;overflow:visible!important}
 #ng27 .v298EditorPlayer .stage.r916{width:min(100%,clamp(292px,calc((100dvh - 330px) * .5625),372px))!important;max-height:58dvh!important;border-radius:26px!important;box-shadow:0 22px 52px rgba(41,91,132,.17),0 0 0 1px rgba(122,184,219,.16)!important}
 #ng27 .v298EditorMural{display:block!important;position:absolute!important;z-index:22!important;left:clamp(-158px,-10vw,-118px)!important;top:20%!important;width:145px!important;color:#6481A5!important;font-family:"Comic Sans MS","Bradley Hand",cursive!important;font-size:14px!important;font-weight:750!important;line-height:1.12!important;text-align:right!important;transform:rotate(-4deg)!important;pointer-events:none!important;text-shadow:0 1px 0 rgba(255,255,255,.9)!important}
 #ng27 .v298EditorTimeline{width:100%;max-width:560px;min-height:74px;display:grid;place-items:center;margin:0 auto}
 #ng27 .v298EditorTimeline .timeline{width:100%!important;margin:0!important;border-radius:16px!important}
 #ng27 .v298EditorMoments{align-self:center;display:grid;grid-template-rows:auto auto repeat(3,minmax(78px,1fr));gap:9px;padding:14px;border:1px solid rgba(143,181,216,.27);border-radius:26px;background:rgba(255,255,255,.88);box-shadow:0 16px 38px rgba(61,104,145,.09),inset 0 1px 0 #fff;backdrop-filter:blur(16px);min-height:360px;max-height:520px;overflow:hidden}
 #ng27 .v298EditorMoments h3{margin:0;font-size:17px;color:#173F76}.v298EditorMoments>p{margin:0 0 2px;font-size:9.5px;line-height:1.25;color:#7890A9;font-weight:750}
 #ng27 .v298MomentCard{display:grid!important;grid-template-columns:64px minmax(0,1fr)!important;gap:10px!important;align-items:center!important;min-height:78px!important;padding:8px!important;border:1px solid rgba(143,181,216,.25)!important;border-radius:18px!important;background:linear-gradient(145deg,#FFFFFF,#F1F9FF)!important;color:#254F7D!important;text-align:left!important;cursor:pointer!important;box-shadow:0 6px 15px rgba(69,111,148,.055)!important}
 #ng27 .v298MomentCard.active{border-color:#67C5F3!important;box-shadow:0 0 0 3px rgba(82,184,239,.11),0 8px 18px rgba(69,111,148,.07)!important}
 #ng27 .v298MomentThumb{height:54px;border-radius:13px;background:radial-gradient(circle at 38% 35%,rgba(122,219,255,.65),transparent 30%),linear-gradient(145deg,#164C79,#0C2742);display:grid;place-items:center;color:#DFF7FF;font-size:17px;font-weight:950;box-shadow:inset 0 0 0 1px rgba(255,255,255,.15)}
 #ng27 .v298MomentText b{display:block;font-size:11.5px}.v298MomentText span{display:block;margin-top:4px;font-size:8.8px;line-height:1.2;color:#7890A8;font-weight:700}
 #ng27 .v298EditorToolbar{width:min(100%,980px);min-height:70px;margin:0 auto;display:flex;align-items:center;justify-content:center;gap:7px;padding:7px 10px;border:1px solid rgba(143,181,216,.25);border-radius:24px;background:rgba(255,255,255,.86);box-shadow:0 13px 30px rgba(61,104,145,.08),inset 0 1px 0 #fff;backdrop-filter:blur(16px);overflow:hidden}
 #ng27 .v298EditorToolbar .railBtn{width:72px!important;height:56px!important;min-width:60px!important;border-radius:16px!important;flex:0 1 72px!important;box-shadow:0 6px 15px rgba(79,118,157,.075)!important}
 #ng27 .v298EditorToolbar .railBtn .ico{width:21px!important;height:21px!important}.v298EditorToolbar .railBtn span{font-size:8px!important;letter-spacing:.045em!important}
 #ng27 .footNote{display:none!important}
}
@media (min-width:761px) and (max-width:1180px){
 #ng27 .v298EditorWorkspace{grid-template-columns:78px minmax(330px,1fr) minmax(220px,260px) 78px;gap:10px}
 #ng27 .v298EditorAd{min-height:270px;border-radius:20px}.v298EditorAd small{display:none}
 #ng27 .v298EditorPlayer .stage.r916{width:min(100%,320px)!important}
 #ng27 .v298EditorMural{left:-108px!important;width:100px!important;font-size:11px!important}
 #ng27 .v298EditorMoments{padding:10px;gap:7px;min-height:320px}.v298MomentCard{grid-template-columns:50px minmax(0,1fr)!important;gap:7px!important}.v298MomentThumb{height:46px!important}
 #ng27 .v298EditorToolbar{gap:4px;padding:6px}.v298EditorToolbar .railBtn{width:61px!important;min-width:52px!important;flex-basis:61px!important}
}
/* END V298 EDITOR REFERENCE LAYOUT */
'''

JS = r'''
<script id="v298EditorRuntime">
(()=>{
 if(!window.matchMedia('(min-width:761px)').matches)return;
 const root=document.getElementById('ng27');
 const shell=root&&root.querySelector('.shell');
 const oldGrid=root&&root.querySelector('.v297EditorGrid');
 if(!root||!shell||!oldGrid||root.querySelector('.v298EditorWorkspace'))return;

 const oldSide=oldGrid.querySelector('.v297EditorSidebar');
 const oldCenter=oldGrid.querySelector('.v297EditorCenter');
 const oldMoments=oldGrid.querySelector('.v297EditorMoments');
 const stageWrap=oldCenter&&oldCenter.querySelector('.stageWrap');
 const oldTimeline=shell.querySelector('.v297EditorTimeline');
 if(!oldSide||!stageWrap||!oldMoments) return;

 root.dataset.v298Layout='reference';
 const workspace=document.createElement('section');
 workspace.className='v298EditorWorkspace';

 const leftAd=document.createElement('aside');
 leftAd.className='v298EditorAd v298EditorAdLeft';
 leftAd.innerHTML='<span>Pubblicità</span><small>Spazio sponsor</small>';

 const center=document.createElement('section');
 center.className='v298EditorCenter';
 const player=document.createElement('div');
 player.className='v298EditorPlayer';
 player.append(stageWrap);

 let mural=shell.querySelector('.gsfGuide');
 if(!mural){mural=document.createElement('div');mural.className='gsfGuide'}
 mural.classList.add('v298EditorMural');
 mural.innerHTML='Tocca direttamente il video<br>per personalizzarlo';
 player.append(mural);
 center.append(player);

 let timelineWrap=oldTimeline;
 if(!timelineWrap){
   const timeline=shell.querySelector('.timeline');
   if(timeline){timelineWrap=document.createElement('div');timelineWrap.append(timeline)}
 }
 if(timelineWrap){timelineWrap.className='v298EditorTimeline';center.append(timelineWrap)}

 const moments=oldMoments;
 moments.className='v298EditorMoments';
 moments.innerHTML=`<h3>Le tue 3 migliori giocate</h3><p>Seleziona il momento che vuoi portare nel montaggio.</p>
 <button class="v298MomentCard active" data-v297-moment="1" data-v298-moment="1"><span class="v298MomentThumb">1</span><span class="v298MomentText"><b>Momento migliore</b><span>La scena aperta nel Game Editor</span></span></button>
 <button class="v298MomentCard" data-v297-moment="2" data-v298-moment="2"><span class="v298MomentThumb">2</span><span class="v298MomentText"><b>Seconda giocata</b><span>Apri la selezione IA per cambiarla</span></span></button>
 <button class="v298MomentCard" data-v297-moment="3" data-v298-moment="3"><span class="v298MomentThumb">3</span><span class="v298MomentText"><b>Terza giocata</b><span>Apri la selezione IA per cambiarla</span></span></button>`;

 const rightAd=document.createElement('aside');
 rightAd.className='v298EditorAd v298EditorAdRight';
 rightAd.innerHTML='<span>Pubblicità</span><small>Spazio sponsor</small>';

 workspace.append(leftAd,center,moments,rightAd);

 const toolbar=document.createElement('nav');
 toolbar.className='v298EditorToolbar';
 [...oldSide.querySelectorAll('.railBtn')].forEach(btn=>toolbar.append(btn));

 oldGrid.replaceWith(workspace);
 workspace.insertAdjacentElement('afterend',toolbar);
})();
</script>
'''


def apply_editor():
    if not EDITOR.is_file():
        raise RuntimeError(f"V298 editor missing: {EDITOR}")
    text = EDITOR.read_text(encoding="utf-8")
    if MARKER not in text:
        pos = text.rfind("</style>")
        if pos < 0:
            raise RuntimeError("V298 style anchor missing")
        text = text[:pos] + CSS + "\n" + text[pos:]
        if "</body>" not in text:
            raise RuntimeError("V298 body anchor missing")
        text = text.replace("</body>", JS + "\n</body>", 1)
        EDITOR.write_text(text, encoding="utf-8")
        print("V298 editor reference layout applied:", EDITOR, flush=True)
    else:
        print("V298 editor reference layout already present", flush=True)


def bump_cache():
    if not EMBED.is_file():
        raise RuntimeError(f"V298 editor embed missing: {EMBED}")
    text = EMBED.read_text(encoding="utf-8")
    updated, count = re.subn(r'"gsf_editor_2027_v\d+"', '"gsf_editor_2027_v298"', text, count=1)
    if count != 1 and '"gsf_editor_2027_v298"' not in text:
        raise RuntimeError("V298 editor cache anchor missing")
    EMBED.write_text(updated, encoding="utf-8")
    print("V298 editor cache key bumped", flush=True)


if __name__ == "__main__":
    apply_editor()
    bump_cache()
