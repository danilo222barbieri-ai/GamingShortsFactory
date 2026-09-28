from pathlib import Path
import ast
import re

src=Path('/app/GamingShortsFactory_V99_FINAL_ARCH.py')
out=Path('/app/GamingShortsFactory_V100_SMART_REFRAME.py')
s=src.read_text(encoding='utf-8')

def replace_function(source,name,new_source):
    tree=ast.parse(source)
    node=next(
        (n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),
        None
    )
    if node is None:
        raise RuntimeError(f'V100 function not found: {name}')
    lines=source.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1]) + new_source.rstrip() + '\n\n' + ''.join(lines[node.end_lineno:])

new_analyze=r'''def _gsf_smart_reframe_analyze(source_path,start,duration,sample_fps=5,analysis_width=320):
    """
    V100 gameplay-aware Smart Reframe for 9:16.
    Tracks coherent motion clusters, suppresses HUD/corner activity, protects
    hook/subtitle safe zones and uses a damped camera controller.
    """
    result={
        "enabled":False,
        "reason":"",
        "track":[],
        "confidence":0.0,
        "movement":0.0,
        "samples":0,
        "profile":"v100-gameplay-safe",
        "hud_suppression":0.0,
        "safe_zones":{"hook_top":0.17,"subtitle_bottom":0.24},
    }

    if np is None:
        result["reason"]="numpy non disponibile"
        return result

    w,h=_gsf_probe_video_size(source_path)
    if not w or not h:
        result["reason"]="dimensioni video non disponibili"
        return result

    source_aspect=float(w)/float(h)
    target_aspect=9.0/16.0
    if source_aspect <= target_aspect*1.08:
        result["reason"]="video già verticale"
        return result

    aw=max(192,int(analysis_width))
    ah=max(108,int(round(aw*h/w)))
    if ah%2:
        ah+=1

    fps=max(3,min(6,int(sample_fps)))
    cmd=[
        FFMPEG_PATH,"-hide_banner","-loglevel","error",
        "-ss",str(max(0.0,float(start))),
        "-i",str(source_path),
        "-t",str(max(.25,float(duration))),
        "-an",
        "-vf",f"fps={fps},scale={aw}:{ah},format=gray",
        "-pix_fmt","gray",
        "-f","rawvideo","pipe:1"
    ]
    try:
        r=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=max(15,int(float(duration)*2.5)+10)
        )
    except Exception as e:
        result["reason"]=f"analisi fallita: {e}"
        return result

    if r.returncode!=0 or not r.stdout:
        result["reason"]="FFmpeg non ha prodotto frame"
        return result

    frame_size=aw*ah
    frame_count=len(r.stdout)//frame_size
    if frame_count<3:
        result["reason"]="pochi frame"
        return result

    raw=np.frombuffer(r.stdout[:frame_count*frame_size],dtype=np.uint8)
    frames=raw.reshape(frame_count,ah,aw)

    crop_fraction=min(1.0,target_aspect/source_aspect)
    half_crop=crop_fraction/2.0
    min_c=max(half_crop,0.05)
    max_c=min(1.0-half_crop,0.95)
    portrait_pressure=max(0.0,min(1.0,(1.0-crop_fraction)/0.70))

    xs=(np.arange(aw,dtype=np.float32)+0.5)/float(aw)

    # Gameplay prior: center remains important, but not so strong that a real
    # subject on either side gets dragged back to the middle.
    center_prior=1.0-0.12*np.minimum(1.0,np.abs(xs-0.5)/0.5)

    # HUD / overlay protection. Most game HUD lives in corners/top/bottom.
    # We do not delete those pixels; we merely reduce their ability to steer
    # the crop. This also reserves practical visual room for hook/subtitles.
    row_weight=np.ones(ah,dtype=np.float32)
    hook_rows=max(1,int(round(ah*0.17)))
    sub_rows=max(1,int(round(ah*0.24)))
    row_weight[:hook_rows]*=0.48
    row_weight[max(0,ah-sub_rows):]*=0.54

    col_weight=np.ones(aw,dtype=np.float32)
    edge=max(1,int(round(aw*0.075)))
    col_weight[:edge]*=0.68
    col_weight[max(0,aw-edge):]*=0.68

    spatial_weight=row_weight[:,None]*col_weight[None,:]
    # Extra corner suppression catches animated minimaps, counters and kill feeds.
    corner_h=max(1,int(round(ah*0.28)))
    corner_w=max(1,int(round(aw*0.19)))
    spatial_weight[:corner_h,:corner_w]*=0.68
    spatial_weight[:corner_h,-corner_w:]*=0.68
    spatial_weight[-corner_h:,:corner_w]*=0.72
    spatial_weight[-corner_h:,-corner_w:]*=0.72

    centers=[0.5]
    confidences=[0.0]
    safe_scores=[1.0]
    hud_scores=[0.0]
    prev_center=0.5
    velocity=0.0
    pending_target=0.5
    pending_count=0

    # Narrow 9:16 crops should feel like a camera operator, not a cursor.
    dead_zone=0.038+0.014*portrait_pressure
    base_max_step=0.050-0.008*portrait_pressure
    accel_limit=0.024

    for i in range(1,frame_count):
        cur=frames[i].astype(np.int16)
        prev=frames[i-1].astype(np.int16)
        diff=np.abs(cur-prev).astype(np.float32)

        total=float(diff.sum())
        mean=float(diff.mean())
        if total<=1.0 or mean<0.14:
            centers.append(prev_center)
            confidences.append(0.0)
            safe_scores.append(1.0)
            hud_scores.append(0.0)
            velocity*=0.72
            continue

        threshold=float(np.percentile(diff,76.0))
        salient=np.maximum(diff-threshold,0.0)
        raw_sal_total=float(salient.sum())
        if raw_sal_total<=1.0:
            centers.append(prev_center)
            confidences.append(0.0)
            safe_scores.append(1.0)
            hud_scores.append(0.0)
            velocity*=0.72
            continue

        weighted=salient*spatial_weight
        col=weighted.sum(axis=0)*center_prior
        weighted_total=float(col.sum())
        if weighted_total<=1.0:
            centers.append(prev_center)
            confidences.append(0.0)
            safe_scores.append(1.0)
            hud_scores.append(0.0)
            velocity*=0.72
            continue

        # Coherent-motion cluster. A global centroid often lands between two
        # unrelated moving areas; the cluster peak is a better gameplay target.
        kernel=max(5,int(round(aw*0.055)))
        if kernel%2==0:
            kernel+=1
        smooth_col=np.convolve(
            col,
            np.ones(kernel,dtype=np.float32)/float(kernel),
            mode="same"
        )
        peak_idx=int(np.argmax(smooth_col))
        cluster_half=max(kernel,int(round(aw*0.12)))
        lo=max(0,peak_idx-cluster_half)
        hi=min(aw,peak_idx+cluster_half+1)
        cluster=col[lo:hi]
        cluster_total=float(cluster.sum())
        global_c=float((col*xs).sum()/weighted_total)
        if cluster_total>1.0:
            cluster_c=float((cluster*xs[lo:hi]).sum()/cluster_total)
        else:
            cluster_c=global_c

        cluster_share=max(0.0,min(1.0,cluster_total/(weighted_total+1e-6)))
        desired=cluster_c*(0.58+0.24*cluster_share)+global_c*(0.42-0.24*cluster_share)

        # Confidence combines amount of useful motion and how concentrated it is.
        p=col/weighted_total
        entropy=float(
            -(p*np.log(p+1e-9)).sum()/max(1e-9,math.log(len(p)))
        )
        concentration=max(0.0,min(1.0,1.0-entropy))
        useful_ratio=max(0.0,min(1.0,float(weighted.sum())/(raw_sal_total+1e-6)))
        saliency_ratio=min(1.0,raw_sal_total/(total+1e-6)*3.0)
        confidence=max(
            0.0,min(
                1.0,
                0.42*saliency_ratio+
                0.30*concentration+
                0.18*cluster_share+
                0.10*useful_ratio
            )
        )

        # Quantify how much raw activity was discounted as likely HUD/overlay.
        hud_supp=max(0.0,min(1.0,1.0-useful_ratio))
        hud_scores.append(hud_supp)
        safe_scores.append(useful_ratio)

        desired=max(min_c,min(max_c,desired))

        # Low-confidence edge motion is commonly HUD animation. It may influence
        # the camera only after it persists, never in one-frame snaps.
        edge_target=(desired<0.18 or desired>0.82)
        if edge_target and confidence<0.42:
            desired=0.72*prev_center+0.28*desired
            confidence*=0.72

        delta=desired-prev_center

        # Dead-zone + hysteresis: micro-motion does not move the crop.
        if abs(delta)<=dead_zone:
            pending_count=0
            pending_target=prev_center
            target=prev_center
        else:
            if abs(desired-pending_target)<=dead_zone*0.80:
                pending_count+=1
            else:
                pending_target=desired
                pending_count=1

            urgent=confidence>=0.62 or abs(delta)>=0.18
            if pending_count<2 and not urgent:
                target=prev_center
            else:
                target=desired

        # Fast initial lock is allowed only on a genuinely reliable sample.
        if i==1 and confidence>=0.50:
            smoothed=target
            velocity=0.0
            centers[0]=smoothed
        else:
            wanted=target-prev_center
            max_step=base_max_step+(0.020 if confidence>=0.68 else 0.0)
            wanted=max(-max_step,min(max_step,wanted))

            # Acceleration clamp avoids abrupt direction reversals.
            dv=max(-accel_limit,min(accel_limit,wanted-velocity))
            velocity=(velocity+dv)*0.90
            if target==prev_center:
                velocity*=0.52

            alpha=0.54 if abs(delta)>=0.16 and confidence>=0.55 else (0.30+0.22*confidence)
            smoothed=prev_center+velocity*alpha
            if (target-prev_center)*(target-smoothed)<0:
                smoothed=target

        smoothed=max(min_c,min(max_c,smoothed))
        centers.append(smoothed)
        confidences.append(confidence)
        prev_center=smoothed

    # Symmetric low-pass pass removes residual one-frame wobble but keeps
    # sustained movement. Three taps are intentionally conservative.
    smoothed=list(centers)
    for _ in range(2):
        nxt=list(smoothed)
        for i in range(1,len(smoothed)-1):
            nxt[i]=(
                0.18*smoothed[i-1]+
                0.64*smoothed[i]+
                0.18*smoothed[i+1]
            )
        smoothed=nxt

    # Half-second control points: smoother than frame-by-frame, more responsive
    # than the old one-point-per-second path on fast gameplay.
    stride=max(1,int(round(fps*0.50)))
    track=[]
    for i in range(0,len(smoothed),stride):
        j=min(len(smoothed),i+stride)
        c=float(np.median(np.asarray(smoothed[i:j],dtype=np.float32)))
        conf=float(np.mean(np.asarray(confidences[i:j],dtype=np.float32)))
        hud=float(np.mean(np.asarray(hud_scores[i:j],dtype=np.float32)))
        safe=float(np.mean(np.asarray(safe_scores[i:j],dtype=np.float32)))
        track.append({
            "t":round(i/float(fps),3),
            "cx":round(max(min_c,min(max_c,c)),6),
            "confidence":round(max(0.0,min(1.0,conf)),4),
            "hud_guard":round(max(0.0,min(1.0,hud)),4),
            "safe_zone_score":round(max(0.0,min(1.0,safe)),4),
        })

    last_t=max(0.0,(len(smoothed)-1)/float(fps))
    if not track or last_t-track[-1]["t"]>0.30:
        track.append({
            "t":round(last_t,3),
            "cx":round(max(min_c,min(max_c,float(smoothed[-1]))),6),
            "confidence":round(max(0.0,min(1.0,float(confidences[-1]))),4),
            "hud_guard":round(max(0.0,min(1.0,float(hud_scores[-1]))),4),
            "safe_zone_score":round(max(0.0,min(1.0,float(safe_scores[-1]))),4),
        })

    movement=0.0
    if len(track)>1:
        movement=sum(
            abs(float(track[i]["cx"])-float(track[i-1]["cx"]))
            for i in range(1,len(track))
        )/max(1,len(track)-1)

    mean_conf=float(np.mean(np.asarray(confidences,dtype=np.float32)))
    mean_hud=float(np.mean(np.asarray(hud_scores,dtype=np.float32)))

    if mean_conf<0.105 or movement<0.0035:
        result.update({
            "reason":"inquadratura stabile: tracking non necessario",
            "track":[
                {
                    "t":0.0,"cx":0.5,
                    "confidence":round(mean_conf,4),
                    "hud_guard":round(mean_hud,4),
                    "safe_zone_score":1.0,
                }
            ],
            "confidence":round(mean_conf,4),
            "movement":round(movement,5),
            "samples":frame_count,
            "hud_suppression":round(mean_hud,4),
        })
        return result

    result.update({
        "enabled":True,
        "reason":"V100 gameplay-aware tracking",
        "track":track,
        "confidence":round(mean_conf,4),
        "movement":round(movement,5),
        "samples":frame_count,
        "hud_suppression":round(mean_hud,4),
    })
    return result
'''

new_smooth=r'''def _gsf_smooth_reframe_track(track):
    """
    V100 camera stabilizer.
    Uses confidence-aware dead-zone, velocity and acceleration limits so a
    sustained subject move is followed while HUD spikes and micro-jitter are not.
    """
    pts=[]
    for item in (track or []):
        try:
            pts.append({
                "t":float(item["t"]),
                "cx":max(0.10,min(0.90,float(item["cx"]))),
                "confidence":max(0.0,min(1.0,float(item.get("confidence",0.55)))),
                "hud_guard":max(0.0,min(1.0,float(item.get("hud_guard",0.0)))),
                "safe_zone_score":max(0.0,min(1.0,float(item.get("safe_zone_score",1.0)))),
            })
        except Exception:
            continue
    pts=sorted(pts,key=lambda x:x["t"])
    if len(pts)<2:
        return pts

    # Light look-ahead median rejects isolated wrong targets before the camera
    # controller sees them.
    desired=[]
    for i,item in enumerate(pts):
        lo=max(0,i-1)
        hi=min(len(pts),i+2)
        nearby=sorted(float(pts[j]["cx"]) for j in range(lo,hi))
        med=nearby[len(nearby)//2]
        conf=float(item["confidence"])
        hud=float(item["hud_guard"])
        blend=max(0.20,min(0.90,0.35+0.55*conf-0.30*hud))
        desired.append(float(item["cx"])*blend+med*(1.0-blend))

    out=[dict(pts[0])]
    out[0]["cx"]=desired[0]
    prev=desired[0]
    velocity=0.0

    for i,item in enumerate(pts[1:],1):
        dt=max(0.05,float(item["t"])-float(pts[i-1]["t"]))
        raw=desired[i]
        conf=float(item["confidence"])
        hud=float(item["hud_guard"])
        delta=raw-prev

        # Dead-zone grows when the signal looks HUD-like or uncertain.
        dead=0.016+0.020*(1.0-conf)+0.018*hud
        if abs(delta)<=dead:
            target=prev
        else:
            target=raw

        # Max pan speed is normalized frame-width per second. High confidence
        # permits a faster catch-up, but never an instant jump.
        max_speed=0.16+0.12*conf
        wanted_v=(target-prev)/dt
        wanted_v=max(-max_speed,min(max_speed,wanted_v))

        max_accel=0.28
        dv=wanted_v-velocity
        dv=max(-max_accel*dt,min(max_accel*dt,dv))
        velocity+=dv
        if target==prev:
            velocity*=max(0.0,1.0-3.2*dt)

        nxt=prev+velocity*dt
        if (target-prev)*(target-nxt)<0:
            nxt=target
            velocity=0.0

        # Low-confidence HUD-ish points cannot pull far from the previous crop.
        if hud>=0.35 and conf<0.45:
            max_hud_pull=0.035
            nxt=max(prev-max_hud_pull,min(prev+max_hud_pull,nxt))

        nxt=max(0.10,min(0.90,nxt))
        row=dict(item)
        row["cx"]=nxt
        out.append(row)
        prev=nxt

    # One final symmetric pass for visually continuous FFmpeg interpolation.
    if len(out)>=3:
        vals=[float(x["cx"]) for x in out]
        for i in range(1,len(out)-1):
            out[i]["cx"]=(
                0.16*vals[i-1]+
                0.68*vals[i]+
                0.16*vals[i+1]
            )
    return out
'''

s=replace_function(s,'_gsf_smart_reframe_analyze',new_analyze)
s=replace_function(s,'_gsf_smooth_reframe_track',new_smooth)

# Never reuse an old V42/V94 tracking cache after changing the algorithm.
s,n=re.subn(
    r"GSF_SMART_REFRAME_VERSION\s*=\s*['\"][^'\"]+['\"]",
    'GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"',
    s,count=1
)
if n!=1:
    raise RuntimeError('V100 Smart Reframe version constant not found')

s=re.sub(
    r'gsf_smart_reframe_cache_v\d+',
    'gsf_smart_reframe_cache_v100',
    s
)

if 'Gaming Shorts Factory · V99 FINAL Architecture' not in s:
    raise RuntimeError('V100 source marker not found')
s=s.replace(
    'Gaming Shorts Factory · V99 FINAL Architecture',
    'Gaming Shorts Factory · V100 Smart Reframe'
)

out.write_text(s,encoding='utf-8')
print(f'V100 Smart Reframe patch applied: {out}')
