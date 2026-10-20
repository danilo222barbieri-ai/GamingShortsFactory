"""Run with GSF_BASE_URL against the real local image or deployed GSF."""
import os
import json
from pathlib import Path
import unittest
from visual.gsf_navigation_stress import browser_page,navigate,metrics,SEQUENCES,force_fallback_fullscreen,assert_gamebar

@unittest.skipUnless(os.environ.get('GSF_BASE_URL'),'requires running GSF_BASE_URL')
class NavigationStability(unittest.TestCase):
    def test_gamebar_closes_editor_lifecycle(self):
        with browser_page() as (page,errors,_):
            navigate(page,'editor')
            navigate(page,'home')
            self.assertEqual(page.evaluate("()=>sessionStorage.getItem('gsf_editor_overlay_open_v223')"),'0')

    def test_fullscreen_cannot_hide_gamebar_on_another_route(self):
        with browser_page() as (page,errors,_):
            navigate(page,'editor')
            force_fallback_fullscreen(page)
            page.evaluate("()=>window.postMessage({type:'GSF_SHELL_NAV',target:'projects'},location.origin)")
            page.wait_for_function("()=>!document.documentElement.classList.contains('gsf-mobile-editor-fullscreen')")
            assert_gamebar(page)
            self.assertFalse(errors,errors)

    def test_route_abort_preserves_navigation_without_false_alive_network_failure(self):
        from visual.gsf_navigation_stress import request_signal_was_aborted,request_surface_is_inactive
        with browser_page() as (page,errors,_):
            pending=[];cancelled=[]
            # Delay the real request, then release it unchanged after navigation.
            # No response or AbortSignal is fabricated by this regression.
            page.route('**/job/status?alive=1**',lambda route:pending.append(route))
            page.on('requestfailed',lambda request:cancelled.append(request) if '/job/status?alive=1' in request.url else None)
            page.evaluate("()=>{const f=[...document.querySelectorAll('iframe')].find(f=>{try{return f.contentDocument?.querySelector('#home154')&&f.contentWindow.GSFAlive}catch(_){return false}});if(!f)throw new Error('Home Alive missing');f.contentWindow.GSFAlive.watchRender()}")
            for _ in range(100):
                if pending:break
                page.wait_for_timeout(50)
            self.assertTrue(pending,'The real Alive poll must be in flight')
            navigate(page,'editor')
            for route in pending:route.continue_()
            for _ in range(100):
                if cancelled:break
                page.wait_for_timeout(50)
            self.assertTrue(cancelled,'The browser must observe the route cancellation')
            for request in cancelled:
                self.assertTrue(request_signal_was_aborted(request))
                self.assertTrue(request_surface_is_inactive(request))
            self.assertEqual(page.evaluate('GSFNavigation.snapshot().target'),'editor')
            assert_gamebar(page)
            self.assertFalse(errors,errors)

    def test_repeated_mobile_sequences(self):
        # GSF is phone-only (V419): desktop browsers get the mobile-only page instead.
        for mobile in (True,):
            with self.subTest(mobile=mobile),browser_page(mobile) as (page,errors,_):
                # Warm the finite lazy surfaces before comparing DOM counts.
                for target in ('hub','ai','editor','short','home'):navigate(page,target)
                baseline=metrics(page)
                print('NAV BASELINE',mobile,json.dumps(baseline),flush=True)
                cycles=max(2,min(10,int(os.environ.get('GSF_NAV_CYCLES','10'))))
                for sequence in SEQUENCES:
                    for cycle in range(cycles):
                        for target in sequence:
                            print('NAV STEP',sequence,cycle,target,flush=True)
                            navigate(page,target)
                            self.assertFalse(errors,{'target':target,'cycle':cycle,'errors':errors})
                    print('NAV SEQUENCE',mobile,sequence,f'passed {cycles} repetitions',flush=True)
                end=metrics(page)
                print('NAV FINAL',mobile,json.dumps(end),flush=True)
                self.maxDiff=None
                if 'listeners' in baseline:self.assertEqual(end['listeners'],baseline['listeners'])
                for kind in ('mutation','resize'):
                    self.assertLessEqual(end['resources'][kind],baseline['resources'][kind])
                self.assertEqual(end['frames'],baseline['frames'])
                self.assertEqual(end['surfaces'],baseline['surfaces'])
                self.assertLessEqual(end['nodes'],baseline['nodes']+10)

    def test_delayed_editor_close_cannot_override_newer_navigation(self):
        with browser_page() as (page,errors,_):
            navigate(page,'editor')
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('#gameEditorApp').wait_for()
            pending=[]
            page.route('**/editor/state/save',lambda route:pending.append(route))
            frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.requestEditorAction('close')")
            for _ in range(100):
                if pending:break
                page.wait_for_timeout(20)
            self.assertTrue(pending,'Editor must dispatch its save before closing')
            navigate(page,'projects')
            pending[0].fulfill(response=pending[0].fetch())
            frame.locator('#editorStatus').filter(has_text='Salvato').wait_for(state='attached')
            # Two frames, or 250 ms if the headless engine stalls rendering updates.
            page.evaluate("()=>new Promise(resolve=>{requestAnimationFrame(()=>requestAnimationFrame(resolve));setTimeout(resolve,250)})")
            self.assertEqual(page.evaluate("()=>window.GSFNavigation.snapshot().target"),'hub')
            self.assertEqual(page.evaluate("()=>window.GSFNavigation.snapshot().section"),'projects')
            assert_gamebar(page)
            self.assertFalse(errors,errors)

    def test_desktop_gets_mobile_only_page(self):
        # GSF_MOBILE_ONLY_V419: a desktop browser never loads the app, only the gate page.
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            engine=os.environ.get('GSF_BROWSER','chromium')
            opts={'headless':True}
            if engine=='chromium':opts.update(executable_path=os.environ.get('GSF_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
            browser=getattr(p,engine).launch(**opts)
            try:
                page=browser.new_context(viewport={'width':1440,'height':1000}).new_page()
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(os.environ['GSF_BASE_URL'],wait_until='load',timeout=60000)
                self.assertIn('GSF_MOBILE_ONLY_GATE_V419',page.content())
                self.assertEqual(page.locator('[data-testid=stApp]').count(),0)
                self.assertEqual(page.locator('#qr svg').count(),1)
                self.assertFalse(errors,errors)
            finally:
                browser.close()

    def test_editor_bridge_remount_adopts_dirty_state_and_history(self):
        with browser_page() as (page,errors,ctx):
            navigate(page,'editor')
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('#gameEditorApp').wait_for()
            page.route('**/editor/state/save',lambda route:None)
            frame.locator('#gameEditorApp').evaluate("()=>{window.__initCount=0;window.addEventListener('message',e=>{if(e.data?.type==='GSF_GAME_EDITOR_INIT')window.__initCount++});window.GSFGameEditor2026.commitEditorState({zoom:1.4});window.GSFGameEditor2026.commitEditorState({zoom:1.9})}")
            before=frame.locator('#gameEditorApp').evaluate("()=>({state:window.GSFGameEditor2026.getState(),undo:!document.querySelector('#undoButton').disabled,src:document.querySelector('video').src,init:window.__initCount})")
            import ast,re
            app_path=Path(__file__).resolve().parents[1]/'app.py'
            value=next(n.value.value for n in ast.walk(ast.parse(app_path.read_text())) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_GSF_PARENT_EDITOR' for t in n.targets))
            script=re.search(r'<script[^>]*>([\s\S]*?)</script>',value).group(1)
            page.evaluate(script)
            page.wait_for_timeout(150)
            after=frame.locator('#gameEditorApp').evaluate("()=>({state:window.GSFGameEditor2026.getState(),undo:!document.querySelector('#undoButton').disabled,src:document.querySelector('video').src,init:window.__initCount})")
            self.assertEqual(after,before)

    def test_replaced_controller_cannot_apply_old_bootstrap(self):
        with browser_page() as (page,errors,_):
            pending=[]
            page.route('**/editor/state',lambda route:pending.append(route))
            navigate(page,'editor',ready=False)
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('#gameEditorApp').wait_for()
            page.wait_for_function("()=>!!document.querySelector('#gsf-editor-overlay-v220 iframe').contentWindow.GSFGameEditor2026")
            for _ in range(100):
                if pending:break
                page.wait_for_timeout(20)
            self.assertTrue(pending)
            frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.commitEditorState({zoom:1.9})")
            import ast,re
            app=Path(__file__).resolve().parents[1]/'app.py'
            value=next(n.value.value for n in ast.walk(ast.parse(app.read_text())) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_GSF_PARENT_EDITOR' for t in n.targets))
            page.evaluate(re.search(r'<script[^>]*>([\s\S]*?)</script>',value).group(1))
            # Controlled obsolete bootstrap response; the new controller must ignore it.
            pending[0].fulfill(status=200,json={'ok':True,'video_url':'','initial_state':{'zoom':1.2,'sourceDuration':15}})
            page.wait_for_timeout(150)
            self.assertEqual(frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState().zoom"),1.9)

    def test_streamlit_rerun_preserves_editor_and_history(self):
        with browser_page() as (page,errors,_):
            navigate(page,'editor')
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('#gameEditorApp').evaluate("()=>{window.GSFGameEditor2026.commitEditorState({zoom:1.4});window.GSFGameEditor2026.commitEditorState({zoom:1.9})}")
            page.evaluate("""()=>{
                const app=document.querySelector('[data-testid="stApp"]');
                if(!app)throw new Error('Streamlit app missing');
                const host=document.querySelector('#gsf-editor-overlay-v220'),frame=host.querySelector('iframe');
                window.__gsfEditorIdentity={host,frame,doc:frame.contentDocument};
                window.__gsfRerunComplete=false;
                let running=false;
                const observer=new MutationObserver(()=>{
                    const state=app.getAttribute('data-test-script-state');
                    if(state==='running')running=true;
                    if(running&&state==='notRunning'){window.__gsfRerunComplete=true;observer.disconnect();}
                });
                observer.observe(app,{attributes:true,attributeFilter:['data-test-script-state']});
                const button=document.querySelector('.st-key-gsf_final_ready_sync_v111 button');
                if(!button)throw new Error('Streamlit rerun control missing');
                button.click();
            }""")
            page.wait_for_function('()=>window.__gsfRerunComplete',timeout=30000)
            self.assertTrue(page.evaluate("()=>{const old=window.__gsfEditorIdentity,host=document.querySelector('#gsf-editor-overlay-v220'),frame=host.querySelector('iframe');return old.host===host&&old.frame===frame&&old.doc===frame.contentDocument}"))
            self.assertAlmostEqual(frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState().zoom"),1.9)
            frame.locator('#undoButton').evaluate("b=>b.click()")
            self.assertAlmostEqual(frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState().zoom"),1.4)
            assert_gamebar(page)
            self.assertFalse(errors,errors)

class ParentBundleContract(unittest.TestCase):
    def test_retired_preview_decodes_replacement_before_cancellation_is_accepted(self):
        from urllib.parse import urlsplit,parse_qs
        from types import SimpleNamespace
        from visual.gsf_navigation_stress import MEDIA_FIXTURE,INSTRUMENT,install_request_ownership,request_media_has_playable_replacement,request_surface_is_inactive,request_failure_is_critical
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            if os.environ.get('GSF_BROWSER'):raise
            self.skipTest('Playwright runs in the blocking WebKit gate')
        with sync_playwright() as playwright:
            engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'))
            options={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']} if engine.name=='chromium' else {}
            browser=engine.launch(**options)
            try:
                page=browser.new_page();held=[];failed=[]
                page.add_init_script(INSTRUMENT);install_request_ownership(page)
                def serve(route):
                    url=urlsplit(route.request.url)
                    if url.path=='/':route.fulfill(content_type='text/html',body="<iframe src='/frame?gen=1'></iframe>")
                    elif url.path=='/away':route.fulfill(content_type='text/html',body='<p>Left the app</p>')
                    elif url.path=='/frame':
                        gen=parse_qs(url.query)['gen'][0]
                        route.fulfill(content_type='text/html',body=f"<div id='home154'><div id='circle'><div class='naPreview'><video muted autoplay preload='auto' src='/editor-media/current?na={gen}'></video></div></div></div>")
                    elif parse_qs(url.query).get('na')==['1']:held.append(route)
                    else:route.fulfill(content_type='video/mp4',body=MEDIA_FIXTURE)
                page.route('**/*',serve)
                page.on('requestfailed',lambda request:failed.append(request))
                page.goto('http://gsf.test/',wait_until='domcontentloaded')
                for _ in range(100):
                    if held:break
                    page.wait_for_timeout(30)
                self.assertTrue(held)
                page.evaluate("document.querySelector('iframe').src='/frame?gen=2'")
                page.wait_for_function("()=>document.querySelector('iframe').contentDocument?.querySelector('video')?.readyState>=2",polling=50)
                for route in held:route.continue_()
                held.clear()
                for _ in range(100):
                    if failed:break
                    page.wait_for_timeout(30)
                self.assertTrue(failed,'Browser must cancel the actual retired media request')
                request=failed[0]
                self.assertTrue(request_media_has_playable_replacement(request,'http://gsf.test'),(request.url,request.resource_type,request.failure))
                self.assertTrue(request_surface_is_inactive(request),'A reused Frame must preserve retirement of the old media document')
                self.assertFalse(request_media_has_playable_replacement(request,'http://other.test'))
                broken=SimpleNamespace(url=request.url,resource_type='media',failure='Connection failed')
                self.assertFalse(request_media_has_playable_replacement(broken,'http://gsf.test'))
                # An active source cancellation and an undecodable replacement remain errors.
                video=page.frame_locator('iframe').locator('video')
                video.evaluate("(v,url)=>{v.src=url;v.load()}",request.url)
                for _ in range(100):
                    if held:break
                    page.wait_for_timeout(20)
                self.assertTrue(held)
                self.assertFalse(request_surface_is_inactive(held[-1].request),'New active media must not inherit a retired document')
                video.evaluate("()=>history.pushState({},'',location.pathname+location.search+'#same-document')")
                self.assertFalse(request_surface_is_inactive(held[-1].request),'pushState must not retire the current video document')
                self.assertFalse(request_media_has_playable_replacement(request,'http://gsf.test'))
                video.evaluate("v=>{v.src='/editor-media/current?na=3';v.load();v.removeAttribute('src');v.load()}")
                for route in held:route.continue_()
                held.clear()
                self.assertFalse(request_media_has_playable_replacement(request,'http://gsf.test'))
                # Leaving the document retires its Frame even if WebKit calls media "other".
                page.goto('http://gsf.test/away',wait_until='domcontentloaded')
                self.assertTrue(request_surface_is_inactive(request))
                self.assertFalse(request_failure_is_critical(request,inactive_surface=request_surface_is_inactive(request),base_url='http://gsf.test'))
            finally:
                browser.close()

    def test_only_cancelled_external_font_requests_are_noncritical(self):
        from types import SimpleNamespace
        from visual.gsf_navigation_stress import request_failure_is_critical
        def request(url,kind='font',failure='Load request cancelled'):
            return SimpleNamespace(url=url,resource_type=kind,failure=failure)
        self.assertFalse(request_failure_is_critical(request('https://fonts.gstatic.com/s/caveat/font.woff2')))
        self.assertTrue(request_failure_is_critical(request('https://gsf.test/fonts/font.woff2')))
        self.assertTrue(request_failure_is_critical(request('https://fonts.gstatic.com/app.js','script')))
        self.assertTrue(request_failure_is_critical(request('https://fonts.gstatic.com/s/font.woff2',failure='Connection failed')))
        self.assertTrue(request_failure_is_critical(request('https://fonts.gstatic.com.attacker.test/font.woff2')))

    def test_completed_timeouts_release_abort_handlers(self):
        import subprocess
        root=Path(__file__).resolve().parents[1]
        program=r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const document={getElementById:()=>null,querySelectorAll:()=>[],addEventListener(){},documentElement:{classList:{toggle(){},remove(){}}}};
const window={WebSocket:class{},addEventListener(){}};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window,document,location:{href:'http://localhost/',origin:'http://localhost'},innerWidth:390,sessionStorage:{setItem(){}},URL,AbortController,MutationObserver:class{},setTimeout,clearTimeout});
const bridge=window.GSFNavigation.bridge('timer-contract',null),signal=bridge.signal;
let retained=0;const add=signal.addEventListener.bind(signal),remove=signal.removeEventListener.bind(signal);
signal.addEventListener=(type,...args)=>{if(type==='abort')retained++;return add(type,...args)};
signal.removeEventListener=(type,...args)=>{if(type==='abort')retained--;return remove(type,...args)};
let called=0;for(let i=0;i<100;i++)bridge.timeout(()=>called++,0);
setTimeout(()=>{assert.equal(called,100);assert.equal(retained,0,'completed timeouts retain abort handlers');bridge.timeout(()=>{throw Error('cancelled callback ran')},30);window.GSFNavigation.bridge('timer-contract',null);},10);
"""
        result=subprocess.run(['node','-e',program,str(root/'web/gsf_navigation_lifecycle.js')],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_parent_bundle_is_complete_parseable_and_idempotent(self):
        import re,subprocess,sys,tempfile,types,runpy
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            package=Path(temporary)/'streamlit'
            (package/'static').mkdir(parents=True)
            index=package/'static/index.html'
            index.write_text('<html><head></head><body><div id="root"></div></body></html>')
            stub=types.ModuleType('streamlit');stub.__file__=str(package/'__init__.py')
            previous=sys.modules.get('streamlit')
            sys.modules['streamlit']=stub
            sys.path.insert(0,str(root/'web'))
            try:
                runpy.run_path(str(root/'web/install_adsense_bridge.py'))
                first=index.read_text()
                try:runpy.run_path(str(root/'web/install_adsense_bridge.py'))
                except SystemExit as error:self.assertEqual(error.code,0)
                self.assertEqual(index.read_text(),first)
            finally:
                sys.path.pop(0)
                if previous is None:sys.modules.pop('streamlit',None)
                else:sys.modules['streamlit']=previous
            self.assertEqual(first.count('id="gsf-navigation-lifecycle"'),1)
            for key in ('editor','ai','social','notifications','footer348','footer350','footer351'):
                self.assertIn("GSFNavigation.bridge('"+key+"'",first)
            script=re.search(r'<script id="gsf-navigation-lifecycle">([\s\S]*?)</script>',first).group(1)
            javascript=Path(temporary)/'parent.js';javascript.write_text(script)
            result=subprocess.run(['node','--check',str(javascript)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            # The production bootstrap runs before Streamlit supplies any CSS.
            # Surface geometry must survive a cold route and React replacement.
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                return  # Fast contracts lack browsers; Production Gate runs WebKit.
            import shutil
            with sync_playwright() as playwright:
                engine=getattr(playwright,os.environ.get('GSF_BROWSER','chromium'))
                executable=shutil.which('chromium') if engine.name=='chromium' else None
                options={'executable_path':executable,'args':['--no-sandbox']} if executable else {}
                browser=engine.launch(**options)
                page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
                page.route('**/*',lambda route:route.fulfill(status=200,json={'ok':False}))
                page.set_content(first)
                page.evaluate("GSFNavigation.navigate({target:'editor'})")
                frame=page.locator('#gsf-editor-overlay-v220 iframe')
                # Measure after finite opening animations, retaining the cold-size assertions.
                frame.evaluate("""async el=>{for(let node=el;node;node=node.parentElement){await Promise.all(node.getAnimations().filter(a=>Number.isFinite(a.effect.getTiming().iterations)).map(a=>a.finished.catch(()=>{})))}}""")
                rect=frame.bounding_box()
                self.assertGreaterEqual(rect['width'],375,'Cold Editor uses browser-default iframe width')
                self.assertGreaterEqual(rect['height'],600,'Cold Editor loses its persistent shell stylesheet')
                self.assertEqual(frame.evaluate("e=>getComputedStyle(e).borderTopWidth"),'0px')
                self.assertEqual(page.locator('.editor-note.left').evaluate("e=>getComputedStyle(e).display"),'none')
                browser.close()

    @unittest.skipUnless(os.environ.get('GSF_BASE_URL'),'requires running GSF_BASE_URL')
    def test_explicit_draft_resume_reinitializes_same_gameplay(self):
        with browser_page() as (page,errors,_):
            calls=[]
            def metadata(route):
                calls.append(True)
                route.fulfill(status=200,json={'ok':True,'ready':False,'video_url':'','initial_state':{'zoom':1.2 if len(calls)==1 else 2.0,'sourceDuration':15}})
            page.route('**/editor/state',metadata)
            # This metadata contract intentionally supplies no media.
            navigate(page,'editor',ready=False)
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('#gameEditorApp').wait_for()
            # The HTML shell can appear before its deferred editor module is ready.
            page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentWindow.GSFGameEditor2026?.getState().zoom===1.2")
            navigate(page,'home')
            page.evaluate("()=>window.postMessage({type:'GSF_SHELL_NAV',target:'editor',resume:true,draft_id:'different-draft'},location.origin)")
            page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentWindow.GSFGameEditor2026?.getState().zoom===2.0")
            assert_gamebar(page)


def test_crea_short_opens_the_canonical_page_and_starts_the_render():
    ROOT = Path(__file__).resolve().parents[1]
    lifecycle = (ROOT / "web/gsf_navigation_lifecycle.js").read_text()
    app = (ROOT / "app.py").read_text()
    share = (ROOT / "web/share_v156_component/index.html").read_text()
    # "short" is an alias of the canonical Crea Short page, never the legacy V343 box.
    assert "if (target==='short') return {target:'social',section:'',createShort:true,requestedAt:Date.now()};" in lifecycle
    # The social surface starts the render once per request when no final Short is ready.
    assert "if(data.createShort)startShortIfNeeded(Number(data.requestedAt)||0)" in app
    assert "if(!requestedAt||requestedAt===lastShortRequest)return;" in app
    assert "fetch('/share/state'" in app
    # The page shows why nothing is rendering yet.
    assert "e.data.type!=='GSF_SHARE_NOTICE'" in share
    assert "sub=shortNotice||'Lo Short finale sta arrivando'" in share


class InspectorCancellationAttribution(unittest.TestCase):
    def test_only_unique_owned_retired_monitor_cancellation_explains_inspector_error(self):
        from visual.gsf_navigation_stress import inspector_error_is_owned_monitor_cancel
        base='https://gsf.test';url=base+'/job/status'
        error={'at':100,'message':'/gsf.test/job/status due to access control checks.',
               'stack':'Fetch API cannot load '+url+' due to access control checks.\n    at unknown (web-inspector://bootstrap.js:371:27)\n    at unknown ('+base+'/gsf-push.js?v=3:117:26)'}
        failed={'at':100.434,'url':url,'failure':'Load request cancelled','resource_type':'fetch',
                'owner':'document:request11','aborted':True,'inactive':True}
        self.assertTrue(inspector_error_is_owned_monitor_cancel(error,[failed],base))
        for key,value in (('owner',None),('aborted',False),('inactive',False),('resource_type','script'),
                          ('failure','Access control check failed'),('url','https://other.test/job/status'),('at',102)):
            with self.subTest(key=key):
                self.assertFalse(inspector_error_is_owned_monitor_cancel(error,[{**failed,key:value}],base))
        self.assertFalse(inspector_error_is_owned_monitor_cancel(error,[],base))
        self.assertFalse(inspector_error_is_owned_monitor_cancel(error,[failed,failed],base),'Ambiguous concurrent requests must fail closed')
        self.assertFalse(inspector_error_is_owned_monitor_cancel(error,[failed,{**failed,'failure':'Connection failed'}],base))
        for stack in (error['stack'].replace('web-inspector://bootstrap.js','https://gsf.test/app.js'),error['stack'].replace('/gsf-push.js','/other.js'),error['stack'].replace(url,base+'/upload')):
            self.assertFalse(inspector_error_is_owned_monitor_cancel({**error,'stack':stack},[failed],base))
        self.assertFalse(inspector_error_is_owned_monitor_cancel({**error,'message':'Uncaught TypeError'},[failed],base))


class FetchSuspensionDelivery(unittest.TestCase):
    def test_owned_fetch_suspension_proof_may_arrive_after_failure_event(self):
        from types import SimpleNamespace
        from visual.gsf_navigation_stress import request_surface_is_inactive
        proof=set()
        frame=SimpleNamespace(is_detached=lambda:False,evaluate=lambda _:False)
        frame.page=SimpleNamespace(wait_for_timeout=lambda _:proof.add('departing-request'))
        request=SimpleNamespace(resource_type='fetch',failure='Load request cancelled',frame=frame,
                                _gsf_fetch_owner=('departing-request',proof))
        self.assertTrue(request_surface_is_inactive(request),'Read the actual delayed lifecycle binding rather than sampling once')
        active=set()
        frame.page=SimpleNamespace(wait_for_timeout=lambda _:None)
        request._gsf_fetch_owner=('active-request',active)
        self.assertFalse(request_surface_is_inactive(request),'Waiting cannot invent suspension evidence for an active request')
