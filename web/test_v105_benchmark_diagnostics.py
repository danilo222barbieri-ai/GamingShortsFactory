#!/usr/bin/env python3
import v105_render_benchmark as bench

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need(hasattr(bench,"describe_process_failure"),"benchmark exposes process-failure diagnostics")
need("SIGKILL" in bench.describe_process_failure(-9,b""),"signal -9 is identified as SIGKILL")
need("returncode=1" in bench.describe_process_failure(1,b"encoder error"),"normal nonzero return code is retained")
need("encoder error" in bench.describe_process_failure(1,b"encoder error"),"stderr tail is retained")

print("V105 benchmark diagnostics: PASS")
