from pathlib import Path
import ast

p=Path('/app/GamingShortsFactory_V98_FINAL_6LANES.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)
targets={
    '_gsf_ai_scan_profile_for_duration',
    '_gsf_ai_scan_base',
    '_gsf_ai_scan_cached',
    '_gsf_ai_rank_v3',
    '_gsf_ai_refine_motion_window',
    '_gsf_score_ai_window',
}
lines=s.splitlines()

for node in ast.walk(tree):
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in targets:
        start=max(1,node.lineno)
        end=getattr(node,'end_lineno',node.lineno)
        print(f'V99DIAG BEGIN {node.name} {start}-{end}')
        for n in range(start,end+1):
            print(f'V99SRC {n}: {lines[n-1]}')
        print(f'V99DIAG END {node.name}')

for needle in (
    '_gsf_ai_rank_v3(',
    '_gsf_ai_scan_cached(',
    'numero_clip=3',
    'profile=',
    'modalita',
):
    print(f'V99CALLS {needle}')
    for i,line in enumerate(lines,1):
        if needle in line:
            a=max(1,i-6); b=min(len(lines),i+12)
            for n in range(a,b+1):
                print(f'V99CALL {n}: {lines[n-1]}')
            print('V99CALL END')
