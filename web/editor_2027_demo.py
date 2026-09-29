import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gaming Shorts Factory · Game Editor 2027", page_icon="🎮", layout="wide")
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],.stApp{background:#07090f!important;}
.block-container{max-width:1380px!important;padding:6px 12px 16px!important;}
header,[data-testid="stHeader"],footer{display:none!important;}
</style>
""", unsafe_allow_html=True)

video_path=Path("/app/demo_assets/demo_final.mp4")
video_b64=base64.b64encode(video_path.read_bytes()).decode("ascii") if video_path.exists() else ""

html = r"""
<div id="gsf27">
<style>
#gsf27{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#f5f7fb;--violet:#8b7cff;--cyan:#65d9ff;--mint:#6ef0c2;--hot:#ff7597;--panel:rgba(8,12,19,.78)}
#gsf27 *{box-sizing:border-box}
#gsf27 button{font:inherit}
#gsf27 .editor{max-width:1080px;margin:0 auto}
#gsf27 .hero{display:grid;grid-template-columns:minmax(0,1fr) 86px;gap:14px;align-items:start}
#gsf27 .stage{position:relative;margin:0 auto;width:min(100%,590px);aspect-ratio:9/16;background:#0b0f16;border-radius:30px;overflow:hidden;border:1px solid rgba(255,255,255,.09);box-shadow:0 28px 78px rgba(0,0,0,.44)}
#gsf27 video{width:100%;height:100%;display:block;object-fit:cover;background:#10131a}
#gsf27 .shade{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(5,7,12,.48),transparent 19%,transparent 67%,rgba(5,7,12,.68))}
#gsf27 .grid{position:absolute;inset:0;pointer-events:none;opacity:.08;background-image:linear-gradient(rgba(255,255,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.12) 1px,transparent 1px);background-size:52px 52px;mask-image:linear-gradient(180deg,transparent,black 20%,black 80%,transparent)}
#gsf27 .corner{position:absolute;width:34px;height:34px;border-color:rgba(101,217,255,.55);border-style:solid;z-index:4;pointer-events:none}
#gsf27 .c1{left:12px;top:12px;border-width:1px 0 0 1px;border-radius:10px 0 0 0}
#gsf27 .c2{right:12px;top:12px;border-width:1px 1px 0 0;border-radius:0 10px 0 0}
#gsf27 .c3{left:12px;bottom:12px;border-width:0 0 1px 1px;border-radius:0 0 0 10px}
#gsf27 .c4{right:12px;bottom:12px;border-width:0 1px 1px 0;border-radius:0 0 10px 0}
#gsf27 .top{position:absolute;top:14px;left:18px;right:18px;display:flex;justify-content:space-between;align-items:center;z-index:7}
#gsf27 .cluster{display:flex;gap:8px;align-items:center}
#gsf27 .glass{border:1px solid rgba(255,255,255,.12);background:rgba(9,13,20,.68);backdrop-filter:blur(16px);color:#fff}
#gsf27 .round{width:40px;height:40px;border-radius:13px;display:grid;place-items:center;cursor:pointer}
#gsf27 .tag{height:40px;padding:0 12px;border-radius:13px;font-weight:800;font-size:12px;letter-spacing:.03em;display:flex;align-items:center;gap:7px}
#gsf27 .statusDot{width:7px;height:7px;border-radius:50%;background:var(--mint);box-shadow:0 0 14px rgba(110,240,194,.7)}
#gsf27 .gameVision{position:absolute;left:16px;top:70px;z-index:6;padding:8px 10px;border-radius:12px;font-size:10px;font-weight:800;letter-spacing:.08em;color:#bfefff;border:1px solid rgba(101,217,255,.22);background:rgba(4,10,17,.48);backdrop-filter:blur(10px)}
#gsf27 .aimMark{position:absolute;left:50%;top:43%;width:54px;height:54px;transform:translate(-50%,-50%);opacity:.38;pointer-events:none}
#gsf27 .aimMark:before,#gsf27 .aimMark:after{content:"";position:absolute;background:rgba(101,217,255,.68)}
#gsf27 .aimMark:before{left:26px;top:4px;width:2px;height:46px}
#gsf27 .aimMark:after{top:26px;left:4px;height:2px;width:46px}
#gsf27 .dock{position:absolute;right:12px;top:78px;z-index:8;display:flex;flex-direction:column;gap:8px}
#gsf27 .tool{width:58px;height:58px;border-radius:18px;border:1px solid rgba(255,255,255,.12);background:rgba(7,11,17,.72);backdrop-filter:blur(16px);color:#f5f7fb;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;transition:.16s}
#gsf27 .tool b{font-size:19px;line-height:1}
#gsf27 .tool span{font-size:8px;font-weight:900;letter-spacing:.06em;opacity:.72}
#gsf27 .tool.active{border-color:rgba(101,217,255,.5);background:linear-gradient(145deg,rgba(101,217,255,.18),rgba(139,124,255,.18));box-shadow:0 0 0 1px rgba(101,217,255,.09),0 0 22px rgba(101,217,255,.16);transform:translateX(-2px)}
#gsf27 .quickAI{position:absolute;right:13px;bottom:20px;z-index:8;width:58px;height:58px;border-radius:18px;border:1px solid rgba(139,124,255,.35);background:linear-gradient(145deg,rgba(139,124,255,.23),rgba(101,217,255,.16));color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;cursor:pointer;box-shadow:0 0 24px rgba(139,124,255,.16)}
#gsf27 .quickAI b{font-size:20px}
#gsf27 .quickAI span{font-size:8px;font-weight:900;letter-spacing:.08em}
#gsf27 .drawer{position:absolute;left:14px;right:82px;bottom:16px;z-index:9;background:var(--panel);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:12px;transition:.18s}
#gsf27 .drawer.hidden{opacity:0;transform:translateY(10px);pointer-events:none}
#gsf27 .drawerHead{display:flex;align-items:center;justify-content:space-between;margin-bottom:9px}
#gsf27 .drawerHead strong{font-size:13px;letter-spacing:.02em}
#gsf27 .drawerHead small{font-size:9px;color:#89dfff;font-weight:900;letter-spacing:.08em}
#gsf27 .closeDraw{border:0;background:transparent;color:#fff;font-size:18px;cursor:pointer}
#gsf27 .strip{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none}
#gsf27 .strip::-webkit-scrollbar{display:none}
#gsf27 .pill{flex:0 0 auto;border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.06);color:#fff;border-radius:12px;padding:8px 11px;font-size:11px;font-weight:800;cursor:pointer}
#gsf27 .pill.sel{background:linear-gradient(135deg,rgba(101,217,255,.92),rgba(139,124,255,.92));color:#081018;border-color:transparent}
#gsf27 .rangeRow{display:grid;grid-template-columns:74px 1fr 34px;gap:8px;align-items:center;margin-top:10px;font-size:11px}
#gsf27 input[type=range]{width:100%}
#gsf27 .gamingStrip{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px}
#gsf27 .smart{border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.045);border-radius:13px;padding:8px 9px;font-size:10px;color:#cdd7e4}
#gsf27 .smart b{display:block;color:#fff;font-size:11px;margin-bottom:2px}
#gsf27 .sideRail{display:flex;flex-direction:column;gap:10px;align-items:center;padding-top:12px}
#gsf27 .sideRail .action{width:66px;min-height:62px;border-radius:19px;border:1px solid rgba(255,255,255,.09);background:#0f151f;color:#f3f6fa;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-size:19px;cursor:pointer}
#gsf27 .sideRail .action span{font-size:8px;font-weight:900;letter-spacing:.06em;opacity:.72}
#gsf27 .sideRail .action.primary{background:linear-gradient(145deg,#eef4ff,#d8e8ff);color:#0b1018}
#gsf27 .sideRail .action.ai{border-color:rgba(139,124,255,.28);color:#dcd7ff}
#gsf27 .timeline{width:min(100%,820px);margin:12px auto 0;padding:12px 14px;background:#0c1119;border:1px solid rgba(255,255,255,.07);border-radius:18px}
#gsf27 .tlMeta{display:flex;justify-content:space-between;align-items:center;color:#91a0b4;font-size:10px;margin-bottom:8px}
#gsf27 .track{position:relative;height:48px;border-radius:12px;overflow:hidden;background:#151d28}
#gsf27 .seg{position:absolute;top:0;bottom:0}
#gsf27 .s1{left:0;width:18%;background:#1b2a3a}
#gsf27 .s2{left:18%;width:22%;background:#25425b}
#gsf27 .s3{left:40%;width:18%;background:#3a4961}
#gsf27 .s4{left:58%;width:20%;background:#244056}
#gsf27 .s5{left:78%;width:22%;background:#182431}
#gsf27 .peak{position:absolute;top:5px;width:6px;height:38px;border-radius:4px;background:rgba(255,117,151,.78)}
#gsf27 .p1{left:25%}.p2{left:51%}.p3{left:68%}
#gsf27 .selection{position:absolute;left:18%;right:18%;top:0;bottom:0;border:2px solid rgba(101,217,255,.9);border-radius:11px;box-shadow:0 0 18px rgba(101,217,255,.12)}
#gsf27 .playhead{position:absolute;left:47%;top:-4px;bottom:-4px;width:2px;background:#fff;box-shadow:0 0 8px rgba(255,255,255,.55)}
#gsf27 .events{display:flex;gap:6px;margin-top:8px;overflow-x:auto;scrollbar-width:none}
#gsf27 .event{flex:0 0 auto;padding:6px 8px;border-radius:9px;background:#101824;border:1px solid rgba(255,255,255,.06);font-size:9px;color:#9fb2c9}
#gsf27 .event.hot{color:#ffd5df;border-color:rgba(255,117,151,.2)}
#gsf27 .hint{text-align:center;color:#627083;font-size:10px;margin-top:9px}
@media(max-width:760px){
  #gsf27 .hero{grid-template-columns:1fr}
  #gsf27 .stage{width:min(100%,455px);border-radius:24px}
  #gsf27 .sideRail{flex-direction:row;justify-content:center;overflow-x:auto;padding-top:0}
  #gsf27 .sideRail .action{width:58px;min-height:54px;border-radius:16px}
  #gsf27 .dock{right:8px;top:72px}
  #gsf27 .tool{width:50px;height:50px;border-radius:16px}
  #gsf27 .quickAI{width:50px;height:50px;right:8px}
  #gsf27 .drawer{left:8px;right:64px;bottom:8px}
  #gsf27 .gamingStrip{grid-template-columns:1fr}
}
</style>

<div class="editor">
  <div class="hero">
    <div>
      <div class="stage">
        <video id="vid" playsinline muted loop autoplay src="data:video/mp4;base64,__VIDEO__"></video>
        <div class="shade"></div><div class="grid"></div>
        <div class="corner c1"></div><div class="corner c2"></div><div class="corner c3"></div><div class="corner c4"></div>
        <div class="aimMark"></div>

        <div class="top">
          <div class="cluster">
            <button class="round glass" title="Indietro">‹</button>
            <button class="tag glass"><span class="statusDot"></span><span id="fmtTop">9:16 SHORT</span></button>
          </div>
          <div class="cluster">
            <button class="round glass" title="Reset">↶</button>
            <button class="round glass" title="Chiudi">✕</button>
          </div>
        </div>

        <div class="gameVision">GAME VISION · ACTIVE</div>

        <div class="dock">
          <button class="tool" data-panel="frame"><b>⌖</b><span>FRAME</span></button>
          <button class="tool" data-panel="look"><b>◫</b><span>LOOK</span></button>
          <button class="tool" data-panel="hud"><b>◎</b><span>HUD</span></button>
          <button class="tool" data-panel="text"><b>Aa</b><span>CAPTION</span></button>
          <button class="tool" data-panel="audio"><b>≋</b><span>AUDIO</span></button>
        </div>

        <button class="quickAI" data-panel="vision"><b>✦</b><span>GAME AI</span></button>

        <div class="drawer hidden" id="drawer">
          <div class="drawerHead">
            <strong id="drawerTitle">Game Vision</strong>
            <small>GSF · 2027</small>
            <button class="closeDraw" id="closeDraw">×</button>
          </div>
          <div id="drawerBody"></div>
        </div>
      </div>

      <div class="timeline">
        <div class="tlMeta"><span>IN 00:08.0</span><span>ACTION MAP</span><span>OUT 00:23.0</span></div>
        <div class="track">
          <div class="seg s1"></div><div class="seg s2"></div><div class="seg s3"></div><div class="seg s4"></div><div class="seg s5"></div>
          <div class="peak p1"></div><div class="peak p2"></div><div class="peak p3"></div>
          <div class="selection"></div><div class="playhead"></div>
        </div>
        <div class="events">
          <span class="event">🎯 AIM LOCK 00:11</span>
          <span class="event hot">⚡ ACTION PEAK 00:15</span>
          <span class="event">💥 KILL EVENT 00:18</span>
          <span class="event">🎙 REACTION 00:21</span>
        </div>
      </div>
    </div>

    <aside class="sideRail">
      <button class="action primary" id="playBtn">▶<span>PLAY</span></button>
      <button class="action">↶<span>UNDO</span></button>
      <button class="action">↷<span>REDO</span></button>
      <button class="action ai" data-panel="vision">✦<span>AI ASSIST</span></button>
      <button class="action">✓<span>DONE</span></button>
    </aside>
  </div>
  <div class="hint">Concept grafico gaming-first · prototipo demo · nessun render reale viene modificato</div>
</div>

<script>
(()=>{
  const root=document.getElementById('gsf27');
  const drawer=root.querySelector('#drawer');
  const title=root.querySelector('#drawerTitle');
  const body=root.querySelector('#drawerBody');
  const video=root.querySelector('#vid');
  const play=root.querySelector('#playBtn');
  const tools=[...root.querySelectorAll('[data-panel]')];

  const panels={
    frame:['Smart Frame',
      '<div class="strip"><button class="pill sel">Player Focus</button><button class="pill">Crosshair</button><button class="pill">Facecam</button><button class="pill">Free Crop</button></div>'+
      '<div class="rangeRow"><span>Tracking</span><input type="range" min="0" max="100" value="82"><b>82</b></div>'],
    look:['Game Look',
      '<div class="strip"><button class="pill sel">Clean</button><button class="pill">Competitive</button><button class="pill">Neon Arena</button><button class="pill">Dark Raid</button><button class="pill">Cinematic Boss</button></div>'+
      '<div class="rangeRow"><span>Intensity</span><input type="range" min="0" max="100" value="64"><b>64</b></div>'],
    hud:['HUD Safe-Zone',
      '<div class="strip"><button class="pill sel">Auto Detect</button><button class="pill">Killfeed Safe</button><button class="pill">Map Safe</button><button class="pill">Facecam Safe</button></div>'+
      '<div class="gamingStrip"><div class="smart"><b>Killfeed</b>area protected</div><div class="smart"><b>Minimap</b>kept visible</div><div class="smart"><b>Facecam</b>smart anchor</div></div>'],
    text:['Gaming Captions',
      '<div class="strip"><button class="pill sel">Impact</button><button class="pill">Clean HUD</button><button class="pill">Reaction</button><button class="pill">Boss Intro</button></div>'+
      '<div class="strip" style="margin-top:8px"><button class="pill">Font</button><button class="pill">Size</button><button class="pill">Position</button><button class="pill">Colors</button></div>'],
    audio:['Game Audio',
      '<div class="strip"><button class="pill sel">Balanced</button><button class="pill">Voice Boost</button><button class="pill">Game Boost</button><button class="pill">Clutch Mode</button></div>'+
      '<div class="rangeRow"><span>Game mix</span><input type="range" min="0" max="200" value="100"><b>100</b></div>'],
    vision:['Game Vision AI',
      '<div class="gamingStrip"><div class="smart"><b>Action Focus</b>tracks the important gameplay area</div><div class="smart"><b>HUD Awareness</b>avoids covering killfeed and minimap</div><div class="smart"><b>Reaction Sync</b>links captions to peaks and voice</div></div>'+
      '<div class="strip" style="margin-top:9px"><button class="pill sel">Auto Gaming</button><button class="pill">FPS</button><button class="pill">Racing</button><button class="pill">Sports</button><button class="pill">Battle Royale</button></div>']
  };

  function wire(){
    body.querySelectorAll('.pill').forEach(p=>p.addEventListener('click',()=>{
      const strip=p.parentElement;
      strip.querySelectorAll('.pill').forEach(x=>x.classList.remove('sel'));
      p.classList.add('sel');
    }));
    body.querySelectorAll('input[type=range]').forEach(r=>r.addEventListener('input',()=>{
      const b=r.parentElement.querySelector('b');
      if(b)b.textContent=r.value;
    }));
  }

  function openPanel(name,btn){
    title.textContent=panels[name][0];
    body.innerHTML=panels[name][1];
    drawer.classList.remove('hidden');
    [...root.querySelectorAll('.tool')].forEach(x=>x.classList.toggle('active',x===btn));
    wire();
  }

  root.querySelectorAll('[data-panel]').forEach(btn=>btn.addEventListener('click',()=>openPanel(btn.dataset.panel,btn)));
  root.querySelector('#closeDraw').addEventListener('click',()=>{
    drawer.classList.add('hidden');
    root.querySelectorAll('.tool').forEach(x=>x.classList.remove('active'));
  });
  play.addEventListener('click',()=>{
    if(video.paused){ video.play(); play.innerHTML='❚❚<span>PAUSE</span>'; }
    else{ video.pause(); play.innerHTML='▶<span>PLAY</span>'; }
  });
})();
</script>
</div>
""".replace("__VIDEO__", video_b64)

components.html(html, height=1120, scrolling=False)
