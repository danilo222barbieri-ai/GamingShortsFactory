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
 def test_action_focus_survives_process_update(self):
  self.page.evaluate("()=>{window.actionCount=0;window.realAction=()=>actionCount++;GSFNotify.upsert('render',{title:'Render pronto',kind:'success',onClick:realAction,ttl:0});window.originalAction=document.querySelector('.gsf-site-toast-action');originalAction.focus();GSFNotify.update('render',{body:'Pronto per aprire'})}")
  self.assertTrue(self.page.evaluate("originalAction===document.querySelector('.gsf-site-toast-action')"))
  self.assertTrue(self.page.evaluate('document.activeElement===originalAction'))
  self.page.locator('.gsf-site-toast-action').click();self.assertEqual(self.page.evaluate('actionCount'),1)
 def test_long_process_persists_then_completes_and_dismisses(self):
  self.page.clock.install();self.page.evaluate("GSFNotify.upsert('long-analysis',{title:'Analisi in corso',kind:'working'})")
  self.page.clock.run_for(12000);self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
  self.page.evaluate("GSFNotify.update('long-analysis',{title:'Pronto',kind:'success'})");self.page.clock.run_for(5000);self.assertEqual(self.page.locator('.gsf-site-toast').count(),0)
 def test_real_alive_events_evolve_one_process_notification(self):
  self.page.evaluate((ROOT/'web/gsf_alive_v418.js').read_text())
  self.page.evaluate("()=>{GSFAlive.emit('ai.started');window.processNotice=document.querySelector('.gsf-site-toast');GSFAlive.emit('ai.found',{count:1})}")
  self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
  self.assertTrue(self.page.evaluate("processNotice===document.querySelector('.gsf-site-toast')"))
  self.assertIn('un momento',self.page.locator('.gsf-site-toast').inner_text())
  self.assertEqual(self.page.locator('.gsf-site-toast').get_attribute('data-kind'),'success')
  self.assertFalse(self.errors,self.errors)
 def test_legacy_show_deduplicates_same_operation(self):
  self.page.evaluate("()=>{GSFNotify.show('Analisi','Avvio','working',{id:'same'});GSFNotify.show('Analisi','Avvio','working',{id:'same'})}")
  self.assertEqual(self.page.locator('.gsf-site-toast').count(),1)
 def test_dark_notifications_respect_actual_header_safe_zone(self):
  self.page.evaluate("GSFNotify.show('Progetto salvato','','success')");self.page.wait_for_timeout(300)
  result=self.page.locator('.gsf-site-toast').evaluate("e=>({top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom,bg:getComputedStyle(e).backgroundColor})")
  self.assertGreaterEqual(result['top'],98);self.assertLessEqual(result['bottom'],764)
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
    self.assertGreaterEqual(box['y'],98);self.assertLessEqual(box['y']+box['height'],height-80)
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
  self.page.frames[1].evaluate(push_code())
  self.assertTrue(self.page.evaluate("document.querySelector('#child').contentWindow.GSFNotify===GSFNotify"))
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
