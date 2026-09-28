from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V100_2_MASTER_QUALITY.py')
out=Path('/app/GamingShortsFactory_V100_3_NATIVE_CROP_HQ.py')
s=src.read_text(encoding='utf-8')

def replace_function(source,name,new_source):
    tree=ast.parse(source)
    node=next(
        (n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),
        None
    )
    if node is None:
        raise RuntimeError(f'V100.3 function not found: {name}')
    lines=source.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1]) + new_source.rstrip() + '\n\n' + ''.join(lines[node.end_lineno:])

new_filter=r'''def _gsf_smart_reframe_filter(track,zoom=1.0,y_pos=0):
    """
    V100.3 native-crop HQ Smart Reframe.

    Crop the original landscape frame FIRST, at source resolution, then upscale
    only the selected 9:16 window to 1080x1920. This avoids scaling the whole
    16:9 frame before cropping, reducing work and preventing an unnecessary
    full-frame resample during camera motion.
    """
    zoom=max(1.0,float(zoom))
    y_pos=float(y_pos)
    cx=_gsf_smart_reframe_cx_expression(track)

    # Source-space crop:
    #   crop_h = source height / zoom
    #   crop_w = crop_h * 9/16
    # force even dimensions for H.264/yuv420 compatibility.
    crop_h=f"max(2,trunc((ih/{zoom})/2)*2)"
    crop_w=f"max(2,trunc(((ih/{zoom})*9/16)/2)*2)"

    return (
        "setpts=PTS-STARTPTS,"
        f"crop=w='{crop_w}':h='{crop_h}':"
        f"x='max(0,min(iw-ow,({cx})*iw-ow/2))':"
        f"y='max(0,min(ih-oh,(ih-oh)/2+({y_pos}/100)*(ih-oh)/2))',"
        "scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,"
        "unsharp=5:5:0.08:3:3:0.02"
    )
'''

s=replace_function(s,'_gsf_smart_reframe_filter',new_filter)

marker='Gaming Shorts Factory · V100.2 Master Quality'
if marker not in s:
    raise RuntimeError('V100.3 source marker not found')
s=s.replace(marker,'Gaming Shorts Factory · V100.3 Native Crop HQ',1)

out.write_text(s,encoding='utf-8')
print(f'V100.3 Native Crop HQ patch applied: {out}')
