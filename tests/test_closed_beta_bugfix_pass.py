"""Regression checks for the reported mobile closed-beta defects."""
import ast
import io
import json
import os
import re
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def companion_functions(names, runtime, bucket=None):
    tree=ast.parse((ROOT/'web/direct_upload_server.py').read_text())
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    namespace={'ROOT':runtime,'Path':Path,'json':json,'os':os,'re':re,'time':time,'threading':threading,
               'ID_RE':re.compile(r'^[A-Za-z0-9_-]{1,80}$'),'S3_BUCKET':'test-bucket','_bucket_enabled':lambda:bucket is not None,'_s3':lambda:bucket,
               '_STATE_LOCKS':{},'_STATE_LOCKS_GUARD':threading.Lock()}
    exec(compile(ast.Module(body=functions,type_ignores=[]),'<companion-regression>','exec'),namespace)
    return namespace


class MemoryBucket:
    def __init__(self):self.objects={};self.fail=False
    def put_object(self,**kwargs):
        if self.fail:raise OSError('storage unavailable')
        self.objects[kwargs['Key']]=kwargs['Body']
    def get_object(self,**kwargs):return {'Body':io.BytesIO(self.objects[kwargs['Key']])}


class ProfilePersistence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.bucket=MemoryBucket()
        self.ns=companion_functions({'_safe_id','_write_json_atomic','_creator_session_key','_creator_profile_key',
                                    '_creator_account_save','_creator_account_load'},self.root,self.bucket)
    def test_local_creator_can_save_photo_and_name_without_forging_account_identity(self):
        profile={'display_name':'Beta creator','avatar':'data:image/png;base64,dGVzdA=='}
        self.ns['_creator_account_save']('browserA',profile)
        saved=self.ns['_creator_account_load']('browserA')
        self.assertEqual(saved['display_name'],'Beta creator');self.assertEqual(saved['avatar'],profile['avatar'])
        self.assertFalse(saved.get('account_id'))
        # A new process/container has no local profile cache; same browser restores from storage.
        (self.root/'sessions/browserA/account.json').unlink()
        restored=self.ns['_creator_account_load']('browserA')
        self.assertEqual(restored['display_name'],profile['display_name'])
        self.assertEqual(restored['avatar'],profile['avatar']);self.assertFalse(restored.get('account_id'))
        self.assertFalse(any(key.startswith('creator-accounts/') for key in self.bucket.objects))
    def test_existing_connected_profile_keeps_identity_and_providers(self):
        profile={'account_id':'accountA','display_name':'Connected','providers':{'google':{'uid':'abc'}}}
        self.ns['_creator_account_save']('browserA',profile)
        self.assertEqual(self.ns['_creator_account_load']('browserA'),profile)
        self.assertIn('creator-accounts/accountA/profile.json',self.bucket.objects)
    def test_failed_persistence_keeps_the_last_committed_local_profile(self):
        old={'account_id':'accountA','display_name':'Before'}
        self.ns['_creator_account_save']('browserA',old);self.bucket.fail=True
        with self.assertRaises(OSError):self.ns['_creator_account_save']('browserA',{**old,'display_name':'Unsaved'})
        self.assertEqual(self.ns['_creator_account_load']('browserA')['display_name'],'Before')




def installed_parent_html():
    """Build the real production parent without supplying transient Streamlit CSS."""
    import runpy,sys,types
    with tempfile.TemporaryDirectory() as directory:
        package=Path(directory)/'streamlit';(package/'static').mkdir(parents=True)
        index=package/'static/index.html';index.write_text('<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
        stub=types.ModuleType('streamlit');stub.__file__=str(package/'__init__.py');old=sys.modules.get('streamlit');sys.modules['streamlit']=stub
        try:runpy.run_path(str(ROOT/'web/install_adsense_bridge.py'));return index.read_text()
        finally:
            if old is None:sys.modules.pop('streamlit',None)
            else:sys.modules['streamlit']=old


class HubColdGeometry(unittest.TestCase):
    def test_duplicate_shell_focus_does_not_reset_internal_scroll(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil
        parent=installed_parent_html();html=(ROOT/'web/creator_hub_v156_component/index.html').read_text()
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                page=browser.new_page(viewport={'width':375,'height':667})
                def route(request):
                    if request.request.url=='http://gsf.test/':request.fulfill(content_type='text/html',body=parent)
                    elif '/creator-hub-v156/' in request.request.url:request.fulfill(content_type='text/html',body=html)
                    else:request.fulfill(json={'ok':True,'csrf_token':'test','account':{'display_name':'Creator'}})
                page.route('**/*',route);page.goto('http://gsf.test/')
                page.wait_for_function('()=>GSFNavigation?.snapshot().surfaces===5');page.evaluate("GSFNavigation.navigate({target:'hub',section:'profile'})")
                hub=page.frame_locator('#gsf-creator-hub-live-v160 iframe');hub.locator('#profileNameInput').wait_for()
                hub.locator('#hub').evaluate('e=>e.scrollTop=e.scrollHeight');page.wait_for_timeout(100)
                before=hub.locator('#hub').evaluate('e=>e.scrollTop');self.assertGreater(before,0)
                page.evaluate("()=>{const f=document.querySelector('#gsf-creator-hub-live-v160 iframe');f.contentWindow.postMessage({type:'GSF_HUB_FOCUS',section:'profile',epoch:GSFNavigation.snapshot().epoch},location.origin)}")
                page.wait_for_timeout(100)
                self.assertEqual(hub.locator('#hub').evaluate('e=>e.scrollTop'),before,'Repeated parent focus must preserve reading position')
            finally:browser.close()

    def test_local_profile_edits_save_immediately_and_survive_reload(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil,base64,struct,zlib
        from urllib.parse import urlsplit
        parent=installed_parent_html();html=(ROOT/'web/creator_hub_v156_component/index.html').read_text()
        state={'ok':True,'csrf_token':'test','account':{'connected':False,'display_name':'Creator'},'social':{},'stats':{},'usage':{},'limits':{},'drafts':[],'shorts':[]};fail=[False]
        def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',1024,256,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x30\x90\xe0'*1024)*256))+chunk(b'IEND',b'')
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                page=browser.new_page(viewport={'width':390,'height':844})
                def route(request):
                    if request.request.url.startswith(("blob:","data:")):
                        request.continue_();return
                    path=urlsplit(request.request.url).path
                    if path=='/':request.fulfill(content_type='text/html',body=parent)
                    elif path=='/creator-hub-v156/':request.fulfill(content_type='text/html',body=html)
                    elif path=='/creator-hub/profile':
                        if fail[0]:request.fulfill(status=503,json={'ok':False,'error':'Salvataggio non disponibile'})
                        else:
                            saved=request.request.post_data_json;state['account'].update(saved);request.fulfill(json={'ok':True,'display_name':state['account']['display_name'],'updated_at':time.time()})
                    elif path=='/creator-hub/state':request.fulfill(json=state)
                    else:request.fulfill(content_type='application/javascript',body='')
                page.route('**/*',route);page.goto('http://gsf.test/?gsf_page=hub');page.wait_for_function('()=>window.GSFNavigation?.snapshot().surfaces===5');page.evaluate("GSFNavigation.navigate({target:'hub',section:'profile'})")
                child=page.frame_locator('#gsf-creator-hub-live-v160 iframe');child.locator('#profileMeta').wait_for(state='attached');child.locator('#hub').evaluate("()=>new Promise((resolve,reject)=>{setTimeout(()=>reject(new Error('State did not settle')),10000);const tick=()=>window.GSFHubV415?.getState().csrf_token?resolve():setTimeout(tick,10);tick()})")
                self.assertFalse(child.locator('#profileNameInput').is_disabled(),'Local Creator editing must not require an unrelated social login')
                # A slow state response captured before the save must not overwrite it.
                snapshot=json.loads(json.dumps(state));pending_state=[]
                page.route('**/creator-hub/state',lambda route:pending_state.append(route))
                child.locator('#hub').evaluate("()=>{window.profileLoadTest=GSFHubV415.loadState()}")
                for _ in range(100):
                    if pending_state:break
                    page.wait_for_timeout(20)
                self.assertTrue(pending_state,'A stale state request must be in flight')
                child.locator('#profileNameInput').fill('Beta creator');child.locator('#saveProfileBtn').click()
                page.wait_for_function("()=>document.querySelector('#gsf-global-header .v343AccountName').textContent==='Beta creator'")
                pending_state[0].fulfill(json=snapshot)
                child.locator('#hub').evaluate('()=>window.profileLoadTest')
                page.unroute('**/creator-hub/state')
                self.assertEqual(child.locator('#profileNameInput').input_value(),'Beta creator','A stale Hub response must not undo the saved name')
                self.assertFalse(child.locator('#accountBtn').is_visible(),'Remove Accedi from settings without removing connected logout')
                with page.expect_file_chooser() as chooser:child.locator('#profileAvatar').click()
                chooser.value.set_files({'name':'profile.png','mimeType':'image/png','buffer':png})
                child.locator('#profileAvatar').evaluate("()=>new Promise((resolve,reject)=>{setTimeout(()=>reject(new Error(document.querySelector('#toastLocal').textContent||'Photo state did not settle')),10000);const tick=()=>window.GSFHubV415.getState().account.avatar?resolve():setTimeout(tick,10);tick()})")
                self.assertTrue(state['account']['avatar'].startswith('data:image/jpeg;base64,'))
                dimensions=child.locator('#profileAvatarImg').evaluate('e=>({width:e.naturalWidth,height:e.naturalHeight})')
                self.assertLessEqual(max(dimensions.values()),512)
                page.reload();page.wait_for_function("()=>window.GSFNavigation?.snapshot().surfaces===5");page.evaluate("GSFNavigation.navigate({target:'hub',section:'profile'})")
                child.locator('#profileNameInput').wait_for();child.locator('#profileNameInput').evaluate("e=>new Promise((resolve,reject)=>{setTimeout(()=>reject(new Error('State did not settle')),10000);const tick=()=>e.value==='Beta creator'?resolve():setTimeout(tick,10);tick()})")
                self.assertTrue(child.locator('#profileAvatar').evaluate("e=>e.classList.contains('has-photo')"))
                fail[0]=True;child.locator('#profileNameInput').fill('Unsaved');child.locator('#saveProfileBtn').click()
                child.locator('#toastLocal').filter(has_text='Salvataggio non disponibile').wait_for()
                self.assertEqual(child.locator('#profileNameInput').input_value(),'Unsaved')
                self.assertEqual(state['account']['display_name'],'Beta creator')
            finally:browser.close()

    def test_header_photo_is_not_replaced_or_hidden_by_legacy_logo_cleanup(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil
        from urllib.parse import urlsplit
        parent=installed_parent_html();avatar='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jG6kAAAAASUVORK5CYII='
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                page=browser.new_page(viewport={'width':390,'height':844})
                def route(request):
                    if urlsplit(request.request.url).path=='/':request.fulfill(content_type='text/html',body=parent)
                    else:request.fulfill(json={'ok':True,'account':{'connected':True,'display_name':'Beta','avatar':avatar}})
                page.route('**/*',route);page.goto('http://gsf.test/')
                image=page.locator('#gsf-global-header .v343Avatar img');image.wait_for(state='attached');page.wait_for_timeout(350)
                self.assertEqual(image.get_attribute('src'),avatar,'Logo cleanup must never claim an account avatar')
                self.assertNotEqual(image.evaluate('e=>getComputedStyle(e).display'),'none')
            finally:browser.close()

    def test_persistent_hub_fills_its_frame_and_keeps_last_card_reachable(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil
        from urllib.parse import urlsplit
        parent=installed_parent_html();hub_html=(ROOT/'web/creator_hub_v156_component/index.html').read_text()
        state={'ok':True,'csrf_token':'test','account':{'connected':False,'display_name':'Creator'},'social':{},'stats':{},'usage':{},'limits':{},'drafts':[],'shorts':[]}
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'))
            executable=shutil.which('chromium') if engine.name=='chromium' else None
            options={'executable_path':executable,'args':['--no-sandbox']} if executable else {}
            browser=engine.launch(**options)
            try:
                for width,height in [(375,667),(390,844),(430,932),(412,915)]:
                    with self.subTest(viewport=(width,height)):
                        page=browser.new_page(viewport={'width':width,'height':height},is_mobile=True,has_touch=True)
                        def route(request):
                            path=urlsplit(request.request.url).path
                            if path=='/':request.fulfill(content_type='text/html',body=parent)
                            elif path=='/creator-hub-v156/':request.fulfill(content_type='text/html',body=hub_html)
                            elif path=='/creator-hub/state':request.fulfill(json=state)
                            else:request.fulfill(content_type='application/javascript',body='')
                        page.route('**/*',route);page.goto('http://gsf.test/?gsf_page=hub')
                        page.wait_for_function('()=>window.GSFNavigation?.snapshot().surfaces===5')
                        page.evaluate("GSFNavigation.navigate({target:'hub'})")
                        frame=page.locator('#gsf-creator-hub-live-v160 iframe');child=page.frame_locator('#gsf-creator-hub-live-v160 iframe')
                        child.locator('#profileMeta').wait_for(state='attached');child.locator('#hub').evaluate("()=>new Promise((resolve,reject)=>{setTimeout(()=>reject(new Error('State did not settle')),10000);const tick=()=>window.GSFHubV415?.getState().csrf_token?resolve():setTimeout(tick,10);tick()})")
                        rect=frame.bounding_box()
                        self.assertGreaterEqual(rect['width'],width*.9,'Cold Hub falls back to browser-default iframe width')
                        self.assertGreaterEqual(rect['height'],height*.6,'Cold Hub depends on transient Streamlit CSS')
                        # Also reproduce the legacy expanded frame that extends under the bar.
                        for expanded in (False,True):
                            if expanded:frame.evaluate("e=>{e.style.cssText='position:fixed!important;inset:32px 0 0!important;width:100%!important;height:calc(100dvh - 32px)!important';window.dispatchEvent(new Event('resize'))}")
                            for view in ('dashboard','projects','live','settings'):
                                child.locator('#hub').evaluate('(e,v)=>GSFHubV415.openView(v)',view)
                                child.locator('#hub').evaluate('e=>e.scrollTop=e.scrollHeight')
                                page.wait_for_timeout(80)
                                result=frame.evaluate("f=>{const d=f.contentDocument,h=d.querySelector('#hub'),v=d.querySelector('.view.active'),r=f.getBoundingClientRect(),bar=document.querySelector('#gsf-global-gamebar').getBoundingClientRect();return {lastBottom:r.top+v.getBoundingClientRect().bottom,barTop:bar.top,scrollTop:h.scrollTop,outerScroll:d.scrollingElement.scrollTop}}")
                                self.assertLessEqual(result['lastBottom'],result['barTop']-8,(view,expanded,result))
                                self.assertEqual(result['outerScroll'],0,'Keep scroll internal to Hub')
                        page.close()
            finally:browser.close()

class PushPreferencePersistence(unittest.TestCase):
    def test_default_off_explicit_on_and_later_off_survive_cache_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);bucket=MemoryBucket()
            ns=companion_functions({'_safe_id','_write_json_atomic','_push_subscription_path','_push_preferences_load','_push_preferences_save'},root,bucket)
            self.assertFalse(ns['_push_preferences_load']('browserA')['enabled'])
            ns['_push_preferences_save']('browserA',{'enabled':True,'revision':10})
            ns['_push_preferences_save']('browserA',{'enabled':False,'revision':20})
            # A delayed ON from an older action must never override OFF.
            ns['_push_preferences_save']('browserA',{'enabled':True,'revision':10})
            self.assertFalse(ns['_push_preferences_load']('browserA')['enabled'])
            (root/'sessions/browserA/.push_preferences.json').unlink()
            self.assertFalse(ns['_push_preferences_load']('browserA')['enabled'])
            self.assertEqual(ns['_push_preferences_load']('browserA')['revision'],20)

class ShortGameplayResults(unittest.TestCase):
    def test_accepts_one_or_two_completed_moments_but_never_stale_requests(self):
        import subprocess,shutil
        if not shutil.which('node'):self.skipTest('Node required')
        text=(ROOT/'web/ai_v221_component/index.html').read_text()
        function=text[text.index('function freshRows('):text.index('async function pollResults(')]
        script="const assert=require('node:assert/strict');let requestId='current',baseline='old';const signature=list=>list.map(d=>String(d.video||'')+'@'+String(d.mtime||'')).join('|');\n"+function+"\nfor(const count of [1,2,3]){const previews=Array.from({length:count},(_,index)=>({video:'clip'+index}));assert.equal(freshRows({request_id:'current',previews}).length,count);assert.equal(freshRows({request_id:'stale',previews}),null)};assert.equal(freshRows({request_id:'current',previews:[]}),null);assert.equal(freshRows({request_id:'current',previews:[{video:'ready'},{video:''}]}),null,'Wait for every expected preview');"
        subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)

    def test_default_moment_and_direct_editor_entry_confirm_alive_selection(self):
        import subprocess
        html=(ROOT/'web/ai_v221_component/index.html').read_text()
        actions=html[html.index('function selectedPayload()'):html.index('function ring(')]
        runtime=(ROOT/'web/gsf_alive_v418.js').read_text()
        script="""const vm=require('node:vm'),assert=require('node:assert/strict');const pure={window:{}};vm.runInNewContext(RUNTIME,pure);const core=pure.window.GSFAlive._core;let fact=core.reduce(core.BASE,'ai.found',{count:1},1000000);const events=[],sent=[];const ctx={state:{selectedMoment:0},rows:()=>[{video:'clip',candidate_id:'first'}],window:{GSFAlive:{state:()=>fact}},alive:(type,data)=>{events.push(type);fact=core.reduce(fact,type,data,1001000)},send:(type,data)=>sent.push(type),stopPlayback(){},renderMoments(){},renderDetail(){},autosave(){}};vm.createContext(ctx);vm.runInContext(ACTIONS,ctx);vm.runInContext('selectMoment(0)',ctx);assert.equal(fact.moment_selected,true,'Clicking the sole/default result must confirm selection');const count=events.length;vm.runInContext('selectMoment(0)',ctx);assert.equal(events.length,count,'The same confirmed card must not repeat guidance');fact=core.reduce(core.BASE,'ai.found',{count:1},1000000);vm.runInContext('editSelectedMoment()',ctx);assert.equal(fact.moment_selected,true,'Direct Editor CTA confirms the displayed moment');assert.deepEqual(sent,['preview','open_editor'],'Keep the existing video handoff');""".replace('RUNTIME',json.dumps(runtime)).replace('ACTIONS',json.dumps(actions))
        subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)

class AliveRouteGeometry(unittest.TestCase):
    def test_ring_tracks_internal_scroll_and_old_voice_never_reappears(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil
        source=(ROOT/'web/gsf_alive_v418.js').read_text()
        child='<html><style>html,body{margin:0;height:100%;overflow:hidden}#scroll{height:100%;overflow:auto}button{display:block;margin:300px 20px 600px;width:150px;height:60px}</style><div id="scroll"><button data-alive-next="upload">Upload</button></div><script>'+source+';GSFAlive.mount({page:"hub"});</script></html>'
        parent='<html><body><script>let target="hub";window.GSFNavigation={snapshot:()=>({target})};window.navigate=t=>{target=t;dispatchEvent(new CustomEvent("gsf:surfacechange"))}</script><iframe style="border:0;width:390px;height:700px"></iframe></body></html>'
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                page=browser.new_page(viewport={'width':390,'height':844})
                page.route('**/*',lambda r:r.fulfill(content_type='text/html',body=parent))
                page.goto('http://gsf.test/');page.locator('iframe').evaluate('(f,html)=>f.srcdoc=html',child)
                frame=page.frame_locator('iframe');frame.locator('#gsf-alive-guide').wait_for()
                frame.locator('#scroll').evaluate('e=>e.scrollTop=100');page.wait_for_timeout(30)
                offset=frame.locator('#gsf-alive-guide').evaluate("e=>e.getBoundingClientRect().top-document.querySelector('button').getBoundingClientRect().top")
                self.assertLess(abs(offset+6),5,'A guide must follow the DOM during scroll, without interpolating old coordinates')
                frame.locator('#scroll').evaluate("()=>GSFAlive.say('Old route message')")
                page.evaluate("navigate('home')")
                self.assertFalse(frame.locator('#gsf-alive-whisper').evaluate("e=>e.classList.contains('on')"),'Suspend must clear voice synchronously')
                page.evaluate("navigate('hub')")
                self.assertFalse(frame.locator('#gsf-alive-whisper').evaluate("e=>e.classList.contains('on')"),'Reopen must not replay old voice')
            finally:browser.close()

class PushBrowserPreference(unittest.TestCase):
    def test_off_never_registers_and_off_survives_reload_with_permission_granted(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil
        from urllib.parse import urlsplit
        ns=companion_functions({'_push_client_bytes'},Path('/tmp'))
        script=ns['_push_client_bytes']().decode();saved={'enabled':False,'revision':0};subscriptions=[]
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                page=browser.new_page()
                page.add_init_script("""window.registrations=0;window.unsubscribed=0;Object.defineProperty(window,'Notification',{value:{permission:'granted'}});window.PushManager={};const sub={toJSON:()=>({endpoint:'https://push.test/sub',keys:{p256dh:'test',auth:'test'}}),unsubscribe:async()=>{window.unsubscribed++;return true}};const reg={pushManager:{getSubscription:async()=>sub}};Object.defineProperty(navigator,'serviceWorker',{value:{register:async()=>{window.registrations++;return reg},getRegistration:async()=>reg}});""")
                def route(request):
                    path=urlsplit(request.request.url).path
                    if path=='/':request.fulfill(content_type='text/html',body='<html><body><script>'+script+'</script></body></html>')
                    elif path=='/push/preferences':
                        if request.request.method=='POST':
                            self.assertEqual(request.request.headers.get('x-gsf-csrf'),'test');saved.update(request.request.post_data_json)
                        request.fulfill(json={'ok':True,**saved,'csrf_token':'test'})
                    elif path=='/push/public-key':request.fulfill(json={'ok':True,'public_key':'dGVzdA'})
                    elif path=='/push/subscribe':subscriptions.append(request.request.post_data_json);request.fulfill(json={'ok':True})
                    else:request.fulfill(json={'ok':True})
                page.route('**/*',route);page.goto('http://gsf.test/')
                self.assertFalse(page.evaluate('GSFPush.ensure()'));self.assertEqual(page.evaluate('registrations'),0)
                page.evaluate("()=>{window.originalRegister=navigator.serviceWorker.register;navigator.serviceWorker.register=async()=>{throw new Error('Push activation failed')}}")
                self.assertEqual(page.evaluate("GSFPush.enable().then(()=>'',e=>e.message)"),'Push activation failed')
                self.assertFalse(saved['enabled'],'Failed activation must not leave a falsely active preference')
                page.evaluate('()=>{navigator.serviceWorker.register=originalRegister}')
                self.assertTrue(page.evaluate('GSFPush.enable()'));self.assertTrue(saved['enabled']);self.assertEqual(len(subscriptions),1)
                self.assertTrue(page.evaluate('GSFPush.disable()'));self.assertFalse(saved['enabled']);self.assertEqual(page.evaluate('unsubscribed'),1)
                self.assertFalse(page.evaluate('GSFPush.ensure()'));page.reload()
                self.assertFalse(page.evaluate('GSFPush.ensure()'));self.assertEqual(page.evaluate('registrations'),0)
                page.evaluate("Notification.permission='denied'")
                self.assertFalse(page.evaluate('GSFPush.enable()'));self.assertFalse(saved['enabled'])
            finally:browser.close()

class PortraitAppContract(unittest.TestCase):
    def test_pwa_requests_portrait_orientation(self):
        ns=companion_functions({'_app_manifest_bytes'},Path('/tmp'))
        self.assertEqual(json.loads(ns['_app_manifest_bytes']())['orientation'],'portrait')

    def test_phone_rotation_preserves_route_and_restores_portrait(self):
        try:from playwright.sync_api import sync_playwright
        except ImportError:self.skipTest('Browser checks run in Production Gate')
        import shutil
        parent=installed_parent_html()
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                context=browser.new_context(**playwright.devices['iPhone 13']);page=context.new_page()
                page.add_init_script("window.testAngle=0;Object.defineProperty(screen,'orientation',{value:{get angle(){return window.testAngle},lock:async()=>{}}})")
                def route(request):
                    if request.request.url=='http://gsf.test/':request.fulfill(content_type='text/html',body=parent)
                    else:request.fulfill(json={'ok':True,'account':{'display_name':'Creator'}})
                page.route('**/*',route);page.goto('http://gsf.test/')
                page.wait_for_function('()=>GSFNavigation?.snapshot().surfaces===5')
                guard=page.locator('#gsf-portrait-guard');guard.wait_for(state='attached',timeout=3000)
                self.assertFalse(guard.is_visible())
                page.evaluate("()=>{window.projectMarker='keep';GSFNavigation.navigate({target:'hub',section:'profile'});window.testAngle=90}")
                page.set_viewport_size({'width':844,'height':390});page.evaluate("dispatchEvent(new Event('orientationchange'))")
                guard.wait_for(state='visible')
                self.assertEqual(page.evaluate('GSFNavigation.snapshot().target'),'hub')
                page.evaluate('window.testAngle=0');page.set_viewport_size({'width':390,'height':844});page.evaluate("dispatchEvent(new Event('orientationchange'))")
                guard.wait_for(state='hidden')
                self.assertEqual(page.evaluate('projectMarker'),'keep')
                self.assertEqual(page.evaluate('GSFNavigation.snapshot().section'),'profile')
                # A virtual keyboard can shrink the viewport without rotating the device.
                page.set_viewport_size({'width':390,'height':300});self.assertFalse(guard.is_visible())
                page.wait_for_function("()=>{const f=document.querySelector('#gsf-creator-hub-live-v160 iframe');return f.contentDocument?.readyState==='complete'&&f.contentWindow.location.pathname.startsWith('/creator-hub-v156')}")
                page.evaluate("()=>{const f=document.querySelector('#gsf-creator-hub-live-v160 iframe'),post=f.contentWindow.postMessage;window.resizeResumeCount=0;f.contentWindow.postMessage=function(data,...args){if(data?.type==='GSF_APP_RESUME')window.resizeResumeCount++;return post.call(this,data,...args)};dispatchEvent(new Event('resize'))}")
                self.assertEqual(page.evaluate('resizeResumeCount'),0,'Ordinary resize must not reset an expanded Editor as a document resume')
            finally:browser.close()

class AliveSubviewGeometry(unittest.TestCase):
    def test_hub_view_change_clears_guidance_for_hidden_controls_immediately(self):
        from playwright.sync_api import sync_playwright
        import shutil
        parent=installed_parent_html();html=(ROOT/'web/creator_hub_v156_component/index.html').read_text()
        with sync_playwright() as p:
            engine=getattr(p,os.environ.get('GSF_BROWSER','chromium'));executable=shutil.which('chromium') if engine.name=='chromium' else None
            browser=engine.launch(**({'executable_path':executable,'args':['--no-sandbox']} if executable else {}))
            try:
                page=browser.new_page(viewport={'width':390,'height':844})
                def route(r):
                    if r.request.url=='http://gsf.test/':r.fulfill(content_type='text/html',body=parent)
                    elif '/creator-hub-v156/' in r.request.url:r.fulfill(content_type='text/html',body=html)
                    else:r.fulfill(json={'ok':True,'csrf_token':'test','account':{'display_name':'Creator'},'social':{},'drafts':[],'shorts':[]})
                page.route('**/*',route);page.goto('http://gsf.test/')
                page.wait_for_function('()=>GSFNavigation?.snapshot().surfaces===5')
                page.evaluate("GSFNavigation.navigate({target:'hub'})")
                hub=page.frame_locator('#gsf-creator-hub-live-v160 iframe')
                hub.locator('#hub').wait_for()
                page.wait_for_function("()=>document.querySelector('#gsf-creator-hub-live-v160 iframe').contentWindow.GSFHubV415?.getState().csrf_token")
                result=hub.locator('#hub').evaluate("""()=>{
                    GSFHubV415.openView('dashboard');GSFAlive.emit('video.cleared');GSFAlive.refresh();
                    const target=[...document.querySelectorAll('[data-alive-next~=upload]')].find(e=>e.getBoundingClientRect().height>0);
                    GSFAlive.say('Scegli un video',{anchor:target});
                    const before=document.querySelector('#gsf-alive-guide').style.display;
                    GSFHubV415.openView('settings');
                    return {before,after:document.querySelector('#gsf-alive-guide').style.display,voice:document.querySelector('#gsf-alive-whisper').classList.contains('on')};
                }""")
                self.assertEqual(result['before'],'block')
                self.assertEqual(result['after'],'none','Hidden dashboard control must immediately lose its guidance ring')
                self.assertFalse(result['voice'],'Guidance for the previous view must disappear with its control')
            finally:browser.close()

class CanonicalIconBuildContract(unittest.TestCase):
    def test_image_build_preserves_the_approved_tracked_icon_bytes(self):
        import shlex,subprocess,sys
        docker=(ROOT/'Dockerfile').read_text()
        line=next(line for line in docker.splitlines() if line.startswith('RUN python -c ') and 'app_icons' in line)
        code=shlex.split(line.split(' && ')[0])[3]
        with tempfile.TemporaryDirectory() as directory:
            icons=Path(directory)
            for path in (ROOT/'web/app_icons').glob('*'):
                if path.is_file():(icons/path.name).write_bytes(path.read_bytes())
            before=(icons/'app-icon.png').read_bytes()
            subprocess.run([sys.executable,'-c',code.replace("'/app/web/app_icons'",repr(directory))],check=True,capture_output=True,text=True)
            self.assertEqual((icons/'app-icon.png').read_bytes(),before,'Build must preserve the approved repository icon')
            self.assertEqual((icons/'apple-touch-icon.png').read_bytes(),before)

class AliveRenderHandoff(unittest.TestCase):
    def test_pending_render_intent_follows_route_before_server_start(self):
        import subprocess,shutil
        if not shutil.which('node'):self.skipTest('Node required')
        source=(ROOT/'web/gsf_alive_v418.js').read_text()
        watch=source[source.index('  let polling = false, probed = false'):source.index('  async function jobStatus()')]
        poll=source[source.index('  async function pollRender()'):source.index('  /* ----- lifecycle ----- */')]
        script="""const vm=require('node:vm'),assert=require('node:assert/strict');const values=new Map();const localStorage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)};function page(){const events=[];const ctx={Date,JSON,localStorage,events,later(){},leader:()=>true,routeGeneration:1,visible:()=>true,state:{active_job:null},jobStatus:async()=>({ok:true,render_status:'running',started_at:Date.now()/1000}),emit:(...args)=>events.push(args)};vm.createContext(ctx);vm.runInContext(SOURCE,ctx);vm.runInContext('probed=true',ctx);return ctx;}(async()=>{const oldPage=page(),newPage=page();vm.runInContext('watchRender()',oldPage);assert.equal(oldPage.events.length,0,'Intent must never fake a running render');await vm.runInContext('pollRender()',newPage);assert.equal(newPage.events[0]?.[0],'render.started','New route must pick up pending render from shared state');values.clear();const waiting=page();vm.runInContext('watchRender()',waiting);let finish;waiting.jobStatus=()=>new Promise(resolve=>finish=resolve);const response=vm.runInContext('pollRender()',waiting);vm.runInContext('watchRender()',waiting);const latest=vm.runInContext('watchFrom',waiting);finish({ok:true,render_status:'running',started_at:Date.now()/1000});await response;assert.equal(JSON.parse(values.get('gsf_alive_render_watch_v418')||'null')?.from,latest,'Old response must preserve newer render intent');assert.ok(vm.runInContext('watchUntil',waiting)>0,'Old response must preserve newer deadline');values.set('gsf_alive_render_watch_v418',JSON.stringify({from:Date.now()-100000,until:Date.now()-10000}));const reload=page();vm.runInContext('probed=false',reload);await vm.runInContext('pollRender()',reload);assert.equal(reload.events[0]?.[0],'render.started','Expired intent must not block detection after reload')})().catch(error=>{console.error(error);process.exitCode=1});""".replace('SOURCE',json.dumps(watch+poll))
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

class MediaCancellationContract(unittest.TestCase):
    def test_only_cancelled_first_party_media_of_suspended_surface_is_expected(self):
        from types import SimpleNamespace
        from visual.gsf_navigation_stress import request_failure_is_critical
        media=SimpleNamespace(resource_type='media',url='http://gsf.test/media/sid/source.mp4',failure='Load request cancelled')
        self.assertFalse(request_failure_is_critical(media,inactive_surface=True,base_url='http://gsf.test'))
        self.assertTrue(request_failure_is_critical(media,inactive_surface=False,base_url='http://gsf.test'))
        alias=SimpleNamespace(**{**vars(media),'url':'http://gsf.test/editor-media/current?na=1'})
        self.assertFalse(request_failure_is_critical(alias,inactive_surface=True,base_url='http://gsf.test'))
        self.assertTrue(request_failure_is_critical(alias,inactive_surface=False,base_url='http://gsf.test'))
        self.assertTrue(request_failure_is_critical(media,inactive_surface=True,base_url='http://different.test'))
        self.assertTrue(request_failure_is_critical(SimpleNamespace(**{**vars(media),'failure':'Connection failed'}),inactive_surface=True,base_url='http://gsf.test'))
        self.assertTrue(request_failure_is_critical(SimpleNamespace(**{**vars(media),'resource_type':'script'}),inactive_surface=True,base_url='http://gsf.test'))

class AlivePollCancellationContract(unittest.TestCase):
    def test_cancelled_poll_requires_observed_signal_and_inactive_surface(self):
        from types import SimpleNamespace
        from visual.gsf_navigation_stress import request_failure_is_critical
        poll=SimpleNamespace(resource_type='fetch',url='http://gsf.test/job/status?alive=1&_=123',failure='Load request cancelled')
        self.assertTrue(request_failure_is_critical(poll,base_url='http://gsf.test'))
        self.assertTrue(request_failure_is_critical(poll,inactive_surface=True,base_url='http://gsf.test'))
        self.assertTrue(request_failure_is_critical(poll,signal_aborted=True,base_url='http://gsf.test'))
        self.assertFalse(request_failure_is_critical(poll,inactive_surface=True,signal_aborted=True,base_url='http://gsf.test'))
        for changed in ({'failure':'Connection failed'},{'url':'http://gsf.test/job/status'},{'url':'http://gsf.test/editor/state'},{'url':'http://other.test/job/status?alive=1'},{'resource_type':'script'}):
            request=SimpleNamespace(**{**vars(poll),**changed})
            self.assertTrue(request_failure_is_critical(request,inactive_surface=True,signal_aborted=True,base_url='http://gsf.test'),changed)

class EditorResumeIdempotence(unittest.TestCase):
    def test_duplicate_resume_preserves_active_fallback_but_real_suspend_stays_mini(self):
        import subprocess,shutil
        if not shutil.which('node'):self.skipTest('Node required')
        source=(ROOT/'web/game_editor_mobile_component/editor.mjs').read_text()
        function=source[source.index('function resumeEditor()'):source.index('document.addEventListener("visibilitychange", () => document.hidden ? suspendEditor()')]
        script="const vm=require('node:vm'),assert=require('node:assert/strict');const states=[];const context={fullscreenFallback:true,document:{fullscreenElement:null},app:{},history:{value:{zoom:1.7}},finishGesture(){},notifyFullscreen:active=>states.push(active),renderState(){}};vm.createContext(context);vm.runInContext(SOURCE,context);vm.runInContext('resumeEditor()',context);assert.equal(states.pop(),true,'Duplicate focus/resume must preserve current fallback fullscreen');context.fullscreenFallback=false;vm.runInContext('resumeEditor()',context);assert.equal(states.pop(),false,'Actual suspension already exited fullscreen and must stay mini');assert.equal(context.history.value.zoom,1.7);".replace('SOURCE',json.dumps(function))
        result=subprocess.run(['node','-e',script],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
