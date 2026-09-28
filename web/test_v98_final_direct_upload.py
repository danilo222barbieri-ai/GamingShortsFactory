from pathlib import Path
import concurrent.futures
import http.client
import importlib.util
import json
import os
import tempfile
import threading

server_path=Path('/app/web/direct_upload_server.py')
source=server_path.read_text(encoding='utf-8')
compile(source,str(server_path),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('MAX_CHUNK_BYTES=40*1024*1024' in source,'server accepts 32MB lanes')
need('os.pwrite' in source,'direct positional writes enabled')
need('.part' not in source,'per-chunk part files removed')
need('for p in parts' not in source,'final recomposition loop removed')
need('os.fsync(fd)' in source,'single final durability sync retained')

spec=importlib.util.spec_from_file_location('gsf_upload_server',server_path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory() as td:
    mod.ROOT=Path(td)
    httpd=mod.ThreadingHTTPServer(('127.0.0.1',0),mod.Handler)
    port=httpd.server_address[1]
    th=threading.Thread(target=httpd.serve_forever,daemon=True)
    th.start()
    try:
        # Deterministic payload, 4 chunks deliberately sent in reverse order.
        payload=bytes((i*37+11)%256 for i in range(5*1024*1024+123))
        count=4
        base=len(payload)//count
        chunks=[]
        start=0
        for i in range(count):
            end=len(payload) if i==count-1 else start+base
            chunks.append((i,start,payload[start:end]))
            start=end

        def send(item):
            i,start,body=item
            c=http.client.HTTPConnection('127.0.0.1',port,timeout=20)
            headers={
                'Content-Type':'application/octet-stream',
                'Content-Length':str(len(body)),
                'X-GSF-Session-ID':'finaltest',
                'X-GSF-Upload-ID':'upload123',
                'X-GSF-Filename':'final_test.mp4',
                'X-GSF-File-Size':str(len(payload)),
                'X-GSF-Chunk-Start':str(start),
                'X-GSF-Chunk-Index':str(i),
                'X-GSF-Chunk-Count':str(count),
            }
            c.request('PUT','/chunk',body=body,headers=headers)
            resp=c.getresponse()
            data=resp.read()
            c.close()
            return resp.status,json.loads(data.decode('utf-8'))

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(send,reversed(chunks)))

        need(all(status==200 for status,_ in results),'four concurrent chunks accepted')
        marker=mod.ROOT/'sessions'/'finaltest'/'media'/'.direct_upload_ready.json'
        need(marker.is_file(),'completion marker written')
        meta=json.loads(marker.read_text(encoding='utf-8'))
        final=Path(meta['path'])
        need(final.is_file(),'final file exists')
        need(final.read_bytes()==payload,'out-of-order parallel upload is byte-identical')
        need(int(meta['size'])==len(payload),'final size metadata correct')
    finally:
        httpd.shutdown()
        httpd.server_close()

print('V98 FINAL direct-upload integration: PASS')
