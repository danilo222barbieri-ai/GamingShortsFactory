"""Continuity regressions use the real installed shell and notification client."""
import ast,json,os,shutil,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def push_code():
 tree=ast.parse((ROOT/'web/direct_upload_server.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_push_client_bytes');ns={}
 exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-notification-client>','exec'),ns)
 return ns['_push_client_bytes']().decode()

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in actual browser gate')
class NotificationContinuity(unittest.TestCase):
 def setUp(self):
  from playwright.sync_api import sync_playwright
  self.playwright=sync_playwright().start();kind=getattr(self.playwright,os.environ['GSF_BROWSER']);options={'headless':True}
  if kind.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
  self.browser=kind.launch(**options);self.addCleanup(self.playwright.stop);self.addCleanup(self.browser.close)
  self.page=self.browser.new_page(viewport={'width':390,'height':844});self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
  self.page.route('**/*',lambda r:r.fulfill(content_type='application/json',body='{"ok":true,"render_status":"idle"}'))
  self.page.goto('http://gsf.test/');self.page.set_content('<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><header id="gsf-global-header" style="position:fixed;top:0;height:90px;width:100%"></header><nav id="gsf-global-gamebar" style="position:fixed;bottom:0;height:80px;width:100%"></nav></body></html>');self.page.evaluate(push_code())
 def test_process_updates_in_place_without_duplicate_toasts(self):
  self.assertEqual(self.page.evaluate('typeof GSFNotify.upsert'),'function','Existing notification engine needs in-place process updates')
  self.page.evaluate("()=>{GSFNotify.upsert('analysis',{title:'Analisi avviata',kind:'working'});window.originalNotice=document.querySelector('.gsf-site-toast');GSFNotify.upsert('analysis',{title:'Cerco i momenti migliori',kind:'working'});}")
  self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
  self.assertTrue(self.page.evaluate("originalNotice===document.querySelector('.gsf-site-toast')"));self.assertIn('Cerco',self.page.locator('.gsf-site-toast').inner_text())
  self.page.evaluate("GSFNotify.update('analysis',{title:'2 momenti trovati',kind:'success'})")
  self.assertTrue(self.page.evaluate("originalNotice===document.querySelector('.gsf-site-toast')"));self.assertIn('2 momenti',self.page.locator('.gsf-site-toast').inner_text());self.assertFalse(self.errors,self.errors)
 def test_notification_copy_and_empty_action_area_do_not_swallow_underlying_taps(self):
  self.page.evaluate("()=>{window.underlyingClicks=0;window.noticeClicks=0;GSFNotify.upsert('overlay',{title:'Render pronto',kind:'success',onClick:()=>noticeClicks++,ttl:0})}")
  self.page.wait_for_function("()=>getComputedStyle(document.querySelector('.gsf-site-toast')).opacity==='1'")
  box=self.page.locator('.gsf-site-toast-actions').bounding_box()
  self.assertIsNotNone(box)
  point={'x':box['x']+8,'y':box['y']+box['height']/2}
  self.page.evaluate("p=>{const b=document.createElement('button');b.id='underlying';b.textContent='Shorts';b.style.cssText='position:fixed;left:'+(p.x-5)+'px;top:'+(p.y-5)+'px;width:20px;height:20px';b.onclick=()=>underlyingClicks++;document.body.append(b)}",point)
  self.page.mouse.click(point['x'],point['y'])
  self.assertEqual(self.page.evaluate('underlyingClicks'),1,'Empty notification action area must not intercept app controls')
  self.page.locator('.gsf-site-toast-action').click()
  self.assertEqual(self.page.evaluate('noticeClicks'),1,'Real notification actions must stay interactive')
  self.page.evaluate("GSFNotify.upsert('close-test',{title:'Analisi',kind:'working'})")
  self.page.locator('[data-notice-id="close-test"] .gsf-site-toast-close').click()
  self.page.locator('[data-notice-id="close-test"]').wait_for(state='detached')

 def test_action_focus_survives_process_update(self):
  self.page.evaluate("()=>{window.actionCount=0;window.realAction=()=>actionCount++;GSFNotify.upsert('render',{title:'Render pronto',kind:'success',onClick:realAction,ttl:0});window.originalAction=document.querySelector('.gsf-site-toast-action');originalAction.focus();GSFNotify.update('render',{body:'Pronto per aprire'})}")
  self.assertTrue(self.page.evaluate("originalAction===document.querySelector('.gsf-site-toast-action')"))
  self.assertTrue(self.page.evaluate('document.activeElement===originalAction'))
  self.page.locator('.gsf-site-toast-action').click();self.assertEqual(self.page.evaluate('actionCount'),1)
 def test_long_process_persists_then_completes_and_dismisses(self):
  self.page.clock.install();self.page.evaluate("GSFNotify.upsert('long-analysis',{title:'Analisi in corso',kind:'working'})")
  self.page.clock.run_for(12000);self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
  self.page.evaluate("GSFNotify.update('long-analysis',{title:'Pronto',kind:'success'})");self.page.clock.run_for(7000);self.assertEqual(self.page.locator('.gsf-site-toast').count(),0)
 def test_real_alive_events_evolve_one_process_notification(self):
  self.page.evaluate((ROOT/'web/gsf_alive_v418.js').read_text())
  self.page.evaluate("()=>{GSFAlive.emit('ai.started');window.processNotice=document.querySelector('.gsf-site-toast');GSFAlive.emit('ai.found',{count:1})}")
  self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
  self.assertTrue(self.page.evaluate("processNotice===document.querySelector('.gsf-site-toast')"))
  self.assertIn('un momento',self.page.locator('.gsf-site-toast').inner_text())
  self.assertEqual(self.page.locator('.gsf-site-toast').get_attribute('data-kind'),'success')
  self.assertFalse(self.errors,self.errors)
 def test_source_process_uses_shared_monitor_and_completes_in_place(self):
  self.page.route('**/direct-upload/bucket/status?*',lambda r:r.fulfill(json={'ok':True,'ready':True}))
  self.page.evaluate("()=>{window.sourceDone=false;GSFNotify.trackSource({upload_id:'clipimport1'}).then(()=>sourceDone=true);window.trackedNotice=document.querySelector('.gsf-site-toast')}")
  self.page.wait_for_function('sourceDone',timeout=4000)
  self.assertTrue(self.page.evaluate("trackedNotice===document.querySelector('.gsf-site-toast')"))
  self.assertEqual(self.page.locator('.gsf-site-toast').get_attribute('data-kind'),'success')
 def test_source_monitor_timeout_also_cleans_up_network_failures(self):
  self.page.route('**/direct-upload/bucket/status?*',lambda r:r.fulfill(status=503,json={'error':'outage'}))
  self.page.clock.install();self.page.evaluate("()=>{window.expiredSource=false;GSFNotify.trackSource({upload_id:'offlineimport'}).then(()=>expiredSource=true)}")
  self.page.clock.fast_forward(601000)
  self.page.wait_for_function('expiredSource',timeout=4000)
  self.assertEqual(self.page.locator('.gsf-site-toast').get_attribute('data-kind'),'warning')
 def test_legacy_show_deduplicates_same_operation(self):
  self.page.evaluate("()=>{GSFNotify.show('Analisi','Avvio','working',{id:'same'});GSFNotify.show('Analisi','Avvio','working',{id:'same'})}")
  self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
 def test_dark_notifications_respect_actual_header_safe_zone(self):
  self.page.evaluate("GSFNotify.show('Progetto salvato','','success')");self.page.wait_for_timeout(300)
  result=self.page.locator('.gsf-site-toast').evaluate("e=>({top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom,bg:getComputedStyle(e).backgroundColor})")
  header=self.page.locator('#gsf-global-header').bounding_box();bar=self.page.locator('#gsf-global-gamebar').bounding_box()
  self.assertGreaterEqual(result['top'],header['y']+header['height']);self.assertLessEqual(result['bottom'],bar['y'])
  self.assertNotIn('255, 255, 255',result['bg'])
 def test_burst_uses_bounded_visible_queue(self):
  self.page.evaluate("()=>{for(let i=0;i<12;i++)GSFNotify.show('Evento '+i,'','info')}")
  self.assertLessEqual(self.page.locator('.gsf-site-toast').count(),2)
 def test_safe_zone_on_required_iphone_viewports(self):
  for width,height in [(375,667),(390,844),(393,852),(430,932)]:
   with self.subTest(viewport=(width,height)):
    self.page.set_viewport_size({'width':width,'height':height})
    self.page.evaluate("GSFNotify.upsert('viewport',{title:'Analisi in corso',kind:'working'})")
    self.page.wait_for_timeout(300)
    box=self.page.locator('[data-notice-id="viewport"]').bounding_box()
    self.assertGreaterEqual(box['x'],0);self.assertLessEqual(box['x']+box['width'],width)
    self.assertGreaterEqual(box['y'],90);self.assertLessEqual(box['y']+box['height'],height-80)
 def test_clearing_project_removes_obsolete_process(self):
  self.page.clock.install();self.page.evaluate((ROOT/'web/gsf_alive_v418.js').read_text())
  self.page.evaluate("()=>{GSFAlive.emit('ai.started');GSFAlive.emit('video.cleared')}")
  self.page.clock.run_for(400);self.assertEqual(self.page.locator('.gsf-site-toast').count(),0)
 def test_ready_action_uses_existing_navigation(self):
  self.page.evaluate("()=>{window.navigations=[];window.GSFNavigation={navigate:o=>navigations.push(o.target)} }")
  self.page.evaluate((ROOT/'web/gsf_alive_v418.js').read_text())
  self.page.evaluate("()=>{GSFAlive.emit('render.started');GSFAlive.emit('render.completed')}")
  self.page.locator('.gsf-site-toast-action').click()
  self.assertEqual(self.page.evaluate('navigations'),['short'])
 def test_child_frame_reuses_parent_notification_service(self):
  self.page.evaluate("()=>{const f=document.createElement('iframe');f.id='child';f.srcdoc='<html><body></body></html>';document.body.append(f)}")
  frame=self.page.frame_locator('#child');frame.locator('body').wait_for(state='attached')
  self.page.frames[1].evaluate("()=>{window.childJobPolls=0;const original=fetch;window.fetch=(url,opts)=>{if(String(url)==='/job/status')childJobPolls++;return original(url,opts)}}")
  self.page.frames[1].evaluate(push_code())
  self.assertTrue(self.page.evaluate("document.querySelector('#child').contentWindow.GSFNotify===GSFNotify"))
  self.page.wait_for_timeout(100)
  self.assertEqual(self.page.frames[1].evaluate('childJobPolls'),0,'Only the parent owns the process monitor')
 def test_reduced_motion_has_no_notification_animation(self):
  self.page.emulate_media(reduced_motion='reduce');self.page.evaluate("GSFNotify.show('Salvato','Progetto pronto','success')")
  result=self.page.locator('.gsf-site-toast').evaluate("e=>({transition:getComputedStyle(e).transitionDuration,animation:getComputedStyle(e.querySelector('.gsf-site-toast-bar')).animationName})")
  self.assertTrue(all(float(x.strip().rstrip('s'))<=.01 for x in result['transition'].split(',')),result)
  self.assertIn(result['animation'],('none',''))

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in actual browser gate')
class ColdSurfaceGeometry(unittest.TestCase):
 def test_ai_frame_is_full_width_without_transient_streamlit_css(self):
  from test_closed_beta_bugfix_pass import installed_parent_html
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   kind=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if kind.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=kind.launch(**options)
   try:
    page=browser.new_page(viewport={'width':390,'height':844});parent=installed_parent_html()
    def route(r):
     if r.request.url=='http://gsf.test/':r.fulfill(content_type='text/html',body=parent)
     elif '/ai-v221/' in r.request.url:r.fulfill(content_type='text/html',body=(ROOT/'web/ai_v221_component/index.html').read_text())
     else:r.fulfill(content_type='application/json',body='{"ok":true,"account":{},"social":{},"drafts":[],"shorts":[]}')
    page.route('**/*',route);page.goto('http://gsf.test/');page.wait_for_function('window.GSFNavigation?.snapshot().surfaces===5')
    page.evaluate("GSFNavigation.navigate({target:'ai'})");page.locator('#gsf-ai-overlay-v221 iframe').wait_for(state='visible')
    rect=page.locator('#gsf-ai-overlay-v221 iframe').bounding_box();self.assertGreaterEqual(rect['width'],388);self.assertGreater(rect['height'],500)
    self.assertEqual(page.evaluate('document.documentElement.scrollWidth'),390)
   finally:browser.close()

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in actual browser gate')
class PlayerContinuity(unittest.TestCase):
 def test_fullscreen_transition_keeps_real_video_and_playback(self):
  from playwright.sync_api import sync_playwright
  from visual.gsf_navigation_stress import MEDIA_FIXTURE
  from urllib.parse import urlsplit
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if engine.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**options)
   try:
    page=browser.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    def route(r):
     path=urlsplit(r.request.url).path
     if path=='/clip.mp4':
      import re
      match=re.fullmatch(r'bytes=(\d+)-(\d*)',r.request.headers.get('range',''))
      headers={'Accept-Ranges':'bytes'}
      if match:
       start=int(match[1]);end=min(int(match[2]) if match[2] else len(MEDIA_FIXTURE)-1,len(MEDIA_FIXTURE)-1)
       headers['Content-Range']=f'bytes {start}-{end}/{len(MEDIA_FIXTURE)}'
       r.fulfill(status=206,content_type='video/mp4',headers=headers,body=MEDIA_FIXTURE[start:end+1])
      else:r.fulfill(content_type='video/mp4',headers=headers,body=MEDIA_FIXTURE)
     else:
      file=ROOT/'web/game_editor_mobile_component'/('index.html' if path=='/' else path.lstrip('/'))
      if file.is_file():r.fulfill(content_type='text/css' if file.suffix=='.css' else 'text/javascript' if file.suffix=='.mjs' else 'text/html',body=file.read_text())
      else:r.fulfill(status=404,body='')
    page.route('**/*',route);page.goto('http://gsf.test/')
    page.wait_for_function('window.GSFGameEditor2026')
    page.evaluate("()=>{window.originalVideo=document.querySelector('video');document.querySelector('#gameEditorApp').requestFullscreen=()=>Promise.reject(new Error('iOS fallback'));window.postMessage({type:'GSF_GAME_EDITOR_INIT',media:{url:'/clip.mp4',duration:2}},location.origin)}")
    page.wait_for_function('document.querySelector("video").readyState>=2')
    page.locator('#playButton').click();page.wait_for_function('document.querySelector("video").currentTime>.1')
    page.locator('video').evaluate("v=>{Object.defineProperty(v,'readyState',{value:1,configurable:true});v.dispatchEvent(new Event('waiting'))}")
    page.locator('.player-buffering').wait_for(state='visible',timeout=2000)
    page.locator('video').evaluate("v=>{delete v.readyState;v.dispatchEvent(new Event('playing'))}")
    page.locator('.player-buffering').wait_for(state='hidden')
    before=page.locator('video').evaluate('v=>v.currentTime')
    page.locator('#enterEditorButton').click()
    self.assertTrue(page.evaluate('originalVideo===document.querySelector("video")'))
    self.assertGreaterEqual(page.locator('video').evaluate('v=>v.currentTime'),before)
    self.assertFalse(page.locator('video').evaluate('v=>v.paused'))
    self.assertTrue(page.locator('#previewStage').evaluate("e=>e.getAnimations().some(a=>a.effect.getKeyframes().some(k=>k.transform&&k.transform!=='none'))"),'The existing player should transition with transform')
    page.wait_for_timeout(280);page.locator('#fullscreenButton').click()
    self.assertTrue(page.evaluate('originalVideo===document.querySelector("video")'))
    self.assertEqual(page.locator('video').count(),1);self.assertFalse(errors,errors)
    page.wait_for_timeout(280);page.emulate_media(reduced_motion='reduce');page.locator('#enterEditorButton').click()
    self.assertEqual(page.locator('#previewStage').evaluate('e=>e.getAnimations().length'),0)
    page.wait_for_function('document.querySelector("video").seekable.length>0');page.locator('video').evaluate('v=>{v.pause();v.currentTime=.5}')
    page.evaluate("()=>{window.GSFGameEditor2026.commitEditorState({inPoint:.25,outPoint:1.75,zoom:1.4});window.beforeScrub=window.GSFGameEditor2026.getState()}")
    track=page.locator('#timelineTrack');rect=track.bounding_box()
    page.mouse.move(rect['x']+rect['width']*.3,rect['y']+rect['height']/2);page.mouse.down()
    page.mouse.move(rect['x']+rect['width']*.75,rect['y']+rect['height']/2,steps=5);page.mouse.up()
    page.wait_for_function('Math.abs(document.querySelector("video").currentTime-1.5)<.15&&!document.querySelector("video").seeking')
    self.assertAlmostEqual(page.locator('video').evaluate('v=>v.currentTime'),1.5,delta=.15)
    self.assertTrue(page.locator('video').evaluate('v=>v.paused'))
    page.mouse.move(rect['x']+rect['width']*.5,rect['y']+rect['height']/2);page.mouse.down()
    page.mouse.move(rect['x']+rect['width']*.95,rect['y']+rect['height']/2,steps=5);page.mouse.up()
    page.wait_for_function('!document.querySelector("video").seeking')
    self.assertAlmostEqual(page.locator('video').evaluate('v=>v.currentTime'),1.75,delta=.02)
    self.assertTrue(page.evaluate('originalVideo===document.querySelector("video")'))
    self.assertEqual(page.evaluate('GSFGameEditor2026.getState()'),page.evaluate('beforeScrub'))
    for width,height in [(375,667),(390,844),(393,852),(430,932)]:
     with self.subTest(timeline_viewport=(width,height)):
      page.set_viewport_size({'width':width,'height':height})
      page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
      geometry=track.evaluate("e=>{const r=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect(),x=r.x+r.width/2;return {height:r.height,bottom:r.bottom,parentBottom:p.bottom,hitTop:e.contains(document.elementFromPoint(x,r.top+2)),hitBottom:e.contains(document.elementFromPoint(x,r.bottom-2))}}")
      self.assertGreaterEqual(geometry['height'],44)
      self.assertLessEqual(geometry['bottom'],geometry['parentBottom']-1)
      self.assertTrue(geometry['hitTop'] and geometry['hitBottom'],geometry)
    self.assertFalse(errors,errors)
   finally:browser.close()

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in actual browser gate')
class NativeBackContinuity(unittest.TestCase):
 def test_editor_to_hub_back_restores_parent_route(self):
  self.assert_parent_back(False)

 def test_late_editor_document_cannot_consume_parent_back(self):
  self.assert_parent_back(True)

 def assert_parent_back(self,delay_editor):
  from test_closed_beta_bugfix_pass import installed_parent_html
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if engine.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**options)
   try:
    page=browser.new_page(viewport={'width':390,'height':844});parent=installed_parent_html();pending=[]
    def serve(r):
     if r.request.url=='http://gsf.test/':r.fulfill(content_type='text/html',body=parent)
     elif delay_editor and '/game-editor-mobile/' in r.request.url and r.request.resource_type=='document':pending.append(r)
     elif r.request.resource_type=='document':r.fulfill(content_type='text/html',body='<html><body>Loaded surface</body></html>')
     else:r.fulfill(json={'ok':True,'account':{},'social':{}})
    page.route('**/*',serve);page.goto('http://gsf.test/');page.wait_for_function('GSFNavigation.snapshot().surfaces===5')
    page.evaluate("GSFNavigation.navigate({target:'editor'})")
    if delay_editor:
     for _ in range(60):
      if pending:break
      page.wait_for_timeout(50)
     self.assertTrue(pending,'Editor document must be in flight')
    else:page.frame_locator('#gsf-editor-overlay-v220 iframe').get_by_text('Loaded surface').wait_for()
    page.evaluate("GSFNavigation.navigate({target:'hub'})");page.frame_locator('#gsf-creator-hub-live-v160 iframe').get_by_text('Loaded surface').wait_for()
    if delay_editor:
     pending.pop().fulfill(content_type='text/html',body='<html><body>Late editor surface</body></html>')
     page.frame_locator('#gsf-editor-overlay-v220 iframe').get_by_text('Late editor surface').wait_for(state='attached')
    page.evaluate('history.back()')
    page.wait_for_function("GSFNavigation.snapshot().target==='editor'",timeout=3000)
    self.assertIn('gsf_page=editor',page.url)
   finally:browser.close()

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in actual browser gate')
class OAuthLibraryReturn(unittest.TestCase):
 def test_legacy_callback_opens_hub_and_restores_requested_library_once(self):
  from test_closed_beta_bugfix_pass import installed_parent_html
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if engine.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**options)
   try:
    for pending in (False,True,"expired"):
     with self.subTest(library_return=pending):
      context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page()
      if pending:page.add_init_script("if(window===top)sessionStorage.setItem('gsf-source-oauth-return',JSON.stringify({provider:'twitch',folder:'videos',created:Date.now()-"+('700000' if pending=='expired' else '0')+"}))")
      parent=installed_parent_html()
      def serve(r):
       if r.request.is_navigation_request() and r.request.frame==page.main_frame:r.fulfill(content_type='text/html',body=parent)
       elif r.request.resource_type=='document':r.fulfill(content_type='text/html',body='<html><body>Hub surface</body></html>')
       else:r.fulfill(json={'ok':True,'account':{},'social':{}})
      page.route('**/*',serve);page.goto('http://gsf.test/?gsf_hub=social&oauth_return=1')
      expected='live' if pending is True else 'social'
      page.wait_for_function("section=>GSFNavigation.snapshot().target==='hub'&&GSFNavigation.snapshot().section===section",arg=expected,timeout=3000)
      self.assertIsNone(page.evaluate("sessionStorage.getItem('gsf-source-oauth-return')"))
      self.assertIn('gsf_page=hub',page.url);self.assertNotIn('gsf_hub=',page.url)
      if pending is True:self.assertEqual(page.evaluate("JSON.parse(sessionStorage.getItem('gsf-source-view')).folder"),'videos')
      context.close()
   finally:browser.close()

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in actual browser gate')
class StartupContinuity(unittest.TestCase):
 def test_canonical_notification_exists_before_home_and_finishes_on_readiness(self):
  from test_closed_beta_bugfix_pass import installed_parent_html
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if engine.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**options)
   try:
    page=browser.new_page(viewport={'width':390,'height':844});parent=installed_parent_html();pending=[];errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def serve(r):
     if r.request.url=='http://gsf.test/':r.fulfill(content_type='text/html',body=parent)
     elif r.request.url=='http://gsf.test/home':pending.append(r)
     else:r.fulfill(json={'ok':True,'render_status':'idle','account':{},'social':{}})
    page.route('**/*',serve);page.goto('http://gsf.test/')
    notice=page.locator('[data-notice-id="alive:startup"]');notice.wait_for(timeout=3000)
    self.assertEqual(notice.get_attribute('data-kind'),'working')
    page.evaluate("()=>{const chrome=document.createElement('header');chrome.dataset.testid='stHeader';chrome.textContent='Deploy';document.body.append(chrome)}")
    self.assertEqual(page.locator('[data-testid="stHeader"]').evaluate('e=>getComputedStyle(e).display'),'none','Late React chrome must be hidden before transient app CSS arrives')
    self.assertEqual(page.locator('#gsf-global-push-client-v258').count(),0,'Canonical client must be available without a late script fetch')
    page.evaluate("()=>{window.bootNotify=GSFNotify;const f=document.createElement('iframe');f.src='/home';document.body.append(f)}")
    for _ in range(60):
     if pending:break
     page.wait_for_timeout(50)
    self.assertTrue(pending)
    pending.pop().fulfill(content_type='text/html',body='<html><body><main id="home154"></main><script>window.__GSF_V333_CTA_TOUCH=true;parent.postMessage({type:"GSF_HOME_READY"},location.origin)</script></body></html>')
    notice.wait_for(state='hidden',timeout=3000)
    self.assertTrue(page.evaluate('bootNotify===GSFNotify'))
    self.assertFalse(errors,errors)
   finally:browser.close()

@unittest.skipUnless(os.environ.get('GSF_BROWSER') and (os.environ.get('GSF_BASE_URL') or os.environ.get('BASE')),'Requires the running production-image browser gate')
class StartupVisual(unittest.TestCase):
 def test_first_frames_four_mobile_viewports_and_standalone(self):
  from playwright.sync_api import sync_playwright
  import tempfile
  base=os.environ.get('GSF_BASE_URL') or os.environ['BASE']
  output=Path(os.environ.get('OUT_DIR') or tempfile.mkdtemp(prefix='gsf-first-frames-'))/'first-frames';output.mkdir(parents=True,exist_ok=True)
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if engine.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**options)
   try:
    for width,height in [(375,667),(390,844),(393,852),(430,932)]:
     for standalone in (False,True):
      with self.subTest(viewport=(width,height),standalone_emulated=standalone):
       context=browser.new_context(**{**p.devices['iPhone 13'],'viewport':{'width':width,'height':height}})
       try:
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        if standalone:page.add_init_script("Object.defineProperty(navigator,'standalone',{value:true});const nativeMatch=window.matchMedia.bind(window);window.matchMedia=q=>q==='(display-mode: standalone)'?{...nativeMatch(q),matches:true,addEventListener(){},removeEventListener(){}}:nativeMatch(q)")
        page.add_init_script("if(window===top){window.__firstFrames=[];const start=performance.now();const sample=t=>{__firstFrames.push({ms:Math.round(t-start),body:!!document.body,bg:getComputedStyle(document.documentElement).backgroundColor,chrome:[...document.querySelectorAll('[data-testid=stHeader],[data-testid=stToolbar],[data-testid=stStatusWidget]')].some(e=>getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().height>0)});if(t-start<1500)requestAnimationFrame(sample)};requestAnimationFrame(sample)}")
        folder=output/f'{width}-{height}-{standalone}';folder.mkdir(exist_ok=True)
        page.goto(base,wait_until='domcontentloaded');page.screenshot(path=str(folder/'first-dom-frame.png'))
        page.wait_for_timeout(100);page.screenshot(path=str(folder/'after100ms.png'))
        page.wait_for_timeout(200);page.screenshot(path=str(folder/'after300ms.png'))
        page.wait_for_function("()=>[...document.querySelectorAll('iframe')].some(f=>{try{return !!f.contentWindow.__GSF_V333_CTA_TOUCH}catch(_){return false}})",timeout=90000)
        page.screenshot(path=str(folder/'ready.png'))
        samples=page.evaluate('__firstFrames');(folder/'evidence.json').write_text(json.dumps({'frames':samples,'errors':errors,'standalone_emulated':standalone},indent=2))
        painted=[sample for sample in samples if sample['body']]
        self.assertTrue(painted,'Capture actual browser rendering frames')
        self.assertTrue(all(sample['bg']=='rgb(5, 13, 22)' and not sample['chrome'] for sample in painted),painted)
        self.assertEqual(page.evaluate('document.documentElement.scrollWidth'),width)
        self.assertFalse(errors,errors)
       finally:context.close()
   finally:browser.close()
