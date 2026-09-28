from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V100_5_MAX_UPLOAD.py')
out=Path('/app/GamingShortsFactory_V100_6_FPS_GUARD.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
segment=ast.get_source_segment(s,node) or ''

old='''                    "-pix_fmt","yuv420p",
                    "-c:a","aac","-b:a","192k",
'''
new='''                    "-pix_fmt","yuv420p",
                    "-fpsmax","60",
                    "-c:a","aac","-b:a","192k",
'''
if old not in segment:
    raise RuntimeError('V100.6 render output block not found')
new_segment=segment.replace(old,new,1)

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+new_segment.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V100.5 MAX Upload'
if marker not in s:
    raise RuntimeError('V100.6 marker source not found')
s=s.replace(marker,'Gaming Shorts Factory · V100.6 FPS Guard',1)

out.write_text(s,encoding='utf-8')
print(f'V100.6 FPS Guard patch applied: {out}')
