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

    def test_repeated_mobile_and_desktop_sequences(self):
        for mobile in (True,False):
            with self.subTest(mobile=mobile),browser_page(mobile) as (page,errors,_):
                # Warm the finite lazy surfaces before comparing DOM counts.
                for target in ('hub','ai','editor','short','home'):navigate(page,target)
                baseline=metrics(page)
                print('NAV BASELINE',mobile,json.dumps(baseline),flush=True)
                for sequence in SEQUENCES:
                    for cycle in range(10):
                        for target in sequence:
                            navigate(page,target)
                            self.assertFalse(errors,{'target':target,'cycle':cycle,'errors':errors})
                    print('NAV SEQUENCE',mobile,sequence,'passed 10 repetitions',flush=True)
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
            page.evaluate("()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
            self.assertEqual(page.evaluate("()=>window.GSFNavigation.snapshot().target"),'hub')
            self.assertEqual(page.evaluate("()=>window.GSFNavigation.snapshot().section"),'projects')
            assert_gamebar(page)
            self.assertFalse(errors,errors)

    def test_desktop_create_short_exits_editor_route(self):
        with browser_page(False) as (page,errors,_):
            navigate(page,'editor')
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('body').wait_for()
            # Observe the render trigger without performing an expensive render.
            page.evaluate("""()=>{const host=document.createElement('div');host.className='st-key-gsf-major-create-short';const button=document.createElement('button');button.textContent='Render test sink';button.onclick=()=>window.__renderTriggered=true;host.appendChild(button);document.body.appendChild(host)}""")
            frame.locator('body').evaluate("()=>parent.postMessage({type:'streamlit:setComponentValue',value:{zoom:1.3,editorAction:'create_short'}},location.origin)")
            page.wait_for_function('()=>window.__renderTriggered===true')
            self.assertEqual(page.evaluate("()=>window.GSFNavigation.snapshot().target"),'home')
            page.evaluate("()=>window.dispatchEvent(new Event('focus'))")
            self.assertEqual(page.locator('#gsf-editor-overlay-v220').get_attribute('aria-hidden'),'true')
            assert_gamebar(page)

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
            frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState()")
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
