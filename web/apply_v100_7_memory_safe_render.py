from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V100_6_FPS_GUARD.py')
out=Path('/app/GamingShortsFactory_V100_7_MEMORY_SAFE_RENDER.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
segment=ast.get_source_segment(s,node) or ''

old='''                    "-preset","medium",
                    "-crf","14",
                    "-threads","2",
                    "-profile:v","high",
'''
new='''                    "-preset","medium",
                    "-crf","14",
                    "-threads","1",
                    "-x264-params","rc-lookahead=16:ref=2:bframes=2",
                    "-profile:v","high",
'''
if old not in segment:
    raise RuntimeError('V100.7 x264 block not found')
new_segment=segment.replace(old,new,1)
new_segment=new_segment.replace(
    'timeout=max(300.0,min(3600.0,duration*24.0))',
    'timeout=max(420.0,min(3600.0,duration*36.0))',
    1
)

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+new_segment.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V100.6 FPS Guard'
if marker not in s:
    raise RuntimeError('V100.7 marker source not found')
s=s.replace(marker,'Gaming Shorts Factory · V100.7 Memory Safe Render',1)

out.write_text(s,encoding='utf-8')
print(f'V100.7 memory-safe render patch applied: {out}')
