"""Isolated V435 materialization probe using real boto3 HTTP transfers.

This is NOT a production bucket or browser-upload test. It exercises the canonical
launcher/materializer/media validation with a streaming S3-compatible local origin.
Run inside an otherwise running production-equivalent container with a 1 GiB limit.
No provider credentials or production objects are read or changed.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import resource
import shutil
import sys
import tempfile
import threading
import time


def run(media: Path, output: Path, counts: list[int]):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'web'))
    import boto3
    from botocore.config import Config
    import direct_upload_server_lowmem as launcher
    server = launcher.server
    media = media.resolve()
    size = media.stat().st_size
    with media.open('rb') as source:
        expected = hashlib.file_digest(source, 'sha256').hexdigest()
    lock = threading.Lock()
    active = peak_transfers = 0

    class Origin(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-Length', str(size))
            self.send_header('ETag', '"probe-local-fixture"')
            self.end_headers()
        def do_GET(self):
            nonlocal active, peak_transfers
            start, end = 0, size - 1
            ranged = self.headers.get('Range', '')
            if ranged:
                left, right = ranged.removeprefix('bytes=').split('-')
                start, end = int(left), int(right) if right else end
            with lock:
                active += 1
                peak_transfers = max(peak_transfers, active)
            try:
                self.send_response(206 if ranged else 200)
                self.send_header('Content-Length', str(end - start + 1))
                self.send_header('ETag', '"probe-local-fixture"')
                if ranged:
                    self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.end_headers()
                with media.open('rb') as source:
                    source.seek(start)
                    remaining = end - start + 1
                    while remaining:
                        chunk = source.read(min(256 * 1024, remaining))
                        if not chunk:
                            raise IOError('fixture ended early')
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            finally:
                with lock:
                    active -= 1

    origin = ThreadingHTTPServer(('127.0.0.1', 0), Origin)
    threading.Thread(target=origin.serve_forever, daemon=True).start()
    client = boto3.client('s3', endpoint_url=f'http://127.0.0.1:{origin.server_port}',
                          aws_access_key_id='isolated-probe', aws_secret_access_key='isolated-probe',
                          region_name='us-east-1', config=Config(s3={'addressing_style': 'path'}, proxies={}))
    result = {'transport': 'local S3-compatible HTTP, real boto3; no production bucket',
              'source_bytes': size, 'batches': []}
    try:
        with tempfile.TemporaryDirectory(prefix='gsf-v435-probe-') as td:
            server.ROOT = Path(td)
            server.S3_BUCKET = 'probe'
            server._S3_CLIENT = client
            # _bucket_enabled checks configuration before returning cached client.
            server.S3_ENDPOINT = f'http://127.0.0.1:{origin.server_port}'
            server.S3_ACCESS_KEY = server.S3_SECRET_KEY = 'isolated-probe'
            for count in counts:
                peak_transfers = 0
                event_path = Path('/sys/fs/cgroup/memory.events')
                before_events = dict((key, int(value)) for key, value in
                                     (line.split() for line in event_path.read_text().splitlines()))
                samples = []
                stop_sampling = threading.Event()
                def sample():
                    while not stop_sampling.is_set():
                        try:
                            samples.append(int(Path('/sys/fs/cgroup/memory.current').read_text()))
                        except OSError:
                            pass
                        stop_sampling.wait(0.02)
                sampler = threading.Thread(target=sample, daemon=True)
                sampler.start()
                started = time.monotonic()
                cpu = time.process_time()
                barrier = threading.Barrier(count)
                def complete(index):
                    sid, uid = f'probe{index}', f'{index:020x}'
                    barrier.wait(timeout=30)
                    server._materialize_bucket_object(sid, uid, 'fixture', media.name,
                                                     'fixture', media.suffix, size, '')
                    folder = server.ROOT / 'sessions' / sid / 'media'
                    marker = json.loads((folder / '.direct_upload_ready.json').read_text())
                    final = Path(marker['path'])
                    assert marker['upload_id'] == uid and marker['size'] == size
                    with final.open('rb') as downloaded:
                        assert hashlib.file_digest(downloaded, 'sha256').hexdigest() == expected
                    assert not (folder / '.direct_upload_error.json').exists()
                    assert not list(folder.glob('*.tmp'))
                with concurrent.futures.ThreadPoolExecutor(max_workers=count) as pool:
                    list(pool.map(complete, range(count)))
                stop_sampling.set()
                sampler.join(timeout=2)
                assert peak_transfers == 1, peak_transfers
                after_events = dict((key, int(value)) for key, value in
                                    (line.split() for line in event_path.read_text().splitlines()))
                oom_delta = {key: after_events.get(key, 0)-before_events.get(key, 0)
                             for key in ('oom', 'oom_kill')}
                assert samples, 'Cgroup memory sampling is required'
                result['batches'].append({'oom_event_delta': oom_delta, 'concurrent_completions': count, 'max_active_transfers': peak_transfers,
                    'duration_seconds': round(time.monotonic()-started, 3),
                    'cpu_seconds': round(time.process_time()-cpu, 3),
                    'process_peak_rss_mib': round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024, 2),
                    'container_idle_mib': round(samples[0]/1048576, 2) if samples else None,
                    'container_peak_mib': round(max(samples)/1048576, 2) if samples else None,
                    'verified_files': count, 'errors': []})
                shutil.rmtree(server.ROOT / 'sessions')
    finally:
        origin.shutdown()
        client.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    assert all(not any(b['oom_event_delta'].values()) for b in result['batches']), 'OOM observed in isolated container; see evidence'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--media', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--counts', type=int, nargs='+', default=[1, 2, 4, 6])
    args = ap.parse_args()
    if not args.counts or any(n not in (1, 2, 4, 6) for n in args.counts):
        ap.error('counts must be 1, 2, 4 or 6')
    run(args.media, args.output, args.counts)
