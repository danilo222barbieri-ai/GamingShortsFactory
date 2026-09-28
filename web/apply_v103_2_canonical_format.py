from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V103_1_CLEAN_HOOK_PIXFMT.py')
out=Path('/app/GamingShortsFactory_V103_2_CANONICAL_FORMAT.py')
s=src.read_text(encoding='utf-8')

helper=r'''def _gsf_normalize_final_fmt(fmt):
    """Canonicalize editor/UI format labels before the final render pipeline."""
    raw=str(fmt or "").strip().lower()
    compact=raw.replace(" ","")
    if "9:16" in compact or "9x16" in compact:
        return "9:16 Short"
    if "16:9" in compact or "16x9" in compact:
        return "16:9"
    return str(fmt or "9:16 Short").strip() or "9:16 Short"


'''
tree=ast.parse(s)
core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
lines=s.splitlines(keepends=True)
s=''.join(lines[:core_node.lineno-1])+helper+''.join(lines[core_node.lineno-1:])

# Normalize fmt at the very start of the final renderer, before any format branch/filter.
tree=ast.parse(s)
core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
body=core_node.body
if not body:
    raise RuntimeError('V103.2 render core has no body')
first=body[0]
if isinstance(first,ast.Expr) and isinstance(getattr(first,'value',None),ast.Constant) and isinstance(first.value.value,str):
    insert_after=int(first.end_lineno)
    insert_text='    fmt=_gsf_normalize_final_fmt(fmt)\n'
    lines=s.splitlines(keepends=True)
    s=''.join(lines[:insert_after])+insert_text+''.join(lines[insert_after:])
else:
    insert_before=int(first.lineno)-1
    insert_text='    fmt=_gsf_normalize_final_fmt(fmt)\n'
    lines=s.splitlines(keepends=True)
    s=''.join(lines[:insert_before])+insert_text+''.join(lines[insert_before:])

# The standalone validator must use the same canonical interpretation.
old='''    expected=(1080,1920) if str(fmt)=="9:16 Short" else (1920,1080)
'''
new='''    fmt=_gsf_normalize_final_fmt(fmt)
    expected=(1080,1920) if fmt=="9:16 Short" else (1920,1080)
'''
if old not in s:
    raise RuntimeError('V103.2 validator expected-size anchor not found')
s=s.replace(old,new,1)

marker='Gaming Shorts Factory · V103.1 Clean Final'
if marker not in s:
    raise RuntimeError('V103.2 marker source not found')
s=s.replace(marker,'Gaming Shorts Factory · V103.2 Canonical Final Format',1)

out.write_text(s,encoding='utf-8')
print(f'V103.2 canonical-format patch applied: {out}')
