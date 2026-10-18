"""Bounded composite readiness check used by the production-image gate."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request


def wait_for_health(url, *, deadline_seconds=180, request_timeout=3, interval=2,
                    container=None):
    deadline = time.monotonic() + deadline_seconds
    last = 'no response'
    previous = None
    while time.monotonic() < deadline:
        if container:
            state = subprocess.run(
                ['docker', 'inspect', '-f', '{{.State.Running}}', container],
                capture_output=True, text=True, timeout=min(2, max(.01, deadline-time.monotonic())))
            if state.returncode or state.stdout.strip() != 'true':
                raise RuntimeError(f'Container {container} stopped before readiness: {state.stderr.strip()}')
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            request = urllib.request.Request(url, headers={'User-Agent':'GSF-Production-Gate'})
            with urllib.request.urlopen(request, timeout=min(request_timeout, remaining)) as response:
                # Health is a small JSON response. Limit body size as well as time.
                body = bytearray()
                while True:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Health response exceeded total deadline')
                    chunk = response.read1(min(4096, 65537-len(body)))
                    if not chunk:
                        break
                    body.extend(chunk)
                    if len(body) > 65536:
                        raise ValueError('Health response is too large')
                payload = json.loads(body)
                if response.status == 200 and all(payload.get(k) is True for k in ('ok', 'companion', 'streamlit')):
                    return payload
                last = f'HTTP {response.status}: {payload}'
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last = f'{type(exc).__name__}: {exc}'
        if last != previous:
            print(f'Waiting for composite health: {last}', flush=True)
            previous = last
        time.sleep(min(interval, max(0, deadline-time.monotonic())))
    raise TimeoutError(f'Composite health not ready within {deadline_seconds}s; last result: {last}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('--container')
    parser.add_argument('--deadline', type=float, default=180)
    args = parser.parse_args()
    payload = wait_for_health(args.url, container=args.container, deadline_seconds=args.deadline)
    print('GSF composite health: PASS', json.dumps(payload), flush=True)


if __name__ == '__main__':
    main()
