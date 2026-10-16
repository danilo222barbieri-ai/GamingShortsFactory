"""The actual entry bootstrap must resolve canonical helpers on every rerun."""
from pathlib import Path
import subprocess
import sys
import unittest


def _check_entry_imports_survive_legacy_web_path_and_module_reload():
    root=Path(__file__).resolve().parents[1]
    program=r'''
import importlib.util,sys
from pathlib import Path
root=Path(sys.argv[1]);web=root/'web'
sys.path[:0]=[str(web),str(root)]
prefix=(root/'app.py').read_text().split('from web.render_gate_v293 import',1)[0]
for _ in range(4):
    # Streamlit may remove user modules while legacy helpers left /app/web on
    # the shared interpreter path; this must never select web/web instead.
    for name in list(sys.modules):
        if name=='web' or name.startswith('web.'):del sys.modules[name]
    exec(compile(prefix,str(root/'app.py'),'exec'),{'__file__':str(root/'app.py')})
    for name,expected in [('web.living_ui',web/'living_ui.py'),
                          ('web.render_gate_v293',web/'render_gate_v293.py'),
                          ('zoomout_v109',web/'zoomout_v109.py'),
                          ('game_brain_v112',web/'game_brain_v112.py')]:
        spec=importlib.util.find_spec(name)
        assert spec and Path(spec.origin).resolve()==expected.resolve(),(name,spec)
print('canonical imports survive four reruns')
'''
    result=subprocess.run([sys.executable,'-c',program,str(root)],capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stdout+result.stderr


class RuntimeImportStability(unittest.TestCase):
    def test_entry_imports_survive_legacy_web_path_and_module_reload(self):
        _check_entry_imports_survive_legacy_web_path_and_module_reload()
