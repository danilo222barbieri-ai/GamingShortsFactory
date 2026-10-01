from pathlib import Path

src=Path("/app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py")
out=Path("/app/GamingShortsFactory_V151_LIVING_HOME.py")
s=src.read_text(encoding="utf-8")

# V151.4: structurally remove only the legacy four-step hero markup.
import ast as _ast
_tree=_ast.parse(s)
_lines=s.splitlines(keepends=True)
_targets=[]
for _node in _ast.walk(_tree):
    if not isinstance(_node,_ast.Call):
        continue
    _fn=_node.func
    if not (isinstance(_fn,_ast.Attribute) and _fn.attr=="markdown"):
        continue
    _seg=_ast.get_source_segment(s,_node) or ""
    if ("Crea il tuo Short in quattro passaggi semplici" in _seg or
        ("CARICA" in _seg and "SCEGLI" in _seg and "MODIFICA" in _seg and "PUBBLICA" in _seg)):
        _targets.append(_node)
if not _targets:
    raise RuntimeError("V151.4 legacy four-step hero source call not found")
for _node in sorted(_targets,key=lambda n:n.lineno,reverse=True):
    _start=_node.lineno-1
    _end=getattr(_node,"end_lineno",_node.lineno)
    _indent=_lines[_start][:_node.col_offset]
    _lines[_start:_end]=[_indent+'st.markdown("", unsafe_allow_html=True)\n']
s="".join(_lines)
print("V151.4 legacy hero removed:",len(_targets))

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
.gsf-home-hero,.hero-wrap,.home-steps,.gsf-steps,.gsf-roadmap,[class*="roadmap"]{display:none!important}\n
/* V151.5 mobile Home composition */
.gsf-account-fab{display:none!important;opacity:0!important;visibility:hidden!important;pointer-events:none!important}
.gsf-v151-homecards{max-width:820px;margin:6px auto 26px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.gsf-v151-card{border:1px solid rgba(183,211,232,.8);border-radius:22px;padding:18px 14px;background:linear-gradient(145deg,rgba(255,255,255,.9),rgba(235,245,253,.8));box-shadow:0 10px 26px rgba(61,104,142,.09);text-align:center;color:#315f86}
.gsf-v151-card b{display:block;font-size:15px;margin:5px 0}.gsf-v151-card small{font-size:11px;color:#7890a5}
.gsf-v151-card .ico{font-size:25px}
.gsf-v151-recent{max-width:820px;margin:0 auto 20px;font-size:16px;font-weight:800;letter-spacing:.05em;color:#426987}
@media(max-width:600px){
 [data-testid="stAppViewContainer"] .main .block-container{padding-top:.25rem!important}
 .gsf-v151-brand{margin:6px 8px 7px!important}
 .gsf-v151-whisper{margin:0 8px 0!important}
 .st-key-v73-upload-shell{min-height:260px!important;padding:13px 0 17px!important}
 .gsf-v151-homecards{grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin:0 4px 18px}
 .gsf-v151-card{border-radius:17px;padding:12px 4px;min-width:0}
 .gsf-v151-card b{font-size:11px}.gsf-v151-card small{font-size:9px}.gsf-v151-card .ico{font-size:21px}
 .gsf-v151-recent{margin:0 8px 14px;font-size:14px}
 /* legacy ad previews stay out of the new Home's first screen */
 [class*="st-key"][class*="ad"],[class*="ads-preview"]{margin-top:18px!important}
}
\n@media(prefers-reduced-motion:reduce){.gsf-v89-upload-visual,.gsf-v89-upload-visual::before,.gsf-v89-upload-visual::after{animation:none!important}}
</style>
<div class="gsf-v151-brand">Gaming Shorts Factory</div>
<div class="gsf-v151-whisper">Trasforma il tuo gameplay in Shorts</div>
""",unsafe_allow_html=True)
'''
s=s.replace(anchor,home+anchor,1)\n
# Insert the new Home action cards immediately after the uploader block's visual
# status and before the legacy workflow continues. They are presentation only.
_cards=r'''
st.markdown(r"""
<div class="gsf-v151-homecards">
 <div class="gsf-v151-card"><span class="ico">✦</span><b>Crea con IA</b><small>Trova i momenti migliori</small></div>
 <div class="gsf-v151-card"><span class="ico">🎮</span><b>Game Editor</b><small>Modifica il gameplay</small></div>
 <div class="gsf-v151-card"><span class="ico">↗</span><b>Crea Short</b><small>Prepara il risultato finale</small></div>
</div>
<div class="gsf-v151-recent">Ultimi progetti</div>
""",unsafe_allow_html=True)
'''
# Place after upload shell closes by using the next stable ad marker if present.
_ad_candidates=['# AD SLOT', 'Pubblicità', 'PUBBLICITÀ']
_pos=-1
for _cand in _ad_candidates:
    _p=s.find(_cand,s.find(anchor)+len(anchor))
    if _p!=-1:
        _pos=_p; break
if _pos!=-1:
    s=s[:_pos]+_cards+s[_pos:]
else:
    # Safe fallback: immediately before the first motor-selection heading.
    _m=s.find('Scegli il tuo motore IA')
    if _m!=-1:
        _ls=s.rfind('\n',0,_m)
        s=s[:_ls+1]+_cards+s[_ls+1:]


# V151.3: retire only the old Creator Hub floating FAB; keep its panel/logic for Game Bar.\ns = s.replace("p+'.gsf-account-fab{z-index:2147483500!important;opacity:1!important;visibility:visible!important;filter:none!important;mix-blend-mode:normal!important}'+", "p+'.gsf-account-fab{display:none!important;opacity:0!important;visibility:hidden!important;pointer-events:none!important}'+")\ns = s.replace("fab.style.opacity='1';\n      fab.style.visibility='visible';\n      fab.style.filter='none';", "fab.style.display='none';\n      fab.style.opacity='0';\n      fab.style.visibility='hidden';\n      fab.style.pointerEvents='none';")\n\n# Make the new uploader language match the approved Home without touching upload mechanics.
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
