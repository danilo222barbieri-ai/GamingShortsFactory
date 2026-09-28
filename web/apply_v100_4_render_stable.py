from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V100_3_NATIVE_CROP_HQ.py')
out=Path('/app/GamingShortsFactory_V100_4_RENDER_STABLE.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
segment=ast.get_source_segment(s,node) or ''

old='''        # V100.2 MASTER QUALITY:
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
new='''        # V100.4 STABLE MASTER:
        # Railway has no Intel QSV device, so final render is software-only.
        # Medium/CRF14 keeps near-master quality while avoiding the slow/1-thread
        # timeout path seen on 60fps iPhone gameplay.
        attempts=[
            (
                "libx264 HQ",
                base+[
                    "-c:v","libx264",
                    "-preset","medium",
                    "-crf","14",
                    "-threads","2",
                    "-profile:v","high",
                    "-level:v","4.2",
                    "-pix_fmt","yuv420p",
                    "-c:a","aac","-b:a","192k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            )
        ]
'''
if old not in segment:
    raise RuntimeError('V100.4 render attempts block not found')
new_segment=segment.replace(old,new,1)

# Give the software render enough wall clock on 60fps material without
# changing normal success-path speed.
new_segment=new_segment.replace(
    'timeout=max(180.0,min(3600.0,duration*15.0))',
    'timeout=max(300.0,min(3600.0,duration*24.0))',
    1
)

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+new_segment.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V100.3 Native Crop HQ'
if marker not in s:
    raise RuntimeError('V100.4 marker source not found')
s=s.replace(marker,'Gaming Shorts Factory · V100.4 Render Stable',1)

out.write_text(s,encoding='utf-8')
print(f'V100.4 stable render patch applied: {out}')
