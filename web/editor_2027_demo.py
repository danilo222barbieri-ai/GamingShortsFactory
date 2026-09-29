import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gaming Shorts Factory · Neural Game Editor 2027", page_icon="🎮", layout="wide")
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],.stApp{background:#05070c!important;}
.block-container{max-width:1500px!important;padding:4px 10px 12px!important;}
header,[data-testid="stHeader"],footer{display:none!important;}
</style>
""", unsafe_allow_html=True)

video_path=Path("/app/demo_assets/demo_final.mp4")
video_b64=base64.b64encode(video_path.read_bytes()).decode("ascii") if video_path.exists() else ""

html=r"""
<div id="ng27">
<svg aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden">
  <symbol id="i-back" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></symbol>
  <symbol id="i-reset" viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.35-5.65L4 8.7"/><path d="M4 4v4.7h4.7"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></symbol>
  <symbol id="i-frame" viewBox="0 0 24 24"><path d="M8 3H4a1 1 0 0 0-1 1v4M16 3h4a1 1 0 0 1 1 1v4M8 21H4a1 1 0 0 1-1-1v-4M16 21h4a1 1 0 0 0 1-1v-4"/><circle cx="12" cy="12" r="2.6"/><path d="M12 6.5v3M12 14.5v3M6.5 12h3M14.5 12h3"/></symbol>
  <symbol id="i-look" viewBox="0 0 24 24"><circle cx="7" cy="8" r="3"/><circle cx="17" cy="8" r="3"/><circle cx="12" cy="17" r="3"/><path d="M9.5 9.5l1.2 4M14.5 9.5l-1.2 4"/></symbol>
  <symbol id="i-hud" viewBox="0 0 24 24"><path d="M4 5h6v5H4zM14 5h6v3h-6zM14 12h6v7h-6zM4 14h6v5H4z"/><path d="M12 4v16"/></symbol>
  <symbol id="i-caption" viewBox="0 0 24 24"><path d="M5 18V7a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v11"/><path d="M7 15h10M8.5 12l2.3-5h2.4l2.3 5M9.5 10h5"/></symbol>
  <symbol id="i-audio" viewBox="0 0 24 24"><path d="M4 14h3l4 4V6L7 10H4zM15 9.5a4 4 0 0 1 0 5M17.5 7a7 7 0 0 1 0 10"/></symbol>
  <symbol id="i-ai" viewBox="0 0 24 24"><path d="M12 2l1.4 4.1L17.5 7.5l-4.1 1.4L12 13l-1.4-4.1-4.1-1.4 4.1-1.4zM18 14l.9 2.6 2.6.9-2.6.9L18 21l-.9-2.6-2.6-.9 2.6-.9zM6 15l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path d="M8 5l11 7-11 7z"/></symbol>
  <symbol id="i-pause" viewBox="0 0 24 24"><path d="M8 5v14M16 5v14"/></symbol>
  <symbol id="i-undo" viewBox="0 0 24 24"><path d="M9 7L4 12l5 5"/><path d="M5 12h7a7 7 0 0 1 7 7"/></symbol>
  <symbol id="i-redo" viewBox="0 0 24 24"><path d="M15 7l5 5-5 5"/><path d="M19 12h-7a7 7 0 0 0-7 7"/></symbol>
  <symbol id="i-done" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7"/></symbol>
  <symbol id="i-scan" viewBox="0 0 24 24"><path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M7 12h10M12 7v10"/></symbol>
</svg>

<style>
#ng27{--cyan:#69dfff;--violet:#8c7dff;--mint:#66f0c3;--pink:#ff7da7;--white:#f6f8fb;--muted:#78869a;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--white)}
#ng27 *{box-sizing:border-box}
#ng27 button{font:inherit}
#ng27 .ico{width:22px;height:22px;display:block;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
#ng27 .ico.ai{stroke-width:1.55}
#ng27 .shell{max-width:1180px;margin:0 auto;padding:12px;border-radius:30px;border:1px solid rgba(255,255,255,.055);background:radial-gradient(circle at 22% 18%,rgba(105,223,255,.08),transparent 26%),radial-gradient(circle at 78% 22%,rgba(140,125,255,.08),transparent 30%),#06090f;box-shadow:0 30px 90px rgba(0,0,0,.32);position:relative;overflow:hidden}
#ng27 .shell:after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.14;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:38px 38px}
#ng27 .topline{position:relative;z-index:3;display:flex;align-items:center;justify-content:space-between;padding:2px 4px 10px}
#ng27 .brand{display:flex;align-items:center;gap:9px}
#ng27 .brandMark{width:34px;height:34px;border-radius:11px;background:linear-gradient(145deg,rgba(105,223,255,.2),rgba(140,125,255,.2));border:1px solid rgba(105,223,255,.24);display:grid;place-items:center}
#ng27 .brandMark .ico{width:18px;height:18px;color:#bcefff}
#ng27 .brandText b{display:block;font-size:11px;letter-spacing:.16em}
#ng27 .brandText span{display:block;font-size:8px;color:#69778b;letter-spacing:.14em;margin-top:2px}
#ng27 .sys{display:flex;align-items:center;gap:7px;font-size:8px;font-weight:900;letter-spacing:.14em;color:#74849a}
#ng27 .sysDot{width:6px;height:6px;border-radius:50%;background:var(--mint);box-shadow:0 0 12px rgba(102,240,195,.7)}
#ng27 .cockpit{position:relative;z-index:2;display:grid;grid-template-columns:76px minmax(0,1fr) 76px;gap:10px;align-items:center}
#ng27 .rail{display:flex;flex-direction:column;gap:9px;align-items:center}
#ng27 .railBtn{width:62px;height:62px;border-radius:19px;border:1px solid rgba(255,255,255,.08);background:rgba(12,18,27,.74);backdrop-filter:blur(16px);color:#dce5ef;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;cursor:pointer;transition:.16s}
#ng27 .railBtn .ico{width:21px;height:21px}
#ng27 .railBtn span{font-size:7.5px;font-weight:900;letter-spacing:.08em;color:#8e9aac}
#ng27 .railBtn:hover,#ng27 .railBtn.active{border-color:rgba(105,223,255,.42);background:linear-gradient(145deg,rgba(105,223,255,.13),rgba(140,125,255,.13));color:#fff;transform:translateY(-1px);box-shadow:0 0 22px rgba(105,223,255,.09)}
#ng27 .railBtn.active span{color:#c6f4ff}
#ng27 .stageWrap{min-width:0}
#ng27 .stage{position:relative;width:min(100%,650px);aspect-ratio:9/16;margin:0 auto;background:#0b1017;border-radius:32px;overflow:hidden;border:1px solid rgba(255,255,255,.1);box-shadow:0 28px 78px rgba(0,0,0,.42)}
#ng27 video{width:100%;height:100%;object-fit:cover;display:block;background:#10141b}
#ng27 .shade{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(3,7,12,.46),transparent 17%,transparent 69%,rgba(3,7,12,.66))}
#ng27 .scanlines{position:absolute;inset:0;pointer-events:none;opacity:.055;background:repeating-linear-gradient(180deg,rgba(255,255,255,.14) 0,rgba(255,255,255,.14) 1px,transparent 1px,transparent 5px)}
#ng27 .corn{position:absolute;width:38px;height:38px;z-index:4;pointer-events:none;border-color:rgba(105,223,255,.52);border-style:solid}
#ng27 .c1{top:12px;left:12px;border-width:1px 0 0 1px;border-radius:11px 0 0 0}.c2{top:12px;right:12px;border-width:1px 1px 0 0;border-radius:0 11px 0 0}.c3{bottom:12px;left:12px;border-width:0 0 1px 1px;border-radius:0 0 0 11px}.c4{bottom:12px;right:12px;border-width:0 1px 1px 0;border-radius:0 0 11px 0}
#ng27 .hudTop{position:absolute;top:15px;left:17px;right:17px;z-index:8;display:flex;justify-content:space-between;align-items:center}
#ng27 .glass{height:40px;border-radius:13px;border:1px solid rgba(255,255,255,.11);background:rgba(7,12,19,.68);backdrop-filter:blur(16px);color:#fff}
#ng27 .hudBtn{width:40px;display:grid;place-items:center;cursor:pointer}
#ng27 .hudBtn .ico{width:18px;height:18px}
#ng27 .cluster{display:flex;gap:7px;align-items:center}
#ng27 .formatTag{padding:0 12px;display:flex;align-items:center;gap:7px;font-size:9px;font-weight:900;letter-spacing:.09em}
#ng27 .signal{width:6px;height:6px;border-radius:50%;background:var(--cyan);box-shadow:0 0 12px rgba(105,223,255,.7)}
#ng27 .visionBadge{position:absolute;left:17px;top:67px;z-index:6;padding:7px 9px;border-radius:10px;border:1px solid rgba(105,223,255,.2);background:rgba(6,12,19,.5);backdrop-filter:blur(12px);font-size:8px;font-weight:900;letter-spacing:.11em;color:#bcefff}
#ng27 .focus{position:absolute;left:50%;top:43%;width:74px;height:74px;transform:translate(-50%,-50%);pointer-events:none;opacity:.34}
#ng27 .focus:before,#ng27 .focus:after{content:"";position:absolute;background:rgba(105,223,255,.7)}
#ng27 .focus:before{left:36px;top:8px;width:1px;height:58px}.focus:after{top:36px;left:8px;height:1px;width:58px}
#ng27 .focusRing{position:absolute;inset:17px;border:1px solid rgba(105,223,255,.6);border-radius:50%}
#ng27 .drawer{position:absolute;left:14px;right:14px;bottom:14px;z-index:10;background:rgba(7,12,19,.8);backdrop-filter:blur(22px);border:1px solid rgba(255,255,255,.1);border-radius:21px;padding:12px;transition:.18s}
#ng27 .drawer.hidden{opacity:0;transform:translateY(11px);pointer-events:none}
#ng27 .drawerHead{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px}
#ng27 .drawerHead strong{font-size:12px;letter-spacing:.04em}
#ng27 .drawerHead small{font-size:8px;color:#8ee8ff;font-weight:900;letter-spacing:.12em}
#ng27 .drawerClose{border:0;background:transparent;color:#b7c2d0;cursor:pointer;padding:2px}
#ng27 .drawerClose .ico{width:16px;height:16px}
#ng27 .strip{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none}.strip::-webkit-scrollbar{display:none}
#ng27 .pill{flex:0 0 auto;border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.05);color:#eaf0f6;border-radius:11px;padding:8px 10px;font-size:10px;font-weight:800;cursor:pointer}
#ng27 .pill.sel{border-color:transparent;background:linear-gradient(135deg,rgba(105,223,255,.92),rgba(140,125,255,.92));color:#071018}
#ng27 .range{display:grid;grid-template-columns:68px 1fr 32px;align-items:center;gap:8px;margin-top:10px;font-size:10px;color:#9aa7b8}
#ng27 input[type=range]{width:100%}
#ng27 .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:8px}
#ng27 .card{padding:8px;border-radius:12px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.035);font-size:9px;color:#8f9cae}.card b{display:block;color:#edf4fa;font-size:10px;margin-bottom:2px}
#ng27 .timeline{width:min(100%,920px);margin:11px auto 0;padding:11px 13px;border-radius:17px;border:1px solid rgba(255,255,255,.07);background:#0a0f17}
#ng27 .tlMeta{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;font-size:8px;font-weight:900;letter-spacing:.09em;color:#738296}
#ng27 .track{position:relative;height:50px;border-radius:11px;overflow:hidden;background:#121a25}
#ng27 .segment{position:absolute;top:0;bottom:0}.s1{left:0;width:20%;background:#172637}.s2{left:20%;width:20%;background:#20405a}.s3{left:40%;width:17%;background:#30475d}.s4{left:57%;width:22%;background:#22394e}.s5{left:79%;width:21%;background:#162433}
#ng27 .peak{position:absolute;top:5px;width:4px;height:40px;border-radius:4px;background:rgba(255,125,167,.82)}.p1{left:28%}.p2{left:53%}.p3{left:70%}
#ng27 .select{position:absolute;left:18%;right:16%;top:0;bottom:0;border:1.5px solid rgba(105,223,255,.95);border-radius:10px;box-shadow:0 0 16px rgba(105,223,255,.12)}
#ng27 .headLine{position:absolute;left:47%;top:-3px;bottom:-3px;width:1.5px;background:#fff;box-shadow:0 0 8px rgba(255,255,255,.55)}
#ng27 .events{display:flex;gap:6px;margin-top:7px;overflow-x:auto;scrollbar-width:none}.event{flex:0 0 auto;padding:5px 7px;border-radius:8px;background:#0f1722;border:1px solid rgba(255,255,255,.055);font-size:8px;font-weight:800;letter-spacing:.04em;color:#8293a8}.event.hot{color:#ffc1d2;border-color:rgba(255,125,167,.18)}
#ng27 .footNote{text-align:center;color:#58667a;font-size:9px;margin-top:8px;letter-spacing:.04em}
@media(max-width:820px){
 #ng27 .cockpit{grid-template-columns:1fr}
 #ng27 .rail{flex-direction:row;justify-content:center;overflow-x:auto}
 #ng27 .rail:first-child{order:2} #ng27 .stageWrap{order:1} #ng27 .rail:last-child{order:3}
 #ng27 .railBtn{width:54px;height:54px;border-radius:16px}
 #ng27 .stage{width:min(100%,470px);border-radius:25px}
}
</style>

<div class="shell">
  <div class="topline">
    <div class="brand">
      <div class="brandMark"><svg class="ico"><use href="#i-scan"/></svg></div>
      <div class="brandText"><b>GAMING SHORTS FACTORY</b><span>NEURAL GAME EDITOR · 2027 CONCEPT</span></div>
    </div>
    <div class="sys"><span class="sysDot"></span>GAME VISION ONLINE</div>
  </div>

  <div class="cockpit">
    <div class="rail">
      <button class="railBtn" data-panel="frame"><svg class="ico"><use href="#i-frame"/></svg><span>FRAME</span></button>
      <button class="railBtn" data-panel="look"><svg class="ico"><use href="#i-look"/></svg><span>LOOK</span></button>
      <button class="railBtn" data-panel="hud"><svg class="ico"><use href="#i-hud"/></svg><span>HUD</span></button>
      <button class="railBtn" data-panel="caption"><svg class="ico"><use href="#i-caption"/></svg><span>CAPTION</span></button>
      <button class="railBtn" data-panel="audio"><svg class="ico"><use href="#i-audio"/></svg><span>AUDIO</span></button>
    </div>

    <div class="stageWrap">
      <div class="stage">
        <video id="video" playsinline muted loop autoplay src="data:video/mp4;base64,__VIDEO__"></video>
        <div class="shade"></div><div class="scanlines"></div>
        <div class="corn c1"></div><div class="corn c2"></div><div class="corn c3"></div><div class="corn c4"></div>
        <div class="focus"><div class="focusRing"></div></div>

        <div class="hudTop">
          <div class="cluster">
            <button class="glass hudBtn"><svg class="ico"><use href="#i-back"/></svg></button>
            <button class="glass formatTag"><span class="signal"></span>9:16 SHORT</button>
          </div>
          <div class="cluster">
            <button class="glass hudBtn"><svg class="ico"><use href="#i-reset"/></svg></button>
            <button class="glass hudBtn"><svg class="ico"><use href="#i-close"/></svg></button>
          </div>
        </div>
        <div class="visionBadge">GAME VISION · SUBJECT LOCK</div>

        <div class="drawer hidden" id="drawer">
          <div class="drawerHead">
            <strong id="drawerTitle">Smart Frame</strong><small>GSF NEURAL MODULE</small>
            <button class="drawerClose" id="drawerClose"><svg class="ico"><use href="#i-close"/></svg></button>
          </div>
          <div id="drawerBody"></div>
        </div>
      </div>

      <div class="timeline">
        <div class="tlMeta"><span>IN · 00:08.0</span><span>GAME EVENT MAP</span><span>OUT · 00:23.0</span></div>
        <div class="track">
          <div class="segment s1"></div><div class="segment s2"></div><div class="segment s3"></div><div class="segment s4"></div><div class="segment s5"></div>
          <div class="peak p1"></div><div class="peak p2"></div><div class="peak p3"></div>
          <div class="select"></div><div class="headLine"></div>
        </div>
        <div class="events">
          <span class="event">AIM LOCK · 00:11</span><span class="event hot">ACTION PEAK · 00:15</span><span class="event">KILL EVENT · 00:18</span><span class="event">VOICE REACTION · 00:21</span>
        </div>
      </div>
    </div>

    <div class="rail">
      <button class="railBtn" id="playBtn"><svg class="ico" id="playIcon"><use href="#i-play"/></svg><span>PLAY</span></button>
      <button class="railBtn"><svg class="ico"><use href="#i-undo"/></svg><span>UNDO</span></button>
      <button class="railBtn"><svg class="ico"><use href="#i-redo"/></svg><span>REDO</span></button>
      <button class="railBtn" data-panel="vision"><svg class="ico ai"><use href="#i-ai"/></svg><span>GAME AI</span></button>
      <button class="railBtn"><svg class="ico"><use href="#i-done"/></svg><span>DONE</span></button>
    </div>
  </div>
  <div class="footNote">VECTOR UI PROTOTYPE · GAMING-FIRST · NO PRODUCTION FUNCTIONS CONNECTED</div>
</div>

<script>
(()=>{
 const root=document.getElementById('ng27'), drawer=root.querySelector('#drawer'), title=root.querySelector('#drawerTitle'), body=root.querySelector('#drawerBody'), video=root.querySelector('#video'), play=root.querySelector('#playBtn');
 const panels={
   frame:['Smart Frame','<div class="strip"><button class="pill sel">Player Focus</button><button class="pill">Crosshair Lock</button><button class="pill">Facecam Anchor</button><button class="pill">Free Crop</button></div><div class="range"><span>Tracking</span><input type="range" min="0" max="100" value="82"><b>82</b></div>'],
   look:['Game Look','<div class="strip"><button class="pill sel">Clean</button><button class="pill">Competitive</button><button class="pill">Neon Arena</button><button class="pill">Dark Raid</button><button class="pill">Boss Cinematic</button></div><div class="range"><span>Intensity</span><input type="range" min="0" max="100" value="64"><b>64</b></div>'],
   hud:['HUD Awareness','<div class="strip"><button class="pill sel">Auto Detect</button><button class="pill">Killfeed Safe</button><button class="pill">Minimap Safe</button><button class="pill">Facecam Safe</button></div><div class="cards"><div class="card"><b>KILLFEED</b>protected zone</div><div class="card"><b>MINIMAP</b>visibility lock</div><div class="card"><b>FACECAM</b>smart anchor</div></div>'],
   caption:['Gaming Captions','<div class="strip"><button class="pill sel">Impact</button><button class="pill">Clean HUD</button><button class="pill">Reaction</button><button class="pill">Boss Intro</button></div><div class="strip" style="margin-top:8px"><button class="pill">Font</button><button class="pill">Size</button><button class="pill">Position</button><button class="pill">Colors</button></div>'],
   audio:['Game Audio','<div class="strip"><button class="pill sel">Balanced</button><button class="pill">Voice Boost</button><button class="pill">Game Boost</button><button class="pill">Clutch Mode</button></div><div class="range"><span>Game Mix</span><input type="range" min="0" max="200" value="100"><b>100</b></div>'],
   vision:['Game Vision AI','<div class="cards"><div class="card"><b>ACTION FOCUS</b>tracks the important gameplay zone</div><div class="card"><b>HUD AWARENESS</b>protects killfeed and minimap</div><div class="card"><b>REACTION SYNC</b>links voice to action peaks</div></div><div class="strip" style="margin-top:8px"><button class="pill sel">Auto Gaming</button><button class="pill">FPS</button><button class="pill">Racing</button><button class="pill">Sports</button><button class="pill">Battle Royale</button></div>']
 };
 function wire(){
   body.querySelectorAll('.pill').forEach(p=>p.onclick=()=>{const row=p.parentElement;row.querySelectorAll('.pill').forEach(x=>x.classList.remove('sel'));p.classList.add('sel')});
   body.querySelectorAll('input[type=range]').forEach(r=>r.oninput=()=>{const b=r.parentElement.querySelector('b');if(b)b.textContent=r.value});
 }
 root.querySelectorAll('[data-panel]').forEach(btn=>btn.onclick=()=>{
   const name=btn.dataset.panel; title.textContent=panels[name][0]; body.innerHTML=panels[name][1]; drawer.classList.remove('hidden');
   root.querySelectorAll('.railBtn[data-panel]').forEach(x=>x.classList.toggle('active',x===btn)); wire();
 });
 root.querySelector('#drawerClose').onclick=()=>{drawer.classList.add('hidden');root.querySelectorAll('.railBtn').forEach(x=>x.classList.remove('active'))};
 play.onclick=()=>{const use=play.querySelector('use');const label=play.querySelector('span');if(video.paused){video.play();use.setAttribute('href','#i-pause');label.textContent='PAUSE'}else{video.pause();use.setAttribute('href','#i-play');label.textContent='PLAY'}};
})();
</script>
</div>
""".replace("__VIDEO__",video_b64)

components.html(html,height=1180,scrolling=False)
