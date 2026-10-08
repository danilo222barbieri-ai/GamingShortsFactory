#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v326_mobile_editor_home_speed.py'
EDITOR=ROOT/'web'/'editor_2027_component'/'index.html'
SHELL=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V326 implementation missing')
spec=importlib.util.spec_from_file_location('v326',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

editor='''<!doctype html><html><head></head><body><div id="ng27" class="expanded"><div class="shell"><div class="topline"></div><div class="cockpit"><div class="rail"><button data-panel="frame"></button><button data-panel="cover"></button><button data-panel="look"></button><button data-panel="hud"></button><button data-panel="caption"></button><button data-panel="audio"></button></div><div class="stageWrap"><div id="stage" class="stage r916"><video id="video"></video><div class="captionPreview" id="captionPreview">CAPTION AUTO</div></div><div class="timeline v325DetachedTimeline"><div class="tlMeta"><span>IN</span><span>TAGLIO</span><span>OUT</span></div><div class="track"></div><div class="trimRow"></div></div></div><div id="v323EditorActions" class="v323EditorActions"><button id="v323CreateShort">CREA SHORT</button><button id="v323SaveDraft">SALVA LA TUA BOZZA</button></div><div class="rail"><button id="playBtn"></button><button id="undoBtn"></button><button id="redoBtn"></button><button data-panel="vision"></button><button id="doneBtn"></button></div></div></div></div></body></html>'''
pe=mod.patch_editor_text(editor)
checks={
 'exact style':'id="v326MobileEditorExact"',
 'runtime':'id="v326MobileEditorRuntime"',
 'parent viewport class':"root.classList.toggle('v326Mobile'",
 'persisted expanded state cleared':"root.classList.remove('expanded')",
 'approved left tools':"const wantedLeft=['frame','caption','look']",
 'approved right tools':"const wantedRight=['audio','vision']",
 'cover mobile suppression':'data-panel="cover"',
 'hud mobile suppression':'data-panel="hud"',
 'player variable':'--v326-player-w',
 'actions row':'grid-row:2!important',
 'timeline row':'grid-row:3!important',
 'fullscreen bridge':'GSF_EDITOR_FULLSCREEN_V326',
}
for name,marker in checks.items():
 if marker not in pe: fail(name+' missing')
 ok(name)
if mod.patch_editor_text(pe)!=pe: fail('V326 editor patch is not idempotent')
ok('editor patch idempotent')

shell='''<iframe src="/share-v156/?v=281" data-src="/share-v156/" data-loaded="1" title="Condividi o scarica"></iframe>\n<iframe src="/creator-hub-v156/?v=284" data-src="/creator-hub-v156/" data-loaded="1" title="Creator Hub"></iframe>\n<iframe class="gsf-editor-frame" src="/editor-live/?v=281" data-src="/editor-live/" data-loaded="1" title="Game Editor"></iframe>\n<iframe src="/ai-v221/?v=281" data-src="/ai-v221/" data-loaded="1" title="Motori IA"></iframe>\n<iframe src="/account/?v=226" data-src="/account/" data-loaded="1" title="Account"></iframe>\n<script>const P=window.parent;const KEY='gsf_ai_overlay_open_v221';const frame=document.querySelector('iframe');const location=window.location;try{if(sessionStorage.getItem(KEY)==='1')setTimeout(()=>open(false),90)}catch(e){};const sendRender=()=>{};</script>\n<style id="gsf-v220-editor-shell"></style><div class="gsf-editor-head"><div>Game Editor<small>Il tuo gameplay resta nel progetto mentre modifichi.</small></div></div>'''
ps=mod.patch_shell_text(shell)
for name,marker in {
 'fresh Home boot guard':'V326_BOOT_HOME_RESET',
 'AI stale-state reset':'gsf_ai_overlay_open_v221',
 'one boot per parent':"P.__GSF_BOOT_HOME_RESET_V326",
 'AI lazy iframe':'src="about:blank" data-src="/ai-v221/" data-loaded="0"',
 'Editor lazy iframe':'src="about:blank" data-src="/editor-live/" data-loaded="0"',
 'Hub lazy iframe':'src="about:blank" data-src="/creator-hub-v156/" data-loaded="0"',
 'Social lazy iframe':'src="about:blank" data-src="/share-v156/" data-loaded="0"',
 'Account lazy iframe':'src="about:blank" data-src="/account/" data-loaded="0"',
 'mobile header fullscreen':'class="v326HeaderFull"',
 'header fullscreen wire':'V326_HEADER_FULL_WIRE',
}.items():
 if marker not in ps: fail(name+' missing')
 ok(name)
if "sessionStorage.getItem(KEY)==='1')setTimeout(()=>open(false),90)" in ps.split('V326_BOOT_HOME_RESET',1)[0]:
 fail('legacy overlay reopen remains before Home boot guard')
if mod.patch_shell_text(ps)!=ps: fail('V326 shell patch is not idempotent')
ok('shell patch idempotent')

if EDITOR.is_file() and 'id="v326MobileEditorExact"' in EDITOR.read_text(encoding='utf-8'):
 live=EDITOR.read_text(encoding='utf-8')
 for marker in ('v326MobileEditorRuntime',"wantedLeft=['frame','caption','look']","wantedRight=['audio','vision']"):
  if marker not in live: fail('runtime editor missing '+marker)
 ok('runtime editor carries exact mobile layout')

if SHELL.is_file() and 'V326_BOOT_HOME_RESET' in SHELL.read_text(encoding='utf-8'):
 live=SHELL.read_text(encoding='utf-8')
 compile(live,str(SHELL),'exec')
 for marker in ('P.__GSF_BOOT_HOME_RESET_V326','src="about:blank"','class="v326HeaderFull"'):
  if marker not in live: fail('runtime shell missing '+marker)
 for marker in ('data-target="home"','data-active="hub"','data-active="projects"','data-active="live"'):
  if marker not in live: fail('canonical navigation marker lost: '+marker)
 ok('runtime shell compiles and canonical navigation survives')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 v325='python /app/web/test_v325_mobile_editor_viewport_fit.py /app'
 patch='python /app/web/fix_v326_mobile_editor_home_speed.py /app'
 test='python /app/web/test_v326_mobile_editor_home_speed.py /app'
 render='python /app/web/apply_v293_render_memory_guard.py'
 if patch not in start or test not in start: fail('V326 startup registration missing')
 if v325 in start and start.index(patch)<start.index(v325): fail('V326 must run after V325 validation')
 if start.index(test)<start.index(patch): fail('V326 test must run after V326 patch')
 if render in start and start.index(test)>start.index(render): fail('V326 must validate before render-memory generation')
 ok('startup order')

print('\nV326 MOBILE EDITOR + HOME BOOT + LAZY SURFACES CONTRACT: PASS')
