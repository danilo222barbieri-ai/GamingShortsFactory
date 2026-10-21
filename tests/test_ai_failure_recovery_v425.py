"""Terminal AI failures must reach the current request, not leave a three-minute spinner."""
import os, unittest
from pathlib import Path
from web import ai_engines_v412 as results
ROOT=Path(__file__).resolve().parents[1]

class FailureContract(unittest.TestCase):
 def test_duration_probe_works_when_ffmpeg_encoder_wrapper_cannot_probe(self):
  import ast,subprocess,shutil,tempfile
  from visual.gsf_navigation_stress import MEDIA_FIXTURE
  tree=ast.parse((ROOT/'app.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_duration_cached');node.decorator_list=[]
  ns={'FFPROBE_PATH':shutil.which('ffprobe'),'subprocess':subprocess}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-duration-reader>','exec'),ns)
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)/'short.mp4';source.write_bytes(MEDIA_FIXTURE)
   duration=ns['_gsf_duration_cached'](str(source),source.stat().st_size,0,'/bin/false')
  self.assertIsNotNone(duration,'Read metadata with ffprobe independently of the encoder wrapper')
  self.assertGreater(duration,0);self.assertLess(duration,5)

 def test_failed_sheet_does_not_return_previous_preview_files(self):
  meta={'items':[],'request_id':'current','status':'failed','error_code':'no_moments','error':'Nessun momento valido trovato.'}
  payload=results.merge_results(meta,[(1,0,123,'old_mini_1_0.mp4')],lambda name:'/media/'+name)
  self.assertEqual(payload.get('status'),'failed')
  self.assertEqual(payload.get('error'),meta['error'])
  self.assertEqual(payload['request_id'],'current');self.assertEqual(payload['previews'],[])

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in blocking OAuth/source browser gate')
class FailureBrowser(unittest.TestCase):
 def test_current_failure_exits_scan_and_allows_retry(self):
  from playwright.sync_api import sync_playwright
  import shutil
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);opts={'headless':True}
   if engine.name=='chromium':opts.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**opts)
   try:
    page=browser.new_page(viewport={'width':390,'height':844})
    page.add_init_script("window.currentAIRequest='';addEventListener('message',e=>{if(e.data?.type==='GSF_AI_UI'&&e.data.action==='create')currentAIRequest=e.data.request_id})")
    def route(r):
     if '/ai/results' in r.request.url:
      request=page.evaluate('currentAIRequest')
      r.fulfill(json={'ok':True,'request_id':request,'previews':[],'status':'failed' if request else 'idle','error':'L’analisi richiede almeno 5 secondi.'})
     else:r.fulfill(content_type='text/html',body=(ROOT/'web/ai_v221_component/index.html').read_text())
    page.route('**/*',route);page.goto('http://gsf.test/')
    page.evaluate("postMessage({type:'GSF_AI_STATE',state:{loaded:true}},location.origin)")
    page.locator('#createAi').click()
    page.wait_for_function("document.querySelector('#aiStatus').textContent.includes('almeno 5 secondi')",timeout=8000)
    self.assertTrue(page.locator('#createAi').is_enabled())
    self.assertFalse(page.locator('[data-view=engines]').evaluate("e=>e.classList.contains('scanning')"))
    self.assertEqual(page.locator('article.short').count(),0)
   finally:browser.close()

class ProviderBudget(unittest.TestCase):
 def test_slow_first_model_does_not_restart_the_full_budget(self):
  from web import semantic_video_v114 as semantic
  from unittest import mock
  from types import SimpleNamespace
  import tempfile
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)/'gameplay.mp4';source.write_bytes(b'controlled transport')
   clock=[0.0];calls=[]
   def generate(*args,**kwargs):
    calls.append(args[6]);clock[0]+=90.0
    raise TimeoutError('ReadTimeout timed out')
   with mock.patch.dict(os.environ,{'GEMINI_API_KEY':'test-not-a-secret','GSF_SEMANTIC_VIDEO_AI':'1','GSF_SEMANTIC_TIMEOUT_SECONDS':'420','GSF_SEMANTIC_STATIC_TIMEOUT_SECONDS':'90','GSF_GEMINI_MODEL':'primary','GSF_GEMINI_FALLBACK_MODELS':'secondary'}),mock.patch.dict('sys.modules',{'google':SimpleNamespace(genai=SimpleNamespace(Client=lambda **kw:object()))}),mock.patch.object(semantic,'_probe_duration_seconds',return_value=20),mock.patch.object(semantic,'_generate_content_semantic',side_effect=generate),mock.patch.object(semantic.time,'perf_counter',side_effect=lambda:clock[0]):
    result=semantic.analyze_gameplay_video(source)
   self.assertEqual(len(calls),1,'An exhausted provider budget must not start another90second call')
   self.assertLessEqual(result['elapsed_seconds'],90)
   self.assertEqual(result['events'],[])

 def test_fast_failure_keeps_backup_model_and_remaining_budget(self):
  from web import semantic_video_v114 as semantic
  from unittest import mock
  from types import SimpleNamespace
  import tempfile
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)/'gameplay.mp4';source.write_bytes(b'controlled transport');clock=[0.0];calls=[];options=[]
   def client(**kwargs):options.append(kwargs['http_options']);return object()
   def generate(*args,**kwargs):
    calls.append((args[1],args[6]))
    if len(calls)==1:clock[0]+=1;raise RuntimeError('503 UNAVAILABLE')
    return {'events':[]}
   with mock.patch.dict(os.environ,{'GEMINI_API_KEY':'test-not-a-secret','GSF_SEMANTIC_VIDEO_AI':'1','GSF_SEMANTIC_TIMEOUT_SECONDS':'420','GSF_SEMANTIC_STATIC_TIMEOUT_SECONDS':'90','GSF_GEMINI_MODEL':'primary','GSF_GEMINI_FALLBACK_MODELS':'secondary'}),mock.patch.dict('sys.modules',{'google':SimpleNamespace(genai=SimpleNamespace(Client=client))}),mock.patch.object(semantic,'_probe_duration_seconds',return_value=20),mock.patch.object(semantic,'_generate_content_semantic',side_effect=generate),mock.patch.object(semantic.time,'perf_counter',side_effect=lambda:clock[0]):
    result=semantic.analyze_gameplay_video(source)
   self.assertEqual(calls,[('primary',90),('secondary',89)])
   self.assertEqual(result['model'],'secondary');self.assertTrue(result['model_fallback']);self.assertNotIn('error',result)
   self.assertEqual(options[0]['retry_options']['attempts'],1)

class RequestIsolation(unittest.TestCase):
 def test_old_failure_cannot_stop_new_analysis(self):
  import subprocess
  html=(ROOT/'web/ai_v221_component/index.html').read_text()
  functions=html[html.index('function freshRows('):html.index('async function startSearch(')]
  script="""const vm=require('node:vm'),assert=require('node:assert/strict');let retries=0;const context={Date,requestId:'current',pollToken:1,awaitingResults:true,state:{processing:true},fetchResults:async()=>({request_id:'older',status:'failed',error:'Old failure',previews:[]}),setTimeout:()=>retries++,setScan:()=>{throw Error('Stale failure must not stop current scan')},render(){},alive(){}};vm.createContext(context);vm.runInContext(SOURCE,context);vm.runInContext('pollResults(1,Date.now()+10000)',context).then(()=>{assert.equal(context.state.processing,true);assert.equal(context.awaitingResults,true);assert.equal(retries,1)}).catch(e=>{console.error(e);process.exit(1)});"""
  import json
  subprocess.run(['node','-e',script.replace('SOURCE',json.dumps(functions))],check=True,capture_output=True,text=True)
