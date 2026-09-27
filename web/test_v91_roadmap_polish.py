from pathlib import Path
import ast,sys,re

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)
funcs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

# Upload: V90 circle stays independent; V91 only adds a small activity strip.
need('_gsf_v89_upload_visual_html' in funcs,'custom upload visual survives')
need('gsf-v91-upload-status' in s,'small upload status exists')
need('Caricamento video…' in s,'upload status label exists')
need('gsfV91UploadMove' in s,'upload activity animation exists')
need(':has([role="progressbar"]) .gsf-v91-upload-status' in s,'status is tied to real upload state')
need('gsf-v89-upload-visual{_loaded_class}' in s,'persistent upload circle interpolation preserved')

# Editor roadmap guards.
for marker in (
    'Inizio / fine',
    'editor_zoom',
    'editor_x',
    'editor_y',
    'editor_volume',
    'editor_brightness',
    'editor_contrast',
    'editor_speed',
    'render_gsf_editor_live_player',
    '"zoom":editor_zoom',
    '"x_pos":editor_x',
    '"y_pos":editor_y',
    '"brightness":editor_brightness',
    '"contrast":editor_contrast',
    '"speed":editor_speed',
    '"volume":editor_volume',
):
    need(marker in s,f'editor/render mapping: {marker}')

# AI roadmap guards: four distinct profiles, exactly three proposed clips.
for marker in (
    'if profile=="action"',
    'elif profile=="reaction"',
    'elif profile=="director"',
    'def _gsf_short_worthiness',
    'def _gsf_score_ai_window',
    'numero_clip=3',
    'st.columns(3, gap="large")',
):
    need(marker in s,f'AI guard: {marker}')

# Final production path remains connected.
for marker in (
    'def _gsf_render_final_recipe',
    'def _gsf_smart_reframe_filter',
    'def _gsf_render_core',
    'subtitle_mode',
    'normalize_audio',
    'polish_audio',
):
    need(marker in s,f'final render guard: {marker}')

# Do not reintroduce the known uploader failures.
for bad in (
    'gsf-v89-upload-visual{{_loaded_class}}',
    '{{_icon}}',
    '{{_label}}',
):
    need(bad not in s,f'no broken uploader token: {bad}')

print('V91 roadmap regression: PASS')
