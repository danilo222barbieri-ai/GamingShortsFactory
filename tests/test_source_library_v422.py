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
