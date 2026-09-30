#!/usr/bin/env python3
import ast, sys
from pathlib import Path

path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V107_1_STABILITY.py")
source=path.read_text(encoding="utf-8")
tree=ast.parse(source)
rows=[]
for node in tree.body:
    if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
        continue
    name=node.name
    low=name.lower()
    if any(k in low for k in ("ai_","scan","moment","candidate","rank","scene","clip","best","event","signal")):
        args=[a.arg for a in node.args.args]
        rows.append((node.lineno,node.end_lineno,name,args))
print("V108_AI_FUNCTIONS_BEGIN")
for row in rows:
    print(f"{row[2]} lines={row[0]}-{row[1]} args={','.join(row[3])}")
print("V108_AI_FUNCTIONS_END")

interesting=[
    "_gsf_ai_scan_base",
    "_gsf_ai_window_features",
    "_gsf_score_ai_window",
    "_gsf_moment_category",
    "_gsf_ai_pick_diverse",
    "_gsf_ai_rank_v3",
    "_gsf_detect_signal_event",
    "_gsf_merge_semantic_and_signal_event",
    "_gsf_smart_event_start",
]
lines=source.splitlines()
for name in interesting:
    node=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if not node:
        continue
    print(f"V108_SOURCE_BEGIN {name}")
    chunk="\n".join(lines[node.lineno-1:min(node.end_lineno,node.lineno+220)])
    print(chunk)
    print(f"V108_SOURCE_END {name}")

# Tail of the main ranker: output/diagnostics contract.
rank=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="_gsf_ai_rank_v3"),None)
if rank:
    print("V108_RANK_TAIL_BEGIN")
    start=max(rank.lineno-1,rank.end_lineno-105)
    print("\n".join(lines[start:rank.end_lineno]))
    print("V108_RANK_TAIL_END")
