"""Owner-scoped source catalog over GSF's existing private object storage."""
import hashlib
import json
import math
import re
from urllib.parse import urlsplit

KINDS={'local_upload','twitch_clip','twitch_vod','twitch_live','youtube_vod','youtube_live'}
STATES={'discovered','importing','ready','failed','unavailable'}

def source_id(owner,kind,provider_user_id,external_id):
    if not owner or kind not in KINDS or not external_id:raise ValueError('Invalid source identity')
    return hashlib.sha256(json.dumps([owner,kind,str(provider_user_id),str(external_id)],separators=(',',':')).encode()).hexdigest()[:32]

def duration_seconds(value):
    try:
        if isinstance(value,str) and re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?',value) and value:
            h,m,s=re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?',value).groups();return int(h or 0)*3600+int(m or 0)*60+int(s or 0)
        number=float(value)
        return number if math.isfinite(number) and number>=0 else None
    except (TypeError,ValueError,OverflowError):return None

def twitch_url(value,thumbnail=False):
    try:
        value=str(value or '');parts=urlsplit(value);host=(parts.hostname or '').lower()
        hosts=('twitch.tv','www.twitch.tv','clips.twitch.tv')
        allowed=host in hosts if not thumbnail else any(host.endswith('.'+suffix) for suffix in ('jtvnw.net','twitchcdn.net','ttvnw.net'))
        if parts.scheme=='https' and allowed and not parts.username and not parts.password and parts.port in (None,443):return value
    except ValueError:pass
    return ''

def public_source(record):
    kind=str(record.get('kind') or '');status=str(record.get('status') or 'discovered')
    ready=status=='ready' and kind in ('local_upload','twitch_clip') and bool(record.get('bucket_key'))
    importable=kind=='twitch_clip' and not ready and status!='importing'
    reason='' if kind in ('local_upload','twitch_clip') else ('La diretta è visibile su Twitch; acquisizione e registrazione non disponibili.' if kind=='twitch_live' else 'Le API ufficiali non forniscono il video da importare in GSF.')
    row={key:str(record.get(key) or '')[:300] for key in ('id','kind','provider','external_id','title','game_name','created_at','started_at')}
    row.update(status=status,duration=duration_seconds(record.get('duration')),thumbnail=twitch_url(record.get('thumbnail'),True),url=twitch_url(record.get('url')),can_import=importable,can_analyze=ready,can_open_editor=ready,import_reason=reason,imported=ready,is_live=kind=='twitch_live' and bool(record.get('is_live')))
    return row

class SourceCatalog:
    def __init__(self,client,bucket,owner):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,160}',str(owner)):raise ValueError('Invalid source owner')
        self.client,self.bucket,self.owner=client,bucket,owner
        self.prefix='source-library/'+owner+'/'
    def key(self,identity):
        if not re.fullmatch(r'[a-f0-9]{32}',str(identity)):raise ValueError('Invalid source ID')
        return self.prefix+identity+'.json'
    def load(self,identity):
        try:raw=self.client.get_object(Bucket=self.bucket,Key=self.key(identity))['Body'].read()
        except Exception as exc:
            code=str(getattr(exc,'response',{}).get('Error',{}).get('Code',''))
            if isinstance(exc,FileNotFoundError) or code in ('NoSuchKey','404'):return {}
            raise
        row=json.loads(raw)
        if not isinstance(row,dict) or row.get('owner_id')!=self.owner or row.get('id')!=identity:raise ValueError('Invalid source record')
        return row
    def save(self,record,conditions=None):
        row=dict(record)
        if row.get('owner_id',self.owner)!=self.owner:raise ValueError('Invalid source owner')
        expected=source_id(self.owner,row.get('kind'),row.get('provider_user_id',''),row.get('external_id'))
        if row.get('id',expected)!=expected or row.get('status','discovered') not in STATES:raise ValueError('Invalid source record')
        # OAuth credentials and temporary media URLs never belong to the catalog.
        allowed=('kind','provider','provider_user_id','external_id','title','thumbnail','url','game_name','created_at','started_at','duration','status','is_live','bucket_key','analysis_key','upload_id','origin_sid','size','local_path','import_started_at','completed_at','intent')
        row={key:row[key] for key in allowed if key in row};row.update(id=expected,owner_id=self.owner,schema=1)
        self.client.put_object(Bucket=self.bucket,Key=self.key(expected),Body=json.dumps(row).encode(),ContentType='application/json',CacheControl='no-store',**(conditions or {}))
        return row
    def save_if_unchanged(self,record,previous):
        # Conditional S3 writes serialize the same source across browser sessions/replicas.
        try:response=self.client.get_object(Bucket=self.bucket,Key=self.key(record['id']))
        except Exception as exc:
            code=str(getattr(exc,'response',{}).get('Error',{}).get('Code',''))
            if not isinstance(exc,FileNotFoundError) and code not in ('NoSuchKey','404','NotFound'):raise
            if previous:raise ValueError('Source changed; reload the library')
            conditions={'IfNoneMatch':'*'}
        else:
            current=json.loads(response['Body'].read())
            if current!=previous:raise ValueError('Source import already changed')
            etag=response.get('ETag')
            if not etag:raise RuntimeError('Conditional source storage unavailable')
            conditions={'IfMatch':etag}
        try:return self.save(record,conditions)
        except Exception as exc:
            code=str(getattr(exc,'response',{}).get('Error',{}).get('Code',''))
            if code in ('PreconditionFailed','ConditionalRequestConflict','412','409'):raise ValueError('Source import already in progress') from None
            raise

    def list(self,provider='upload',folder='imported',after=''):
        args={'Bucket':self.bucket,'Prefix':self.prefix,'MaxKeys':21}
        if after:args['StartAfter']=self.key(after)
        page=self.client.list_objects_v2(**args)
        keys=sorted(r['Key'] for r in page.get('Contents',[]) if re.fullmatch(re.escape(self.prefix)+r'[a-f0-9]{32}\.json',r['Key']))
        if after:keys=[k for k in keys if k>self.key(after)]
        selected=keys[:20];rows=[]
        for key in selected:
            row=self.load(key.rsplit('/',1)[-1][:-5])
            if row and row.get('provider')==provider and (folder!='imported' or row.get('status')=='ready'):rows.append(public_source(row))
        cursor=selected[-1].rsplit('/',1)[-1][:-5] if selected and (len(keys)>20 or page.get('IsTruncated')) else ''
        return {'data':rows,'cursor':cursor,'provider':provider,'folder':folder}
