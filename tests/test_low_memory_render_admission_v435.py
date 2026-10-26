"""The existing render gate must admit one frontend job across processes."""
import importlib.util
import multiprocessing
import os
from pathlib import Path
import queue
import threading
import time

import pytest

pytest.importorskip('fcntl', reason='Linux frontend admission uses POSIX process locks')
ROOT = Path(__file__).resolve().parents[1]


def load_gate():
    spec = importlib.util.spec_from_file_location('isolated_gate', ROOT/'web/render_gate_v293.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def child_gate(start, messages, release=None, fail=False):
    gate = load_gate()
    messages.put(('ready', time.monotonic()))
    start.wait(5)
    try:
        with gate.render_slot():
            # Final render's nested postprocessing must retain its own slot.
            with gate.render_slot('postprocess'):
                assert gate._ACTIVE == 1
            messages.put(('enter', time.monotonic()))
            if release is not None:
                release.wait(5)
            else:
                time.sleep(.25)
            messages.put(('exit', time.monotonic()))
            if fail:
                raise ValueError('controlled render failure')
    except ValueError:
        messages.put(('failed', time.monotonic()))


def setup_env(monkeypatch, root):
    monkeypatch.setenv('GSF_RUNTIME_ROOT', str(root))
    monkeypatch.setenv('GSF_LOW_MEMORY_WEB', '1')
    monkeypatch.setenv('GSF_FINAL_RENDER_SLOTS', '1')
    monkeypatch.setenv('GSF_RENDER_QUEUE_TIMEOUT', '3')


def stop_children(children):
    for child in children:
        child.join(2)
        if child.is_alive():
            child.terminate()
            child.join(2)


def test_existing_gate_serializes_independent_frontend_processes(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    ctx = multiprocessing.get_context('spawn')
    start, messages = ctx.Event(), ctx.Queue()
    children = [ctx.Process(target=child_gate, args=(start, messages)) for _ in range(2)]
    try:
        for child in children:
            child.start()
        assert [messages.get(timeout=10)[0] for _ in children] == ['ready', 'ready']
        start.set()
        events = [messages.get(timeout=10) for _ in range(4)]
        active = peak = 0
        for kind, stamp in sorted(events, key=lambda row: row[1]):
            active += 1 if kind == 'enter' else -1
            peak = max(active, peak)
        assert peak == 1, 'Thread semaphores do not serialize independent render processes'
    finally:
        start.set()
        stop_children(children)
        messages.close()
    assert [child.exitcode for child in children] == [0, 0]


def test_process_queue_deadline_releases_local_slot_and_recovers_after_failure(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    ctx = multiprocessing.get_context('spawn')
    start, release, messages = ctx.Event(), ctx.Event(), ctx.Queue()
    owner = ctx.Process(target=child_gate, args=(start, messages, release, True))
    owner.start()
    try:
        assert messages.get(timeout=10)[0] == 'ready'
        start.set()
        assert messages.get(timeout=10)[0] == 'enter'
        gate = load_gate()
        monkeypatch.setenv('GSF_RENDER_QUEUE_TIMEOUT', '.1')
        begun = time.monotonic()
        with pytest.raises(TimeoutError, match='Render occupato'):
            with gate.render_slot():
                pytest.fail('Another process still owns the render slot')
        assert time.monotonic()-begun < 1
        assert gate._ACTIVE == 0
        assert not getattr(gate._THREAD_STATE, 'owns_slot', False)
        release.set()
        owner.join(5)
        assert owner.exitcode == 0
        # Both the native process lock and local semaphore must have been released.
        with gate.render_slot('retry'):
            with gate.render_slot('nested'):
                assert gate._ACTIVE == 1
        assert gate._ACTIVE == 0
    finally:
        release.set()
        stop_children([owner])
        messages.close()


def test_low_memory_frontend_cannot_opt_into_two_heavy_encoders(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    monkeypatch.setenv('GSF_FINAL_RENDER_SLOTS', '2')
    assert load_gate()._configured_slots() == 1
    monkeypatch.setenv('GSF_LOW_MEMORY_WEB', '0')
    assert load_gate()._configured_slots() == 2


def test_queue_capacity_timeout_is_terminal_not_retried_per_encoder():
    import ast
    from contextlib import contextmanager
    import subprocess
    tree = ast.parse((ROOT/'app.py').read_text())
    core = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=='_gsf_render_core')
    block = next(n for n in ast.walk(core) if isinstance(n, ast.Try)
                 and any(isinstance(stmt, ast.With) and any(
                     isinstance(item.context_expr, ast.Call)
                     and isinstance(item.context_expr.func, ast.Name)
                     and item.context_expr.func.id=='_gsf_render_slot_v293'
                     for item in stmt.items) for stmt in n.body))
    attempts = []
    @contextmanager
    def busy(label):
        attempts.append(label)
        raise TimeoutError('Render occupato: riprova tra poco (attesa massima raggiunta).')
        yield  # contextmanager protocol
    loop = ast.For(target=ast.Name(id='encoder',ctx=ast.Store()),
                   iter=ast.List(elts=[ast.Constant('first'),ast.Constant('fallback')],ctx=ast.Load()),
                   body=[block],orelse=[])
    ns = {'time':time, 'subprocess':subprocess, '_gsf_render_slot_v293':busy,
          '_diag_started':time.perf_counter(), '_diag_timeout':600, 'cmd':[],
          'fmt':'9:16 Short','duration':15,'last_error':'', '_gsf_perf_event':lambda *a,**kw:None}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[loop],type_ignores=[])), '<actual-render-admission-handler>', 'exec'),ns)
    assert len(attempts)==1, 'Trying another encoder cannot create capacity; do not restart the queue wait'
    assert 'occupato' in ns['last_error']


def test_background_quality_inspection_waits_for_the_existing_render_slot(tmp_path, monkeypatch):
    import ast
    import sys
    setup_env(monkeypatch, tmp_path)
    gate = load_gate()
    monkeypatch.setitem(sys.modules, 'web.render_gate_v293', gate)
    source = tmp_path/'final.mp4'
    source.write_bytes(b'x'*2048)
    inspected, stored = threading.Event(), threading.Event()
    observed = []
    reports = []
    def inspect(path):
        observed.append(getattr(gate._THREAD_STATE, 'owns_slot', False))
        inspected.set()
        return {'status':'pass','score':100}
    def store(sid, report):
        reports.append(report)
        stored.set()
    tree = ast.parse((ROOT/'web/direct_upload_server.py').read_text())
    node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_quality_schedule')
    ns = {'_safe_id':str,'Path':Path,'os':os,'time':time,'threading':threading,
          '_quality_load':lambda sid:{},'_QUALITY_LOCK':threading.Lock(),'_QUALITY_CACHE':{},
          '_quality_inspect':inspect,'_quality_store':store}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-quality-scheduler>','exec'),ns)
    with gate.render_slot('final'):
        ns['_quality_schedule']('quality-test',source)
        assert not inspected.wait(.15), 'Background quality decoding bypasses render admission and adds RAM pressure'
    assert stored.wait(2)
    assert observed == [True]
    assert reports[0]['status']=='pass'


def test_cinematic_low_memory_bounds_decoder_filter_and_encoder_without_changing_quality(monkeypatch):
    import importlib.util
    import subprocess
    spec=importlib.util.spec_from_file_location('cinematic_budget', ROOT/'web/cinematic_render_v125.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    captured=[]
    monkeypatch.setenv('GSF_LOW_MEMORY_WEB','1')
    monkeypatch.setattr(module.subprocess,'run',lambda cmd,**kw: captured.append(cmd) or subprocess.CompletedProcess(cmd,0,'',''))
    tail=module._encode_tail(True)
    command=['/usr/bin/ffmpeg','-y','-i','source.mp4','-i','replay.mp4','-filter_complex','[0:v]null[vout]']+tail+['final.mp4']
    module._run(command)
    actual=captured[0]
    prefix=actual[:actual.index('-i')]
    assert '-filter_complex_threads' in prefix, 'Cinematic graph bypassed the frontend filter-thread budget'
    assert prefix[prefix.index('-filter_complex_threads')+1]=='1'
    assert prefix[prefix.index('-threads')+1]=='1', 'Decoder threads must be bounded before input'
    for index,arg in enumerate(actual):
        if arg=='-i':
            assert actual[index-2:index]==['-threads','1']
    assert tail[tail.index('-threads')+1]=='1'
    assert tail[tail.index('-crf')+1]=='14'
    assert tail[tail.index('-pix_fmt')+1]=='yuv420p'
    monkeypatch.setenv('GSF_LOW_MEMORY_WEB','0')
    assert module._encode_tail(True)[module._encode_tail(True).index('-threads')+1]=='2'


def test_director_cold_open_does_not_buffer_the_whole_main_video(monkeypatch,tmp_path):
    import sys
    sys.path.insert(0,str(ROOT/'web'))
    import director_render_exec_v143 as director
    commands=[]
    monkeypatch.setattr(director,'probe_media',lambda path:{'duration':15.,'has_audio':True,'width':1080,'height':1920})
    monkeypatch.setattr(director,'_run',lambda cmd,**kw:commands.append(cmd))
    assert director._prepend_cold_open(tmp_path/'source.mp4',tmp_path/'out.mp4',.7,6.)
    command=commands[0]
    assert command.count('-i')==2, 'One input feeding late cold-open and full main buffers hundreds of full-resolution frames'
    assert command.index('-ss')<command.index('-i')
    assert command.index('-t')<command.index('-i')
    graph=command[command.index('-filter_complex')+1]
    assert 'trim=' not in graph
    assert '[1:v]' in graph and '[1:a]' in graph
    assert 'concat=n=2:v=1:a=1' in graph


def test_nested_postprocessing_survives_module_reload(tmp_path,monkeypatch):
    setup_env(monkeypatch,tmp_path)
    monkeypatch.setenv('GSF_RENDER_QUEUE_TIMEOUT','.05')
    outer=load_gate()
    inner=load_gate()
    with outer.render_slot('final'):
        with inner.render_slot('reimported-director'):
            assert outer._ACTIVE==1
