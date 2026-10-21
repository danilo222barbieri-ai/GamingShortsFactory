"""Publication outcomes must preserve privacy and distinguish guided sharing from published posts."""
import io,json,os,tempfile,unittest
from pathlib import Path
from web import publish_multi_v413 as publish
ROOT=Path(__file__).resolve().parents[1]

class Response(io.BytesIO):
 def __init__(self,payload=None,status=200):
  super().__init__(json.dumps(payload or {}).encode());self.status=status

class TikTokRecovery(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.video=Path(self.temp.name)/'short.mp4';self.video.write_bytes(b'x'*4096);self.calls=[]
 def opener(self,rows):
  def call(req,timeout):
   self.calls.append((req.full_url,req.data,req.method));return rows.pop(0)
  return call
 def success(self):return [Response({'data':{'upload_url':'https://upload.tiktok.test/file','publish_id':'post1'},'error':{'code':'ok'}}),Response(status=201),Response({'data':{'status':'PUBLISH_COMPLETE'},'error':{'code':'ok'}})]
 def creator(self):return Response({'data':{'privacy_level_options':['PUBLIC_TO_EVERYONE','SELF_ONLY']},'error':{'code':'ok'}})
 def test_public_rejection_does_not_silently_publish_private(self):
  rows=[self.creator(),Response({'error':{'code':'unaudited_client_can_only_post_to_private_accounts','message':'internal text'}}),*self.success()]
  with self.assertRaises(publish.PublishError) as caught:publish.tiktok_direct_post('test-token',str(self.video),{},'public',opener=self.opener(rows))
  self.assertEqual(getattr(caught.exception,'code',''),'unaudited_client_can_only_post_to_private_accounts')
  self.assertIn('approv',str(caught.exception).lower());self.assertEqual(len(self.calls),2)
 def test_provider_error_is_readable_and_does_not_expose_raw_message(self):
  rows=[Response({'error':{'code':'rate_limit_exceeded','message':'internal-provider-detail'}})]
  with self.assertRaises(publish.PublishError) as caught:publish.tiktok_direct_post('test-token',str(self.video),{},'public',opener=self.opener(rows))
  self.assertIn('Attendi',str(caught.exception));self.assertNotIn('internal-provider-detail',str(caught.exception))
  self.assertEqual(getattr(caught.exception,'code',''),'rate_limit_exceeded')
 def test_privacy_is_never_changed_when_option_is_unavailable(self):
  for wanted,options in [('private',['PUBLIC_TO_EVERYONE']),('public',['SELF_ONLY']),('unlisted',['PUBLIC_TO_EVERYONE','SELF_ONLY'])]:
   with self.subTest(wanted=wanted),self.assertRaises(publish.PublishError):publish._tiktok_privacy(options,wanted)
 def test_non_json_http_failure_has_a_readable_code(self):
  import urllib.error
  def refused(req,timeout):raise urllib.error.HTTPError(req.full_url,403,'Forbidden',{},io.BytesIO(b'<html>internal detail</html>'))
  with self.assertRaises(publish.PublishError) as caught:publish.tiktok_direct_post('test-token',str(self.video),{},'public',opener=refused)
  self.assertIn('TikTok',str(caught.exception));self.assertEqual(getattr(caught.exception,'code',''),'http_403')

 def test_explicit_private_publication_remains_supported(self):
  out=publish.tiktok_direct_post('test-token',str(self.video),{},'private',opener=self.opener([self.creator(),*self.success()]))
  self.assertTrue(out['ok']);self.assertEqual(out['privacy'],'SELF_ONLY');self.assertFalse(out['private_only'])

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in blocking browser gate')
class GuidedShareRecovery(unittest.TestCase):
 def setUp(self):
  from playwright.sync_api import sync_playwright
  import shutil,urllib.parse
  from visual.gsf_navigation_stress import MEDIA_FIXTURE
  self.playwright=sync_playwright().start();self.addCleanup(self.playwright.stop)
  engine=getattr(self.playwright,os.environ['GSF_BROWSER']);opts={'headless':True}
  if engine.name=='chromium':opts.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
  self.browser=engine.launch(**opts);self.addCleanup(self.browser.close)
  self.page=self.browser.new_page(viewport={'width':390,'height':844});self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
  self.job={'id':'manual1','state':'finished','results':{'facebook':{'platform':'facebook','label':'Facebook','status':'manual','caption':'Test caption'}}};self.statuses=[];self.polls=0
  def route(r):
   path=urllib.parse.urlsplit(r.request.url).path
   if path=='/':r.fulfill(content_type='text/html',body=(ROOT/'web/share_v156_component/index.html').read_text())
   elif path=='/share/state':r.fulfill(json={'ok':True,'ready':True,'revision':'test','csrf_token':'csrf','publish_supported':['youtube','tiktok'],'social':{'tiktok':True},'publish_job':{}})
   elif path=='/publish/multi':r.fulfill(json={'ok':True,'job':self.job})
   elif path=='/publish/status':
    self.polls+=1
    if self.statuses:self.job=self.statuses.pop(0)
    r.fulfill(json={'ok':True,'job':self.job})
   elif path=='/share/final':r.fulfill(content_type='video/mp4',body=MEDIA_FIXTURE)
   else:r.fulfill(json={'ok':True,'render_status':'idle'})
  self.page.route('**/*',route)
 def open(self,platform):
  self.page.goto('http://gsf.test/');self.page.wait_for_function("!document.querySelector('#publishBtn').disabled")
  for name in ('youtube','tiktok','instagram','facebook'):
   button=self.page.locator('.plat[data-platform='+name+']')
   if (button.get_attribute('aria-pressed')=='true')!=(name==platform):button.click()
 def test_guided_only_result_does_not_leave_publication_running(self):
  self.open('facebook');self.page.locator('#publishBtn').click();self.page.locator('#results .row').wait_for()
  self.assertNotEqual(self.page.evaluate('GSFAlive.state().active_job'),'publish','Guided-only work is ready for manual sharing, not a running publication')
  self.assertIn('condividi',self.page.locator('#coreTitle').inner_text().lower())
  self.assertIn('Facebook',self.page.locator('#results').inner_text());self.assertNotIn('Pubblicato',self.page.locator('#results').inner_text())
  self.assertFalse(self.errors,self.errors)
 def test_instagram_personal_account_can_share_video_in_mobile_layouts(self):
  self.job={'id':'instagram1','state':'finished','results':{'instagram':{'platform':'instagram','label':'Instagram','status':'manual','caption':'Test caption'}}}
  self.page.add_init_script("""Object.defineProperty(navigator,'share',{value:async(data)=>{window.sharedFile={name:data.files[0].name,size:data.files[0].size,type:data.files[0].type}}});Object.defineProperty(navigator,'canShare',{value:()=>true});""")
  for width,height in [(375,667),(390,844),(393,852),(430,932)]:
   with self.subTest(width=width):
    self.page.set_viewport_size({'width':width,'height':height});self.open('instagram');self.page.locator('#publishBtn').click()
    row=self.page.locator('#results .row');row.wait_for()
    self.assertIn('account personale',row.inner_text())
    link=row.get_by_role('link',name='Apri Instagram');self.assertEqual(link.get_attribute('href'),'https://www.instagram.com/')
    box=link.bounding_box();self.assertGreaterEqual(box['x'],0);self.assertLessEqual(box['x']+box['width'],width)
    row.get_by_role('button',name='Condividi',exact=True).click();self.page.wait_for_function('!!window.sharedFile')
    shared=self.page.evaluate('window.sharedFile');self.assertGreater(shared['size'],0);self.assertEqual(shared['type'],'video/mp4')
    self.assertFalse(self.page.evaluate('GSFAlive.state().published'))
  self.assertFalse(self.errors,self.errors)
 def test_denied_clipboard_does_not_claim_caption_copied(self):
  self.page.add_init_script("""Object.defineProperty(navigator,'share',{value:undefined});Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>{throw new Error('denied')}}});document.execCommand=()=>false;""")
  self.open('facebook');self.page.locator('#publishBtn').click();self.page.locator('#results .row').get_by_role('button',name='Condividi',exact=True).click()
  self.page.wait_for_function("document.body.innerText.includes('Copia il testo dalla sezione Testi')")
  self.assertNotIn('Testo copiato',self.page.locator('body').inner_text());self.assertFalse(self.errors,self.errors)
 def test_tiktok_pending_confirmation_keeps_polling_until_confirmed(self):
  def job(status,pending=False):return {'id':'post1','state':'running' if status=='queued' else 'finished','results':{'tiktok':{'platform':'tiktok','label':'TikTok','status':status,'confirmation_pending':pending,'error':'In attesa di conferma TikTok' if pending else ''}}}
  self.job=job('queued');self.statuses=[job('error',True),job('done')]
  self.open('tiktok');self.page.locator('#publishBtn').click();self.page.locator('#results').get_by_text('In attesa di conferma TikTok',exact=False).wait_for(timeout=6000)
  self.assertFalse(self.page.evaluate('GSFAlive.state().published'))
  self.page.wait_for_function('GSFAlive.state().published===true',timeout=9000)
  self.assertGreaterEqual(self.polls,2);self.assertFalse(self.errors,self.errors)
