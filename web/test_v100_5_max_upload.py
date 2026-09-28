from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V100.5 MAX Upload' in s,'V100.5 marker')
need('Math.min(10,requestedConcurrency)' in s,'desktop bucket upload capped at 10 lanes')
need('Math.min(6,requestedConcurrency)' in s,'mobile bucket upload capped at 6 lanes')
need('speedMBs.toFixed(1)' in s,'live MB/s display installed')
need("partSize=Number(init.part_size||caps.part_size||32*1024*1024)" in s,'32MB bucket parts preserved')
need('gsfPutPresignedRetry' in s,'per-part bucket retry preserved')
need('/direct-upload/bucket/complete' in s,'bucket completion flow preserved')
need('"libx264 HQ"' in s,'V100.4 software render preserved')
need('"-preset","medium"' in s,'V100.4 medium render preserved')
need('"-crf","14"' in s,'V100.4 CRF14 preserved')
need('"-threads","2"' in s,'V100.4 render threads preserved')
core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''
need('"h264_qsv"' not in core,'QSV remains absent')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('numero_clip=3' in s,'AI 3 clips preserved')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'approved player sizing preserved')

print('V100.5 MAX Upload regression: PASS')
