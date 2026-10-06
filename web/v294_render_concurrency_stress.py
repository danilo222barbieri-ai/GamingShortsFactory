#!/usr/bin/env python3
import concurrent.futures
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "/app/web")
import v105_render_benchmark as bench

bench.FFMPEG = os.environ.get("GSF_BENCH_FFMPEG", "/usr/local/bin/ffmpeg")
bench.FFPROBE = os.environ.get("GSF_BENCH_FFPROBE", "/usr/bin/ffprobe")


def pct(values, p):
    xs = sorted(values)
    if not xs:
        return 0.0
    return xs[max(0, min(len(xs) - 1, math.ceil(len(xs) * p) - 1))]


def one(source, root, stage, index):
    out = root / f"{stage}-{index}.mp4"
    row = bench.run_profile(source, out, "medium_crf14_t1", timeout=420)
    row["stage"] = stage
    row["index"] = index
    row["output"] = str(out)
    row["exists"] = out.is_file()
    row["bytes"] = out.stat().st_size if out.is_file() else 0
    return row


def main():
    root = Path(tempfile.mkdtemp(prefix="gsf_v294_render_"))
    try:
        source = root / "source.mp4"
        cmd = bench.synthetic_fixture_command(source, duration=8)
        print("V294_RENDER_SOURCE_CMD " + json.dumps(cmd), flush=True)
        t0 = time.perf_counter()
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        source_s = time.perf_counter() - t0
        if r.returncode != 0 or not source.is_file():
            print("V294_RENDER_SOURCE_FAIL " + bench.describe_process_failure(r.returncode, r.stderr), flush=True)
            return 2
        print("V294_RENDER_SOURCE " + json.dumps({"bytes": source.stat().st_size, "seconds": round(source_s, 3)}), flush=True)

        for n in (1, 2, 4, 6):
            stage = f"c{n}"
            print(f"V294_RENDER_STAGE_START {stage}", flush=True)
            rows = []
            errors = []
            wall0 = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
                futures = {ex.submit(one, source, root, stage, i): i for i in range(n)}
                for f in concurrent.futures.as_completed(futures):
                    idx = futures[f]
                    try:
                        row = f.result()
                        rows.append(row)
                        print("V294_RENDER_FLOW " + json.dumps(row, sort_keys=True, default=str), flush=True)
                    except Exception as exc:
                        errors.append({"index": idx, "error": repr(exc)})
                        print("V294_RENDER_FLOW_ERROR " + repr(exc), flush=True)
            wall = time.perf_counter() - wall0
            elapsed = [float(x.get("elapsed_seconds") or 0) for x in rows]
            bad = [x for x in rows if int(x.get("returncode", 1)) != 0 or not (x.get("master") or {}).get("ok")]
            summary = {
                "stage": stage,
                "jobs": n,
                "ok": len(rows) - len(bad),
                "failed": len(errors) + len(bad),
                "wall_s": round(wall, 3),
                "p50_render_s": round(pct(elapsed, .50), 3),
                "p95_render_s": round(pct(elapsed, .95), 3),
                "max_render_s": round(max(elapsed) if elapsed else 0, 3),
                "peak_container_memory_bytes": max([int(x.get("peak_memory_bytes") or 0) for x in rows] or [0]),
                "outputs": [int(x.get("bytes") or 0) for x in rows],
            }
            print("V294_RENDER_STAGE " + json.dumps(summary, sort_keys=True), flush=True)
            if errors or bad:
                print("V294_RENDER_SAFETY_STOP " + json.dumps({"errors": errors, "bad": bad}, default=str), flush=True)
                return 3
            time.sleep(3)
        print("V294_RENDER_CONCURRENCY_STRESS: PASS", flush=True)
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
