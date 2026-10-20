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
