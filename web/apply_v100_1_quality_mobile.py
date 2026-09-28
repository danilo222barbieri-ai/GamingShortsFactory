from pathlib import Path
import ast
import re

src=Path('/app/GamingShortsFactory_V100_SMART_REFRAME.py')
out=Path('/app/GamingShortsFactory_V100_1_QUALITY_MOBILE.py')
s=src.read_text(encoding='utf-8')

def replace_function(source,name,new_source):
    tree=ast.parse(source)
    node=next(
        (n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),
        None
    )
    if node is None:
        raise RuntimeError(f'V100.1 function not found: {name}')
    lines=source.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1]) + new_source.rstrip() + '\n\n' + ''.join(lines[node.end_lineno:])

new_filter=r'''def _gsf_smart_reframe_filter(track,zoom=1.0,y_pos=0):
    """
    V100.1 HQ landscape -> 1080x1920 Smart Reframe.
    Lanczos scaling preserves HUD/text detail; a deliberately light unsharp
    pass restores perceived crispness after the unavoidable 16:9 -> 9:16
    enlargement without creating visible halos.
    """
    zoom=max(1.0,float(zoom))
    y_pos=float(y_pos)
    cx=_gsf_smart_reframe_cx_expression(track)

    return (
        "setpts=PTS-STARTPTS,"
        "scale=-2:1920:flags=lanczos+accurate_rnd+full_chroma_int,"
        f"scale=iw*{zoom}:ih*{zoom}:flags=lanczos+accurate_rnd+full_chroma_int,"
        "crop=1080:1920:"
        f"x='max(0,min(iw-ow,({cx})*iw-ow/2))':"
        f"y='max(0,min(ih-oh,(ih-oh)/2+({y_pos}/100)*(ih-oh)/2))',"
        "unsharp=5:5:0.22:3:3:0.08"
    )
'''

s=replace_function(s,'_gsf_smart_reframe_filter',new_filter)

# Higher final encode quality. V94 intentionally introduced one production
# x264 and one QSV quality value; change those exact values only.
if '"-crf","21"' not in s:
    raise RuntimeError('V100.1 x264 CRF21 target not found')
s=s.replace('"-crf","21"','"-crf","18"',1)

if '"-global_quality","21"' not in s:
    raise RuntimeError('V100.1 QSV quality21 target not found')
s=s.replace('"-global_quality","21"','"-global_quality","18"',1)

# Mobile-only breathing room between the user-facing "Anteprima" label and
# the following main render_gsf_player call. Discover it from AST so no editor
# or result player gets moved accidentally.
tree=ast.parse(s)
lines=s.splitlines(keepends=True)

def call_name(node):
    if isinstance(node,ast.Attribute):
        return node.attr
    if isinstance(node,ast.Name):
        return node.id
    return ''

labels=[]
players=[]
for node in ast.walk(tree):
    if isinstance(node,ast.Call):
        name=call_name(node.func)
        if name=='render_gsf_player':
            players.append(node)
        if name in ('markdown','subheader','header','caption','write'):
            vals=[
                x.value for x in ast.walk(node)
                if isinstance(x,ast.Constant) and isinstance(x.value,str)
            ]
            text=' '.join(vals)
            low=text.lower()
            if 'anteprima' in low and 'live' not in low:
                labels.append(node)

pairs=[]
for label in labels:
    after=[
        p for p in players
        if p.lineno>label.end_lineno and p.lineno-label.end_lineno<=45
    ]
    if after:
        p=min(after,key=lambda x:x.lineno)
        pairs.append((label,p))

# Remove duplicate same label/player pairs from AST walk.
unique={}
for label,player in pairs:
    unique[(label.lineno,player.lineno)]=(label,player)
pairs=list(unique.values())

if len(pairs)!=1:
    contexts=[]
    for label in labels:
        contexts.append(
            f'label {label.lineno}: '+
            ''.join(lines[max(0,label.lineno-2):min(len(lines),label.end_lineno+3)]).strip()
        )
    raise RuntimeError(
        'V100.1 expected exactly one Anteprima -> main player pair, '
        f'found {len(pairs)}; labels={contexts}'
    )

label,player=pairs[0]
insert_at=player.lineno-1
indent=re.match(r'\s*',lines[insert_at]).group(0)
spacer=(
    indent+'st.markdown("""<style>\\n'
    '.gsf-mobile-preview-gap{display:none;height:0}\\n'
    '@media (max-width:768px){.gsf-mobile-preview-gap{display:block;height:12px;line-height:12px}}\\n'
    '</style><div class="gsf-mobile-preview-gap" aria-hidden="true"></div>""", '
    'unsafe_allow_html=True)\\n'
)
lines.insert(insert_at,spacer)
s=''.join(lines)

if 'Gaming Shorts Factory · V100 Smart Reframe' not in s:
    raise RuntimeError('V100.1 source marker not found')
s=s.replace(
    'Gaming Shorts Factory · V100 Smart Reframe',
    'Gaming Shorts Factory · V100.1 Quality + Mobile Preview'
)

out.write_text(s,encoding='utf-8')
print(
    f'V100.1 patch applied: {out} | mobile preview label line={label.lineno} '
    f'player line={player.lineno}'
)
