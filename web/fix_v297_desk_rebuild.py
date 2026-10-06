#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path("/app")
WEB = ROOT / "web"
HUB = WEB / "creator_hub_v156_component" / "index.html"
AI = WEB / "ai_v221_component" / "index.html"
EDITOR = WEB / "editor_2027_component" / "index.html"
SHARE = WEB / "share_v156_component" / "index.html"
APP = ROOT / "GamingShortsFactory_V154_STRUCTURAL_HOME.py"
EDITOR_EMBED = WEB / "editor_2027_embed.py"

HUB_CSS = r'''
/* V297 DESK REBUILD — HUB */
@media (min-width:761px){
 #hub[data-v297-layout="hub"]{display:grid!important;grid-template-columns:190px minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr)!important;gap:18px!important;padding:16px 22px!important;overflow:hidden!important}
 #hub .v297HubSidebar{min-height:0;border:1px solid rgba(143,181,216,.26);border-radius:30px;background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(240,248,255,.86));box-shadow:0 18px 46px rgba(52,104,151,.10),inset 0 1px 0 #fff;padding:18px 12px;display:flex;flex-direction:column;gap:10px;backdrop-filter:blur(18px)}
 #hub .v297HubBrand{padding:4px 8px 16px;font-size:20px;font-weight:950;letter-spacing:-.035em;color:#126CC7}.v297HubBrand small{display:block;margin-top:3px;font-size:7px;letter-spacing:.20em;color:#7891AA}
 #hub .v297HubNav{display:grid;gap:8px}.v297HubNav button{border:1px solid transparent;border-radius:18px;background:transparent;color:#5A76A0;min-height:58px;padding:9px 11px;display:flex;align-items:center;gap:10px;text-align:left;font-size:11px;font-weight:850;cursor:pointer}.v297HubNav button:hover,.v297HubNav button.active{background:linear-gradient(145deg,#E8F8FF,#EEF0FF);border-color:#C9E6F7;color:#1D78CE;box-shadow:0 9px 22px rgba(59,132,194,.11)}
 #hub .v297HubNavIcon{width:34px;height:34px;border-radius:12px;background:#EDF7FF;display:grid;place-items:center;font-size:17px;flex:0 0 auto}
 #hub .v297HubMain{min-width:0;min-height:0;display:grid;grid-template-rows:auto minmax(0,1fr);gap:12px}
 #hub .v297HubMain>.top{min-height:72px!important;padding:0 4px!important}.v297HubMain h1{font-size:clamp(31px,2.5vw,42px)!important}.v297HubMain .subtitle{font-size:12px!important}
 #hub .v297HubMain>.stage{min-height:0!important;overflow:hidden!important}
 #hub .view[data-view="dashboard"] .dashboard{grid-template-rows:126px minmax(0,1fr)!important;gap:14px!important}
 #hub .profileCard{min-height:126px!important;padding:18px 20px!important;border-radius:28px!important;background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(239,249,255,.90))!important}
 #hub .profileCard .avatar{width:72px!important;height:72px!important;border-radius:22px!important}.profileCard .profileName{font-size:23px!important}.profileCard .profileMeta{font-size:11px!important}
 #hub .folders{grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:repeat(3,minmax(0,1fr))!important;gap:14px!important}
 #hub .folder{padding:18px 20px!important;border:1px solid rgba(143,181,216,.24)!important;border-radius:24px!important;background:rgba(255,255,255,.92)!important;box-shadow:0 12px 30px rgba(61,104,145,.08),inset 0 1px 0 #fff!important}
 #hub .folderIcon{width:54px!important;height:54px!important;border-radius:18px!important;font-size:21px!important}.folder h2{font-size:18px!important}.folder p{font-size:10.5px!important}.folderFoot{font-size:9px!important}
 #hub .detailHeadText h2{font-size:24px!important}.detailHeadText p{font-size:11px!important}.detailCard{padding:18px!important;border-radius:26px!important}
 #hub .socialGrid{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:12px!important}.socialCard{grid-template-columns:1fr!important;align-items:start!important;min-height:148px!important;padding:15px!important}.socialLogo{width:46px!important;height:46px!important;border-radius:15px!important}.socialName{font-size:13px!important}.socialState{font-size:9px!important}.connectBtn{width:100%;font-size:9px!important;min-height:34px!important}
 #hub .stats{gap:12px!important}.stat{padding:15px!important;border-radius:18px!important}.stat b{font-size:25px!important}.stat small{font-size:9px!important}
}
/* END V297 DESK REBUILD — HUB */
'''

HUB_JS = r'''
<script id="v297HubRuntime">
(()=>{
 if(!window.matchMedia('(min-width:761px)').matches)return;
 const root=document.getElementById('hub'); if(!root||root.querySelector('.v297HubSidebar'))return;
 const top=root.querySelector(':scope > .top'),stage=root.querySelector(':scope > .stage'); if(!top||!stage)return;
 const main=document.createElement('div'); main.className='v297HubMain';
 root.insertBefore(main,top); main.append(top,stage);
 const side=document.createElement('aside'); side.className='v297HubSidebar';
 side.innerHTML=`<div class="v297HubBrand">GSF<small>CREATOR HUB</small></div><nav class="v297HubNav">
 <button class="active" data-v297-target="dashboard"><span class="v297HubNavIcon">⌂</span>Panoramica</button>
 <button data-v297-target="profile"><span class="v297HubNavIcon">◎</span>Profilo</button>
 <button data-v297-target="social"><span class="v297HubNavIcon">↗</span>Account Social</button>
 <button data-v297-target="drafts"><span class="v297HubNavIcon">▱</span>Le mie Bozze</button>
 <button data-v297-target="shorts"><span class="v297HubNavIcon">▶</span>I miei Shorts</button>
 <button data-v297-target="project"><span class="v297HubNavIcon">▣</span>Progetti</button>
 </nav>`;
 root.insertBefore(side,main);
 const activate=(name)=>{side.querySelectorAll('[data-v297-target]').forEach(b=>b.classList.toggle('active',b.dataset.v297Target===name))};
 side.addEventListener('click',e=>{
   const btn=e.target.closest('[data-v297-target]'); if(!btn)return; const target=btn.dataset.v297Target; activate(target);
   if(target==='dashboard'){
     root.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.dataset.view==='dashboard'));
     return;
   }
   const folder=root.querySelector('.folder[data-folder="'+target+'"]'); if(folder)folder.click();
 });
 const obs=new MutationObserver(()=>{const active=root.querySelector('.view.active');if(active&&active.dataset.view)activate(active.dataset.view==='dashboard'?'dashboard':active.dataset.view)});
 obs.observe(stage,{subtree:true,attributes:true,attributeFilter:['class']});
})();
</script>
'''

AI_CSS = r'''
/* V297 DESK REBUILD — AI */
@media (min-width:761px){
 #ai221[data-v297-layout="ai"]{display:grid!important;grid-template-columns:180px minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr)!important;gap:18px!important;padding:16px 22px!important;overflow:hidden!important}
 #ai221 .v297AiSidebar{border:1px solid rgba(143,181,216,.25);border-radius:30px;background:rgba(255,255,255,.88);box-shadow:0 18px 45px rgba(61,104,145,.09),inset 0 1px 0 #fff;padding:18px 12px;display:flex;flex-direction:column;gap:9px;backdrop-filter:blur(18px)}
 #ai221 .v297AiBrand{padding:4px 8px 14px;color:#1777D1;font-size:18px;font-weight:950}.v297AiBrand small{display:block;margin-top:4px;font-size:7px;letter-spacing:.18em;color:#7A91A9}
 #ai221 .v297AiNav{display:grid;gap:8px}.v297AiNav button{min-height:58px;border:1px solid transparent;border-radius:18px;background:transparent;color:#5E78A0;font-size:10.5px;font-weight:850;text-align:left;padding:9px 11px;cursor:pointer}.v297AiNav button.active{background:linear-gradient(145deg,#E6F7FF,#EDF0FF);border-color:#C8E6F7;color:#1B79D3;box-shadow:0 9px 22px rgba(66,143,204,.12)}
 #ai221 .v297AiMain{min-width:0;min-height:0;overflow:auto;padding-right:3px}.v297AiMain>.top{min-height:86px!important;margin:0 0 12px!important;align-items:center!important}.v297AiMain h1{font-size:clamp(36px,3vw,52px)!important}.v297AiMain .subtitle{font-size:13px!important;max-width:720px}
 #ai221 .v297AiHero{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 18px;margin-bottom:12px;border:1px solid rgba(125,177,216,.25);border-radius:24px;background:linear-gradient(115deg,rgba(255,255,255,.94),rgba(225,246,255,.86));box-shadow:0 12px 30px rgba(61,104,145,.07)}.v297AiHero b{font-size:17px}.v297AiHero span{font-size:10px;color:#7389A3;font-weight:700}.v297AiOrb{width:58px;height:58px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 35% 30%,#fff,#BEEAFF 48%,#62BDF4);box-shadow:0 0 0 8px rgba(116,205,249,.10),0 10px 24px rgba(56,142,205,.16);font-size:25px}
 #ai221 .panel{padding:16px!important;border-radius:27px!important}.v297AiMain .panel+.panel{margin-top:14px!important}.v297AiMain .engines{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:14px!important}.v297AiMain .engine{min-height:188px!important;padding:16px!important;border-radius:23px!important}.v297AiMain .engineIcon{width:52px!important;height:52px!important;font-size:23px!important}.v297AiMain .engine h3{font-size:19px!important}.v297AiMain .engine p{font-size:11px!important}.v297AiMain .selectBtn{min-height:40px!important;font-size:10px!important}
 #ai221 .v297AiMoments{margin-top:14px!important}.v297AiMoments .moments{grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:12px!important}.v297AiMoments .moment{min-height:154px!important;padding:9px!important}.v297AiMoments .thumb{height:108px!important}.v297AiMoments .moment b{font-size:11px!important}
}
/* END V297 DESK REBUILD — AI */
'''

AI_JS = r'''
<script id="v297AiRuntime">
(()=>{
 if(!window.matchMedia('(min-width:761px)').matches)return;
 const root=document.getElementById('ai221'); if(!root||root.querySelector('.v297AiSidebar'))return;
 const main=document.createElement('section'); main.className='v297AiMain';
 const side=document.createElement('aside'); side.className='v297AiSidebar';
 side.innerHTML=`<div class="v297AiBrand">GSF AI<small>CREA CON IA</small></div><nav class="v297AiNav"><button class="active">✦ &nbsp; Motori IA</button><button data-nav="editor">🎮 &nbsp; Game Editor</button><button data-nav="hub">▣ &nbsp; Progetti</button><button data-nav="home">⌂ &nbsp; Home</button></nav>`;
 const movable=[...root.children].filter(el=>el.classList.contains('top')||el.classList.contains('panel'));
 root.prepend(side); root.append(main); movable.forEach(el=>main.append(el));
 const hero=document.createElement('div'); hero.className='v297AiHero'; hero.innerHTML='<div><b>4 motori IA, un solo obiettivo</b><br><span>Trova i momenti migliori e crea uno Short spettacolare.</span></div><div class="v297AiOrb">✦</div>';
 const top=main.querySelector('.top'); if(top)top.insertAdjacentElement('afterend',hero);
 const panels=main.querySelectorAll('.panel'); if(panels[1])panels[1].classList.add('v297AiMoments');
 main.querySelectorAll('.engine').forEach(engine=>engine.dataset.v297RealEngine='1');
 side.addEventListener('click',e=>{const b=e.target.closest('[data-nav]');if(!b)return;try{parent.postMessage({type:'GSF_SHELL_NAV',target:b.dataset.nav},location.origin)}catch(_e){}});
})();
</script>
'''

EDITOR_CSS = r'''
/* V297 DESK REBUILD — EDITOR */
@media (min-width:761px){
 #ng27[data-v297-layout="editor"]{width:100%!important;height:100%!important;overflow:hidden!important;background:radial-gradient(circle at 50% 40%,rgba(184,230,255,.36),transparent 48%),linear-gradient(180deg,#FAFDFF,#F1F8FD)!important}
 #ng27 .shell{max-width:1560px!important;height:100%!important;margin:0 auto!important;padding:14px 18px!important;border-radius:0!important;overflow:hidden!important;background:transparent!important}
 #ng27 .v297EditorGrid{display:grid!important;grid-template-columns:110px minmax(360px,520px) minmax(300px,1fr)!important;gap:20px!important;align-items:center!important;justify-content:center!important;min-height:0!important;height:calc(100% - 154px)!important}
 #ng27 .v297EditorSidebar{display:flex;flex-direction:column;gap:10px;align-items:center;justify-content:center;min-height:0}.v297EditorSidebar .railBtn{width:86px!important;height:76px!important;border-radius:22px!important}.v297EditorSidebar .railBtn .ico{width:28px!important;height:28px!important}.v297EditorSidebar .railBtn span{font-size:9px!important}
 #ng27 .v297EditorCenter{min-width:0;min-height:0;display:grid;place-items:center;height:100%}.v297EditorCenter .stageWrap{width:100%;height:100%;display:grid;place-items:center}.v297EditorCenter .stage.r916{width:min(100%,400px)!important;max-height:100%!important;border-radius:28px!important;box-shadow:0 24px 55px rgba(38,95,137,.18)!important}
 #ng27 .v297EditorMoments{align-self:center;display:grid;gap:12px;padding:16px;border:1px solid rgba(143,181,216,.26);border-radius:28px;background:rgba(255,255,255,.84);box-shadow:0 18px 42px rgba(61,104,145,.09),inset 0 1px 0 #fff;backdrop-filter:blur(16px)}.v297EditorMoments h3{margin:0 0 2px;font-size:18px;color:#153E76}.v297EditorMoments p{margin:0 0 6px;font-size:10px;color:#758AA3;font-weight:700}.v297MomentCard{border:1px solid rgba(143,181,216,.24);border-radius:18px;background:linear-gradient(145deg,#fff,#F1F9FF);padding:12px;text-align:left;color:#234D7C;min-height:82px;cursor:pointer}.v297MomentCard b{display:block;font-size:13px}.v297MomentCard span{display:block;margin-top:4px;font-size:9px;color:#7A8FA7}.v297MomentCard.active{border-color:#68C7F5;box-shadow:0 0 0 3px rgba(85,184,240,.12)}
 #ng27 .v297EditorTimeline{height:78px;display:grid;place-items:center;margin-top:8px}.v297EditorTimeline .timeline{width:min(100%,980px)!important;margin:0 auto!important}
 #ng27 .createShortJourney{width:min(100%,720px)!important;margin:8px auto 0!important}.createShortJourneyBtn{min-height:58px!important;border-radius:20px!important;font-size:12px!important}
 #ng27 .cockpit{display:contents!important}
}
@media (min-width:761px) and (max-height:820px){#ng27 .v297EditorGrid{height:calc(100% - 130px)!important}.v297EditorCenter .stage.r916{width:min(100%,330px)!important}.v297EditorSidebar .railBtn{width:74px!important;height:62px!important}.v297MomentCard{min-height:66px!important}}
/* END V297 DESK REBUILD — EDITOR */
'''

EDITOR_JS = r'''
<script id="v297EditorRuntime">
(()=>{
 if(!window.matchMedia('(min-width:761px)').matches)return;
 const root=document.getElementById('ng27'),shell=root&&root.querySelector('.shell'),cockpit=root&&root.querySelector('.cockpit'); if(!root||!shell||!cockpit||root.querySelector('.v297EditorGrid'))return;
 const rails=[...cockpit.querySelectorAll(':scope > .rail')],stageWrap=cockpit.querySelector('.stageWrap'); if(!stageWrap)return;
 const grid=document.createElement('div'); grid.className='v297EditorGrid';
 const side=document.createElement('aside'); side.className='v297EditorSidebar'; rails.forEach(rail=>[...rail.children].forEach(btn=>side.append(btn)));
 const center=document.createElement('section'); center.className='v297EditorCenter'; center.append(stageWrap);
 const moments=document.createElement('aside'); moments.className='v297EditorMoments'; moments.innerHTML='<h3>Momenti IA</h3><p>Il momento corrente e le alternative restano a portata di click.</p><button class="v297MomentCard active" data-v297-moment="1"><b>1 · Momento corrente</b><span>Quello aperto nel Game Editor</span></button><button class="v297MomentCard" data-v297-moment="2"><b>2 · Alternativa IA</b><span>Torna ai momenti per cambiare scena</span></button><button class="v297MomentCard" data-v297-moment="3"><b>3 · Alternativa IA</b><span>Torna ai momenti per cambiare scena</span></button>';
 cockpit.replaceWith(grid); grid.append(side,center,moments);
 const timeline=shell.querySelector('.timeline'); if(timeline){const tw=document.createElement('div');tw.className='v297EditorTimeline';timeline.parentNode.insertBefore(tw,timeline);tw.append(timeline);grid.insertAdjacentElement('afterend',tw)}
 moments.addEventListener('click',e=>{const b=e.target.closest('[data-v297-moment]');if(!b)return;if(b.dataset.v297Moment!=='1'){try{parent.postMessage({type:'GSF_SHELL_NAV',target:'ai'},location.origin)}catch(_e){}}});
})();
</script>
'''

SHARE_CSS = r'''
/* V297 DESK REBUILD — SHARE */
@media (min-width:761px){
 #share[data-v297-layout="share"]{overflow:hidden!important;padding:18px 24px 20px!important}.v297ShareGrid{display:grid!important;grid-template-columns:minmax(250px,330px) minmax(0,1fr)!important;gap:20px!important;min-height:0!important;height:calc(100% - 92px)!important}.v297SharePreview{min-height:0;display:grid;grid-template-rows:minmax(0,1fr) auto;gap:10px;padding:13px;border:1px solid rgba(143,181,216,.25);border-radius:30px;background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(230,247,255,.87));box-shadow:0 18px 44px rgba(61,104,145,.10),inset 0 1px 0 #fff}.v297SharePhone{position:relative;min-height:0;margin:auto;height:100%;max-height:650px;aspect-ratio:9/16;border-radius:28px;overflow:hidden;background:linear-gradient(160deg,#163B64,#08192E);box-shadow:0 18px 42px rgba(31,77,115,.22),0 0 0 4px rgba(112,205,250,.18)}.v297SharePhone video{width:100%;height:100%;object-fit:cover;display:block;background:#102D4A}.v297SharePhone:after{content:'SHORT 9:16';position:absolute;left:12px;top:12px;padding:5px 8px;border-radius:999px;background:rgba(4,24,45,.62);color:#fff;font-size:8px;font-weight:900;letter-spacing:.08em}.v297SharePreviewMeta{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:9px;color:#6F85A0;font-weight:800}.v297SharePreviewMeta b{font-size:12px;color:#153F79}.v297ShareMain{min-width:0;min-height:0;overflow:auto;padding-right:2px}.v297ShareMain .section{padding:16px!important;border-radius:28px!important}.v297ShareMain .socials{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:12px!important}.v297ShareMain .card{min-height:226px!important;padding:15px!important;border-radius:22px!important}.v297ShareMain .logo{width:52px!important;height:52px!important}.v297ShareMain .card h3{font-size:16px!important}.v297ShareMain .card p{font-size:10px!important}.v297ShareMain .open{min-height:40px!important}.v297ShareMain .downloadRow{grid-template-columns:minmax(0,1fr) auto!important;gap:14px!important}.v297ShareMain .downloadBtn{min-height:54px!important;font-size:12px!important}.v297ShareMain .secondary{min-height:46px!important}
}
/* END V297 DESK REBUILD — SHARE */
'''

SHARE_JS = r'''
<script id="v297ShareRuntime">
(()=>{
 if(!window.matchMedia('(min-width:761px)').matches)return;
 const root=document.getElementById('share'); if(!root||root.querySelector('.v297ShareGrid'))return;
 const sections=[...root.querySelectorAll(':scope > .section')]; if(!sections.length)return;
 const grid=document.createElement('div'); grid.className='v297ShareGrid';
 const preview=document.createElement('aside'); preview.className='v297SharePreview'; preview.innerHTML='<div class="v297SharePhone"><video id="v297PreviewVideo" playsinline controls preload="metadata"></video></div><div class="v297SharePreviewMeta"><div><b>Anteprima Short</b><br>1080×1920 · H.264 · fino a 60 FPS</div><span>9:16</span></div>';
 const main=document.createElement('section'); main.className='v297ShareMain'; sections.forEach(s=>main.append(s));
 root.append(grid); grid.append(preview,main);
 const state={video_url:''};
 fetch('/share/state',{cache:'no-store',credentials:'same-origin'}).then(r=>r.json()).then(j=>{state.video_url=String(j.video_url||'');const v=document.getElementById('v297PreviewVideo');if(v&&state.video_url){v.src=state.video_url;v.load()}}).catch(()=>{});
})();
</script>
'''


def inject(path: Path, marker: str, root_old: str, root_new: str, css: str, js: str):
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print("V297 already applied:", path, flush=True)
        return
    if root_old not in text:
        raise RuntimeError(f"V297 root anchor missing in {path}: {root_old}")
    text = text.replace(root_old, root_new, 1)
    pos = text.rfind("</style>")
    if pos < 0:
        raise RuntimeError("V297 style anchor missing: " + str(path))
    text = text[:pos] + css + "\n" + text[pos:]
    if "</body>" not in text:
        raise RuntimeError("V297 body anchor missing: " + str(path))
    text = text.replace("</body>", js + "\n</body>", 1)
    path.write_text(text, encoding="utf-8")
    print("V297 desk rebuilt:", path, flush=True)


def patch_cache():
    text = APP.read_text(encoding="utf-8")
    for route in ("creator-hub-v156", "share-v156", "ai-v221"):
        text = re.sub(rf"/{re.escape(route)}/\?v=\d+", f"/{route}/?v=297", text)
    for required in ("/creator-hub-v156/?v=297", "/share-v156/?v=297", "/ai-v221/?v=297"):
        if required not in text:
            raise RuntimeError("V297 shell cache marker missing: " + required)
    APP.write_text(text, encoding="utf-8")

    embed = EDITOR_EMBED.read_text(encoding="utf-8")
    embed, count = re.subn(r'"gsf_editor_2027_v\d+"', '"gsf_editor_2027_v297"', embed, count=1)
    if count != 1 and '"gsf_editor_2027_v297"' not in embed:
        raise RuntimeError("V297 editor asset key anchor missing")
    EDITOR_EMBED.write_text(embed, encoding="utf-8")
    print("V297 cache keys bumped", flush=True)


if __name__ == "__main__":
    for p in (HUB, AI, EDITOR, SHARE, APP, EDITOR_EMBED):
        if not p.is_file():
            raise RuntimeError("V297 required file missing: " + str(p))
    inject(HUB, "V297 DESK REBUILD — HUB", '<main id="hub">', '<main id="hub" data-v297-layout="hub">', HUB_CSS, HUB_JS)
    inject(AI, "V297 DESK REBUILD — AI", '<main id="ai221">', '<main id="ai221" data-v297-layout="ai">', AI_CSS, AI_JS)
    editor_text = EDITOR.read_text(encoding="utf-8")
    editor_anchor = '<div id="ng27" data-editor-build="2027.6-zoomout">'
    if editor_anchor not in editor_text:
        m = re.search(r'<div id="ng27"[^>]*>', editor_text)
        if not m:
            raise RuntimeError("V297 editor root anchor missing")
        editor_anchor = m.group(0)
    editor_new = editor_anchor[:-1] + ' data-v297-layout="editor">'
    inject(EDITOR, "V297 DESK REBUILD — EDITOR", editor_anchor, editor_new, EDITOR_CSS, EDITOR_JS)
    inject(SHARE, "V297 DESK REBUILD — SHARE", '<main id="share">', '<main id="share" data-v297-layout="share">', SHARE_CSS, SHARE_JS)
    patch_cache()
