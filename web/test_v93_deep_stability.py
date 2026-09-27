from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)
funcs={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('"v70_duration_" not in _GSF_TRANSIENT_WIDGET_PREFIXES' in s,'duration button prefix excluded from persistent restore')
need('stFileChipIconSpinner' in s,'real Streamlit upload spinner drives compact upload status')
need('nuova_durata=float(duration)' in s,'AI Director keeps requested 15s/30s duration')
need('_gsf_v93_release_analysis_memory' in funcs,'pre-render memory release helper exists')
need('gsf_ai_voice_cache_v40' in s,'analysis voice cache released')
need('_gsf_ai_whisper_tiny' in s and '_cached.clear()' in s,'Whisper Tiny cache can be released before render')
need('_gsf_v93_release_analysis_memory()\n                    _final_result=_gsf_render_final_recipe(' in s,'memory release runs immediately before final render')
need('numero_clip=3' in s,'three-clip contract preserved')
need('key="upload_v73"' in s,'stable uploader key preserved')
need('gsf-v89-upload-visual' in s,'approved uploader circle preserved')
need('Gaming Shorts Factory · V93 Deep Stability' in s,'V93 version marker')
print('V93 deep stability regression: PASS')
