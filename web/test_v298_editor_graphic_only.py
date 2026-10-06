#!/usr/bin/env python3
from fix_v298_editor_graphic_only import patch_editor_text, patch_embed_text

fixture = '''<!doctype html><html><head><style>/* V297 DESK REBUILD — EDITOR */</style></head><body>
<div id="ng27" data-v297-layout="editor"><div class="shell">
<div class="gsfGuide">Tocca direttamente il video per personalizzarlo<span class="arr">↝</span></div>
<div class="v297EditorGrid"><aside class="v297EditorSidebar"><button class="railBtn" data-panel="frame"><span>FRAME</span></button></aside><section class="v297EditorCenter"><div class="stageWrap"><div class="stage r916" id="stage"><video id="video"></video></div></div></section><aside class="v297EditorMoments"><h3>Momenti IA</h3><p>Momenti</p><button class="v297MomentCard"></button><button class="v297MomentCard"></button><button class="v297MomentCard"></button></aside></div>
<div class="v297EditorTimeline"><div class="timeline"></div></div>
</div></div><script id="v297EditorRuntime"></script></body></html>'''

out = patch_editor_text(fixture)
assert 'V298 EDITOR GRAPHIC ONLY' in out
assert 'data-v298-layout="graphic-only"' in out
assert '@media (min-width:1024px)' in out
assert 'v298EditorAdLeft' in out and 'v298EditorAdRight' in out
assert 'v298EditorMuralLeft' in out and 'v298EditorMuralRight' in out
assert 'v298EditorToolbar' in out
assert 'v298EditorTimeline' in out
assert 'v298EditorMoments' in out
assert '.v297EditorSidebar{display:none!important}' in out
assert out.count('id="video"') == 1, 'the working video player must not be replaced or duplicated'
assert patch_editor_text(out) == out, 'editor patch must be idempotent'

embed = 'components.declare_component("gsf_editor_2027_v297", path="x")'
patched_embed = patch_embed_text(embed)
assert 'gsf_editor_2027_v298' in patched_embed
assert patch_embed_text(patched_embed) == patched_embed

print('V298 editor graphic-only contract: PASS')
