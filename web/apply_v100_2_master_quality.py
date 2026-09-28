from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V100_1_QUALITY_MOBILE.py')
out=Path('/app/GamingShortsFactory_V100_2_MASTER_QUALITY.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(
    n for n in tree.body
    if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core'
)
segment=ast.get_source_segment(s,node) or ''
old='''        attempts=[
            (
                "Intel QSV",
                base+[
                    "-c:v","h264_qsv",
                    "-preset","veryfast",
                    "-global_quality","18",
                    "-c:a","aac","-b:a","160k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            ),
            (
                "libx264",
                base+[
                    "-c:v","libx264",
                    "-preset","veryfast",
                    "-crf","18",
                    "-c:a","aac","-b:a","160k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            )
        ]
'''
new='''        # V100.2 MASTER QUALITY:
        # software x264 first. On moving 9:16 gameplay, the previous QSV/
        # veryfast path traded too much fine detail for speed.
        attempts=[
            (
                "libx264 Master",
                base+[
                    "-c:v","libx264",
                    "-preset","slow",
                    "-crf","13",
                    "-profile:v","high",
                    "-level:v","4.2",
                    "-pix_fmt","yuv420p",
                    "-c:a","aac","-b:a","192k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            ),
            (
                "Intel QSV HQ fallback",
                base+[
                    "-c:v","h264_qsv",
                    "-preset","slow",
                    "-global_quality","14",
                    "-pix_fmt","nv12",
                    "-c:a","aac","-b:a","192k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            )
        ]
'''
if old not in segment:
    raise RuntimeError('V100.2 encoder attempts block not found')
new_segment=segment.replace(old,new,1)

# Replace only the render-core function.
lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+new_segment.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

# The stronger V100.1 sharpening can emphasize source compression during pans.
# Keep only a very light restoration pass now that the encode is near-master.
old_sharp='unsharp=5:5:0.22:3:3:0.08'
new_sharp='unsharp=5:5:0.10:3:3:0.03'
if old_sharp not in s:
    raise RuntimeError('V100.2 sharpen target not found')
s=s.replace(old_sharp,new_sharp,1)

marker='Gaming Shorts Factory · V100.1 Quality + Mobile Preview'
if marker not in s:
    raise RuntimeError('V100.2 source marker not found')
s=s.replace(marker,'Gaming Shorts Factory · V100.2 Master Quality',1)

out.write_text(s,encoding='utf-8')
print(f'V100.2 Master Quality patch applied: {out}')
