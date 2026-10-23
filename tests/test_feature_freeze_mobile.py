from pathlib import Path

# Release regression contract: these four assertions and the synced Alive runtime must stay green through Railway promotion.
ROOT = Path(__file__).resolve().parents[1]


def test_short_source_uses_full_available_duration_without_entering_long_ai_wait():
    from web.ai_engines_v412 import effective_analysis_duration

    assert effective_analysis_duration(9.0, 15.0) == 9.0
    assert effective_analysis_duration(18.0, 30.0) == 18.0
    assert effective_analysis_duration(42.0, 60.0) == 42.0
    assert effective_analysis_duration(90.0, 60.0) == 60.0
    assert effective_analysis_duration(4.9, 15.0) == 4.9

    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "effective_analysis_duration" in app
    assert "_gsf_effective_analysis_duration" in app


def test_oauth_callbacks_return_to_the_canonical_creator_hub_shell():
    server = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
    nav = (ROOT / "web/gsf_navigation_lifecycle.js").read_text(encoding="utf-8")

    assert 'target="/?gsf_page=hub&gsf_section=social"' in server
    assert "oauth_return" in server
    assert "GSF_OAUTH_CANONICAL_RETURN" in nav
    assert "q.has('oauth_return')" in nav


def test_mobile_home_uses_nested_frame_height_after_shell_is_ready():
    home = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")
    assert "GSF_HOME_NESTED_VIEWPORT_FIX" in home
    assert "html.gsf-v343-parent-ready #home154" in home
    assert "height:100%!important" in home
    assert "min-height:100%!important" in home
    assert "max-height:100%!important" in home


def test_alive_notification_pill_cannot_expand_over_the_phone_ui():
    alive = (ROOT / "web/gsf_alive_v418.js").read_text(encoding="utf-8")
    assert "GSF_ALIVE_COMPACT_PILL" in alive
    assert "max-width:min(78vw,320px)" in alive
    assert "text-overflow:ellipsis" in alive
    assert "overflow:hidden" in alive


"""Feature-freeze regressions: real canonical JS/CSS, controlled provider transport."""
import ast
import json
import os
import unittest
from pathlib import Path
from unittest.mock import Mock
from web import ai_engines_v412 as ai

ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = [(375, 667), (390, 844), (393, 852), (430, 932)]

def literal_function(path, name):
    node = next(n for n in ast.parse((ROOT/path).read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), ns)
    return ns[name]()

class WholeSource(unittest.TestCase):
    def test_actual_app_request_publishes_candidate_before_full_analysis(self):
        import tempfile, textwrap, time
        from contextlib import nullcontext
        class State(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
        source_code=(ROOT/'app.py').read_text(encoding='utf-8')
        marker='        from web.ai_engines_v412 import whole_source_meta'
        start=source_code.index(marker) if marker in source_code else source_code.index('        if _gsf_create_ai_clicked:\n            try:\n                _gsf_analysis_source_duration=')
        end=source_code.index('        if st.session_state.get("auto_clip_modalita") != modalita:',start)
        code=compile(textwrap.dedent(source_code[start:end]),'<actual-app-ai-request>','exec')
        for source,requested in [(9,15),(18,30),(42,60),(3,15)]:
            for failed in (False,True):
                with self.subTest(source=source,failed=failed),tempfile.TemporaryDirectory() as folder:
                    root=Path(folder);video=root/'source.mp4';video.write_bytes(b'controlled transport')
                    state=State(gsf_v412_request_id='request')
                    def scan(*args,**kwargs):
                        meta=ai.read_results_meta(root)
                        self.assertEqual(meta['status'],'analyzing','Candidate must exist before AI starts')
                        self.assertEqual(meta['items'][0]['end_time'],source)
                        if failed:raise RuntimeError('provider failure')
                        return {'meta':{},'motion':[1],'audio':[1]},False
                    scanner=Mock(side_effect=scan);ranker=Mock(return_value=([(0.0,0.0)],{'__event_map__':[{'type':'reaction'}],'__brain_v112__':{'selected':[{'start':0}]}}))
                    voice=Mock(return_value=((.5,.7,'reaction',{'type':'victory'}),False))
                    st=Mock(session_state=state);st.spinner.side_effect=lambda *a:nullcontext()
                    ns=dict(st=st,Path=Path,time=time,durata_video=lambda p:source,duration=requested,
                        _source_path=video,GSF_SESSION_ROOT=root,GSF_PREVIEW_DIR=root,_gsf_create_ai_clicked=True,
                        _gsf_media_url=lambda p:'/media/'+p,_gsf_media_relative=lambda p:p.name,
                        _gsf_session_tempdir=lambda prefix:tempfile.TemporaryDirectory(),
                        _gsf_save_persistent_state=lambda:None,_video_cache_token='source',modalita='action',
                        _gsf_v291_profile='action',GSF_AI_ENGINE_VERSION='test',_gsf_ai_rank_v3=ranker,
                        _gsf_ai_scan_cached=scanner,_gsf_ai_voice_cached=voice)
                    exec(code,ns)
                    scanner.assert_called_once()
                    if failed:ranker.assert_not_called()
                    else:ranker.assert_called_once_with(str(video),'action',clip_duration=source,numero_clip=1,cache_token='source')
                    if not failed:voice.assert_called_once_with(str(video),0.0,float(source),cache_token='source',force=True)
                    final=ai.read_results_meta(root)
                    self.assertEqual(final['status'],'failed' if failed else 'success')
                    self.assertEqual(state.auto_clip_candidati,[0.0])
                    self.assertEqual(state.clip_rifinite,{0.0:source})

    def test_actual_app_duration_bridge_preserves_sixty_seconds(self):
        tree=ast.parse((ROOT/'app.py').read_text(encoding='utf-8'))
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test).startswith('_gsf_v291_profile in'))
        class State(dict):
            __getattr__=dict.get
        st=Mock(session_state=State(gsf_v291_requested_duration=60))
        ns={'st':st,'_gsf_v291_profile':'auto'}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-duration-bridge>','exec'),ns)
        self.assertEqual(ns['duration'],60)

    def test_actual_home_editor_bridge_uses_candidate_length(self):
        import subprocess
        html=(ROOT/'web/home_v154_component/index.html').read_text(encoding='utf-8')
        start=html.index('   if(action==="open_editor"){')
        end=html.index('   if(action==="create_short"){',start)
        script="""const vm=require('node:vm'),assert=require('node:assert/strict');
        for(const [source,requested] of [[9,15],[18,30],[42,60]]){
          let opened;const context={action:'open_editor',e:{data:{index:0,video:'/media/source.mp4',start_time:0,end_time:source}},previewData:[],duration:requested,engine:'auto',shellNav:(target,data)=>opened={target,...data},value:()=>{}};
          vm.runInNewContext('(()=>{'+SOURCE+'})()',context);
          assert.equal(opened.duration,source);assert.equal(opened.start_time,0);assert.equal(opened.video_url,'/media/source.mp4');
        }""".replace('SOURCE',json.dumps(html[start:end]))
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_short_sources_keep_whole_candidate_and_full_analysis(self):
        for source, requested in [(9,15), (18,30), (42,60), (3,15)]:
            with self.subTest(source=source, requested=requested):
                scan = Mock(return_value=({'meta': {'semantic': 'full-video'}, 'motion': [1]}, False))
                rank = Mock(return_value=([(0.0,0.0)],{'__event_map__':[{'type':'reaction'}],'__brain_v112__':{'selected':[{'start':0}]}}))
                result, diagnostics = ai.run_duration_analysis('source.mp4', 'auto', requested,
                    source_duration=source, rank=rank, scan=scan, cache_token='source')
                scan.assert_called_once_with('source.mp4', cache_token='source')
                rank.assert_called_once_with('source.mp4','auto',clip_duration=source,numero_clip=1,cache_token='source')
                self.assertEqual(result, [(0.0, 0.0)])
                self.assertTrue(diagnostics['__whole_source__'])
                self.assertEqual(diagnostics['__event_map__'],[{'type':'reaction'}])
                self.assertTrue(diagnostics['__brain_v112__']['selected'])
                meta = ai.whole_source_meta(source, requested, request_id='current', video_url='/media/source.mp4')
                payload = ai.merge_results(meta, [], lambda p: '/media/'+p)
                self.assertEqual(payload['status'], 'analyzing')
                self.assertEqual(payload['previews'][0]['video'], '/media/source.mp4')
                self.assertEqual(payload['previews'][0]['end_time'], source)
                self.assertEqual(payload['previews'][0]['label'], 'Il tuo video è già pronto')

    def test_long_and_equal_sources_still_use_normal_ranker(self):
        for source, requested in [(15,15), (30,15), (30,30), (60,60), (90,60)]:
            with self.subTest(source=source, requested=requested):
                rank = Mock(return_value=([(0.8, 4)], {'normal': True})); scan = Mock()
                result = ai.run_duration_analysis('source.mp4', 'action', requested,
                    source_duration=source, rank=rank, scan=scan, cache_token='video')
                self.assertEqual(result, rank.return_value)
                rank.assert_called_once_with('source.mp4','action',clip_duration=requested,numero_clip=3,cache_token='video')
                scan.assert_not_called()
                self.assertIsNone(ai.whole_source_meta(source, requested, request_id='id', video_url='/media/source'))

    def test_analysis_failure_is_not_swallowed_or_replaced_by_success(self):
        with self.assertRaisesRegex(RuntimeError, 'provider failure'):
            ai.run_duration_analysis('source.mp4','auto',15,source_duration=9,
                rank=Mock(),scan=Mock(side_effect=RuntimeError('provider failure')))

    def test_scan_error_metadata_is_an_error_not_ai_success(self):
        for key in ('audio_error','video_error'):
            with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,'Analisi'):
                ai.run_duration_analysis('source.mp4','auto',15,source_duration=9,
                    rank=Mock(),scan=Mock(return_value=({'audio':[0],'motion':[0],'meta':{key:'timeout'}},False)))

    def test_abandoned_pending_job_returns_explicit_timeout(self):
        import time
        for whole in (False,True):
            meta=ai.whole_source_meta(9,15,request_id='current',video_url='/media/source.mp4') if whole else {'items':[],'request_id':'current','status':'analyzing'}
            meta['updated_at']=time.time()-121
            result=ai.merge_results(meta,[],lambda p:'/media/'+p)
            self.assertEqual(result['status'],'failed')
            self.assertIn('tempo',result['error'])
            self.assertEqual(result['request_id'],'current')
            self.assertEqual(len(result['previews']),int(whole))

    def test_actual_ranker_analyzes_whole_window_even_below_five_seconds(self):
        import time
        tree=ast.parse((ROOT/'app.py').read_text(encoding='utf-8'))
        rank=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_ai_rank_v3')
        for duration in (3,9,18,42):
            with self.subTest(duration=duration):
                scan={'step':.5,'meta':{},'audio':[.5]*int(duration*2),'motion':[.5]*int(duration*2)}
                def features(scan,start,window):
                    self.assertEqual(start,0)
                    self.assertEqual(window,duration,'Analyze the actual source window, never a longer segment')
                    raise RuntimeError('window reached')
                ns={'time':time,'_gsf_profile_from_mode':lambda m:'auto','_gsf_ai_scan_cached':lambda *a,**k:(scan,False),'_gsf_ai_window_features':features}
                exec(compile(ast.Module(body=[rank],type_ignores=[]),'<actual-whole-window-ranker>','exec'),ns)
                with self.assertRaisesRegex(RuntimeError,'window reached'):ns['_gsf_ai_rank_v3']('source.mp4','auto',duration)

    def test_actual_scan_records_decoder_failure_but_accepts_absent_audio(self):
        import math,re,time,subprocess
        from concurrent.futures import ThreadPoolExecutor
        tree=ast.parse((ROOT/'app.py').read_text(encoding='utf-8'))
        scan=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_ai_scan_base')
        for failed_stream,has_audio in [('video',True),('audio',True),('audio',False)]:
            with self.subTest(stream=failed_stream,has_audio=has_audio):
                def capture(cmd,**kwargs):
                    stream='audio' if '-vn' in cmd else 'video'
                    return subprocess.CompletedProcess(cmd,1 if stream==failed_stream else 0,'','decoder unavailable')
                ns=dict(math=math,re=re,time=time,ThreadPoolExecutor=ThreadPoolExecutor,
                    subprocess=Mock(run=Mock(side_effect=capture)),durata_video=lambda p:9,
                    _gsf_ai_scan_profile_for_duration=lambda n:dict(video_fps=2,analysis_width=144,tier='short',adaptive=False),
                    _gsf_source_has_audio=lambda p:has_audio,FFMPEG_PATH='ffmpeg',
                    _gsf_interpolate_motion_points=lambda p,n:[0]*n,_gsf_norm_series=lambda p:p)
                exec(compile(ast.Module(body=[scan],type_ignores=[]),'<actual-full-scan>','exec'),ns)
                result=ns['_gsf_ai_scan_base']('source.mp4')
                self.assertEqual(bool(result['meta'][failed_stream+'_error']),failed_stream=='video' or has_audio)

@unittest.skipUnless(os.environ.get('GSF_BROWSER'), 'Set GSF_BROWSER for mobile browser regressions')
class Mobile(unittest.TestCase):
    def setUp(self):
        from playwright.sync_api import sync_playwright
        self.p = sync_playwright().start(); self.addCleanup(self.p.stop)
        self.browser = getattr(self.p, os.environ['GSF_BROWSER']).launch(headless=True)
        self.addCleanup(self.browser.close)

    def page(self, width, height):
        page = self.browser.new_page(viewport={'width':width,'height':height})
        self.addCleanup(page.close)
        return page

    def test_whole_source_is_immediately_editable_while_ai_runs(self):
        html = (ROOT/'web/ai_v221_component/index.html').read_text(encoding='utf-8')
        for width,height in VIEWPORTS:
            for source,requested in [(9,15),(18,30),(42,60)]:
                with self.subTest(viewport=width, source=source):
                    page = self.page(width,height)
                    page.add_init_script("window.messages=[];addEventListener('message',e=>{if(e.data?.type==='GSF_AI_UI')messages.push(e.data)})")
                    stage = {'status':'analyzing'}
                    def route(r):
                        if '/ai/results' in r.request.url:
                            req = page.evaluate("messages.findLast(x=>x.action==='create')?.request_id||''")
                            row = {'index':0,'start_time':0,'end_time':source,'video':'/media/source.mp4','whole_source':True,'label':'Il tuo video è già pronto','why':f'Dura {source} s, quindi non serve cercare un segmento da {requested} s.'}
                            r.fulfill(json={'ok':True,'request_id':req,'status':stage['status'],'whole_source':True,'previews':[row] if req else [],'error':'Analisi non riuscita' if stage['status']=='failed' else ''})
                        elif '/media/' in r.request.url: r.fulfill(status=204)
                        else: r.fulfill(content_type='text/html',body=html)
                    page.route('**/*',route); page.goto('http://gsf.test/')
                    page.evaluate('(duration)=>postMessage({type:"GSF_AI_STATE",state:{loaded:true,duration}},location.origin)',requested)
                    page.locator('#createAi').click()
                    page.locator('#editMoment').wait_for(state='visible',timeout=4000)
                    self.assertTrue(page.locator('#editMoment').is_enabled())
                    self.assertIn('Il tuo video è già pronto', page.locator('#detailTitle').inner_text())
                    self.assertIn(str(source)+' s',page.locator('#detailWhy').inner_text())
                    stage['status']='failed'
                    page.wait_for_function("document.querySelector('#detailWhy').textContent.includes('Analisi non riuscita')",timeout=5000)
                    page.locator('#editMoment').click()
                    page.wait_for_function("messages.some(x=>x.action==='open_editor'&&x.end_time===SOURCE)".replace('SOURCE',str(source)))

    def test_notification_pill_has_no_layout_shift_or_duplicate_alive(self):
        code=literal_function('web/direct_upload_server.py','_push_client_bytes').decode()
        for width,height in VIEWPORTS:
            with self.subTest(width=width):
                page=self.page(width,height)
                page.route('**/*',lambda r:r.fulfill(json={'ok':True,'render_status':'idle'}))
                page.goto('http://gsf.test/')
                page.set_content('<header id="gsf-global-header" style="height:44px"></header><main id="content" style="height:400px">Gameplay</main><nav id="gsf-global-gamebar" style="position:fixed;bottom:10px;height:66px"></nav>')
                before=page.locator('#content').bounding_box();page.evaluate(code)
                page.evaluate("()=>{const s={last:'ai.started',active_job:'ai',message:'IA · Analizzo il gameplay…',seq:1,updated:1};GSFNotify.alive(s);GSFNotify.alive(s)}")
                self.assertEqual(page.locator('.gsf-site-toast').count(),1)
                self.assertLessEqual(page.locator('.gsf-site-toast').bounding_box()['height'],40)
                self.assertEqual(page.locator('#content').bounding_box(),before)
                pill=page.locator('.gsf-site-toast').bounding_box()
                header=page.locator('#gsf-global-header').bounding_box()
                self.assertLessEqual(pill['y']+pill['height'],header['y']+header['height'])

    def test_oauth_keeps_parent_shell_and_returns_to_social(self):
        hub=(ROOT/'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
        navigation=(ROOT/'web/gsf_navigation_lifecycle.js').read_text(encoding='utf-8')
        for width,height in VIEWPORTS:
            with self.subTest(width=width):
                page=self.page(width,height)
                def route(r):
                    path=r.request.url
                    if '/creator-hub/state' in path:r.fulfill(json={'ok':True,'social':{},'account':{}})
                    elif '/creator-hub-v156/' in path:r.fulfill(content_type='text/html',body=hub)
                    elif '/social-connect/' in path:r.fulfill(content_type='text/html',body="<script>location.replace('/?gsf_hub=social&oauth_return=1')</script>")
                    elif 'oauth_return=' in path:r.fulfill(content_type='text/html',body='<script>'+navigation+'</script>')
                    elif '/push/' in path:r.fulfill(json={'ok':True})
                    else:r.fulfill(content_type='text/html',body='<header id="gsf-global-header" style="height:44px">GSF</header><div id="gsf-creator-hub-live-v160" class="is-open" style="position:fixed;top:44px;bottom:90px;left:0;right:0"><iframe style="width:100%;height:100%;border:0" src="/creator-hub-v156/?view=social"></iframe></div><nav id="gsf-global-gamebar" style="position:fixed;bottom:10px;height:66px">Game Bar</nav>')
                page.context.route('**/*',route);page.goto('http://gsf.test/?gsf_page=hub&gsf_section=social')
                page.evaluate('window.shellIdentity={}')
                frame=page.frame_locator('iframe')
                frame.locator('#hub').wait_for()
                page.locator('iframe').evaluate("f=>f.contentWindow.postMessage({type:'GSF_HUB_FOCUS',section:'social'},location.origin)")
                frame.locator('[data-connect="youtube"]').wait_for(state='visible',timeout=4000)
                before=page.locator('iframe').bounding_box()
                with page.expect_popup(timeout=4000) as event:frame.locator('[data-connect="youtube"]').click()
                popup=event.value;popup.wait_for_event('close',timeout=5000) if not popup.is_closed() else None
                self.assertTrue(page.evaluate('!!window.shellIdentity'))
                self.assertEqual(page.locator('iframe').bounding_box(),before)
                self.assertIn('gsf_section=social',page.url)
                self.assertTrue(frame.locator('[data-connect="youtube"]').is_visible())

    def test_home_shell_bottom_surfaces_are_dark(self):
        # Replay the canonical persistent shell controller, including legacy footer controllers.
        tree=ast.parse((ROOT/'app.py').read_text(encoding='utf-8'))
        shell=next(n.value.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and any(isinstance(t,ast.Name) and t.id=='_GSF_PARENT_SHELL' for t in n.targets))
        import re
        css=ast.literal_eval(re.search(r"const NA_SHELL_CSS=('(?:\\.|[^'\\])*');",shell).group(1))
        for width,height in VIEWPORTS:
            with self.subTest(width=width):
                page=self.page(width,height)
                page.route('**/*',lambda r:r.fulfill(json={'ok':True}))
                page.goto('http://gsf.test/')
                page.set_content('<style>[data-testid=stBottom],[data-testid=stBottomBlockContainer]{background:white}</style><div data-testid="stAppViewContainer"><main data-testid="stMain"></main><div data-testid="stBottom"><div data-testid="stBottomBlockContainer" style="position:fixed;bottom:0;height:20px;width:100%"></div></div></div>')
                page.evaluate('window.GSFNavigation={snapshot:()=>({target:"home"}),bridge:()=>({listen(){},timeout(){},interval(){},signal:new AbortController().signal})}')
                page.add_style_tag(content=css)
                for selector in ['[data-testid=stBottom]','[data-testid=stBottomBlockContainer]']:
                    self.assertEqual(page.locator(selector).evaluate('e=>getComputedStyle(e).backgroundColor'),'rgb(5, 13, 22)')

if __name__=='__main__':unittest.main()
