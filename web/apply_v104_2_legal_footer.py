from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_1_RENDER_DIAGNOSTICS.py')
out=Path('/app/GamingShortsFactory_V104_2_LEGAL_FOOTER.py')
s=src.read_text(encoding='utf-8')

# Add the two public legal links to the existing bottom footer only.
needle='Beta web/mobile · Sessione persistente'
if needle not in s:
    raise RuntimeError('V104.2 footer marker missing')

# Locate the COMPLETE Python statement that renders the existing footer.
# The previous implementation inserted after the physical line containing
# the text, which can sit inside a multi-line st.markdown(...) call and
# therefore break indentation/syntax. AST gives us the real statement end.
tree=ast.parse(s)
footer_node=None
for node in ast.walk(tree):
    if isinstance(node, ast.Expr):
        segment=ast.get_source_segment(s,node) or ''
        if needle in segment:
            footer_node=node
            break
if footer_node is None or not getattr(footer_node,'end_lineno',None):
    raise RuntimeError('V104.2 footer statement not found')

lines=s.splitlines(keepends=True)
insert_at=sum(len(x) for x in lines[:footer_node.end_lineno])
indent=' ' * int(getattr(footer_node,'col_offset',0) or 0)
legal_line=(
    indent
    + 'st.markdown("""<div style="text-align:center;margin-top:8px;font-size:.88rem;color:#60788d">'
      '<a href="/privacy" target="_blank" style="color:#60788d;text-decoration:none">Privacy</a>'
      '<span style="padding:0 10px">·</span>'
      '<a href="/terms" target="_blank" style="color:#60788d;text-decoration:none">Termini</a>'
      '</div>""", unsafe_allow_html=True)\n'
)
s=s[:insert_at]+legal_line+s[insert_at:]

out.write_text(s,encoding='utf-8')

# Fail the build here if the generated application is not valid Python.
compile(s,str(out),'exec')
print(f'V104.2 legal footer applied and compiled: {out}')
