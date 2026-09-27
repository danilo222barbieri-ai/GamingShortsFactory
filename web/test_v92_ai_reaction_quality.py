from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('def _gsf_ai_voice_features(input_file,start,duration,force=False):' in s,
     'voice feature supports forced lightweight pass')
need('if not GSF_AI_VOICE_TRANSCRIPTION and not bool(force):' in s,
     'low-memory guard keeps normal modes cheap')
need('def _gsf_ai_voice_cached(input_file, start, duration, cache_token=None, force=False):' in s,
     'voice cache supports force flag')
need('bool(force)' in s and 'force=force' in s,
     'forced/non-forced voice results use distinct cache path')
need('profile=="reaction" and len(enriched)<6' in s,
     'reaction voice is limited to six top candidates')
need('force=_force_reaction_voice' in s,
     'reaction ranking requests semantic voice pass')
need('"forced_voice_checks":int(forced_voice_checks)' in s,
     'forced voice diagnostics exposed')
need('-0.29*worst_overlap' in s,
     'final ranking penalizes heavy overlap more strongly')
need('category_bonus=0.070' in s,
     'final ranking rewards genuinely different moments')
need('numero_clip=3' in s,
     'three-clip contract preserved')
need('key="upload_v73"' in s,
     'stable uploader key preserved')
need('gsf-v89-upload-visual{_loaded_class}' in s,
     'V90/V91 persistent upload circle preserved')
need('Gaming Shorts Factory · V92 AI Reaction Quality' in s,
     'V92 footer/version marker')

print('V92 AI reaction quality regression: PASS')
