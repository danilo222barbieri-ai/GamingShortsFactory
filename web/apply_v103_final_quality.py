from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V102_SMART_HOOK.py')
out=Path('/app/GamingShortsFactory_V103_FINAL_QUALITY.py')
s=src.read_text(encoding='utf-8')
tree=ast.parse(s)

core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''

old_args='''                    "-profile:v","high",
                    "-level:v","4.2",
                    "-pix_fmt","yuv420p",
                    "-fpsmax","60",
                    "-c:a","aac","-b:a","192k",
                    "-movflags","+faststart",
                    str(output_path)
'''
new_args='''                    "-profile:v","high",
                    "-level:v","4.2",
                    "-tag:v","avc1",
                    "-pix_fmt","yuv420p",
                    "-fpsmax","60",
                    "-c:a","aac","-b:a","192k",
                    "-ar","48000",
                    "-ac","2",
                    "-metadata:s:v:0","rotate=0",
                    "-movflags","+faststart",
                    str(output_path)
'''
if old_args not in core:
    raise RuntimeError('V103 codec block not found')
core=core.replace(old_args,new_args,1)

old_success='''            if r.returncode==0 and os.path.exists(output_path) and os.path.getsize(output_path)>0:
                return {
                    "ok":True,
                    "path":str(output_path),
                    "encoder":encoder,
                    "seconds":round(time.perf_counter()-t0,2),
                    "subtitle_words":len(used_words),
                    "subtitle_error":subtitle_error,
                    "smart_reframe":reframe_meta,
                    "reframe_cache_hit":bool(reframe_cache_hit),
                    "hook_text":_hook_text,
                    "audio_polish":bool(polish_audio),
                    "error":"",
                }
'''
new_success='''            if r.returncode==0 and os.path.exists(output_path) and os.path.getsize(output_path)>0:
                social_master=_gsf_validate_social_master(output_path,fmt=fmt)
                if not social_master.get("ok"):
                    last_error=(
                        "Master MP4 non compatibile: "
                        + "; ".join(social_master.get("errors") or ["verifica fallita"])
                    )
                    continue
                return {
                    "ok":True,
                    "path":str(output_path),
                    "encoder":encoder,
                    "seconds":round(time.perf_counter()-t0,2),
                    "subtitle_words":len(used_words),
                    "subtitle_error":subtitle_error,
                    "smart_reframe":reframe_meta,
                    "reframe_cache_hit":bool(reframe_cache_hit),
                    "hook_text":_hook_text,
                    "audio_polish":bool(polish_audio),
                    "social_master":social_master,
                    "error":"",
                }
'''
if old_success not in core:
    raise RuntimeError('V103 success return block not found')
core=core.replace(old_success,new_success,1)

helpers=r'''def _gsf_probe_social_master(path):
    import json as _json
    probe=shutil.which("ffprobe") or "ffprobe"
    cmd=[
        probe,"-v","error",
        "-show_entries",
        "stream=index,codec_type,codec_name,codec_tag_string,profile,level,pix_fmt,width,height,avg_frame_rate,r_frame_rate,sample_rate,channels:format=format_name,duration,size,bit_rate",
        "-of","json",str(path)
    ]
    try:
        r=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,timeout=25
        )
        if r.returncode!=0:
            return {"ok":False,"error":(r.stderr or "")[-1200:]}
        data=_json.loads(r.stdout or "{}")
        return {"ok":True,"data":data}
    except Exception as e:
        return {"ok":False,"error":str(e)}


def _gsf_ratio_float(value):
    try:
        a,b=str(value or "0/1").split("/",1)
        b=float(b)
        return float(a)/b if b else 0.0
    except Exception:
        try:
            return float(value or 0.0)
        except Exception:
            return 0.0


def _gsf_validate_social_master(path,fmt="9:16 Short"):
    """Strict post-render gate for YouTube Shorts, TikTok and Reels."""
    probed=_gsf_probe_social_master(path)
    if not probed.get("ok"):
        return {
            "ok":False,
            "errors":["ffprobe non disponibile: "+str(probed.get("error",""))],
            "probe":{}
        }

    data=probed.get("data") or {}
    streams=data.get("streams") or []
    video=next((x for x in streams if x.get("codec_type")=="video"),{})
    audio=next((x for x in streams if x.get("codec_type")=="audio"),{})
    errors=[]

    expected=(1080,1920) if str(fmt)=="9:16 Short" else (1920,1080)
    if str(video.get("codec_name","")).lower()!="h264":
        errors.append("video non H.264")
    if str(video.get("codec_tag_string","")).lower()!="avc1":
        errors.append("tag video non avc1")
    if str(video.get("pix_fmt","")).lower()!="yuv420p":
        errors.append("pixel format non yuv420p")
    if (int(video.get("width") or 0),int(video.get("height") or 0))!=expected:
        errors.append(
            f"risoluzione {video.get('width')}x{video.get('height')} invece di {expected[0]}x{expected[1]}"
        )

    fps=max(
        _gsf_ratio_float(video.get("avg_frame_rate")),
        _gsf_ratio_float(video.get("r_frame_rate"))
    )
    if fps<=0.0 or fps>60.05:
        errors.append(f"fps non compatibili ({fps:.2f})")

    if str(audio.get("codec_name","")).lower()!="aac":
        errors.append("audio non AAC")
    if int(audio.get("sample_rate") or 0)!=48000:
        errors.append("audio non 48 kHz")
    if int(audio.get("channels") or 0)!=2:
        errors.append("audio non stereo")

    format_name=str((data.get("format") or {}).get("format_name","")).lower()
    if not ("mp4" in format_name or "mov" in format_name):
        errors.append("contenitore non MP4/MOV")

    return {
        "ok":not errors,
        "errors":errors,
        "video":{
            "codec":video.get("codec_name"),
            "tag":video.get("codec_tag_string"),
            "profile":video.get("profile"),
            "level":video.get("level"),
            "pix_fmt":video.get("pix_fmt"),
            "width":video.get("width"),
            "height":video.get("height"),
            "fps":round(fps,3),
        },
        "audio":{
            "codec":audio.get("codec_name"),
            "sample_rate":audio.get("sample_rate"),
            "channels":audio.get("channels"),
        },
        "format":{
            "name":format_name,
            "duration":(data.get("format") or {}).get("duration"),
            "size":(data.get("format") or {}).get("size"),
            "bit_rate":(data.get("format") or {}).get("bit_rate"),
        },
    }


'''
lines=s.splitlines(keepends=True)
s=''.join(lines[:core_node.lineno-1])+helpers+core.rstrip()+'\n\n'+''.join(lines[core_node.end_lineno:])

marker='Gaming Shorts Factory · V102 Smart Hook'
if marker not in s:
    raise RuntimeError('V103 marker source missing')
s=s.replace(marker,'Gaming Shorts Factory · V103 Final Quality',1)

out.write_text(s,encoding='utf-8')
print(f'V103 Final Quality applied: {out}')
