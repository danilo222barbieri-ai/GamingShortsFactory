from pathlib import Path
import ast
import math
import sys

sys.path.insert(0,"/app/web")
from editor_2027_embed import editor_2027_clip_bounds, editor_2027_render_kwargs, _editor_video_url

frontend=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
wrapper=Path("/app/web/editor_2027_embed.py").read_text(encoding="utf-8")
app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V107_PRODUCTION_UI.py")
app=app_path.read_text(encoding="utf-8")

for marker in (
    'name="viewport"',
    "viewport-fit=cover",
    "playsinline",
    "streamlit:componentReady",
    "streamlit:render",
    "streamlit:setComponentValue",
    "sendStateToPython(payload)",
    "MODIFICHE APPLICATE",
):
    if marker not in frontend:
        raise SystemExit(f"FAIL Editor 2027 component protocol missing: {marker}")


for marker in (
    "GSF_EDITOR_FULLSCREEN_V2",
    "gsfFullscreenFallback",
    "enterEditorFullscreen",
    "exitEditorFullscreen",
    "root.classList.add('expanded')",
    "span.textContent='FULL'",
    "span.textContent='FULL ×2'",
    "span.textContent='RIDUCI'",
    "syncPlayToggle",
    "playing?'#i-pause':'#i-play'",
    "captionMode",
    "Smart Safe",
    "Usa la trascrizione reale",
):
    if marker not in frontend:
        raise SystemExit(f"FAIL Editor 2027 simplified/fullscreen control missing: {marker}")

if "#ng27 .zoomEditorBtn{display:none!important}" in frontend:
    raise SystemExit("FAIL mobile Editor zoom/fullscreen control is still hidden")
if 'id="pauseBtn"' in frontend or "pauseBtn" in frontend:
    raise SystemExit("FAIL Editor 2027 still exposes a separate Pause control")
if "APPLICA TESTO" in frontend or "data-color=" in frontend:
    raise SystemExit("FAIL Caption still contains redundant Apply controls")
if "GAME EVENT MAP" in frontend or "AIM LOCK · 00:03" in frontend:
    raise SystemExit("FAIL Editor still shows fake static event-map data")
if "#ng27 .shade,#ng27 .scanlines{display:none!important}" not in frontend:
    raise SystemExit("FAIL decorative preview effects still alter the rendered look")


# Component startup syntax guardrails added after V108 regression.
if "if(!isMobileEditor function syncPlayToggle" in frontend:
    raise SystemExit("FAIL Editor 2027 contains corrupted Play/Pause JavaScript")
if frontend.count("function syncPlayToggle(){") != 1:
    raise SystemExit("FAIL Editor 2027 Play/Pause toggle function count is not exactly one")
if frontend.count("video.addEventListener('loadedmetadata',()=>{") != 1:
    raise SystemExit("FAIL Editor 2027 loadedmetadata listener is missing or duplicated")
if "sendMessage(COMPONENT_READY,{apiVersion:1});" not in frontend:
    raise SystemExit("FAIL Editor 2027 cannot complete Streamlit component handshake")
if frontend.index("sendMessage(COMPONENT_READY,{apiVersion:1});") > frontend.index("function syncPlayToggle(){"):
    raise SystemExit("FAIL Streamlit component handshake moved after optional editor controls")


# Startup regression guards are intentionally targeted. JavaScript regex
# literals make a hand-written generic delimiter parser unreliable here.

for marker in (
    'gsf_editor_2027_v1084',
    'gsf-editor-unsaved-v1084:',
    'persistLocalState',
    'touch-action:manipulation',
    '#ng27 video{pointer-events:none!important}',
    "payload.editorVersion='2027.4'",
):
    source = wrapper if marker=='gsf_editor_2027_v1084' else frontend
    if marker not in source:
        raise SystemExit("FAIL Editor 2027 mobile/desktop interaction hardening missing: "+marker)


# Desktop control contract: three-state fullscreen, one Play/Pause, live
# contextual panels, Undo/Redo and DONE must coexist with mobile hardening.
for marker in (
    'data-editor-build="2027.4-touch"',
    "span.textContent='FULL'",
    "span.textContent='FULL ×2'",
    "span.textContent='RIDUCI'",
    "root.classList.add('expanded')",
    "root.classList.remove('expanded')",
    "playing?'#i-pause':'#i-play'",
    "root.querySelector('#undoBtn').onclick",
    "root.querySelector('#redoBtn').onclick",
    "root.querySelector('#doneBtn').onclick",
    "openPanel(btn.dataset.panel,btn)",
    "applyState(); commit(); flash()",
):
    if marker not in frontend:
        raise SystemExit("FAIL Editor desktop interaction contract missing: "+marker)
if frontend.count('id="playBtn"') != 1:
    raise SystemExit("FAIL desktop Editor does not have exactly one Play/Pause button")
if 'id="pauseBtn"' in frontend:
    raise SystemExit("FAIL desktop Editor still exposes a separate Pause button")

if "components.html(" in wrapper:
    raise SystemExit("FAIL Editor 2027 still uses display-only components.html")
if "declare_component(" not in wrapper:
    raise SystemExit("FAIL Editor 2027 V1 component is not declared")
if "_editor_component_for" not in wrapper or '_EDITOR_2027_COMPONENT = components.declare_component' not in wrapper:
    raise SystemExit("FAIL Editor 2027 does not use one stable static component")
if 'f"gsf_editor_2027_{digest}"' in wrapper or "editor2027_components" in wrapper:
    raise SystemExit("FAIL Editor 2027 still declares dynamic per-video component assets")
if 'return "/editor-media/current?v=" + quote(fingerprint, safe="")' not in wrapper:
    raise SystemExit("FAIL Editor 2027 web source is not registered through current-media resolver")
if "/editor-media/current?ts=" not in frontend:
    raise SystemExit("FAIL Editor 2027 iframe cannot self-load current media")
if "base64.b64encode(p.read_bytes())" not in wrapper:
    raise SystemExit("FAIL Editor 2027 local fallback is missing")
if "editor2027_manual_" not in app or "crea_anteprima(_gsf_manual_path,_gsf_manual_proxy" not in app:
    raise SystemExit("FAIL Scegli scena does not create a browser-safe H.264 editor proxy")
if "_gsf_manual_editor_media" not in app:
    raise SystemExit("FAIL Scegli scena does not feed the browser-safe proxy to Editor 2027")
if "\\n" in frontend:
    raise SystemExit("FAIL Editor 2027 frontend contains visible literal newline markers")
if 'st.button("PERSONALIZZA IL TUO GAMEPLAY"' not in app or "gsf-major-personalize" not in app:
    raise SystemExit("FAIL PERSONALIZZA does not use the same native CTA button structure")
if "Anteprima sorgente caricata nascosta per UX" not in app:
    raise SystemExit("FAIL uploaded-source preview is not hidden in production")
if "render_kwargs=_gsf_manual_render_kwargs" not in app:
    raise SystemExit("FAIL Editor 2027 state is not attached to final render recipe")
if "editor_2027_state=dict(_gsf_manual_editor_state)" not in app:
    raise SystemExit("FAIL Editor 2027 state snapshot is not retained in recipe")
if '"inline_editor"' not in app or "float(start)+float(_gsf_inline_rel_start)" not in app:
    raise SystemExit("FAIL inline Editor 2027 IN/OUT is not mapped onto original AI source")
if "render_kwargs=_gsf_inline_kwargs" not in app:
    raise SystemExit("FAIL inline Editor 2027 settings are not attached to final AI render")

sample={
    "zoom":1.4,"panX":25,"panY":-25,
    "brightness":120,"contrast":130,
    "speed":1.25,"volume":80,"muted":False,
    "audioMode":"Game Boost",
    "look":"Competitive","intensity":75,
    "captionOn":True,"captionMode":"Auto","captionText":"CLUTCH",
    "captionSize":36,"captionY":70,
    "textColor":"#ffffff","activeColor":"#ffd400","outlineColor":"#000000",
    "inPoint":2.0,"outPoint":12.0,
    "visionEnabled":True,
}
start,duration=editor_2027_clip_bounds(sample,15)
if not (math.isclose(start,2.0) and math.isclose(duration,10.0)):
    raise SystemExit("FAIL Editor 2027 IN/OUT mapping")
kw=editor_2027_render_kwargs(sample,{})
checks={
    "zoom":1.4,
    "x_pos":100.0,
    "y_pos":-100.0,
    "brightness":0.2,
    "contrast":1.3,
    "speed":1.25,
    "volume":80,
    "filter_preset":"Gaming / Vibrante",
    "filter_intensity":75,
    "smart_reframe":True,
}
for key,expected in checks.items():
    actual=kw.get(key)
    if isinstance(expected,float):
        if not math.isclose(float(actual),expected,rel_tol=1e-6,abs_tol=1e-6):
            raise SystemExit(f"FAIL Editor 2027 mapping {key}: {actual} != {expected}")
    elif actual!=expected:
        raise SystemExit(f"FAIL Editor 2027 mapping {key}: {actual} != {expected}")

# Caption/HUD contract: every visible simplified control must affect the render.
fixed=editor_2027_render_kwargs({
    "captionMode":"Fixed","captionOn":True,"captionText":"TESTO MANUALE",
    "hudMode":"Off","visionEnabled":False,
},{ "editor_sub_live_words":[{"text":"AUTO","start":0.0,"end":0.2}] })
if fixed.get("subtitle_words") is not None:
    raise SystemExit("FAIL Fixed Caption still uses automatic transcript words")
if fixed.get("subtitle_text")!="TESTO MANUALE" or not fixed.get("subtitles_enabled"):
    raise SystemExit("FAIL Fixed Caption does not reach final render text")

auto_no_voice=editor_2027_render_kwargs({
    "captionMode":"Auto","captionOn":True,"captionText":"NO SCOPE CLUTCH!",
    "hudMode":"Off","visionEnabled":False,
},{})
if auto_no_voice.get("subtitle_text"):
    raise SystemExit("FAIL Auto Caption can still burn placeholder/demo text")

off_caption=editor_2027_render_kwargs({
    "captionMode":"Off","captionOn":False,
    "hudMode":"Off","visionEnabled":False,
},{})
if off_caption.get("subtitles_enabled") or off_caption.get("subtitle_text") or off_caption.get("subtitle_words"):
    raise SystemExit("FAIL Caption Off still emits subtitles")

hud_safe=editor_2027_render_kwargs({
    "captionMode":"Off","hudMode":"Smart Safe","visionEnabled":False,
},{})
if not hud_safe.get("smart_reframe"):
    raise SystemExit("FAIL HUD Smart Safe does not enable the real smart reframe engine")

cinema=editor_2027_render_kwargs({
    "captionMode":"Off","look":"Boss Cinematic","visionEnabled":False,
},{})
if cinema.get("filter_preset")!="Cinematico":
    raise SystemExit("FAIL Cinema Look does not map to the final render preset")

tree=ast.parse(app)
core=None
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name=="_gsf_render_core":
        core=node
        break
if core is None:
    raise SystemExit("FAIL final render core not found")
allowed={a.arg for a in core.args.args}
unsupported=set(kw)-allowed
if unsupported:
    raise SystemExit("FAIL Editor 2027 emits unsupported render args: "+",".join(sorted(unsupported)))

print("Editor 2027 bidirectional render contract: PASS")
