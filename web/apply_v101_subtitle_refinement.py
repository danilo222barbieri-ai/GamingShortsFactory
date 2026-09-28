from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V100_8_FAST_RENDER.py')
out=Path('/app/GamingShortsFactory_V101_SUBTITLE_REFINEMENT.py')
s=src.read_text(encoding='utf-8')
tree=ast.parse(s)

node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_write_render_ass')

replacement=r'''def _gsf_refine_subtitle_words(words):
    """Normalize Whisper word timings without changing their semantic order."""
    cleaned=[]
    for raw in (words or []):
        tx=str((raw or {}).get("text","") or "").strip()
        if not tx:
            continue
        try:
            start=max(0.0,float(raw.get("start",0.0)))
        except Exception:
            start=0.0
        try:
            end=float(raw.get("end",start+.12))
        except Exception:
            end=start+.12
        if cleaned and start<cleaned[-1]["start"]:
            start=cleaned[-1]["start"]
        end=max(start+.055,end)
        item=dict(raw)
        item["text"]=tx
        item["start"]=start
        item["end"]=end
        cleaned.append(item)

    # Resolve overlapping timestamps so the active-word handoff is deterministic.
    for i in range(len(cleaned)-1):
        cur=cleaned[i]
        nxt=cleaned[i+1]
        ns=float(nxt["start"])
        if ns>float(cur["start"]) and float(cur["end"])>ns:
            cur["end"]=max(float(cur["start"])+.055,ns)
    return cleaned


def _gsf_subtitle_visual_units(text):
    units=0.0
    for ch in str(text or ""):
        if ch.isspace():
            units+=.34
        elif ch in "ilI1'.,:;!|":
            units+=.50
        elif ch in "MW@#%&":
            units+=1.16
        else:
            units+=1.0
    return max(1.0,units)


def _gsf_subtitle_auto_size(base_size,text,fmt="9:16 Short"):
    """Keep the user's chosen size as the ceiling; shrink only to prevent overflow."""
    base=int(max(24,min(180,int(base_size))))
    width=1080 if fmt=="9:16 Short" else 1920
    safe_width=width*(.76 if fmt=="9:16 Short" else .84)
    units=_gsf_subtitle_visual_units(text)
    fitted=int(safe_width/max(1.0,units*.58))
    return int(max(24,min(base,fitted)))


def _gsf_subtitle_safe_xy(fmt,x_pct,y_pct,text,font_size,w_res,h_res):
    """Clamp only when manual placement would enter common Shorts/Reels/TikTok UI zones."""
    if fmt=="9:16 Short":
        left,right,top,bottom=.08,.88,.18,.76
    else:
        left,right,top,bottom=.05,.95,.08,.90

    line_w=min((right-left)*w_res,_gsf_subtitle_visual_units(text)*float(font_size)*.58)
    half_w=max(float(font_size)*.6,line_w/2.0)
    half_h=max(float(font_size)*.65,24.0)

    requested_x=max(0.0,min(1.0,float(x_pct)/100.0))*w_res
    requested_y=max(0.0,min(1.0,float(y_pct)/100.0))*h_res

    min_x=left*w_res+half_w
    max_x=right*w_res-half_w
    if min_x>max_x:
        safe_x=(left+right)*.5*w_res
    else:
        safe_x=max(min_x,min(max_x,requested_x))

    min_y=top*h_res+half_h
    max_y=bottom*h_res-half_h
    if min_y>max_y:
        safe_y=(top+bottom)*.5*h_res
    else:
        safe_y=max(min_y,min(max_y,requested_y))
    return int(round(safe_x)),int(round(safe_y))


def _gsf_write_render_ass(
    ass_file, words, fallback_text="",
    font="Arial", size=92, x_pct=50, y_pct=78,
    text_color="#FFFFFF", active_color="#FFD400",
    outline_color="#000000", fmt="9:16 Short",
    hook_text="", hook_duration=1.8, hook_y_pct=15
):
    """
    V101 refinement only:
    - precise active-word timing;
    - current-word highlight preserved;
    - automatic shrink only when needed;
    - safe social placement while preserving manual choices when already safe.
    """
    if fmt=="9:16 Short":
        w_res,h_res=1080,1920
    else:
        w_res,h_res=1920,1080

    base_fs=int(max(24,min(180,int(size))))
    primary=_gsf_hex_to_ass(text_color,"#FFFFFF")
    active=_gsf_hex_to_ass(active_color,"#FFD400")
    outline=_gsf_hex_to_ass(outline_color,"#000000")
    safe_font=str(font or "Arial").replace(","," ")

    hook_y=int(max(7,min(35,float(hook_y_pct)))/100.0*h_res)
    hook_size=84 if fmt=="9:16 Short" else 64

    ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w_res}
PlayResY: {h_res}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{safe_font},{base_fs},{primary},{active},{outline},&H78000000,-1,0,0,0,100,100,0,0,1,5,2,5,20,20,20,1
Style: Hook,Arial Black,{hook_size},&H00FFFFFF,&H0000D7FF,&H00000000,&H72000000,-1,0,0,0,100,100,0,0,1,7,3,8,40,40,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    wrote=False

    hook=_gsf_clean_burnin_text(hook_text)
    if hook:
        hook=_gsf_wrap_hook(hook)
        hook_end=max(.65,min(2.4,float(hook_duration)))
        hook_line=(
            r"{\an8\pos("+str(w_res//2)+","+str(hook_y)+
            r")\fad(90,180)}"+_gsf_ass_escape(hook)
        )
        hook_line=hook_line.replace(r"\\N",r"\N")
        ass+=(
            f"Dialogue: 2,0:00:00.00,{_gsf_ass_time(hook_end)},"
            f"Hook,,0,0,0,,{hook_line}\n"
        )
        wrote=True

    words=_gsf_refine_subtitle_words(words)
    if words:
        groups=_gsf_subtitle_groups(words)
        longest_text=max(
            (" ".join(str((w or {}).get("text","") or "").strip() for w in g).strip() for g in groups),
            key=lambda t:_gsf_subtitle_visual_units(t),
            default=""
        )
        effective_fs=_gsf_subtitle_auto_size(base_fs,longest_text,fmt)

        for group in groups:
            plain_parts=[_gsf_ass_escape(item.get("text","")) for item in group]
            plain_line=" ".join(plain_parts).strip()
            if not plain_line:
                continue
            gx,gy=_gsf_subtitle_safe_xy(
                fmt,x_pct,y_pct,
                " ".join(str((w or {}).get("text","") or "").strip() for w in group),
                effective_fs,w_res,h_res
            )
            neutral_positioned=(
                r"{\an5\pos("+str(gx)+","+str(gy)+r")\fs"+str(effective_fs)+r"}"+
                plain_line
            )

            for local_idx,word in enumerate(group):
                parts=[]
                for j,item in enumerate(group):
                    tx=_gsf_ass_escape(item.get("text",""))
                    if j==local_idx:
                        parts.append(
                            r"{\c"+active+r"\b1}"+tx+
                            r"{\c"+primary+r"\b1}"
                        )
                    else:
                        parts.append(tx)
                line=" ".join(parts).strip()
                if not line:
                    continue

                a=max(0.0,float(word.get("start",0.0)))
                own_end=max(a+.055,float(word.get("end",a+.12)))
                next_start=None
                if local_idx+1<len(group):
                    try:
                        next_start=max(a+.055,float(group[local_idx+1].get("start",own_end)))
                    except Exception:
                        next_start=None

                if next_start is not None:
                    active_end=max(a+.055,min(own_end,next_start))
                else:
                    active_end=own_end+.08

                positioned=(
                    r"{\an5\pos("+str(gx)+","+str(gy)+r")\fs"+str(effective_fs)+r"}"+
                    line
                )
                ass+=(
                    f"Dialogue: 0,{_gsf_ass_time(a)},{_gsf_ass_time(active_end)},"
                    f"Default,,0,0,0,,{positioned}\n"
                )
                wrote=True

                # Keep the phrase visible during a natural inter-word gap,
                # but remove the highlight when nobody is speaking.
                if next_start is not None and next_start>active_end+.015:
                    ass+=(
                        f"Dialogue: 0,{_gsf_ass_time(active_end)},{_gsf_ass_time(next_start)},"
                        f"Default,,0,0,0,,{neutral_positioned}\n"
                    )

    elif str(fallback_text or "").strip():
        raw=str(fallback_text or "").strip()
        effective_fs=_gsf_subtitle_auto_size(base_fs,raw,fmt)
        gx,gy=_gsf_subtitle_safe_xy(fmt,x_pct,y_pct,raw,effective_fs,w_res,h_res)
        line=_gsf_ass_escape(raw)
        positioned=(
            r"{\an5\pos("+str(gx)+","+str(gy)+r")\fs"+str(effective_fs)+r"}"+
            line
        )
        ass+=(
            f"Dialogue: 0,0:00:00.00,9:59:59.00,"
            f"Default,,0,0,0,,{positioned}\n"
        )
        wrote=True

    if not wrote:
        return False

    with open(ass_file,"w",encoding="utf-8") as f:
        f.write(ass)
    return True
'''

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+replacement.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

# Keep the live preview aligned with V101 auto-size and common social safe zones.
old_preview='''    sx=max(5.0,min(95.0,float(subtitle_x)))
    sy=max(5.0,min(95.0,float(subtitle_y)))
    # Scale ASS-like 1080x1920 values to the small live viewport.
    live_font=max(13,min(48,float(subtitle_size)*(frame_h/1920.0)*1.25*float(ps.get("scale",1.0))))
    words=subtitle_words or []
'''
new_preview='''    words=_gsf_refine_subtitle_words(subtitle_words or [])
    _preview_groups=_gsf_subtitle_groups(words) if words else []
    _preview_longest=max(
        (" ".join(str((w or {}).get("text","") or "").strip() for w in g).strip() for g in _preview_groups),
        key=lambda t:_gsf_subtitle_visual_units(t),
        default=str(subtitle_text or "")
    )
    _preview_fmt="9:16 Short" if frame_h>=frame_w else "16:9"
    _preview_w,_preview_h=((1080,1920) if _preview_fmt=="9:16 Short" else (1920,1080))
    _preview_fs=_gsf_subtitle_auto_size(subtitle_size,_preview_longest,_preview_fmt)
    _px,_py=_gsf_subtitle_safe_xy(
        _preview_fmt,subtitle_x,subtitle_y,_preview_longest,_preview_fs,_preview_w,_preview_h
    )
    sx=100.0*_px/_preview_w
    sy=100.0*_py/_preview_h
    # Scale ASS-like values to the small live viewport.
    live_font=max(13,min(48,float(_preview_fs)*(frame_h/_preview_h)*1.25*float(ps.get("scale",1.0))))
'''
if old_preview not in s:
    raise RuntimeError('V101 live preview subtitle block not found')
s=s.replace(old_preview,new_preview,1)

marker='Gaming Shorts Factory · V100.8 Fast Render'
if marker not in s:
    raise RuntimeError('V101 version marker source not found')
s=s.replace(marker,'Gaming Shorts Factory · V101 Subtitle Refinement',1)

out.write_text(s,encoding='utf-8')
print(f'V101 subtitle refinement applied: {out}')
