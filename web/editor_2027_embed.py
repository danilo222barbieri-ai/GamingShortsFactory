import base64
from pathlib import Path
import streamlit.components.v1 as components

_TEMPLATE = r'''
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
#ng27{--cyan:#55c8ee;--violet:#8278e8;--mint:#59cfa8;--pink:#e889a3;--ink:#33485b;--muted:#718397;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink)}
#ng27 *{box-sizing:border-box}
#ng27 button,#ng27 input{font:inherit}
#ng27 button{cursor:pointer}
#ng27 .ico{width:22px;height:22px;display:block;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
#ng27 .ico.ai{stroke-width:1.55}
#ng27 .shell{max-width:640px;margin:0 auto;padding:6px;border-radius:26px;border:1px solid #d9e7f0;background:radial-gradient(circle at 18% 12%,rgba(126,211,239,.26),transparent 30%),radial-gradient(circle at 84% 18%,rgba(171,159,238,.20),transparent 34%),linear-gradient(145deg,#f7fbfe 0%,#eef6fb 52%,#f4f2fb 100%);box-shadow:0 16px 38px rgba(71,101,126,.12);position:relative;overflow:hidden}
#ng27 .shell:after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.38;background-image:linear-gradient(rgba(111,142,164,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(111,142,164,.05) 1px,transparent 1px);background-size:34px 34px}
#ng27 .topline{position:relative;z-index:3;display:flex;align-items:center;justify-content:space-between;padding:0 3px 6px}
#ng27 .brand{display:flex;align-items:center;gap:9px}
#ng27 .brandMark{width:27px;height:27px;border-radius:10px;background:linear-gradient(145deg,#ffffff,#dde6ec);border:1px solid #c8d5de;box-shadow:inset 0 1px 0 #fff,0 3px 8px rgba(83,105,123,.08);display:grid;place-items:center}
#ng27 .brandMark .ico{width:15px;height:15px;color:#526a7c}
#ng27 .brandText b{display:block;font-size:9px;letter-spacing:.16em}
#ng27 .brandText span{display:block;font-size:7px;color:#7d8fa0;letter-spacing:.14em;margin-top:2px}
#ng27 .sys{display:flex;align-items:center;gap:7px;font-size:8px;font-weight:900;letter-spacing:.14em;color:#6f8293}
#ng27 .sysDot{width:6px;height:6px;border-radius:50%;background:var(--mint);box-shadow:0 0 12px rgba(102,240,195,.7)}
#ng27 .cockpit{position:relative;z-index:2;display:grid;grid-template-columns:42px minmax(0,1fr) 42px;gap:4px;align-items:center}
#ng27 .rail{display:flex;flex-direction:column;gap:4px;align-items:center}
#ng27 .railBtn{width:39px;height:39px;border-radius:12px;border:1px solid #c4cfd7;background:linear-gradient(145deg,#ffffff 0%,#e6ebef 40%,#cfd6dc 100%);box-shadow:inset 0 1px 0 #fff,inset 0 -1px 0 rgba(92,111,126,.10),0 4px 9px rgba(73,94,110,.10);color:#405566;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;transition:.16s}
#ng27 .railBtn .ico{width:15px;height:15px}
#ng27 .railBtn span{font-size:5.9px;font-weight:900;letter-spacing:.08em;color:#677c8d}
#ng27 .railBtn:hover,#ng27 .railBtn.active{border-color:#9fcddd;background:linear-gradient(145deg,#fbfeff 0%,#d4e9f0 50%,#ddd7f0 100%);color:#29495e;transform:translateY(-1px);box-shadow:inset 0 1px 0 #fff,0 6px 13px rgba(76,120,145,.14)}
#ng27 .railBtn.active span{color:#3f708a}
#ng27 .stageWrap{min-width:0}
#ng27 .stage{position:relative;margin:0 auto;background:#0b1017;overflow:hidden;border:1px solid rgba(255,255,255,.1);box-shadow:0 18px 48px rgba(0,0,0,.34);transition:width .24s,aspect-ratio .24s,border-radius .24s}
#ng27 .stage.r916{width:min(100%,360px);aspect-ratio:9/16;border-radius:26px}
#ng27 video{width:100%;height:100%;object-fit:cover;display:block;background:#10141b;transform-origin:center center;transition:filter .16s,transform .16s}
#ng27 .shade{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(3,7,12,.46),transparent 17%,transparent 69%,rgba(3,7,12,.66))}
#ng27 .scanlines{position:absolute;inset:0;pointer-events:none;opacity:.055;background:repeating-linear-gradient(180deg,rgba(255,255,255,.14) 0,rgba(255,255,255,.14) 1px,transparent 1px,transparent 5px)}
#ng27 .corn{position:absolute;width:38px;height:38px;z-index:4;pointer-events:none;border-color:rgba(105,223,255,.52);border-style:solid}
#ng27 .c1{top:12px;left:12px;border-width:1px 0 0 1px;border-radius:11px 0 0 0}
#ng27 .c2{top:12px;right:12px;border-width:1px 1px 0 0;border-radius:0 11px 0 0}
#ng27 .c3{bottom:12px;left:12px;border-width:0 0 1px 1px;border-radius:0 0 0 11px}
#ng27 .c4{bottom:12px;right:12px;border-width:0 1px 1px 0;border-radius:0 0 11px 0}
#ng27 .hudTop{position:absolute;top:15px;left:17px;right:17px;z-index:8;display:flex;justify-content:space-between;align-items:center}
#ng27 .glass{height:30px;border-radius:12px;border:1px solid #c4cdd5;background:linear-gradient(145deg,rgba(255,255,255,.95),rgba(205,214,222,.93));backdrop-filter:blur(16px);box-shadow:inset 0 1px 0 #fff,0 4px 9px rgba(50,68,82,.14);color:#354b5c}
#ng27 .hudBtn{width:30px;display:grid;place-items:center}
#ng27 .hudBtn .ico{width:18px;height:18px}
#ng27 .cluster{display:flex;gap:7px;align-items:center}
#ng27 .formatTag{padding:0 8px;display:flex;align-items:center;gap:7px;font-size:9px;font-weight:900;letter-spacing:.09em}
#ng27 .signal{width:6px;height:6px;border-radius:50%;background:var(--cyan);box-shadow:0 0 12px rgba(105,223,255,.7)}
#ng27 .visionBadge{position:absolute;left:17px;top:62px;z-index:6;padding:6px 8px;border-radius:9px;border:1px solid rgba(190,210,220,.65);background:rgba(241,247,250,.82);backdrop-filter:blur(12px);font-size:8px;font-weight:900;letter-spacing:.11em;color:#4d758b;box-shadow:0 3px 9px rgba(37,58,73,.10)}
#ng27 .focus{position:absolute;left:50%;top:43%;width:74px;height:74px;transform:translate(-50%,-50%);pointer-events:none;opacity:.34;transition:left .16s,top .16s}
#ng27 .focus:before,#ng27 .focus:after{content:"";position:absolute;background:rgba(105,223,255,.7)}
#ng27 .focus:before{left:36px;top:8px;width:1px;height:58px}
#ng27 .focus:after{top:36px;left:8px;height:1px;width:58px}
#ng27 .focusRing{position:absolute;inset:17px;border:1px solid rgba(105,223,255,.6);border-radius:50%}
#ng27 .safeZone{position:absolute;z-index:5;pointer-events:none;border:1px dashed rgba(102,240,195,.78);background:rgba(102,240,195,.045);border-radius:10px;display:none}
#ng27 .safeZone.show{display:block}
#ng27 .safeZone span{position:absolute;top:5px;left:7px;font-size:7px;font-weight:900;letter-spacing:.08em;color:#baf7e3}
#ng27 .killZone{right:16px;top:92px;width:34%;height:15%}
#ng27 .mapZone{left:16px;bottom:90px;width:29%;height:25%}
#ng27 .faceZone{right:16px;bottom:90px;width:28%;height:27%}
#ng27 .captionPreview{position:absolute;z-index:7;left:50%;top:76%;transform:translate(-50%,-50%);width:82%;text-align:center;font-size:24px;font-weight:950;line-height:1.02;color:#fff;text-shadow:-2px -2px 0 #000,2px -2px 0 #000,-2px 2px 0 #000,2px 2px 0 #000,0 4px 18px rgba(0,0,0,.55);pointer-events:none;transition:top .15s,font-size .15s,color .15s}
#ng27 .captionPreview.off{display:none}
#ng27 .captionPreview .hotWord{color:#ffd400}
#ng27 .drawer{position:absolute;left:12px;right:12px;bottom:12px;z-index:10;background:rgba(244,249,252,.94);backdrop-filter:blur(22px);border:1px solid rgba(188,204,215,.88);border-radius:18px;padding:10px;transition:.18s;box-shadow:0 11px 24px rgba(29,49,64,.15)}
#ng27 .drawer.hidden{opacity:0;transform:translateY(11px);pointer-events:none}
#ng27 .drawerHead{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px}
#ng27 .drawerHead strong{font-size:12px;letter-spacing:.04em}
#ng27 .drawerHead small{font-size:8px;color:#5f8fa5;font-weight:900;letter-spacing:.12em}
#ng27 .drawerClose{border:0;background:transparent;color:#647889;padding:2px}
#ng27 .drawerClose .ico{width:16px;height:16px}
#ng27 .strip{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none}
#ng27 .strip::-webkit-scrollbar{display:none}
#ng27 .pill{flex:0 0 auto;border:1px solid #ccd8e0;background:linear-gradient(145deg,#ffffff,#e5ebef);color:#496071;border-radius:10px;padding:7px 9px;font-size:9px;font-weight:800;box-shadow:inset 0 1px 0 #fff}
#ng27 .pill.sel{border-color:#9fcddd;background:linear-gradient(135deg,#c8edf8,#d8d1f1);color:#294a5f}
#ng27 .range{display:grid;grid-template-columns:74px 1fr 34px;align-items:center;gap:7px;margin-top:8px;font-size:9px;color:#687d8e}
#ng27 .range input[type=range]{width:100%}
#ng27 .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:8px}
#ng27 .card{padding:7px;border-radius:11px;border:1px solid #d3dee5;background:rgba(255,255,255,.70);font-size:8px;color:#758897}
#ng27 .card b{display:block;color:#40576a;font-size:9px;margin-bottom:2px}
#ng27 .colorGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:9px}
#ng27 .colorBox{padding:7px;border-radius:11px;border:1px solid #d3dee5;background:rgba(255,255,255,.70)}
#ng27 .colorBox label{display:block;font-size:8px;font-weight:900;letter-spacing:.08em;color:#718495;margin-bottom:5px}
#ng27 .colorRow{display:flex;gap:6px;align-items:center}
#ng27 .colorRow input[type=color]{width:36px;height:30px;border:0;padding:0;background:transparent}
#ng27 .applyBtn{height:29px;border-radius:9px;border:1px solid #bdcbd4;background:linear-gradient(145deg,#ffffff,#dde5ea);color:#496173;font-size:8px;font-weight:900;letter-spacing:.05em;padding:0 8px}
#ng27 .textRow{display:flex;gap:7px;margin-top:8px}
#ng27 .textRow input{flex:1;min-width:0;height:32px;border-radius:10px;border:1px solid #c9d5dd;background:#ffffff;color:#3f5567;padding:0 9px;font-size:9px}
#ng27 .timeline{width:min(100%,560px);margin:4px auto 0;padding:5px 7px;border-radius:15px;border:1px solid #d2dfe7;background:linear-gradient(145deg,rgba(255,255,255,.84),rgba(231,239,245,.90));box-shadow:0 6px 16px rgba(73,94,110,.08)}
#ng27 .tlMeta{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;font-size:7.5px;font-weight:900;letter-spacing:.09em;color:#6f8293}
#ng27 .track{position:relative;height:27px;border-radius:10px;overflow:hidden;background:#dbe7ee}
#ng27 .segment{position:absolute;top:0;bottom:0}
#ng27 .s1{left:0;width:20%;background:#d7e5ed}
#ng27 .s2{left:20%;width:20%;background:#c3ddea}
#ng27 .s3{left:40%;width:17%;background:#d7d4ec}
#ng27 .s4{left:57%;width:22%;background:#cbdce8}
#ng27 .s5{left:79%;width:21%;background:#dce8ef}
#ng27 .peak{position:absolute;top:5px;width:4px;height:22px;border-radius:4px;background:rgba(255,125,167,.82)}
#ng27 .p1{left:28%}
#ng27 .p2{left:53%}
#ng27 .p3{left:70%}
#ng27 .select{position:absolute;left:0;right:0;top:0;bottom:0;border:1.5px solid rgba(105,223,255,.95);border-radius:10px;box-shadow:0 0 16px rgba(105,223,255,.12);pointer-events:none}
#ng27 .headLine{position:absolute;left:0;top:-3px;bottom:-3px;width:1.5px;background:#fff;box-shadow:0 0 8px rgba(255,255,255,.55);pointer-events:none}
#ng27 .events{display:flex;gap:5px;margin-top:5px;overflow-x:auto;scrollbar-width:none}
#ng27 .event{flex:0 0 auto;padding:3px 6px;border-radius:8px;background:#f7fbfd;border:1px solid #d5e1e8;font-size:7.5px;font-weight:800;letter-spacing:.04em;color:#728698}
#ng27 .event.hot{color:#ffc1d2;border-color:rgba(255,125,167,.18)}
#ng27 .trimRow{display:grid;grid-template-columns:38px 1fr 46px 38px 1fr 46px;gap:5px;align-items:center;margin-top:6px;font-size:8px;font-weight:900;letter-spacing:.05em;color:#75859a}
#ng27 .trimRow input{width:100%}
#ng27 .trimValue{color:#52697b}
#ng27 .toast{position:absolute;left:50%;bottom:18px;z-index:14;transform:translate(-50%,14px);opacity:0;pointer-events:none;padding:8px 12px;border-radius:11px;border:1px solid rgba(102,240,195,.18);background:rgba(5,13,17,.88);backdrop-filter:blur(14px);color:#baf7e3;font-size:9px;font-weight:900;letter-spacing:.05em;transition:.2s}
#ng27 .toast.show{opacity:1;transform:translate(-50%,0)}
#ng27 .footNote{text-align:center;color:#738597;font-size:8px;margin-top:5px;letter-spacing:.04em}
@media(max-width:820px){
 #ng27 .cockpit{grid-template-columns:1fr}
 #ng27 .rail{flex-direction:row;justify-content:center;overflow-x:auto}
 #ng27 .rail:first-child{order:2}
 #ng27 .stageWrap{order:1}
 #ng27 .rail:last-child{order:3}
 #ng27 .railBtn{width:54px;height:54px;border-radius:16px}
 #ng27 .stage.r916{width:min(100%,360px)}
 #ng27 .captionPreview{font-size:28px}
 #ng27 .trimRow{grid-template-columns:34px 1fr 42px;row-gap:5px}
 #ng27 .cards,#ng27 .colorGrid{grid-template-columns:1fr}
}
</style>

<div class="shell">
  <div class="topline">
    <div class="brand">
      <div class="brandMark"><svg class="ico"><use href="#i-scan"/></svg></div>
      <div class="brandText"><b>GAMING SHORTS FACTORY</b><span>NEURAL GAME EDITOR · LIVE PREVIEW</span></div>
    </div>
    <div class="sys"><span class="sysDot"></span><span id="sysText">GAME VISION ONLINE</span></div>
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
      <div class="stage r916" id="stage">
        <video id="video" playsinline muted loop autoplay src="data:video/mp4;base64,__VIDEO__"></video>
        <div class="shade"></div><div class="scanlines"></div>
        <div class="corn c1"></div><div class="corn c2"></div><div class="corn c3"></div><div class="corn c4"></div>
        <div class="focus" id="focus"><div class="focusRing"></div></div>
        <div class="safeZone killZone" id="killZone"><span>KILLFEED SAFE</span></div>
        <div class="safeZone mapZone" id="mapZone"><span>MINIMAP SAFE</span></div>
        <div class="safeZone faceZone" id="faceZone"><span>FACECAM SAFE</span></div>
        <div class="captionPreview" id="captionPreview">NO SCOPE <span class="hotWord">CLUTCH!</span></div>

        <div class="hudTop">
          <div class="cluster">
            <button class="glass hudBtn" id="backBtn" title="Indietro"><svg class="ico"><use href="#i-back"/></svg></button>
            <div class="glass formatTag"><span class="signal"></span><span id="formatLabel">9:16 SHORT</span></div>
          </div>
          <div class="cluster">
            <button class="glass hudBtn" id="resetBtn" title="Reset"><svg class="ico"><use href="#i-reset"/></svg></button>
            <button class="glass hudBtn" id="closeBtn" title="Chiudi pannello"><svg class="ico"><use href="#i-close"/></svg></button>
          </div>
        </div>

        <div class="visionBadge" id="visionBadge">GAME VISION · SUBJECT LOCK</div>

        <div class="drawer hidden" id="drawer">
          <div class="drawerHead">
            <strong id="drawerTitle">Smart Frame</strong><small>GSF LIVE MODULE</small>
            <button class="drawerClose" id="drawerClose"><svg class="ico"><use href="#i-close"/></svg></button>
          </div>
          <div id="drawerBody"></div>
        </div>
        <div class="toast" id="toast">PREVIEW AGGIORNATA</div>
      </div>

      <div class="timeline">
        <div class="tlMeta"><span id="inMeta">IN · 00:00.0</span><span>GAME EVENT MAP</span><span id="outMeta">OUT · 00:15.0</span></div>
        <div class="track">
          <div class="segment s1"></div><div class="segment s2"></div><div class="segment s3"></div><div class="segment s4"></div><div class="segment s5"></div>
          <div class="peak p1"></div><div class="peak p2"></div><div class="peak p3"></div>
          <div class="select" id="selection"></div><div class="headLine" id="playhead"></div>
        </div>
        <div class="events">
          <span class="event">AIM LOCK · 00:03</span><span class="event hot">ACTION PEAK · 00:07</span><span class="event">KILL EVENT · 00:10</span><span class="event">VOICE REACTION · 00:13</span>
        </div>
        <div class="trimRow">
          <span>IN</span><input id="inRange" type="range" min="0" max="14.5" step="0.1" value="0"><span class="trimValue" id="inValue">00:00.0</span>
          <span>OUT</span><input id="outRange" type="range" min="0.5" max="15" step="0.1" value="15"><span class="trimValue" id="outValue">00:15.0</span>
        </div>
      </div>
    </div>

    <div class="rail">
      <button class="railBtn" id="playBtn"><svg class="ico"><use id="playUse" href="#i-play"/></svg><span id="playLabel">PLAY</span></button>
      <button class="railBtn" id="undoBtn"><svg class="ico"><use href="#i-undo"/></svg><span>UNDO</span></button>
      <button class="railBtn" id="redoBtn"><svg class="ico"><use href="#i-redo"/></svg><span>REDO</span></button>
      <button class="railBtn" data-panel="vision"><svg class="ico ai"><use href="#i-ai"/></svg><span>GAME AI</span></button>
      <button class="railBtn" id="doneBtn"><svg class="ico"><use href="#i-done"/></svg><span>DONE</span></button>
    </div>
  </div>
  <div class="footNote">DEMO FUNZIONALE PREVIEW · FORMAT / FRAME / LOOK / HUD / CAPTION / AUDIO / IN-OUT / UNDO-REDO ATTIVI</div>
</div>

<script>
(()=>{
 const root=document.getElementById('ng27');
 const stage=root.querySelector('#stage');
 const video=root.querySelector('#video');
 const drawer=root.querySelector('#drawer');
 const title=root.querySelector('#drawerTitle');
 const body=root.querySelector('#drawerBody');
 const toast=root.querySelector('#toast');
 const caption=root.querySelector('#captionPreview');
 const focus=root.querySelector('#focus');
 const playUse=root.querySelector('#playUse');
 const playLabel=root.querySelector('#playLabel');
 const formatLabel=root.querySelector('#formatLabel');
 const visionBadge=root.querySelector('#visionBadge');
 const sysText=root.querySelector('#sysText');
 const selection=root.querySelector('#selection');
 const playhead=root.querySelector('#playhead');
 const inRange=root.querySelector('#inRange');
 const outRange=root.querySelector('#outRange');
 const inValue=root.querySelector('#inValue');
 const outValue=root.querySelector('#outValue');
 const inMeta=root.querySelector('#inMeta');
 const outMeta=root.querySelector('#outMeta');
 const zones={
   kill:root.querySelector('#killZone'),
   map:root.querySelector('#mapZone'),
   face:root.querySelector('#faceZone')
 };

 const defaults={
   zoom:1,panX:0,panY:0,
   look:'Clean',intensity:64,brightness:100,contrast:100,
   hudMode:'Off',
   captionOn:true,captionText:'NO SCOPE CLUTCH!',captionSize:36,captionY:76,
   textColor:'#ffffff',activeColor:'#ffd400',outlineColor:'#000000',
   muted:true,volume:100,speed:1,
   inPoint:0,outPoint:15,
   aiMode:'Auto Gaming'
 };
 let state={...defaults};
 let history=[JSON.stringify(state)];
 let historyIndex=0;
 let duration=15;

 const cloneState=()=>JSON.parse(JSON.stringify(state));
 function commit(){
   const snap=JSON.stringify(state);
   if(history[historyIndex]===snap) return;
   history=history.slice(0,historyIndex+1);
   history.push(snap);
   historyIndex=history.length-1;
 }
 function flash(msg='PREVIEW AGGIORNATA'){
   toast.textContent=msg;
   toast.classList.add('show');
   clearTimeout(flash.t);
   flash.t=setTimeout(()=>toast.classList.remove('show'),950);
 }
 function fmtTime(v){
   v=Math.max(0,Number(v)||0);
   const m=Math.floor(v/60), s=v-m*60;
   return String(m).padStart(2,'0')+':'+s.toFixed(1).padStart(4,'0');
 }
 function filterFor(s){
   const t=Math.max(0,Math.min(1,s.intensity/100));
   let extra='';
   if(s.look==='Competitive') extra=' saturate('+(1+.42*t)+') contrast('+(1+.12*t)+')';
   if(s.look==='Neon Arena') extra=' saturate('+(1+.58*t)+') hue-rotate('+(4*t)+'deg) contrast('+(1+.11*t)+')';
   if(s.look==='Dark Raid') extra=' saturate('+(1-.18*t)+') brightness('+(1-.12*t)+') contrast('+(1+.18*t)+')';
   if(s.look==='Boss Cinematic') extra=' saturate('+(1-.13*t)+') sepia('+(0.12*t)+') contrast('+(1+.14*t)+')';
   return 'brightness('+(s.brightness/100)+') contrast('+(s.contrast/100)+')'+extra;
 }
 function applyState(){
   stage.classList.add('r916');
   formatLabel.textContent='9:16 SHORT';

   video.style.transform='translate('+state.panX+'%,'+state.panY+'%) scale('+state.zoom+')';
   video.style.filter=filterFor(state);
   video.muted=state.muted;
   video.volume=Math.max(0,Math.min(1,state.volume/100));
   video.playbackRate=state.speed;

   const words=String(state.captionText||'').trim().split(/\s+/);
   let html='';
   if(words.length){
     const last=words.pop();
     html=(words.join(' ')+' <span class="hotWord">'+last+'</span>').trim();
   }
   caption.innerHTML=html || 'NO SCOPE <span class="hotWord">CLUTCH!</span>';
   caption.classList.toggle('off',!state.captionOn);
   caption.style.fontSize=state.captionSize+'px';
   caption.style.top=state.captionY+'%';
   caption.style.color=state.textColor;
   caption.style.textShadow=
      '-2px -2px 0 '+state.outlineColor+',2px -2px 0 '+state.outlineColor+
      ',-2px 2px 0 '+state.outlineColor+',2px 2px 0 '+state.outlineColor+',0 4px 18px rgba(0,0,0,.55)';
   caption.querySelectorAll('.hotWord').forEach(x=>x.style.color=state.activeColor);

   Object.values(zones).forEach(z=>z.classList.remove('show'));
   if(state.hudMode==='Auto Detect'){zones.kill.classList.add('show');zones.map.classList.add('show');zones.face.classList.add('show')}
   if(state.hudMode==='Killfeed Safe') zones.kill.classList.add('show');
   if(state.hudMode==='Minimap Safe') zones.map.classList.add('show');
   if(state.hudMode==='Facecam Safe') zones.face.classList.add('show');

   focus.style.left=(50+state.panX*.7)+'%';
   focus.style.top=(43+state.panY*.7)+'%';
   visionBadge.textContent='GAME VISION · '+(state.aiMode==='Auto Gaming'?'SUBJECT LOCK':state.aiMode.toUpperCase());
   sysText.textContent='GAME VISION · '+state.aiMode.toUpperCase();

   inRange.max=Math.max(.5,duration-.5);
   outRange.max=duration;
   inRange.value=state.inPoint;
   outRange.value=state.outPoint;
   inValue.textContent=fmtTime(state.inPoint);
   outValue.textContent=fmtTime(state.outPoint);
   inMeta.textContent='IN · '+fmtTime(state.inPoint);
   outMeta.textContent='OUT · '+fmtTime(state.outPoint);
   const left=(state.inPoint/duration)*100;
   const right=100-(state.outPoint/duration)*100;
   selection.style.left=left+'%';
   selection.style.right=right+'%';
 }
 function choosePill(container,value){
   container.querySelectorAll('.pill').forEach(p=>p.classList.toggle('sel',p.dataset.value===String(value)));
 }
 function wirePills(key,after){
   body.querySelectorAll('.pill[data-key="'+key+'"]').forEach(p=>{
     p.onclick=()=>{
       state[key]=p.dataset.value;
       choosePill(p.parentElement,state[key]);
       if(after) after(p.dataset.value);
       applyState(); commit(); flash();
     };
   });
 }
 function wireRange(id,key,cast,after){
   const el=body.querySelector('#'+id);
   if(!el)return;
   el.oninput=()=>{
     state[key]=cast(el.value);
     const b=el.parentElement.querySelector('b');
     if(b)b.textContent=String(state[key]);
     if(after)after(state[key]);
     applyState();
   };
   el.onchange=()=>{commit();flash()};
 }
 function openPanel(name,btn){
   const templates={
    frame:['Smart Frame',
      '<div class="strip">'+
      '<button class="pill framePreset" data-value="focus">Player Focus</button>'+
      '<button class="pill framePreset" data-value="cross">Crosshair Lock</button>'+
      '<button class="pill framePreset" data-value="face">Facecam Anchor</button>'+
      '<button class="pill framePreset" data-value="free">Free</button></div>'+
      '<div class="range"><span>Zoom</span><input id="zoomR" type="range" min="1" max="2" step=".05" value="'+state.zoom+'"><b>'+state.zoom.toFixed(2)+'</b></div>'+
      '<div class="range"><span>Orizzontale</span><input id="panXR" type="range" min="-25" max="25" step="1" value="'+state.panX+'"><b>'+state.panX+'</b></div>'+
      '<div class="range"><span>Verticale</span><input id="panYR" type="range" min="-25" max="25" step="1" value="'+state.panY+'"><b>'+state.panY+'</b></div>'],
    look:['Game Look',
      '<div class="strip">'+
      ['Clean','Competitive','Neon Arena','Dark Raid','Boss Cinematic'].map(x=>'<button class="pill" data-key="look" data-value="'+x+'">'+x+'</button>').join('')+
      '</div>'+
      '<div class="range"><span>Intensità</span><input id="intensityR" type="range" min="0" max="100" step="1" value="'+state.intensity+'"><b>'+state.intensity+'</b></div>'+
      '<div class="range"><span>Luce</span><input id="brightR" type="range" min="70" max="130" step="1" value="'+state.brightness+'"><b>'+state.brightness+'</b></div>'+
      '<div class="range"><span>Contrasto</span><input id="contrastR" type="range" min="70" max="150" step="1" value="'+state.contrast+'"><b>'+state.contrast+'</b></div>'],
    hud:['HUD Awareness',
      '<div class="strip">'+
      ['Off','Auto Detect','Killfeed Safe','Minimap Safe','Facecam Safe'].map(x=>'<button class="pill" data-key="hudMode" data-value="'+x+'">'+x+'</button>').join('')+
      '</div><div class="cards"><div class="card"><b>KILLFEED</b>zona protetta</div><div class="card"><b>MINIMAP</b>sempre visibile</div><div class="card"><b>FACECAM</b>ancoraggio smart</div></div>'],
    caption:['Gaming Captions',
      '<div class="strip"><button class="pill" data-key="captionOn" data-value="true">Attivi</button><button class="pill" data-key="captionOn" data-value="false">Nessuno</button></div>'+
      '<div class="textRow"><input id="captionTextInput" value="'+String(state.captionText).replace(/"/g,'&quot;')+'"><button class="applyBtn" id="captionApply">APPLICA TESTO</button></div>'+
      '<div class="range"><span>Dimensione</span><input id="captionSizeR" type="range" min="18" max="70" step="1" value="'+state.captionSize+'"><b>'+state.captionSize+'</b></div>'+
      '<div class="range"><span>Posizione</span><input id="captionYR" type="range" min="15" max="88" step="1" value="'+state.captionY+'"><b>'+state.captionY+'</b></div>'+
      '<div class="colorGrid">'+
        '<div class="colorBox"><label>TESTO</label><div class="colorRow"><input id="textColorDraft" type="color" value="'+state.textColor+'"><button class="applyBtn" data-color="text">APPLICA</button></div></div>'+
        '<div class="colorBox"><label>PAROLA ATTIVA</label><div class="colorRow"><input id="activeColorDraft" type="color" value="'+state.activeColor+'"><button class="applyBtn" data-color="active">APPLICA</button></div></div>'+
        '<div class="colorBox"><label>BORDO</label><div class="colorRow"><input id="outlineColorDraft" type="color" value="'+state.outlineColor+'"><button class="applyBtn" data-color="outline">APPLICA</button></div></div>'+
      '</div>'],
    audio:['Game Audio',
      '<div class="strip">'+
      '<button class="pill audioPreset" data-value="mute">Muto</button>'+
      '<button class="pill audioPreset" data-value="original">Originale</button>'+
      '<button class="pill audioPreset" data-value="boost">Game Boost</button></div>'+
      '<div class="range"><span>Volume</span><input id="volumeR" type="range" min="0" max="100" step="1" value="'+state.volume+'"><b>'+state.volume+'</b></div>'+
      '<div class="strip" style="margin-top:9px">'+[.5,.75,1,1.25,1.5,2].map(x=>'<button class="pill speedPill" data-value="'+x+'">'+x+'×</button>').join('')+'</div>'],
    vision:['Game Vision AI',
      '<div class="cards"><div class="card"><b>ACTION FOCUS</b>segue la zona di gameplay più importante</div><div class="card"><b>HUD AWARENESS</b>protegge killfeed e minimap</div><div class="card"><b>REACTION SYNC</b>adatta look e caption al tipo di gioco</div></div>'+
      '<div class="strip" style="margin-top:8px">'+
      ['Auto Gaming','FPS','Racing','Sports','Battle Royale'].map(x=>'<button class="pill aiPreset" data-value="'+x+'">'+x+'</button>').join('')+
      '</div>']
   };
   const tpl=templates[name];
   title.textContent=tpl[0];
   body.innerHTML=tpl[1];
   drawer.classList.remove('hidden');
   root.querySelectorAll('.railBtn[data-panel]').forEach(x=>x.classList.toggle('active',x===btn));

   if(name==='look'){
     wirePills('look');choosePill(body,state.look);
     wireRange('intensityR','intensity',Number);
     wireRange('brightR','brightness',Number);
     wireRange('contrastR','contrast',Number);
   }
   if(name==='hud'){wirePills('hudMode');choosePill(body,state.hudMode)}
   if(name==='frame'){
     wireRange('zoomR','zoom',Number);
     wireRange('panXR','panX',Number);
     wireRange('panYR','panY',Number);
     body.querySelectorAll('.framePreset').forEach(p=>p.onclick=()=>{
       const v=p.dataset.value;
       if(v==='focus'){state.zoom=1.18;state.panX=0;state.panY=0}
       if(v==='cross'){state.zoom=1.32;state.panX=0;state.panY=-4}
       if(v==='face'){state.zoom=1.12;state.panX=-10;state.panY=8}
       if(v==='free'){state.zoom=1;state.panX=0;state.panY=0}
       applyState();commit();openPanel('frame',btn);flash(v.toUpperCase()+' ATTIVO');
     });
   }
   if(name==='caption'){
     body.querySelectorAll('.pill[data-key="captionOn"]').forEach(p=>{
       p.classList.toggle('sel',String(state.captionOn)===p.dataset.value);
       p.onclick=()=>{state.captionOn=p.dataset.value==='true';applyState();commit();openPanel('caption',btn);flash()};
     });
     body.querySelector('#captionApply').onclick=()=>{
       state.captionText=body.querySelector('#captionTextInput').value||'NO SCOPE CLUTCH!';
       applyState();commit();flash('TESTO APPLICATO');
     };
     wireRange('captionSizeR','captionSize',Number);
     wireRange('captionYR','captionY',Number);
     body.querySelectorAll('[data-color]').forEach(b=>b.onclick=()=>{
       const kind=b.dataset.color;
       if(kind==='text')state.textColor=body.querySelector('#textColorDraft').value;
       if(kind==='active')state.activeColor=body.querySelector('#activeColorDraft').value;
       if(kind==='outline')state.outlineColor=body.querySelector('#outlineColorDraft').value;
       applyState();commit();flash('COLORE APPLICATO');
     });
   }
   if(name==='audio'){
     body.querySelectorAll('.audioPreset').forEach(p=>p.onclick=()=>{
       const v=p.dataset.value;
       if(v==='mute'){state.muted=true}
       if(v==='original'){state.muted=false;state.volume=100}
       if(v==='boost'){state.muted=false;state.volume=100}
       applyState();commit();openPanel('audio',btn);video.play().catch(()=>{});flash();
     });
     wireRange('volumeR','volume',Number,v=>{state.muted=v===0});
     body.querySelectorAll('.speedPill').forEach(p=>{
       p.classList.toggle('sel',Number(p.dataset.value)===state.speed);
       p.onclick=()=>{state.speed=Number(p.dataset.value);applyState();commit();openPanel('audio',btn);flash('VELOCITÀ '+state.speed+'×')};
     });
   }
   if(name==='vision'){
     body.querySelectorAll('.aiPreset').forEach(p=>{
       p.classList.toggle('sel',p.dataset.value===state.aiMode);
       p.onclick=()=>{
         const mode=p.dataset.value;state.aiMode=mode;
         if(mode==='Auto Gaming'){state.look='Competitive';state.intensity=55;state.zoom=1.12;state.panX=0;state.panY=-2;state.hudMode='Auto Detect';state.captionSize=34}
         if(mode==='FPS'){state.look='Competitive';state.intensity=74;state.zoom=1.28;state.panX=0;state.panY=-4;state.hudMode='Killfeed Safe';state.captionSize=32}
         if(mode==='Racing'){state.look='Neon Arena';state.intensity=58;state.zoom=1.08;state.panX=0;state.panY=5;state.hudMode='Off';state.captionSize=30}
         if(mode==='Sports'){state.look='Clean';state.intensity=45;state.zoom=1.08;state.panX=0;state.panY=0;state.hudMode='Off';state.captionSize=30}
         if(mode==='Battle Royale'){state.look='Dark Raid';state.intensity=62;state.zoom=1.16;state.panX=2;state.panY=-2;state.hudMode='Minimap Safe';state.captionSize=34}
         applyState();commit();openPanel('vision',btn);flash(mode.toUpperCase()+' PRESET');
       };
     });
   }
 }
 function restore(snapshot){
   state=JSON.parse(snapshot);
   applyState();
   flash('STATO RIPRISTINATO');
   drawer.classList.add('hidden');
   root.querySelectorAll('.railBtn').forEach(x=>x.classList.remove('active'));
 }
 root.querySelectorAll('[data-panel]').forEach(btn=>btn.onclick=()=>openPanel(btn.dataset.panel,btn));
 root.querySelector('#drawerClose').onclick=()=>{drawer.classList.add('hidden');root.querySelectorAll('.railBtn').forEach(x=>x.classList.remove('active'))};
 root.querySelector('#closeBtn').onclick=root.querySelector('#drawerClose').onclick;
 root.querySelector('#backBtn').onclick=()=>flash('DEMO: RITORNO NON COLLEGATO');
 root.querySelector('#resetBtn').onclick=()=>{state={...defaults};commit();applyState();flash('RESET COMPLETO')};
 root.querySelector('#undoBtn').onclick=()=>{if(historyIndex>0){historyIndex--;restore(history[historyIndex])}else flash('NESSUN UNDO')};
 root.querySelector('#redoBtn').onclick=()=>{if(historyIndex<history.length-1){historyIndex++;restore(history[historyIndex])}else flash('NESSUN REDO')};
 root.querySelector('#doneBtn').onclick=()=>flash('PREVIEW SALVATA · DEMO');
 root.querySelector('#playBtn').onclick=()=>{
   if(video.paused){
     if(video.currentTime<state.inPoint||video.currentTime>=state.outPoint)video.currentTime=state.inPoint;
     video.play().catch(()=>{});
   }else video.pause();
 };
 video.addEventListener('play',()=>{playUse.setAttribute('href','#i-pause');playLabel.textContent='PAUSE'});
 video.addEventListener('pause',()=>{playUse.setAttribute('href','#i-play');playLabel.textContent='PLAY'});
 video.addEventListener('loadedmetadata',()=>{
   duration=Math.max(.5,Math.min(60,video.duration||15));
   state.outPoint=duration;
   defaults.outPoint=duration;
   history=[JSON.stringify(state)];historyIndex=0;
   applyState();
 });
 video.addEventListener('timeupdate',()=>{
   if(video.currentTime>state.outPoint+.04||video.currentTime<state.inPoint-.1){
     video.currentTime=state.inPoint;
   }
   playhead.style.left=Math.max(0,Math.min(100,(video.currentTime/duration)*100))+'%';
 });
 inRange.oninput=()=>{
   let v=Number(inRange.value);
   if(v>state.outPoint-.5)v=state.outPoint-.5;
   state.inPoint=Math.max(0,v);applyState();video.currentTime=state.inPoint;
 };
 inRange.onchange=()=>{commit();flash('IN AGGIORNATO')};
 outRange.oninput=()=>{
   let v=Number(outRange.value);
   if(v<state.inPoint+.5)v=state.inPoint+.5;
   state.outPoint=Math.min(duration,v);applyState();
 };
 outRange.onchange=()=>{commit();flash('OUT AGGIORNATO')};

 applyState();
})();
</script>
</div>
'''

def render_editor_2027_embed(video_path, height=760):
    p=Path(video_path)
    data=base64.b64encode(p.read_bytes()).decode("ascii") if p.is_file() else ""
    html=_TEMPLATE.replace("__VIDEO__",data)
    components.html(html,height=int(height),scrolling=False)
