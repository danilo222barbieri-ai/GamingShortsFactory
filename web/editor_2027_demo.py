import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gaming Shorts Factory · Editor 2027", page_icon="🎬", layout="wide")
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],.stApp{background:#07090f!important;}
.block-container{max-width:1280px!important;padding:8px 14px 18px!important;}
header,[data-testid="stHeader"],footer{display:none!important;}
</style>
""", unsafe_allow_html=True)

video_path=Path("/app/demo_assets/demo_final.mp4")
video_b64=base64.b64encode(video_path.read_bytes()).decode("ascii") if video_path.exists() else ""

html=f"""
<div id="ed27" class="ed27">
  <style>
    #ed27{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#f7f8fb;}}
    #ed27 *{{box-sizing:border-box}}
    #ed27 .shell{{display:grid;grid-template-columns:minmax(0,1fr) 92px;gap:14px;align-items:start;max-width:980px;margin:0 auto;}}
    #ed27 .stageWrap{{min-width:0}}
    #ed27 .stage{{position:relative;margin:0 auto;width:min(100%,520px);aspect-ratio:9/16;background:#10141d;border-radius:28px;overflow:hidden;border:1px solid rgba(255,255,255,.08);box-shadow:0 22px 60px rgba(0,0,0,.35);}}
    #ed27 video{{width:100%;height:100%;object-fit:cover;background:#111;display:block}}
    #ed27 .shade{{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.34),transparent 18%,transparent 70%,rgba(0,0,0,.52));}}
    #ed27 .topbar{{position:absolute;top:12px;left:12px;right:12px;display:flex;align-items:center;justify-content:space-between;gap:8px;z-index:5}}
    #ed27 .cluster{{display:flex;align-items:center;gap:7px}}
    #ed27 .chip,#ed27 .iconBtn{{border:1px solid rgba(255,255,255,.14);background:rgba(12,15,22,.66);backdrop-filter:blur(14px);color:#fff;box-shadow:none;}}
    #ed27 .iconBtn{{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;font-size:17px;cursor:pointer}}
    #ed27 .chip{{height:42px;border-radius:14px;padding:0 13px;font-weight:700;cursor:pointer}}
    #ed27 .mode{{position:absolute;right:12px;top:72px;z-index:6;display:flex;flex-direction:column;gap:9px}}
    #ed27 .tool{{width:54px;height:54px;border:1px solid rgba(255,255,255,.13);background:rgba(9,12,18,.70);backdrop-filter:blur(16px);border-radius:18px;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;cursor:pointer;transition:.18s}}
    #ed27 .tool b{{font-size:20px;line-height:1}}
    #ed27 .tool span{{font-size:9px;font-weight:700;opacity:.84}}
    #ed27 .tool.active{{background:rgba(255,255,255,.94);color:#090b10;transform:scale(1.03)}}
    #ed27 .drawer{{position:absolute;left:12px;right:78px;bottom:14px;z-index:7;background:rgba(9,12,18,.76);backdrop-filter:blur(18px);border:1px solid rgba(255,255,255,.13);border-radius:20px;padding:12px;min-height:112px;transition:.2s}}
    #ed27 .drawer.hidden{{opacity:0;transform:translateY(12px);pointer-events:none}}
    #ed27 .drawerHead{{display:flex;align-items:center;justify-content:space-between;margin-bottom:9px}}
    #ed27 .drawerHead strong{{font-size:14px}}
    #ed27 .drawerHead small{{opacity:.55}}
    #ed27 .closeDraw{{background:transparent;border:0;color:#fff;font-size:18px;cursor:pointer}}
    #ed27 .strip{{display:flex;gap:8px;overflow-x:auto;padding-bottom:3px;scrollbar-width:none}}
    #ed27 .strip::-webkit-scrollbar{{display:none}}
    #ed27 .pill{{flex:0 0 auto;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.07);color:#fff;border-radius:13px;padding:9px 12px;font-size:12px;font-weight:700;cursor:pointer}}
    #ed27 .pill.sel{{background:#fff;color:#080a0e}}
    #ed27 .rangeRow{{display:grid;grid-template-columns:72px 1fr 42px;align-items:center;gap:8px;margin-top:10px}}
    #ed27 input[type=range]{{width:100%}}
    #ed27 .timeline{{width:min(100%,720px);margin:12px auto 0;background:#0e121a;border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:12px 14px}}
    #ed27 .tlTop{{display:flex;justify-content:space-between;gap:12px;font-size:12px;color:#aab2c2;margin-bottom:8px}}
    #ed27 .track{{height:42px;border-radius:12px;background:linear-gradient(90deg,#1c2634 0 8%,#24374e 8% 18%,#1d2a3b 18% 42%,#334c68 42% 59%,#223145 59% 74%,#192331 74% 100%);position:relative;overflow:hidden}}
    #ed27 .window{{position:absolute;left:18%;right:18%;top:0;bottom:0;border:2px solid #fff;border-radius:10px;box-shadow:0 0 0 999px rgba(0,0,0,.16)}}
    #ed27 .playhead{{position:absolute;left:47%;top:-3px;bottom:-3px;width:2px;background:#fff}}
    #ed27 .railTitle{{text-align:center;margin:10px 0 8px;color:#c9d0dc;font-size:13px;font-weight:700}}
    #ed27 .rail{{display:flex;flex-direction:column;gap:10px;align-items:center;padding-top:8px}}
    #ed27 .rail button{{width:64px;min-height:60px;border:1px solid rgba(255,255,255,.10);background:#111620;color:#eef2f7;border-radius:19px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-size:20px;cursor:pointer}}
    #ed27 .rail button span{{font-size:9px;font-weight:800;opacity:.72}}
    #ed27 .rail .primary{{background:#f7f8fa;color:#0b0d11}}
    #ed27 .hint{{max-width:980px;margin:10px auto 0;text-align:center;color:#7f8999;font-size:12px}}
    @media(max-width:760px){{
      #ed27 .shell{{grid-template-columns:1fr;}}
      #ed27 .railTitle{{display:none}}
      #ed27 .rail{{position:relative;flex-direction:row;justify-content:center;overflow-x:auto;padding:0 0 6px}}
      #ed27 .rail button{{width:54px;min-height:52px;border-radius:16px}}
      #ed27 .stage{{width:min(100%,430px);border-radius:22px}}
      #ed27 .mode{{right:8px;top:64px}}
      #ed27 .tool{{width:48px;height:48px;border-radius:16px}}
      #ed27 .drawer{{right:64px;left:8px;bottom:8px}}
    }}
  </style>

  <div class="shell">
    <div class="stageWrap">
      <div class="stage">
        <video id="vid" playsinline muted loop autoplay src="data:video/mp4;base64,{video_b64}"></video>
        <div class="shade"></div>

        <div class="topbar">
          <div class="cluster">
            <button class="iconBtn" title="Indietro">‹</button>
            <button class="chip" id="fmtTop">9:16</button>
          </div>
          <div class="cluster">
            <button class="iconBtn" title="Reset">↶</button>
            <button class="iconBtn" title="Chiudi">✕</button>
          </div>
        </div>

        <div class="mode">
          <button class="tool" data-panel="format"><b>▣</b><span>FORMATO</span></button>
          <button class="tool" data-panel="filter"><b>◐</b><span>FILTRI</span></button>
          <button class="tool" data-panel="image"><b>☼</b><span>IMMAGINE</span></button>
          <button class="tool" data-panel="subs"><b>Aa</b><span>TESTO</span></button>
          <button class="tool" data-panel="audio"><b>♪</b><span>AUDIO</span></button>
        </div>

        <div class="drawer hidden" id="drawer">
          <div class="drawerHead"><strong id="drawerTitle">Filtri</strong><small>Editor 2027</small><button class="closeDraw" id="closeDraw">×</button></div>
          <div id="drawerBody"></div>
        </div>
      </div>

      <div class="timeline">
        <div class="tlTop"><span>IN 00:08.0</span><span>15.0 s</span><span>OUT 00:23.0</span></div>
        <div class="track"><div class="window"></div><div class="playhead"></div></div>
      </div>
    </div>

    <aside>
      <div class="railTitle">Azioni rapide</div>
      <div class="rail">
        <button class="primary" id="playBtn">▶<span>PLAY</span></button>
        <button>↶<span>UNDO</span></button>
        <button>↷<span>REDO</span></button>
        <button>✦<span>AI</span></button>
        <button>✓<span>FATTO</span></button>
      </div>
    </aside>
  </div>
  <div class="hint">Prototipo grafico · nessun render o impostazione reale viene modificata</div>

  <script>
  (()=>{{
    const root=document.getElementById('ed27');
    const drawer=root.querySelector('#drawer');
    const title=root.querySelector('#drawerTitle');
    const body=root.querySelector('#drawerBody');
    const video=root.querySelector('#vid');
    const play=root.querySelector('#playBtn');
    const tools=[...root.querySelectorAll('.tool')];
    const panels={{
      format: ['Formato','<div class="strip"><button class="pill sel">9:16 Short</button><button class="pill">16:9 Originale</button><button class="pill">1:1</button></div>'],
      filter: ['Filtri','<div class="strip"><button class="pill sel">Originale</button><button class="pill">Vibrante</button><button class="pill">Cinema</button><button class="pill">Caldo</button><button class="pill">Freddo</button><button class="pill">B/N</button></div><div class="rangeRow"><span>Intensità</span><input type="range" min="0" max="100" value="70"><b>70</b></div>'],
      image: ['Immagine','<div class="strip"><button class="pill">Zoom</button><button class="pill">Posizione</button><button class="pill">Luce</button><button class="pill">Contrasto</button><button class="pill">Velocità</button></div><div class="rangeRow"><span>Valore</span><input type="range" min="0" max="100" value="50"><b>50</b></div>'],
      subs: ['Sottotitoli','<div class="strip"><button class="pill sel">Automatici</button><button class="pill">Manuali</button><button class="pill">Nessuno</button></div><div class="strip" style="margin-top:9px"><button class="pill">Font</button><button class="pill">Dimensione</button><button class="pill">Posizione</button><button class="pill">Colori</button></div>'],
      audio: ['Audio','<div class="strip"><button class="pill sel">Originale</button><button class="pill">Muto</button><button class="pill">Voce+</button></div><div class="rangeRow"><span>Volume</span><input type="range" min="0" max="200" value="100"><b>100</b></div>']
    }};
    function openPanel(name,btn){{
      title.textContent=panels[name][0]; body.innerHTML=panels[name][1]; drawer.classList.remove('hidden');
      tools.forEach(x=>x.classList.toggle('active',x===btn));
      body.querySelectorAll('.pill').forEach(p=>p.addEventListener('click',()=>{{
        const strip=p.parentElement; strip.querySelectorAll('.pill').forEach(x=>x.classList.remove('sel')); p.classList.add('sel');
        if(name==='format') root.querySelector('#fmtTop').textContent=p.textContent.includes('16:9')?'16:9':'9:16';
      }}));
      body.querySelectorAll('input[type=range]').forEach(r=>r.addEventListener('input',()=>{{ const b=r.parentElement.querySelector('b'); if(b)b.textContent=r.value; }}));
    }}
    tools.forEach(btn=>btn.addEventListener('click',()=>openPanel(btn.dataset.panel,btn)));
    root.querySelector('#closeDraw').addEventListener('click',()=>{{drawer.classList.add('hidden');tools.forEach(x=>x.classList.remove('active'));}});
    play.addEventListener('click',()=>{{ if(video.paused){{video.play();play.firstChild.textContent='❚❚';}}else{{video.pause();play.firstChild.textContent='▶';}} }});
  }})();
  </script>
</div>
"""

components.html(html, height=980, scrolling=False)
