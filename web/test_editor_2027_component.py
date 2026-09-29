from pathlib import Path
import ast
import math
import sys

sys.path.insert(0,"/app/web")
from editor_2027_embed import editor_2027_clip_bounds, editor_2027_render_kwargs

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

if "components.html(" in wrapper:
    raise SystemExit("FAIL Editor 2027 still uses display-only components.html")
if "declare_component(" not in wrapper:
    raise SystemExit("FAIL Editor 2027 V1 component is not declared")
if "_editor_component_for" not in wrapper or 'src="{safe_url}"' not in wrapper:
    raise SystemExit("FAIL Editor 2027 does not bake the real video URL into the iframe HTML")
if "PLAYER HTML5 ADATTIVO DEFINITIVO" not in app:
    raise SystemExit("FAIL approved unified HTML5 source player missing from production app")
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
    "captionOn":True,"captionText":"CLUTCH",
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
