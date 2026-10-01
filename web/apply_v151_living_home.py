from pathlib import Path

src=Path("/app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py")
out=Path("/app/GamingShortsFactory_V151_LIVING_HOME.py")
s=src.read_text(encoding="utf-8")

anchor='with st.container(key="v73-upload-shell"):\n'
if anchor not in s:
    raise RuntimeError("V151 uploader anchor missing")

home=r'''
# V151 visual shell only: the V150.2 engine/state contracts stay untouched.
st.markdown(r"""
<style id="gsf-v151-living-home">
:root{--gsf-ink:#102d63;--gsf-blue:#5fa8ff;--gsf-glass:rgba(255,255,255,.68)}
[data-testid="stAppViewContainer"]{
 background:
 radial-gradient(circle at 15% 8%,rgba(125,190,255,.22),transparent 26%),
 radial-gradient(circle at 86% 18%,rgba(143,255,224,.16),transparent 24%),
 radial-gradient(circle at 54% 72%,rgba(183,156,255,.12),transparent 28%),
 linear-gradient(145deg,#fbfdff 0%,#f4f9ff 52%,#fbfdff 100%) !important;
}
.gsf-v151-brand{font-size:clamp(20px,2.2vw,30px);font-weight:650;letter-spacing:.18em;color:#345b91;margin:4px 0 24px}
.gsf-v151-whisper{font-size:clamp(18px,2vw,28px);font-style:italic;color:#6685b1;text-align:center;margin:0 auto 8px;opacity:.92}
.st-key-v73-upload-shell{min-height:360px!important;padding:28px 0 34px!important}
.gsf-v89-upload-visual{
 width:300px!important;height:300px!important;min-width:300px!important;min-height:300px!important;
 max-width:300px!important;max-height:300px!important;
 background:linear-gradient(145deg,rgba(255,255,255,.82),rgba(221,238,255,.70))!important;
 border:1px solid rgba(117,199,255,.72)!important;
 box-shadow:0 18px 55px rgba(67,140,214,.18),0 0 0 18px rgba(125,219,255,.08),0 0 0 36px rgba(130,246,225,.055)!important;
 animation:gsf151Breath 3.4s ease-in-out infinite!important;
 backdrop-filter:blur(18px);
}
.gsf-v89-upload-visual:not(.is-loaded)::before,
.gsf-v89-upload-visual:not(.is-loaded)::after{
 content:"";position:absolute;inset:-18px;border-radius:50%;pointer-events:none;
 border:2px solid rgba(90,207,255,.36);
 animation:gsf151Orbit 5.8s linear infinite;
}
.gsf-v89-upload-visual:not(.is-loaded)::after{inset:-34px;border-color:rgba(128,245,220,.24);animation-duration:8.2s;animation-direction:reverse}
.gsf-v89-upload-icon{font-size:64px!important;color:#4f93ef!important;text-shadow:0 0 20px rgba(75,160,255,.24)}
.gsf-v89-upload-label{width:210px!important;max-width:210px!important;font-size:20px!important;color:var(--gsf-ink)!important;text-transform:uppercase;letter-spacing:.015em}
.gsf-v89-upload-label::after{content:"\\A Al resto penso io";white-space:pre;display:block;margin-top:9px;font-size:15px;font-weight:500;font-style:italic;text-transform:none;color:#6f8db8}
@keyframes gsf151Breath{0%,100%{transform:scale(1);filter:brightness(1)}50%{transform:scale(1.018);filter:brightness(1.045)}}
@keyframes gsf151Orbit{0%{transform:rotate(0);box-shadow:0 -5px 16px rgba(85,211,255,.28)}50%{box-shadow:0 5px 20px rgba(150,126,255,.18)}100%{transform:rotate(360deg);box-shadow:0 -5px 16px rgba(85,211,255,.28)}}
.gsf-v151-bar{
 position:fixed;z-index:999990;left:50%;bottom:18px;transform:translateX(-50%);
 width:min(760px,calc(100vw - 28px));padding:10px 12px;border:1px solid rgba(255,255,255,.82);
 border-radius:34px;background:rgba(248,252,255,.78);backdrop-filter:blur(24px) saturate(145%);
 box-shadow:0 18px 45px rgba(45,91,145,.16);display:grid;grid-template-columns:repeat(5,1fr);gap:4px;
}
.gsf-v151-nav{border:0;background:transparent;border-radius:24px;padding:10px 4px;color:#6780a5;font:inherit;font-weight:650;cursor:pointer;transition:.18s ease}
.gsf-v151-nav:hover{background:rgba(213,235,255,.58);transform:translateY(-1px);color:#286fca}
.gsf-v151-nav.active{background:linear-gradient(145deg,rgba(191,229,255,.72),rgba(224,239,255,.76));color:#166ed4;box-shadow:0 7px 20px rgba(64,145,226,.13)}
.gsf-v151-nav span{display:block;font-size:20px;line-height:1.05;margin-bottom:4px}
[data-testid="stAppViewContainer"] .main .block-container{padding-bottom:116px!important}
@media(max-width:600px){
 .gsf-v151-brand{text-align:center;font-size:18px;letter-spacing:.13em;margin-bottom:14px}
 .gsf-v151-whisper{font-size:17px}
 .st-key-v73-upload-shell{min-height:305px!important;padding-top:20px!important}
 .gsf-v89-upload-visual{width:248px!important;height:248px!important;min-width:248px!important;min-height:248px!important;max-width:248px!important;max-height:248px!important}
 .gsf-v89-upload-icon{font-size:56px!important}.gsf-v89-upload-label{font-size:17px!important}
 .gsf-v151-bar{bottom:9px;border-radius:28px;padding:7px 6px}.gsf-v151-nav{font-size:11px;padding:8px 2px}.gsf-v151-nav span{font-size:18px}
}
/* V151.1 approved Home replaces legacy hero. */
.gsf-hero{display:none!important}
@media(max-width:600px){.gsf-hero{display:none!important}.gsf-v151-brand{text-align:left!important;margin:18px 8px 12px!important;font-size:17px!important;letter-spacing:.14em!important}.gsf-v151-whisper{text-align:left!important;margin:0 8px 4px!important;font-size:16px!important}.st-key-v73-upload-shell{margin-top:0!important;min-height:292px!important;padding:24px 0!important}.gsf-v89-upload-visual{width:226px!important;height:226px!important;min-width:226px!important;min-height:226px!important;max-width:226px!important;max-height:226px!important}.gsf-v89-upload-label{font-size:16px!important;width:180px!important;max-width:180px!important}.gsf-v89-upload-label::after{font-size:13px!important}.gsf-v151-bar{width:calc(100vw - 18px)!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;padding:6px 4px!important}.gsf-v151-nav{min-width:0!important;width:100%!important;font-size:10px!important;overflow:hidden!important;white-space:nowrap!important}}
@media(prefers-reduced-motion:reduce){.gsf-v89-upload-visual,.gsf-v89-upload-visual::before,.gsf-v89-upload-visual::after{animation:none!important}}
</style>
<div class="gsf-v151-brand">Gaming Shorts Factory</div>
<div class="gsf-v151-whisper">Trasforma il tuo gameplay in Shorts</div>
""",unsafe_allow_html=True)
'''
s=s.replace(anchor,home+anchor,1)

# Make the new uploader language match the approved Home without touching upload mechanics.
s=s.replace('_label = "Video caricato" if loaded else "Carica il tuo video"',
            '_label = "Video caricato" if loaded else "Carica il tuo gameplay"',1)

# Persistent Game Bar. It delegates to the existing controls/pages: no duplicate business logic.
bar=r'''
st.markdown(r"""
<div class="gsf-v151-bar" id="gsf-v151-bar">
 <button class="gsf-v151-nav active" data-gsf-target="home"><span>⌂</span>Home</button>
 <button class="gsf-v151-nav" data-gsf-target="ai"><span>✦</span>AI</button>
 <button class="gsf-v151-nav" data-gsf-target="editor"><span>🎮</span>Editor</button>
 <button class="gsf-v151-nav" data-gsf-target="hub"><span>▣</span>Hub</button>
 <button class="gsf-v151-nav" data-gsf-target="social"><span>⌯</span>Social</button>
</div>
<script>
(()=>{
 const root=window.parent.document;
 const norm=s=>(s||"").replace(/\\s+/g," ").trim().toLowerCase();
 const find=(words)=>[...root.querySelectorAll("button,a")].find(el=>words.some(w=>norm(el.innerText).includes(w)));
 const targets={
  ai:["crea con ia","crea con ai"],
  editor:["apri game editor","game editor"],
  hub:["creator hub"],
  social:["social","condividi o scarica"]
 };
 document.querySelectorAll(".gsf-v151-nav").forEach(btn=>btn.addEventListener("click",()=>{
   const key=btn.dataset.gsfTarget;
   if(key==="home"){root.scrollingElement.scrollTo({top:0,behavior:"smooth"});return;}
   const el=find(targets[key]||[]);
   if(el){el.click();}
 }));
})();
</script>
""",unsafe_allow_html=True)
'''
s += "\n"+bar+"\n"

s=s.replace("Gaming Shorts Factory · V148 Analytics Learning","Gaming Shorts Factory · V151 Living Home")
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V151 Living Home applied:",out)
