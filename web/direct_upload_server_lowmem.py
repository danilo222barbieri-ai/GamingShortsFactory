#!/usr/bin/env python3
"""Low-memory launcher for the canonical direct-upload server.

The frontend service is limited to about 1 GB. Upload completion materializes the
persisted source from S3 onto local disk; that boundary must stay serialized and
must not let boto3 build a large threaded read-ahead queue.
"""
from __future__ import annotations

import threading
from boto3.s3.transfer import TransferConfig as _TransferConfig

import direct_upload_server as server


_MATERIALIZE_GATE=threading.BoundedSemaphore(1)


def _low_memory_transfer_config(*args, **kwargs):
    # V435: hard cap the transfer manager used by the upload companion. The
    # browser-to-bucket multipart upload is already direct; this protects the
    # bucket-to-local completion step that runs on the 1 GB frontend.
    kwargs["max_concurrency"]=1
    kwargs["max_io_queue"]=2
    kwargs["io_chunksize"]=256*1024
    kwargs["use_threads"]=False
    return _TransferConfig(*args, **kwargs)


server.TransferConfig=_low_memory_transfer_config
_original_materialize=server._materialize_bucket_object


def _materialize_bucket_object(*args, **kwargs):
    with _MATERIALIZE_GATE:
        return _original_materialize(*args, **kwargs)


server._materialize_bucket_object=_materialize_bucket_object


def main():
    server.ROOT.mkdir(parents=True,exist_ok=True)
    server._ensure_bucket_cors()
    server._ai_learning_restore()
    server._start_proactive_guardian()
    server._start_social_analytics_worker()
    server._start_twitch_token_validation()
    httpd=server.ThreadingHTTPServer(("127.0.0.1",server.PORT),server.Handler)
    print(
        f"GSF direct upload server LOWMEM listening on 127.0.0.1:{server.PORT} "
        f"bucket={'on' if server._bucket_enabled() else 'off'} "
        f"worker={'on' if server.WORKER_URL else 'off'}",
        flush=True,
    )
    httpd.serve_forever()


if __name__=="__main__":
    main()
