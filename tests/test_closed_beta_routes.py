"""The public save-current action must reach its actual companion handler."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ClosedBetaRoutes(unittest.TestCase):
    def test_save_current_has_a_companion_route(self):
        nginx=(ROOT/'web/nginx.conf.template').read_text()
        match=re.search(r'location = /drafts/save-current\s*\{(.*?)(?=\n    location|\Z)',nginx,re.S)
        self.assertIsNotNone(match, 'Save draft currently falls through to Streamlit and returns HTTP 405')
        self.assertIn('proxy_pass http://127.0.0.1:8502',match.group(1))
        self.assertIn('X-GSF-Session-ID $gsf_session_cookie',match.group(1))
        self.assertIn('limit_except POST',match.group(1))


class PublicComponentDeepLinks(unittest.TestCase):
    def test_top_level_routes_keep_the_global_shell_and_iframes_keep_canonical_bytes(self):
        import os
        import urllib.request
        import urllib.error
        base=os.environ.get('GSF_BASE_URL')
        if not base:
            self.skipTest('requires running image GSF_BASE_URL')
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args):
                return None
        client=urllib.request.build_opener(NoRedirect)
        headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile Safari/604.1'}
        for path,target,component in (
            ('/game-editor-mobile/','editor','game_editor_mobile_component'),
            ('/editor-live/','editor','editor_2027_component'),
            ('/creator-hub-v156/','hub','creator_hub_v156_component'),
            ('/ai-v221/','ai','ai_v221_component'),
            ('/share-v156/','short','share_v156_component')):
            with self.subTest(path=path):
                request=urllib.request.Request(base+path,headers={**headers,'Sec-Fetch-Dest':'document'})
                try:
                    response=client.open(request,timeout=5)
                except urllib.error.HTTPError as exc:
                    response=exc
                with response:
                    self.assertEqual(response.status,302)
                    from urllib.parse import urlsplit
                    location=urlsplit(response.headers['Location'])
                    self.assertEqual(location.path+'?'+location.query,'/?gsf_page='+target)
                request=urllib.request.Request(base+path,headers={**headers,'Sec-Fetch-Dest':'iframe'})
                with client.open(request,timeout=5) as response:
                    self.assertEqual(response.read(),(ROOT/'web'/component/'index.html').read_bytes())


class ColdBrowserAssetBurst(unittest.TestCase):
    def test_real_nginx_accepts_browser_assets_and_still_limits_overload(self):
        import os
        import subprocess
        if not os.environ.get('GSF_BASE_URL'):
            self.skipTest('requires running production image')
        import textwrap
        probe=textwrap.dedent(r"""
            import http.server,socket,threading,tempfile,subprocess,time
            from pathlib import Path
            release=threading.Event()
            class Held(http.server.BaseHTTPRequestHandler):
             protocol_version='HTTP/1.1'
             def log_message(self,*args):pass
             def do_GET(self):
              self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'x');self.wfile.flush();release.wait(20);self.wfile.write(b'x')
            up=http.server.ThreadingHTTPServer(('127.0.0.1',18501),Held);threading.Thread(target=up.serve_forever,daemon=True).start()
            with tempfile.TemporaryDirectory() as td:
             root=Path(td);template=Path('/app/web/nginx.conf.template').read_text().replace('${PORT}','18580').replace('127.0.0.1:8501','127.0.0.1:18501')
             config=root/'nginx.conf';config.write_text('worker_processes 1;\npid '+str(root/'pid')+';\nerror_log '+str(root/'error.log')+' notice;\nevents {worker_connections 1024;}\nhttp {access_log off;\n'+template+'\n}')
             nginx=subprocess.Popen(['nginx','-p',td,'-c',str(config),'-g','daemon off;'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
             sockets=[]
             try:
              for _ in range(100):
               try:s=socket.create_connection(('127.0.0.1',18580),timeout=1);s.close();break
               except OSError:time.sleep(.02)
              statuses=[]
              for _ in range(160):
               s=socket.create_connection(('127.0.0.1',18580),timeout=3);s.settimeout(3);s.sendall(b'GET /static/js/cold-load-test.js HTTP/1.1\r\nHost: localhost\r\nUser-Agent: iPhone Mobile Safari\r\nX-Real-IP: 10.10.10.10\r\nConnection: close\r\n\r\n');data=b''
               while b'\r\n\r\n' not in data:data+=s.recv(4096)
               statuses.append(int(data.split(b' ')[1]));sockets.append(s)
              print({status:statuses.count(status) for status in set(statuses)},flush=True)
              assert statuses[:64]==[200]*64, 'cold browser asset burst rejected'
              assert 503 in statuses, 'connection flood protection must remain active'
              errors=(root/'error.log').read_text();print('\n'.join(x for x in errors.splitlines() if 'limiting connections' in x)[-1200:],flush=True)
             finally:
              release.set()
              for s in sockets:s.close()
              nginx.terminate();nginx.wait(timeout=5);up.shutdown()
        """)
        result=subprocess.run(['docker','exec','-i',os.environ.get('GSF_GATE_CONTAINER','gsf-production-gate'),'python','-'],
                              input=probe,text=True,capture_output=True,timeout=35)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()
