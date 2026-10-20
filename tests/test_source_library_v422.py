"""Source catalog contracts: real persistence and companion helpers; provider transport only is fake."""
import importlib,io,json,os,tempfile,unittest
from pathlib import Path
from test_social_oauth_v421 import Bucket,namespace
ROOT=Path(__file__).resolve().parents[1]

class CatalogTests(unittest.TestCase):
 def setUp(self):
  self.assertIsNotNone(importlib.util.find_spec('web.gsf_sources_v422'),'Shared source model is missing')
  self.sources=importlib.import_module('web.gsf_sources_v422');self.bucket=Bucket()
 def catalog(self,owner='accountA'):return self.sources.SourceCatalog(self.bucket,'bucket',owner)
 def record(self,owner='accountA',external='clip1'):
  return {'id':self.sources.source_id(owner,'twitch_clip','creator',external),'kind':'twitch_clip','provider':'twitch','provider_user_id':'creator','external_id':external,'title':'Gameplay','status':'ready','bucket_key':'uploads/browserA/upload1/video.mp4','size':123,'local_path':'/private/video.mp4','access_token':'must-not-leak'}
 def test_ids_are_owner_and_provider_account_scoped(self):
  sid=self.sources.source_id
  self.assertNotEqual(sid('A','twitch_clip','u','clip'),sid('B','twitch_clip','u','clip'))
  self.assertNotEqual(sid('A','twitch_clip','u','clip'),sid('A','twitch_clip','v','clip'))
  self.assertEqual(sid('A','twitch_clip','u','clip'),sid('A','twitch_clip','u','clip'))
 def test_public_record_excludes_private_fields(self):
  row=self.sources.public_source(self.record());self.assertTrue(row['can_analyze']);self.assertTrue(row['can_open_editor'])
  for field in ('owner_id','bucket_key','local_path','access_token','refresh_token','analysis_key'):self.assertNotIn(field,row)
 def test_live_and_vod_never_offer_import(self):
  for kind in ('twitch_live','twitch_vod','youtube_live','youtube_vod'):
   row=self.sources.public_source({**self.record(),'kind':kind,'status':'discovered'});self.assertFalse(row['can_import']);self.assertFalse(row['can_analyze']);self.assertTrue(row['import_reason'])
 def test_record_survives_new_catalog_instance_and_owner_isolation(self):
  record=self.record();self.catalog().save(record)
  self.assertEqual(self.catalog().load(record['id'])['external_id'],'clip1')
  self.assertEqual(self.catalog('accountB').load(record['id']),{})
 def test_failed_persistence_keeps_previous_record(self):
  row=self.record();self.catalog().save(row);self.bucket.fail=True
  with self.assertRaises(OSError):self.catalog().save({**row,'title':'Uncommitted'})
  self.bucket.fail=False;self.assertEqual(self.catalog().load(row['id'])['title'],'Gameplay')
 def test_catalog_rejects_forged_identity_or_path(self):
  with self.assertRaises(ValueError):self.catalog().save({**self.record(),'id':'../foreign'})
  with self.assertRaises(ValueError):self.catalog().save({**self.record(),'owner_id':'accountB'})
 def test_listing_filters_real_persisted_sources(self):
  self.catalog().save(self.record());self.catalog().save({**self.record(external='clip2'),'status':'failed'})
  rows=self.catalog().list('twitch','imported')['data'];self.assertEqual(len(rows),1);self.assertEqual(rows[0]['external_id'],'clip1')
 def test_concurrent_catalog_write_cannot_replace_new_import(self):
  catalog=self.catalog();row=self.record();catalog.save(row);previous=catalog.load(row['id'])
  original_get=self.bucket.get_object
  def racing_get(**kwargs):
   snapshot=original_get(**kwargs)
   self.bucket.objects[kwargs['Key']]=json.dumps({**previous,'upload_id':'new-import'}).encode()
   return snapshot
  self.bucket.get_object=racing_get
  with self.assertRaises(ValueError):catalog.save_if_unchanged({**row,'status':'importing'},previous)
  self.bucket.get_object=original_get
  self.assertEqual(catalog.load(row['id'])['upload_id'],'new-import')
 def test_two_initial_imports_cannot_claim_same_source(self):
  catalog=self.catalog();row={**self.record(),'status':'importing'}
  catalog.save_if_unchanged(row,{})
  with self.assertRaises(ValueError):catalog.save_if_unchanged(row,{})
 def test_duration_and_metadata_are_not_invented(self):
  f=self.sources.duration_seconds;self.assertEqual(f('1h2m3s'),3723);self.assertEqual(f(12.5),12.5)
  for value in ('bad',None,-5,float('nan')):self.assertIsNone(f(value))
  row=self.sources.public_source({**self.record(),'thumbnail':'javascript:alert(1)','game_name':None});self.assertEqual(row['thumbnail'],'');self.assertEqual(row['game_name'],'')

class SourceOwnerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.bucket=Bucket();self.ns=namespace(self.root,self.bucket)
 def owner(self):
  self.assertTrue(callable(self.ns.get('_source_owner')),'Source ownership resolver missing');return self.ns['_source_owner']('browserA')
 def test_sid_reuse_follows_current_verified_account(self):
  self.ns['_creator_account_save']('browserA',{'account_id':'accountA'});a=self.owner()
  self.ns['_creator_account_save']('browserA',{'account_id':'accountB'});self.assertNotEqual(a,self.owner())
 def test_storage_failure_never_downgrades_account_to_guest(self):
  self.ns['_creator_account_save']('browserA',{'account_id':'accountA'});self.bucket.fail=True
  self.assertTrue(callable(self.ns.get('_source_owner')),'Source ownership resolver missing')
  with self.assertRaises(OSError):self.ns['_source_owner']('browserA')

class TwitchDiscoveryTests(SourceOwnerTests):
 def setUp(self):
  super().setUp();self.ns['_twitch_access']=lambda *a,**kw:{'user_id':'creator'};self.calls=[]
 def api(self,path,data):
  def call(sid,endpoint,params=None):
   self.calls.append((endpoint,params))
   if endpoint==path:return {'data':data}
   if endpoint=='games':return {'data':[{'id':'game1','name':'Fortnite'}]}
   raise AssertionError(endpoint)
  self.ns['_twitch_api']=call
 def test_offline_is_real_empty_live_state(self):
  self.api('streams',[]);self.assertEqual(self.ns['_twitch_content']('browserA','live')['data'],[])
  self.assertEqual(self.calls[0][1]['user_id'],'creator')
 def test_live_has_no_import_capability(self):
  self.api('streams',[{'id':'stream1','user_id':'creator','title':'Ranked','game_name':'Fortnite','thumbnail_url':'https://static-cdn.jtvnw.net/live/{width}x{height}.jpg','started_at':'2026-10-20T20:00:00Z','type':'live'}])
  row=self.ns['_twitch_content']('browserA','live')['data'][0];self.assertFalse(row['importable']);self.assertTrue(row['is_live']);self.assertIn('640x360',row['thumbnail']);self.assertTrue(row['import_reason'])
 def test_own_clip_has_thumbnail_category_and_duration(self):
  self.api('clips',[{'id':'clip1','broadcaster_id':'creator','title':'Win','game_id':'game1','duration':12.5,'thumbnail_url':'https://static-cdn.jtvnw.net/clip.jpg'}])
  row=self.ns['_twitch_content']('browserA','clips')['data'][0];self.assertEqual(row['game_name'],'Fortnite');self.assertEqual(row['duration'],12.5);self.assertTrue(row['thumbnail']);self.assertTrue(row['importable']);self.assertEqual(len(row['source_id']),32)
 def test_long_vod_has_no_media_import(self):
  self.api('videos',[{'id':'vod1','user_id':'creator','duration':'24h2m3s','type':'highlight','title':'Long highlight'}])
  row=self.ns['_twitch_content']('browserA','videos')['data'][0];self.assertEqual(row['duration'],86523);self.assertEqual(row['video_type'],'highlight');self.assertFalse(row['importable']);self.assertTrue(row['import_reason'])
 def test_missing_category_is_not_api_failure(self):
  self.api('clips',[{'id':'clip1','broadcaster_id':'creator','game_id':'game1'}]);original=self.ns['_twitch_api']
  self.ns['_twitch_api']=lambda sid,path,params=None:(_ for _ in ()).throw(OSError()) if path=='games' else original(sid,path,params)
  self.assertEqual(self.ns['_twitch_content']('browserA','clips')['data'][0]['game_name'],'')
 def test_foreign_broadcaster_is_excluded(self):
  self.api('streams',[{'id':'other','user_id':'foreign'}]);self.assertEqual(self.ns['_twitch_content']('browserA','live')['data'],[])

class SourceReuseTests(SourceOwnerTests):
 def setUp(self):
  super().setUp();self.sources=importlib.import_module('web.gsf_sources_v422');self.ns.update(MAX_FILE_BYTES=4*1024**3)
  self.media=self.root/'sessions/browserA/media';self.media.mkdir(parents=True,exist_ok=True)
  from visual.gsf_navigation_stress import MEDIA_FIXTURE
  self.asset=self.media/'source_clip_upload1.mp4';self.asset.write_bytes(MEDIA_FIXTURE)
  self.catalog_owner='guest-browserA';identity=self.sources.source_id(self.catalog_owner,'twitch_clip','creator','clip1')
  self.record={'id':identity,'owner_id':self.catalog_owner,'kind':'twitch_clip','provider':'twitch','provider_user_id':'creator','external_id':'clip1','title':'Win','status':'ready','bucket_key':'uploads/browserA/upload1/video.mp4','analysis_key':'analysis/browserA/upload1/result.json','origin_sid':'browserA','upload_id':'upload1','size':len(MEDIA_FIXTURE),'local_path':str(self.asset)}
  self.bucket.objects[self.record['bucket_key']]=MEDIA_FIXTURE
  self.bucket.head_object=lambda **kw:{'ContentLength':len(self.bucket.objects[kw['Key']])} if kw['Key'] in self.bucket.objects else (_ for _ in ()).throw(FileNotFoundError())
  self.sources.SourceCatalog(self.bucket,'bucket',self.catalog_owner).save(self.record)
 def function(self,name):
  self.assertTrue(callable(self.ns.get(name)),name+' missing');return self.ns[name]
 def test_catalog_listing_confirms_real_imported_asset(self):
  result=self.function('_source_list')('browserA','twitch','imported','');self.assertEqual(result['data'][0]['id'],self.record['id']);self.assertTrue(result['data'][0]['can_analyze'])
 def test_missing_object_is_not_ready(self):
  self.bucket.objects.pop(self.record['bucket_key']);result=self.function('_source_list')('browserA','twitch','imported','');self.assertFalse(result['data'][0]['can_analyze']);self.assertEqual(result['data'][0]['status'],'unavailable')
 def test_reused_source_does_not_download_or_materialize_again(self):
  calls=[];self.ns['_materialize_bucket_object']=lambda *a,**kw:calls.append(a)
  result=self.function('_source_activate')('browserA',self.record['id'],'ai');self.assertTrue(result['ready']);self.assertTrue(result['reused']);self.assertFalse(calls)
  marker=json.loads((self.media/'.direct_upload_ready.json').read_text());self.assertEqual(marker['source_id'],self.record['id'])
 def test_foreign_source_cannot_activate(self):
  self.ns['_creator_account_save']('browserA',{'account_id':'other'})
  with self.assertRaises(LookupError):self.function('_source_activate')('browserA',self.record['id'],'ai')
 def test_invalid_target_cannot_activate(self):
  with self.assertRaises(ValueError):self.function('_source_activate')('browserA',self.record['id'],'publish')
 def test_failed_activation_keeps_previous_project(self):
  marker=self.media/'.direct_upload_ready.json';marker.write_text('{"upload_id":"previous"}')
  self.bucket.objects.pop(self.record['bucket_key'])
  with self.assertRaises(LookupError):self.function('_source_activate')('browserA',self.record['id'],'ai')
  self.assertEqual(json.loads(marker.read_text())['upload_id'],'previous')
 def test_import_in_progress_is_not_downloaded_again(self):
  import time
  self.sources.SourceCatalog(self.bucket,'bucket',self.catalog_owner).save({**self.record,'status':'importing','import_started_at':time.time()})
  self.ns['_twitch_access']=lambda *a,**k:{'user_id':'creator'}
  self.ns['_twitch_clip_source']=lambda *a,**k:(_ for _ in ()).throw(AssertionError('Duplicate download'))
  with self.assertRaises(ValueError):self.ns['_twitch_import_start']('browserA','clip1')
 def test_interrupted_import_becomes_retryable(self):
  import time
  row={**self.record,'status':'importing','import_started_at':time.time()-601}
  checked=self.ns['_source_checked'](row)
  self.assertNotEqual(checked['status'],'importing')
  self.assertTrue(self.sources.public_source(checked)['can_import'])
 def test_same_clip_import_reuses_catalog_before_twitch_media_request(self):
  self.ns['_twitch_access']=lambda *a,**k:{'user_id':'creator'}
  self.ns['_twitch_clip_source']=lambda *a,**k:(_ for _ in ()).throw(AssertionError('Duplicate Twitch media download'))
  result=self.ns['_twitch_import_start']('browserA','clip1');self.assertTrue(result.get('reused'),'Existing imported clip must be reused')
 def test_upload_requires_captured_owner_and_is_registered_once(self):
  self.function('_source_capture_upload')('browserA','upload2')
  marker={'upload_id':'upload2','name':'new.mp4','path':str(self.asset),'bucket_key':'uploads/browserA/upload2/new.mp4','size':self.record['size']}
  self.bucket.objects[marker['bucket_key']]=self.asset.read_bytes()
  self.function('_source_register_marker')('browserA',marker);self.function('_source_register_marker')('browserA',marker)
  rows=self.function('_source_list')('browserA','upload','imported','')['data'];self.assertEqual(len(rows),1)
 def test_legacy_upload_is_not_assigned_to_new_account(self):
  marker={'upload_id':'legacy','path':str(self.asset),'bucket_key':'uploads/browserA/legacy/video.mp4','size':self.record['size']}
  self.ns['_creator_account_save']('browserA',{'account_id':'replacement'})
  self.function('_source_register_marker')('browserA',marker)
  self.assertEqual(self.function('_source_list')('browserA','upload','imported','')['data'],[])
 def test_account_switch_after_upload_start_does_not_transfer_asset(self):
  self.function('_source_capture_upload')('browserA','upload2');self.ns['_creator_account_save']('browserA',{'account_id':'replacement'})
  self.function('_source_register_marker')('browserA',{'upload_id':'upload2','path':str(self.asset),'bucket_key':'uploads/browserA/upload2/video.mp4','size':self.record['size']})
  self.assertEqual(self.function('_source_list')('browserA','upload','imported','')['data'],[])

from test_social_oauth_v421 import TwitchImport
class TwitchLibraryReceipt(TwitchImport):
 def test_successful_real_media_import_is_persisted_in_library(self):
  marker,_,_=self.run_import()
  rows=self.ns['_source_list']('browserA','twitch','imported')['data']
  self.assertEqual(len(rows),1)
  self.assertEqual(rows[0]['external_id'],'clip1')
  self.assertTrue(rows[0]['can_analyze'])
  self.assertEqual(json.loads(marker.read_bytes())['source_id'],rows[0]['id'])

class TwitchImportMetadataRace(TwitchImport):
 def test_metadata_refresh_during_commit_does_not_fail_valid_import(self):
  # run_import uses the real importer, persistent bucket and FFprobe validator.
  factory=self.ns['_source_catalog'];injected=[]
  def catalog_for(sid):
   catalog=factory(sid);original=catalog.save_if_unchanged
   def save(record,previous):
    if record.get('status')=='ready' and not injected:
     injected.append(True);catalog.save({**record,'status':'importing','title':'Titolo aggiornato durante import'})
    return original(record,previous)
   catalog.save_if_unchanged=save
   return catalog
  self.ns['_source_catalog']=catalog_for
  marker,_,_=self.run_import()
  row=json.loads(marker.read_bytes())
  self.assertTrue(injected);self.assertEqual(row['upload_id'],'new-import')
  self.assertFalse(marker.with_name('.direct_upload_error.json').exists())

@unittest.skipUnless(os.environ.get('GSF_BROWSER'),'Runs in blocking browser gate')
class SourceLibraryBrowser(unittest.TestCase):
 def test_real_catalog_folders_actions_and_mobile_geometry(self):
  import shutil,urllib.parse
  from playwright.sync_api import sync_playwright
  fixture=SourceReuseTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  fixture.ns['_twitch_access']=lambda *a,**k:{'user_id':'creator'}
  def api(sid,path,params=None):
   if path=='games':return {'data':[]}
   if path=='streams':return {'data':[]}
   if path=='videos':return {'data':[{'id':'vod1','user_id':'creator','title':'VOD ufficiale','url':'https://www.twitch.tv/videos/vod1','duration':'1h2m3s'}]}
   return {'data':[{'id':'clip1','broadcaster_id':'creator','title':'Clip già importata','url':'https://clips.twitch.tv/clip1','duration':20}]}
  fixture.ns['_twitch_api']=api
  connection={'on':True}
  with sync_playwright() as p:
   engine=getattr(p,os.environ['GSF_BROWSER']);options={'headless':True}
   if engine.name=='chromium':options.update(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   browser=engine.launch(**options)
   try:
    page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("window.GSFNavigation={snapshot:()=>({target:'hub',epoch:1,section:'live'})}")
    def route(r):
     url=urllib.parse.urlsplit(r.request.url);q=urllib.parse.parse_qs(url.query)
     if url.path=='/':r.fulfill(content_type='text/html',body=(ROOT/'web/creator_hub_v156_component/index.html').read_text())
     elif url.path=='/creator-hub/state':r.fulfill(json={'ok':True,'csrf_token':'csrf','account':{'display_name':'Creator'},'social':{'twitch':connection['on']}})
     elif url.path=='/social-connect/twitch/content':r.fulfill(json={'ok':True,**fixture.ns['_twitch_content']('browserA',q.get('type',['clips'])[0])})
     elif url.path=='/creator-hub/sources':r.fulfill(json={'ok':True,**fixture.ns['_source_list']('browserA',q.get('provider',['upload'])[0])})
     else:r.fulfill(json={'ok':True})
    page.route('**/*',route)
    for width,height in [(375,667),(390,844),(393,852),(430,932)]:
     with self.subTest(viewport=(width,height)):
      page.set_viewport_size({'width':width,'height':height});page.goto('http://gsf.test/')
      page.locator('[data-source-open]').wait_for();self.assertEqual(page.locator('[data-source-import]').count(),0)
      self.assertIn('Già importato',page.locator('#sourceLibrary').inner_text())
      page.locator('[data-source-folder="videos"]').click();page.get_by_text('VOD ufficiale',exact=True).wait_for()
      self.assertEqual(page.locator('[data-source-import]').count(),0);self.assertEqual(page.locator('[data-source-open]').count(),0)
      self.assertIn('API ufficiali',page.locator('#sourceLibrary').inner_text())
      page.locator('[data-source-folder="live"]').click();page.get_by_text('Il canale non è in diretta.',exact=True).wait_for()
      page.locator('[data-source-folder="imported"]').click();page.locator('[data-source-editor]').wait_for()
      self.assertEqual(page.evaluate('document.documentElement.scrollWidth'),width)
    page.reload();page.locator('[data-source-editor]').wait_for()
    self.assertEqual(page.locator('[data-source-folder="imported"]').get_attribute('aria-pressed'),'true')
    connection['on']=False;page.reload();page.locator('[data-source-editor]').wait_for(timeout=2000)
    self.assertIn('Twitch scollegato',page.locator('#sourceLibrary').inner_text())
    page.locator('[data-source-folder="clips"]').click();page.locator('[data-source-connect]').wait_for()
    self.assertFalse(errors,errors)
   finally:browser.close()
