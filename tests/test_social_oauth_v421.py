"""Social OAuth regressions: real helpers and HTTP routes, isolated storage/API transport."""
import ast,base64,hashlib,hmac,io,json,os,re,secrets,tempfile,threading,time,unittest,urllib.parse,urllib.request,uuid,sys
from pathlib import Path
from types import SimpleNamespace
from cryptography.fernet import Fernet,InvalidToken
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from web import gsf_social_oauth_v421 as social421

class Bucket:
    def __init__(self):self.objects={};self.fail=False
    def put_object(self,**kw):
        if self.fail:raise OSError('storage unavailable')
        current=self.objects.get(kw['Key'])
        etag='"'+hashlib.md5(current).hexdigest()+'"' if current is not None else None
        if (kw.get('IfNoneMatch')=='*' and current is not None) or ('IfMatch' in kw and kw['IfMatch']!=etag):
            error=OSError('conditional conflict');error.response={'Error':{'Code':'PreconditionFailed'}};raise error
        self.objects[kw['Key']]=kw['Body']
    def get_object(self,**kw):
        if self.fail:raise OSError('storage unavailable')
        if kw['Key'] not in self.objects:
            e=FileNotFoundError();e.response={'Error':{'Code':'NoSuchKey'}};raise e
        return {'Body':io.BytesIO(self.objects[kw['Key']]),'ETag':'"'+hashlib.md5(self.objects[kw['Key']]).hexdigest()+'"'}
    def delete_object(self,**kw):
        if self.fail:raise OSError('storage unavailable')
        self.objects.pop(kw['Key'],None)
    def list_objects_v2(self,**kw):return {'Contents':[{'Key':k} for k in self.objects if k.startswith(kw.get('Prefix',''))]}

class Reply:
    def __init__(self,sid='browserA',data=b'',ctype='application/x-www-form-urlencoded'):
        self.headers={'X-GSF-Session-ID':sid,'Content-Length':str(len(data)),'Content-Type':ctype};self.rfile=io.BytesIO(data);self.wfile=io.BytesIO();self.status=0;self.response={}
    def send_response(self,status):self.status=status
    def send_header(self,key,value):self.response[key]=value
    def end_headers(self):pass

def namespace(root,bucket):
    import html,urllib.error
    ns=dict(globals(),ROOT=root,S3_BUCKET='bucket',_bucket_enabled=lambda:True,_s3=lambda:bucket,
      PUBLIC_APP_URL='https://gsf.test',META_APP_ID='meta-app',META_APP_SECRET='meta-secret',INSTAGRAM_APP_ID='ig-app',INSTAGRAM_APP_SECRET='ig-secret',
      INSTAGRAM_REDIRECT_URI='https://gsf.test/auth/instagram/callback',FACEBOOK_REDIRECT_URI='https://gsf.test/auth/facebook/callback',
      META_GRAPH_VERSION='v24.0',FACEBOOK_SCOPES='public_profile,pages_show_list',META_SCOPES='pages_show_list,instagram_basic,instagram_content_publish,pages_read_engagement',INSTAGRAM_SCOPES='instagram_business_basic,instagram_business_content_publish,instagram_business_manage_insights',
      ID_RE=re.compile(r'^[A-Za-z0-9_-]{1,80}$'),_STATE_LOCKS={},_STATE_LOCKS_GUARD=threading.Lock(),_ANALYTICS_LOCK=threading.Lock(),_CONTENT_MEMORY_LOCK=threading.Lock(),_ANALYTICS_TICK={},html=html)
    ns['_social421']=social421
    tree=ast.parse((ROOT/'web/direct_upload_server.py').read_text())
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)],type_ignores=[]),'<real-companion>','exec'),ns)
    ns.update(_bucket_enabled=lambda:True,_s3=lambda:bucket)
    return ns

class MetaOAuth(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.bucket=Bucket();self.ns=namespace(self.root,self.bucket)
        self.env=unittest.mock.patch.dict(os.environ,{'GSF_DATA_ENCRYPTION_KEY':'test-key'});self.env.start();self.addCleanup(self.env.stop)
    def begin(self,provider='facebook',prefix='gsfacf_'):
        return self.ns['_creator_state_begin']('browserA',provider,prefix)
    def test_facebook_callback_rejects_another_browser_before_exchange(self):
        state=self.begin();calls=[];self.ns['_oauth_json']=lambda *a,**k:calls.append(a) or {}
        reply=Reply('browserB');self.ns['_creator_facebook_callback'](reply,{'state':[state],'code':['private-code']})
        self.assertEqual(reply.status,400);self.assertFalse(calls,'Cross-session callback must not exchange or attach another browser token')
    def test_facebook_start_uses_dedicated_redirect(self):
        reply=Reply();self.ns['_creator_facebook_start'](reply,'browserA');q=urllib.parse.parse_qs(urllib.parse.urlsplit(reply.response['Location']).query)
        self.assertEqual(q['redirect_uri'],['https://gsf.test/auth/facebook/callback']);self.assertNotIn('email',q['scope'][0])
    def test_signed_callback_exists_before_any_session_guard(self):
        self.assertTrue('_meta_signed_callback' in self.ns,'Public signed callbacks are not implemented yet')

    def signed(self,uid='42',secret='meta-secret',**fields):
        data={'algorithm':'HMAC-SHA256','user_id':uid,**fields};enc=lambda b:base64.urlsafe_b64encode(b).decode().rstrip('=')
        body=enc(json.dumps(data).encode());return enc(hmac.new(secret.encode(),body.encode(),hashlib.sha256).digest())+'.'+body
    def call_signed(self,kind='data-deletion',signed=None):
        reply=Reply('',urllib.parse.urlencode({'signed_request':signed or self.signed()}).encode());self.ns['_meta_signed_callback'](reply,kind);return reply
    def test_valid_signature_and_wrong_algorithm_or_malformed_payload(self):
        social=social421
        self.assertEqual(social.verify_meta_signed_request(self.signed(),'meta-secret'),'42')
        for value in [self.signed(secret='wrong'),self.signed(algorithm='none'),'x.y','garbage',self.signed(uid='../42'),self.signed(uid=42)]:
            with self.subTest(case=value[:8]),self.assertRaises(ValueError):social.verify_meta_signed_request(value,'meta-secret')
    def test_unknown_user_deletion_returns_durable_private_status(self):
        reply=self.call_signed();self.assertEqual(reply.status,200);body=json.loads(reply.wfile.getvalue());code=body['confirmation_code'];self.assertIn('/auth/meta/data-deletion/status?code='+code,body['url'])
        status=Reply('');self.ns['_meta_deletion_status'](status,{'code':[code]});self.assertEqual(status.status,200);self.assertEqual(json.loads(status.wfile.getvalue())['status'],'completed')
        self.assertEqual(set(json.loads(status.wfile.getvalue())),{'status','completed_at'})
        missing=Reply('');self.ns['_meta_deletion_status'](missing,{'code':['x'*32]});self.assertEqual(missing.status,404)
    def test_wrong_signature_does_not_touch_storage(self):
        reply=self.call_signed(signed=self.signed(secret='wrong'));self.assertEqual(reply.status,400);self.assertFalse(self.bucket.objects)
    def seed(self):
        for sid,uid in [('browserA','42'),('browserB','99')]:
            profile={'account_id':'account'+uid,'display_name':'Meta '+uid,'providers':{'facebook':{'id':uid,'display_name':'Meta '+uid},'google':{'id':'google'+uid}}}
            self.ns['_creator_account_save'](sid,profile)
            self.ns['_social_connection_save'](sid,'facebook',{'access_token':'private-token-'+uid,'facebook_user_id':uid})
            self.ns['_meta_index_add']('facebook',uid,sid)
            self.ns['_oauth_object_save']('social-connections/'+sid+'/instagram.json',{'ig_user_id':'ig'+uid,'facebook_user_id':uid,'oauth_mode':'facebook_login','access_token':'private-ig'},True)
            self.ns['_oauth_object_save']('social-connections/'+sid+'/tiktok.json',{'access_token':'keep-tiktok'},True)
            self.ns['_oauth_object_save']('social-analytics/'+sid+'/analytics_v148.json',{'records':[{'platform':'Facebook','content_id':'remove'},{'platform':'YouTube','content_id':'keep'}]})
            (self.root/'sessions'/sid/'project.json').write_text('{"keep":true}')
    def test_deauthorize_removes_only_matching_meta_data_and_preserves_project(self):
        self.seed();reply=self.call_signed('deauthorize');self.assertEqual(reply.status,200)
        self.assertFalse(self.ns['_social_connection_load']('browserA','facebook'))
        self.assertTrue(self.ns['_social_connection_load']('browserB','facebook'))
        self.assertNotIn('social-connections/browserA/instagram.json',self.bucket.objects)
        self.assertIn('social-connections/browserA/tiktok.json',self.bucket.objects)
        profile=self.ns['_creator_account_load']('browserA');self.assertNotIn('facebook',profile['providers']);self.assertIn('google',profile['providers']);self.assertNotIn('display_name',profile)
        self.assertTrue((self.root/'sessions/browserA/project.json').exists())
        analytics=self.ns['_oauth_object_read']('social-analytics/browserA/analytics_v148.json');self.assertEqual(analytics['records'],[{'platform':'YouTube','content_id':'keep'}])
        self.assertNotIn('private-token',reply.wfile.getvalue().decode())
    def test_stale_reverse_index_never_deletes_a_new_users_connection(self):
        self.seed();self.ns['_meta_index_add']('facebook','42','browserB')
        self.assertEqual(self.call_signed('deauthorize').status,200)
        self.assertTrue(self.ns['_social_connection_load']('browserB','facebook'),'An old session association cannot authorize deleting the current different provider account')
        self.assertIn('facebook',self.ns['_creator_account_load']('browserB')['providers'])
    def test_credentials_do_not_follow_the_browser_into_another_gsf_account(self):
        self.seed();profile=self.ns['_creator_account_load']('browserA');profile['account_id']='replacement-account';self.ns['_creator_account_save']('browserA',profile)
        self.assertFalse(self.ns['_social_connection_load']('browserA','facebook'),'The session cookie alone is not ownership after a different GSF login')
    def test_meta_derived_memory_is_anonymized_without_deleting_video_recipe(self):
        self.seed();key='content-memory/browserA/memory_v145.json'
        self.bucket.objects[key]=json.dumps([{'fingerprint':'recipe','start':3,'platform':'Facebook','performance_score':99,'analytics_updated_at':1}]).encode()
        self.assertEqual(self.call_signed().status,200)
        row=json.loads(self.bucket.objects[key])[0];self.assertEqual(row['fingerprint'],'recipe');self.assertEqual(row['start'],3);self.assertNotIn('platform',row);self.assertNotIn('performance_score',row)
    def test_inflight_analytics_cannot_restore_deleted_meta_records(self):
        self.seed()
        def collect(sid,row):
            if row['platform']=='Facebook':self.assertEqual(self.call_signed().status,200)
            return row
        self.ns['_analytics_collect_one']=collect
        self.ns['_analytics_collect_all']('browserA',force=True)
        rows=self.ns['_oauth_object_read']('social-analytics/browserA/analytics_v148.json')['records']
        self.assertEqual(rows,[{'platform':'YouTube','content_id':'keep'}])
    def test_partial_deletion_retry_finishes_remaining_meta_cleanup(self):
        self.seed();save=self.ns['_oauth_object_save'];failed=[]
        def once(key,payload,*args,**kwargs):
            if key=='social-analytics/browserA/analytics_v148.json' and not failed:failed.append(True);raise OSError('temporary storage failure')
            return save(key,payload,*args,**kwargs)
        self.ns['_oauth_object_save']=once
        self.assertEqual(self.call_signed().status,503)
        self.assertEqual(self.call_signed().status,200)
        rows=self.ns['_oauth_object_read']('social-analytics/browserA/analytics_v148.json')['records']
        self.assertEqual(rows,[{'platform':'YouTube','content_id':'keep'}],'A retry must finish after token/profile removal already succeeded')
    def test_instagram_deletion_after_sid_reuse_preserves_current_owner_identity_and_analytics(self):
        self.ns['_creator_account_save']('browserA',{'account_id':'accountA','providers':{'instagram':{'id':'42'}}})
        self.ns['_instagram_user_save']('browserA',{'ig_user_id':'42','access_token':'old-owner-token'})
        self.ns['_meta_index_add']('instagram','42','browserA')
        self.ns['_creator_account_save']('browserA',{'account_id':'accountB','display_name':'Creator B','providers':{'instagram':{'id':'99','display_name':'Creator B'}}})
        self.ns['_oauth_object_save']('social-analytics/browserA/analytics_v148.json',{'records':[{'platform':'Instagram','content_id':'B-content','meta_owner_id':'accountB'},{'platform':'Instagram','content_id':'A-content','meta_owner_id':'accountA'}]})
        self.ns['_meta_index_add']('instagram','99','browserA')
        reply=self.call_signed(signed=self.signed(secret='ig-secret'));self.assertEqual(reply.status,200)
        profile=self.ns['_creator_account_load']('browserA');self.assertEqual(profile['providers']['instagram']['id'],'99');self.assertEqual(profile['display_name'],'Creator B')
        rows=self.ns['_oauth_object_read']('social-analytics/browserA/analytics_v148.json')['records'];self.assertEqual(rows,[{'platform':'Instagram','content_id':'B-content','meta_owner_id':'accountB'}])
        self.assertTrue(self.ns['_oauth_object_read'](self.ns['_meta_index_key']('instagram','99'),True))
        old_profile=self.ns['_oauth_object_read'](self.ns['_creator_profile_key']('accountA'));self.assertNotIn('instagram',old_profile['providers'])
    def test_inflight_collection_preserves_new_owner_rows_after_old_owner_deletion(self):
        self.test_instagram_deletion_after_sid_reuse_preserves_current_owner_identity_and_analytics()
        # Recreate an old association and token alongside B's surviving records.
        self.ns['_oauth_object_save']('social-connections/browserA/instagram.json',{'owner_id':'accountA','ig_user_id':'42','access_token':'old'},True)
        self.ns['_meta_index_add']('instagram','42','browserA')
        def collect(sid,row):
            self.assertEqual(self.call_signed(signed=self.signed(secret='ig-secret')).status,200)
            return row
        self.ns['_analytics_collect_one']=collect
        self.ns['_analytics_collect_all']('browserA',force=True)
        rows=self.ns['_oauth_object_read']('social-analytics/browserA/analytics_v148.json')['records']
        self.assertEqual(rows,[{'platform':'Instagram','content_id':'B-content','meta_owner_id':'accountB'}])
    def test_data_deletion_failure_never_reports_success(self):
        self.bucket.fail=True;reply=self.call_signed();self.assertEqual(reply.status,503)
    def test_missing_secret_is_not_an_unsigned_bypass(self):
        self.ns.update(META_APP_SECRET='',INSTAGRAM_APP_SECRET='');self.assertEqual(self.call_signed().status,503)
    def test_callback_state_is_single_use_session_bound_and_expiring(self):
        state=self.begin();self.assertFalse(self.ns['_social_state_finish'](Reply('browserB'),state,'gsfacf_','facebook'))
        self.assertFalse(self.ns['_social_state_finish'](Reply(),state+'!','gsfacf_','facebook'))
        self.assertTrue(self.ns['_social_state_finish'](Reply(),state,'gsfacf_','facebook'))
        self.assertFalse(self.ns['_social_state_finish'](Reply(),state,'gsfacf_','facebook'))
        state=self.begin();path=self.root/'social_oauth'/(state+'.json');data=json.loads(path.read_text());data['created']=time.time()-901;path.write_text(json.dumps(data))
        self.assertFalse(self.ns['_social_state_finish'](Reply(),state,'gsfacf_','facebook'))
    def test_facebook_exchange_and_pages_persist_encrypted(self):
        state=self.begin();calls=[]
        def api(url,**kw):
            calls.append((url,kw))
            if '/oauth/access_token' in url:return {'access_token':'private-token','expires_in':3600}
            if '/me/accounts' in url:return {'data':[{'id':'page1','access_token':'private-page'}]}
            return {'id':'42','name':'Creator'}
        self.ns['_oauth_json']=api;reply=Reply();self.ns['_creator_facebook_callback'](reply,{'state':[state],'code':['private-code']})
        self.assertEqual(reply.status,302);saved=self.ns['_social_connection_load']('browserA','facebook');self.assertEqual(saved['pages'][0]['id'],'page1')
        self.assertFalse(any(b'private-token' in data for data in self.bucket.objects.values()))
        self.assertTrue(all('private-token' not in url and 'private-code' not in url for url,_ in calls))
    def test_callback_denial_and_api_error_do_not_echo_private_input(self):
        for denied in (True,False):
            state=self.begin();self.ns['_oauth_json']=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('private-token private-code'))
            reply=Reply();query={'state':[state],'code':['private-code']}
            if denied:query['error']=['private-error']
            self.ns['_creator_facebook_callback'](reply,query)
            self.assertIn(reply.status,(400,502));self.assertNotIn(b'private-',reply.wfile.getvalue())
    def test_user_disconnect_requires_provider_revocation(self):
        self.seed();calls=[];self.assertTrue('_meta_disconnect' in self.ns,'Remote deauthorization is missing')
        self.ns['_oauth_json']=lambda url,**kw:calls.append((url,kw)) or {'success':True}
        self.ns['_meta_disconnect']('browserA','facebook')
        self.assertEqual(calls[0][1]['method'],'DELETE');self.assertIn('/me/permissions',calls[0][0]);self.assertNotIn('private-token',calls[0][0])
        self.assertFalse(self.ns['_social_connection_load']('browserA','facebook'))
    def test_instagram_token_commit_updates_cache_only_after_persistence(self):
        self.ns['_instagram_user_save']('browserA',{'access_token':'old','ig_user_id':'42'})
        self.ns['_instagram_user_write_local']('browserA',{'access_token':'old','ig_user_id':'42'})
        self.ns['_instagram_user_save']('browserA',{'access_token':'new','ig_user_id':'42'})
        self.assertEqual(self.ns['_instagram_user_load']('browserA')['access_token'],'new')
        self.bucket.fail=True
        with self.assertRaises(OSError):self.ns['_instagram_user_save']('browserA',{'access_token':'unsaved','ig_user_id':'42'})
        self.bucket.fail=False
        self.assertEqual(self.ns['_instagram_user_load']('browserA')['access_token'],'new')
    def test_expired_meta_permission_can_be_disconnected(self):
        self.seed()
        def revoked(*args,**kwargs):
            raise urllib.error.HTTPError('https://graph.facebook.com/me/permissions',400,'Bad Request',{},io.BytesIO(b'{"error":{"code":190}}'))
        self.ns['_oauth_json']=revoked
        self.ns['_meta_disconnect']('browserA','facebook')
        self.assertFalse(self.ns['_social_connection_load']('browserA','facebook'))
    def test_unrelated_meta_bad_request_keeps_connection(self):
        self.seed()
        def bad_request(*args,**kwargs):
            raise urllib.error.HTTPError('https://graph.facebook.com/me/permissions',400,'Bad Request',{},io.BytesIO(b'{"error":{"code":100}}'))
        self.ns['_oauth_json']=bad_request
        with self.assertRaises(urllib.error.HTTPError):self.ns['_meta_disconnect']('browserA','facebook')
        self.assertTrue(self.ns['_social_connection_load']('browserA','facebook'))
    def test_remote_disconnect_failure_keeps_connection_for_retry(self):
        self.seed();self.assertTrue('_meta_disconnect' in self.ns,'Remote deauthorization is missing')
        self.ns['_oauth_json']=lambda *a,**k:(_ for _ in ()).throw(OSError('network unavailable'))
        with self.assertRaises(OSError):self.ns['_meta_disconnect']('browserA','facebook')
        self.assertTrue(self.ns['_social_connection_load']('browserA','facebook'))
    def test_public_signed_route_does_not_require_browser_session(self):
        from http.server import BaseHTTPRequestHandler
        tree=ast.parse((ROOT/'web/direct_upload_server.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Handler')
        self.ns.update(BaseHTTPRequestHandler=BaseHTTPRequestHandler,urlparse=urllib.parse.urlparse,parse_qs=urllib.parse.parse_qs)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<real-http-router>','exec'),self.ns)
        reply=Reply('',urllib.parse.urlencode({'signed_request':self.signed()}).encode());reply.path='/auth/meta/data-deletion'
        self.ns['Handler'].do_POST(reply);self.assertEqual(reply.status,200)
        forbidden=Reply('browserA',b'{"platform":"facebook"}','application/json');forbidden.path='/creator-hub/social/disconnect'
        self.ns['Handler'].do_POST(forbidden);self.assertEqual(forbidden.status,403)

class TikTokOAuth(unittest.TestCase):
    # Inherit storage/session cases too: providers share the same GSF boundary.
    def setUp(self):
        MetaOAuth.setUp(self);self.ns.update(TIKTOK_CLIENT_KEY='tt-key',TIKTOK_CLIENT_SECRET='tt-secret',TIKTOK_REDIRECT_URI='https://gsf.test/auth/tiktok/callback',TIKTOK_SCOPE='user.info.basic,video.publish')
    def test_tiktok_start_uses_dedicated_callback_and_exact_session_state(self):
        reply=Reply();self.ns['_tiktok_oauth_start'](reply,'browserA');q=urllib.parse.parse_qs(urllib.parse.urlsplit(reply.response['Location']).query)
        self.assertEqual(q['redirect_uri'],['https://gsf.test/auth/tiktok/callback']);self.assertIn('video.publish',q['scope'][0]);self.assertNotIn('video.upload',q['scope'][0])
        pending=json.loads((self.root/'social_oauth'/(q['state'][0]+'.json')).read_text());self.assertEqual(pending['provider'],'tiktok')
    def test_tiktok_cross_browser_callback_never_exchanges_token(self):
        reply=Reply();self.ns['_tiktok_oauth_start'](reply,'browserA');q=urllib.parse.parse_qs(urllib.parse.urlsplit(reply.response['Location']).query);calls=[];self.ns['_oauth_json']=lambda *a,**kw:calls.append(a) or {}
        other=Reply('browserB');self.ns['_tiktok_oauth_callback'](other,{'state':q['state'],'code':['private-code']});self.assertEqual(other.status,400);self.assertFalse(calls)
    def test_tiktok_valid_exchange_and_disconnect_use_existing_encrypted_storage(self):
        start=Reply();self.ns['_tiktok_oauth_start'](start,'browserA')
        query=urllib.parse.parse_qs(urllib.parse.urlsplit(start.response['Location']).query)
        calls=[]
        def official(url,**kwargs):
            calls.append((url,kwargs))
            if '/oauth/token/' in url:return {'access_token':'tt-access','refresh_token':'tt-refresh','open_id':'owner','scope':'user.info.basic,video.publish','expires_in':3600}
            if '/user/info/' in url:return {'data':{'user':{'open_id':'owner','display_name':'Creator'}}}
            if '/oauth/revoke/' in url:return {}
            raise AssertionError('Unexpected provider endpoint')
        self.ns['_oauth_json']=official
        callback=Reply();self.ns['_tiktok_oauth_callback'](callback,{'state':query['state'],'code':['private-code']})
        self.assertEqual(callback.status,302)
        self.assertEqual(self.ns['_tiktok_user_load']('browserA')['open_id'],'owner')
        self.assertNotIn(b'tt-access',self.bucket.objects[self.ns['_tiktok_user_key']('browserA')])
        self.assertNotIn('private-code',calls[0][0])
        self.ns['_tiktok_disconnect']('browserA')
        self.assertFalse(self.ns['_tiktok_user_load']('browserA'))
    def test_failed_token_persistence_keeps_last_committed_credentials(self):
        self.ns['_tiktok_user_save']('browserA',{'access_token':'old','open_id':'owner'})
        self.bucket.fail=True
        with self.assertRaises(OSError):self.ns['_tiktok_user_save']('browserA',{'access_token':'unsaved','open_id':'owner'})
        self.bucket.fail=False;self.assertEqual(self.ns['_tiktok_user_load']('browserA')['access_token'],'old')
    def test_refresh_failure_cannot_return_an_expired_token(self):
        self.ns['_tiktok_user_load']=lambda sid:{'access_token':'expired','open_id':'owner','refresh_token':'refresh','expires_at':time.time()-5}
        self.ns['_oauth_json']=lambda *a,**kw:(_ for _ in ()).throw(OSError('private-token'))
        with self.assertRaises(ValueError):self.ns['_tiktok_analytics_token']('browserA')
    def test_refresh_rotates_and_persists_only_matching_owner(self):
        token={'access_token':'expired','open_id':'owner','refresh_token':'old-refresh','expires_at':time.time()-5};saved=[]
        self.ns['_tiktok_user_load']=lambda sid:token
        self.ns['_tiktok_user_save']=lambda sid,data:saved.append(data)
        self.ns['_oauth_json']=lambda *a,**kw:{'access_token':'new-token','refresh_token':'new-refresh','open_id':'owner','expires_in':3600,'refresh_expires_in':7200}
        out=self.ns['_tiktok_analytics_token']('browserA');self.assertEqual(out['refresh_token'],'new-refresh');self.assertTrue(saved);self.assertGreater(out['expires_at'],time.time())
        self.ns['_oauth_json']=lambda *a,**kw:{'access_token':'wrong-user','open_id':'different','expires_in':3600}
        with self.assertRaises(ValueError):self.ns['_tiktok_analytics_token']('browserA')

from unittest import mock

class TikTokPublication(unittest.TestCase):
    def setUp(self):
        from web import publish_multi_v413
        self.pm=publish_multi_v413;self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.video=Path(self.tmp.name)/'short.mp4';self.video.write_bytes(b'x'*4096)
    def transport(self,statuses):
        responses=[{'data':{'privacy_level_options':['SELF_ONLY']},'error':{'code':'ok'}},{'data':{'upload_url':'https://upload.tiktok.test/file','publish_id':'p_1'},'error':{'code':'ok'}},None]+[{'data':{'status':s},'error':{'code':'ok'}} for s in statuses]
        calls=[]
        def opener(req,timeout=0):
            calls.append(req.full_url);data=responses.pop(0);resp=io.BytesIO(json.dumps(data or {}).encode());resp.status=201 if data is None else 200;return resp
        return opener,calls
    def test_failed_post_after_successful_upload_cannot_be_reported_published(self):
        opener,calls=self.transport(['FAILED'])
        with self.assertRaises(self.pm.PublishError):self.pm.tiktok_direct_post('token',str(self.video),{'caption':'Test'},'private',opener=opener)
    def test_last_put_timeout_retains_the_known_publish_id(self):
        opener,_calls=self.transport(['PUBLISH_COMPLETE'])
        def ambiguous(req,timeout=0):
            if req.get_method()=='PUT':raise TimeoutError('accepted bytes, response lost')
            return opener(req,timeout)
        with self.assertRaises(self.pm.PublishUnconfirmed) as err:self.pm.tiktok_direct_post('token',str(self.video),{'caption':'Test'},'private',opener=ambiguous)
        self.assertEqual(err.exception.publish_id,'p_1')
    def test_only_publish_complete_is_success(self):
        opener,calls=self.transport(['PUBLISH_COMPLETE']);out=self.pm.tiktok_direct_post('token',str(self.video),{'caption':'Test'},'private',opener=opener)
        self.assertTrue(out['ok']);self.assertTrue(any('/status/fetch/' in u for u in calls),'Upload accepted is not publication confirmed')
    def test_bounded_processing_retains_id_and_never_claims_success(self):
        self.assertTrue(hasattr(self.pm,'PublishUnconfirmed'),'Unknown publication needs retained status identity')
        opener,calls=self.transport(['PROCESSING_UPLOAD']*30)
        with mock.patch.object(self.pm.time,'sleep'),self.assertRaises(self.pm.PublishUnconfirmed) as err:self.pm.tiktok_direct_post('token',str(self.video),{'caption':'Test'},'private',opener=opener)
        self.assertEqual(err.exception.publish_id,'p_1');self.assertEqual(len(calls),33)

class TwitchOAuth(unittest.TestCase):
    def setUp(self):
        MetaOAuth.setUp(self);self.ns.update(TWITCH_CLIENT_ID='tw-id',TWITCH_CLIENT_SECRET='tw-secret',TWITCH_SCOPES='channel:manage:clips',TWITCH_REDIRECT_URI='https://gsf.test/auth/twitch/callback')
    def api(self,url,**kw):
        if '/oauth2/token' in url:return {'access_token':'tw-access','refresh_token':'tw-refresh','expires_in':3600,'scope':['channel:manage:clips']}
        if '/validate' in url:return {'client_id':'tw-id','user_id':'42','scopes':['channel:manage:clips'],'expires_in':3600}
        if '/users' in url:return {'data':[{'id':'42','login':'creator','display_name':'Creator'}]}
        if '/clips/downloads' in url:return {'data':[{'clip_id':'clip1','landscape_download_url':'https://production.assets.clips.twitchcdn.net/clip.mp4'}]}
        if '/clips' in url:return {'data':[{'id':'clip1','broadcaster_id':'42','title':'Clip','duration':20,'url':'https://clips.twitch.tv/clip1'}]}
        if '/videos' in url:return {'data':[{'id':'vod1','user_id':'42','title':'VOD','url':'https://www.twitch.tv/videos/vod1'}]}
        return {}
    def connected(self):
        self.assertTrue('_twitch_oauth_start' in self.ns,'Twitch OAuth is not implemented')
        self.ns['_oauth_json']=self.api;reply=Reply();self.ns['_twitch_oauth_start'](reply,'browserA');q=urllib.parse.parse_qs(urllib.parse.urlsplit(reply.response['Location']).query)
        callback=Reply();self.ns['_twitch_oauth_callback'](callback,{'state':q['state'],'code':['private-code']});self.assertEqual(callback.status,302);return q
    def test_content_retry_preserves_reconnect_error(self):
        def access(sid,force_validate=False):
            if force_validate:raise social421.TwitchError("Ricollega Twitch.",401)
            return {'access_token':'private-access'}
        self.ns['_twitch_access']=access
        self.ns['_oauth_json']=lambda *a,**kw:(_ for _ in ()).throw(urllib.error.HTTPError('https://api.twitch.tv/helix/clips',401,'provider private details',{},None))
        with self.assertRaises(social421.TwitchError) as error:self.ns['_twitch_api']('browserA','clips')
        self.assertEqual(error.exception.status,401)
        self.assertIn('Ricollega',str(error.exception))
    def test_content_errors_keep_actionable_status_without_provider_details(self):
        self.ns['_twitch_access']=lambda *a,**kw:{'access_token':'private-access'}
        for status,expected in [(403,403),(429,429),(500,503),(503,503)]:
            with self.subTest(status=status):
                self.ns['_oauth_json']=lambda *a,**kw:(_ for _ in ()).throw(urllib.error.HTTPError('https://api.twitch.tv/helix/clips',status,'private-access',{},None))
                with self.assertRaises(social421.TwitchError) as error:self.ns['_twitch_api']('browserA','clips')
                self.assertEqual(error.exception.status,expected)
                self.assertNotIn('private-access',str(error.exception))
    def test_code_exchange_validation_and_identity_are_bound_to_session(self):
        q=self.connected();self.assertEqual(q['redirect_uri'],['https://gsf.test/auth/twitch/callback']);self.assertEqual(q['scope'],['channel:manage:clips'])
        self.assertEqual(self.ns['_twitch_access']('browserA')['user_id'],'42')
        with self.assertRaises(social421.TwitchError):self.ns['_twitch_access']('browserB')
        self.assertFalse(any(b'tw-access' in raw for raw in self.bucket.objects.values()))
    def test_state_mismatch_and_denial_do_not_exchange(self):
        self.assertTrue('_twitch_oauth_start' in self.ns,'Twitch OAuth is not implemented');reply=Reply();self.ns['_twitch_oauth_start'](reply,'browserA');q=urllib.parse.parse_qs(urllib.parse.urlsplit(reply.response['Location']).query)
        calls=[];self.ns['_oauth_json']=lambda *a,**kw:calls.append(a) or {}
        denied=Reply('browserB');self.ns['_twitch_oauth_callback'](denied,{'state':q['state'],'code':['code']});self.assertEqual(denied.status,400);self.assertFalse(calls)
        cancelled=Reply();self.ns['_twitch_oauth_callback'](cancelled,{'state':q['state'],'error':['access_denied']});self.assertEqual(cancelled.status,400);self.assertFalse(calls)
    def test_periodic_validation_and_refresh(self):
        self.connected();token=self.ns['_social_connection_load']('browserA','twitch');token['validated_at']=time.time()-3601;token['expires_at']=time.time()-1;self.ns['_social_connection_save']('browserA','twitch',token)
        calls=[]
        def api(url,**kw):calls.append(url);return self.api(url,**kw)
        self.ns['_oauth_json']=api;out=self.ns['_twitch_access']('browserA');self.assertGreater(out['expires_at'],time.time());self.assertTrue(any('/token' in u for u in calls));self.assertTrue(any('/validate' in u for u in calls))
    def test_disconnect_revokes_and_removes_credentials(self):
        self.connected();calls=[];self.ns['_oauth_json']=lambda url,**kw:calls.append((url,kw)) or {}
        self.ns['_twitch_disconnect']('browserA');self.assertIn('/revoke',calls[0][0]);self.assertNotIn('tw-access',calls[0][0]);self.assertFalse(self.ns['_social_connection_load']('browserA','twitch'))
    def test_clips_are_officially_importable_but_vods_are_metadata_only(self):
        self.connected();clips=self.ns['_twitch_content']('browserA','clips');vods=self.ns['_twitch_content']('browserA','videos')
        self.assertTrue(clips['data'][0]['importable']);self.assertFalse(vods['data'][0]['importable']);self.assertIn('API',vods['data'][0]['import_reason'])
    def test_other_broadcaster_and_deleted_clip_cannot_be_imported(self):
        self.connected()
        self.ns['_twitch_api']=lambda sid,path,params=None:{'data':[{'id':'clip1','broadcaster_id':'99'}]}
        with self.assertRaises(PermissionError):self.ns['_twitch_clip_source']('browserA','clip1')
        self.ns['_twitch_api']=lambda *a,**kw:{'data':[]}
        with self.assertRaises(LookupError):self.ns['_twitch_clip_source']('browserA','deleted')
    def test_api_outage_preserves_connection_and_project(self):
        self.connected();(self.root/'sessions/browserA/project.json').write_text('{"keep":true}')
        self.ns['_oauth_json']=lambda *a,**kw:(_ for _ in ()).throw(OSError('private-token'))
        with self.assertRaises(social421.TwitchError):self.ns['_twitch_content']('browserA','clips')
        self.assertTrue(self.ns['_social_connection_load']('browserA','twitch'));self.assertTrue((self.root/'sessions/browserA/project.json').exists())

class TwitchImport(unittest.TestCase):
    setUp=TwitchOAuth.setUp
    api=TwitchOAuth.api
    connected=TwitchOAuth.connected
    def test_official_media_download_has_host_redirect_and_size_boundaries(self):
        url='https://production.assets.clips.twitchcdn.net/file.mp4?signature=private'
        for bad in ['http://production.assets.clips.twitchcdn.net/x','https://127.0.0.1/x','https://twitchcdn.net.evil.test/x','https://user:secret@production.assets.clips.twitchcdn.net/x']:
            with self.subTest(url=bad),self.assertRaises(social421.TwitchError):social421.validate_twitch_media_url(bad)
        self.assertEqual(social421.validate_twitch_media_url(url),url)
        target=self.root/'clip.tmp';response=io.BytesIO(b'valid-media');response.headers={'Content-Length':'11'}
        self.assertEqual(social421.download_twitch_clip(url,target,100,opener=lambda *a,**kw:response),11)
        self.assertEqual(target.read_bytes(),b'valid-media')
        oversized=io.BytesIO(b'oversized');oversized.headers={}
        other=self.root/'bad.tmp'
        with self.assertRaises(social421.TwitchError):social421.download_twitch_clip(url,other,2,opener=lambda *a,**kw:oversized)
        self.assertFalse(other.exists())
    def run_import(self,fail=False,replace=False):
        import subprocess,shutil
        self.assertIsNotNone(shutil.which("ffprobe"),"Import contracts require the real FFprobe media validator")
        from visual.gsf_navigation_stress import MEDIA_FIXTURE
        self.connected();media=self.root/'sessions/browserA/media';media.mkdir(parents=True,exist_ok=True)
        marker=media/'.direct_upload_ready.json';old=b'{"upload_id":"old","path":"old-project.mp4"}';marker.write_bytes(old)
        source=self.ns['_twitch_clip_source']('browserA','clip1');lock=threading.Lock();lock.acquire();prescan=[]
        self.bucket.head_object=lambda **kw:{'ContentLength':len(self.bucket.objects[kw['Key']])}
        self.bucket.upload_file=lambda filename,bucket,key,**kw:self.bucket.objects.__setitem__(key,Path(filename).read_bytes())
        self.ns.update(subprocess=subprocess,ALLOWED_EXT={'.mp4','.mov','.mkv'},TransferConfig=lambda **kw:object(),MAX_FILE_BYTES=10000000,_materialize_concurrency=lambda:1,_trigger_prescan=lambda row:prescan.append(row),unquote=urllib.parse.unquote)
        def open_url(*a,**kw):
            if fail:raise OSError('private signed media URL')
            response=io.BytesIO(MEDIA_FIXTURE);response.headers={'Content-Length':str(len(MEDIA_FIXTURE))};return response
        if replace:marker.write_bytes(b'{"upload_id":"new-user-upload"}')
        with mock.patch('urllib.request.build_opener',return_value=SimpleNamespace(open=open_url)):
            self.ns['_twitch_import_run']('browserA','new-import',source,old,lock)
        self.assertFalse(lock.locked());return marker,old,prescan
    def test_clip_uses_existing_persistent_upload_marker_and_prescan(self):
        marker,old,prescan=self.run_import();data=json.loads(marker.read_bytes());self.assertEqual(data['upload_id'],'new-import');self.assertTrue(Path(data['path']).exists());self.assertIn(data['bucket_key'],self.bucket.objects);self.assertTrue(prescan)
    def test_download_failure_preserves_previous_project(self):
        marker,old,_=self.run_import(fail=True);self.assertEqual(marker.read_bytes(),old)
        error=json.loads((marker.parent/'.direct_upload_error.json').read_text());self.assertEqual(error['upload_id'],'new-import');self.assertNotIn('private',error['error'])
    def test_import_never_overwrites_a_newer_upload(self):
        marker,_,_=self.run_import(replace=True);self.assertEqual(json.loads(marker.read_bytes())['upload_id'],'new-user-upload')
    def test_revoke_accepts_the_official_empty_http_response(self):
        original=self.ns['_oauth_json'];self.connected();self.ns['_oauth_json']=original
        with mock.patch('urllib.request.urlopen',return_value=io.BytesIO(b'')):
            self.ns['_twitch_disconnect']('browserA')
        self.assertFalse(self.ns['_social_connection_load']('browserA','twitch'))

class PublicOAuthRouting(unittest.TestCase):
    def test_nginx_public_callbacks_are_reachable_without_mobile_or_session(self):
        base=os.environ.get('GSF_BASE_URL')
        if not base:self.skipTest('Requires the real production image')
        for route in ('facebook','instagram','tiktok','twitch'):
            request=urllib.request.Request(base+'/auth/'+route+'/callback?state=invalid&code=not-a-real-code',headers={'User-Agent':'Desktop route verification'})
            with self.subTest(provider=route):
                try:response=urllib.request.urlopen(request,timeout=15)
                except urllib.error.HTTPError as err:response=err
                with response:
                    self.assertEqual(response.status,400);self.assertNotIn(b'not-a-real-code',response.read());self.assertEqual(response.headers.get('Cache-Control').split(',')[0].strip(),'no-store');self.assertEqual(response.headers.get('Referrer-Policy'),'no-referrer')
        for route in ('deauthorize','data-deletion'):
            request=urllib.request.Request(base+'/auth/meta/'+route,data=b'',method='POST')
            try:response=urllib.request.urlopen(request,timeout=15)
            except urllib.error.HTTPError as err:response=err
            with response:self.assertEqual(response.status,400)

class TwitchHubBrowser(unittest.TestCase):
    def test_connected_twitch_clip_import_and_vod_limit_use_source_library(self):
        if not os.environ.get('GSF_BROWSER'):self.skipTest('Runs in the blocking real WebKit gate')
        from playwright.sync_api import sync_playwright
        import shutil
        html=(ROOT/'web/creator_hub_v156_component/index.html').read_text();posts=[];errors=[]
        with sync_playwright() as p:
            engine=getattr(p,os.environ['GSF_BROWSER']);options={'executable_path':shutil.which('chromium'),'args':['--no-sandbox']} if engine.name=='chromium' else {}
            browser=engine.launch(**options)
            try:
                page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda error:errors.append(str(error)))
                page.add_init_script("window.GSFNavigation={snapshot:()=>({target:'hub',epoch:1})};")
                def route(r):
                    url=urllib.parse.urlsplit(r.request.url)
                    if url.path=='/':r.fulfill(content_type='text/html',body='<p>Imported into existing AI route</p>' if url.query else html)
                    elif url.path=='/creator-hub/state':r.fulfill(json={'ok':True,'csrf_token':'csrf','account':{'display_name':'Creator'},'social':{'twitch':True},'drafts':[],'shorts':[]})
                    elif url.path=='/social-connect/twitch/content':
                        vod='type=videos' in url.query;r.fulfill(json={'ok':True,'data':[{'id':'vod1' if vod else 'clip1','title':'My VOD' if vod else 'My Clip','importable':not vod,'can_import':not vod,'external_id':'clip1' if not vod else 'vod1','import_reason':'Le API ufficiali Twitch non espongono il file VOD.' if vod else ''}]})
                    elif url.path=='/social-connect/twitch/import':posts.append(r.request.post_data_json);self.assertEqual(r.request.headers.get('x-gsf-csrf'),'csrf');r.fulfill(status=202,json={'ok':True,'upload_id':'import1'})
                    elif url.path=='/direct-upload/bucket/status':r.fulfill(json={'ok':True,'ready':True})
                    else:r.fulfill(json={'ok':True})
                page.route('**/*',route);page.goto('http://gsf.test/')
                page.locator('.socialDot[data-social="twitch"].connected').wait_for();page.locator('[data-open="live"]').click()
                page.locator('[data-source-folder="videos"]').click();page.get_by_text('My VOD',exact=True).wait_for();self.assertEqual(page.locator('[data-source-import]').count(),0)
                page.locator('[data-source-folder="clips"]').click();page.locator('[data-source-import="clip1"]').click();page.wait_for_url('**/?gsf_page=ai')
                self.assertEqual(posts,[{'type':'clips','clip_id':'clip1'}]);self.assertFalse(errors,errors)
            finally:browser.close()

if __name__=='__main__':unittest.main()
