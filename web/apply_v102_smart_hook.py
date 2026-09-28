from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V101_SUBTITLE_REFINEMENT.py')
out=Path('/app/GamingShortsFactory_V102_SMART_HOOK.py')
s=src.read_text(encoding='utf-8')
tree=ast.parse(s)

# Distinguish "automatic hook" from an explicit OFF state without changing old recipes.
if '_GSF_HOOK_OFF_V102' not in s:
    anchor='_GSF_HOOK_TEMPLATES = {'
    if anchor not in s:
        raise RuntimeError('V102 hook templates anchor missing')
    s=s.replace(anchor,'_GSF_HOOK_OFF_V102 = "__GSF_HOOK_OFF_V102__"\n\n'+anchor,1)

# Replace only the hook chooser: strong detected events or actual spoken content.
tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_hook_from_diag')
replacement=r'''def _gsf_hook_transcript_excerpt(diag, max_chars=52):
    """Use only words actually spoken in the selected moment; never invent copy."""
    diag=diag or {}
    raw=diag.get("transcript","")
    if isinstance(raw,(list,tuple)):
        raw=" ".join(str(x or "") for x in raw)
    text=_gsf_clean_burnin_text(raw)
    text=re.sub(r"\s+"," ",text).strip()
    if not text:
        return ""

    features=diag.get("features") or {}
    reaction=max(
        float(features.get("reaction",0.0)),
        float(features.get("reaction_cue",0.0)),
    )
    speech=float(features.get("speech",0.0))
    hook_score=float(features.get("hook_score",0.0))

    # Spoken text becomes a hook only when voice/reaction is genuinely relevant.
    if reaction<0.40 and not (speech>=0.50 and hook_score>=0.46):
        return ""

    filler={"eh","ehm","uh","um","ok","okay","si","sì","no","allora","cioè","dai","vai"}
    pieces=re.split(r"(?<=[!?\.])\s+|\s*[|\n]+\s*",text)
    candidates=[]
    for piece in pieces:
        piece=str(piece or "").strip(" -–—")
        words=piece.split()
        if not (2<=len(words)<=9):
            continue
        if len(piece)<7:
            continue
        if all(re.sub(r"[^\wàèéìòù]","",w.lower()) in filler for w in words):
            continue
        if len(piece)>int(max_chars):
            piece=" ".join(words[:7]).strip()
        if 7<=len(piece)<=int(max_chars):
            candidates.append(piece)

    if not candidates:
        words=text.split()
        if 2<=len(words)<=7 and len(text)<=int(max_chars):
            candidates=[text]

    if not candidates:
        return ""

    # Prefer an expressive sentence, otherwise the shortest faithful excerpt.
    candidates.sort(key=lambda x:(0 if ("!" in x or "?" in x) else 1,len(x)))
    return candidates[0][:int(max_chars)].strip()


def _gsf_hook_from_diag(diag, manual_hook=""):
    """
    V102: manual text wins; OFF is explicit; automatic hooks are used only
    when the selected content provides strong semantic evidence.
    """
    manual=str(manual_hook or "").strip()
    if manual==_GSF_HOOK_OFF_V102:
        return ""
    if manual:
        return manual[:70]

    diag=diag or {}
    features=diag.get("features") or {}
    event_type=str(features.get("event_type","") or "")
    event_score=float(features.get("event_score",0.0))
    category=str(features.get("moment_category","") or "")
    reaction=max(
        float(features.get("reaction",0.0)),
        float(features.get("reaction_cue",0.0)),
    )
    hook_score=float(features.get("hook_score",0.0))
    speech=float(features.get("speech",0.0))

    # Strong recognized gameplay events are factual/content-specific.
    if event_score>=0.64 and event_type in _GSF_HOOK_TEMPLATES:
        return _GSF_HOOK_TEMPLATES[event_type]

    spoken=_gsf_hook_transcript_excerpt(diag)
    if spoken:
        if category=="reaction" and reaction>=0.40:
            return spoken
        if category=="story" and hook_score>=0.50:
            return spoken
        if speech>=0.58 and hook_score>=0.48:
            return spoken

    # No generic "AZIONE PURA / ECCO IL MOMENTO" fallback.
    return ""
'''
lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+replacement.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

# Add a lightweight hook preview renderer. It burns the same ASS hook layer as final render.
anchor='''def _gsf_auto_hook_for_start(start, manual_hook=""):
    return _gsf_hook_from_diag(
        _gsf_diag_for_start(start),
        manual_hook=manual_hook
    )
'''
if anchor not in s:
    raise RuntimeError('V102 auto hook helper anchor missing')
preview_helper=r'''
def _gsf_v102_hook_preview_bytes(video_bytes, hook_text, duration, fmt="9:16 Short"):
    raw=bytes(video_bytes or b"")
    if len(raw)<1024:
        return raw
    hook=_gsf_clean_burnin_text(hook_text)
    if not hook:
        return raw
    if not FFMPEG_PATH:
        return raw

    temp_dir=_gsf_session_mkdtemp("gsf_hook_preview_v102_")
    src_path=os.path.join(temp_dir,"preview_source.mp4")
    ass_path=os.path.join(temp_dir,"hook_preview.ass")
    out_path=os.path.join(temp_dir,"hook_preview.mp4")
    with open(src_path,"wb") as f:
        f.write(raw)

    hook_duration=min(2.0,max(1.15,float(duration)*0.12))
    ok=_gsf_write_render_ass(
        ass_path,[],fallback_text="",
        fmt=fmt,
        hook_text=hook,
        hook_duration=hook_duration,
        hook_y_pct=15
    )
    if not ok:
        return raw

    try:
        cmd=[
            FFMPEG_PATH,"-hide_banner","-loglevel","error","-y",
            "-i",src_path,
            "-vf",f"ass={ass_path}",
            "-c:v","libx264","-preset","ultrafast","-crf","20",
            "-threads","1","-pix_fmt","yuv420p","-fpsmax","60",
            "-c:a","aac","-b:a","128k",
            "-movflags","+faststart",out_path
        ]
        r=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=max(90.0,min(300.0,float(duration)*12.0))
        )
        if r.returncode==0 and os.path.exists(out_path) and os.path.getsize(out_path)>1024:
            with open(out_path,"rb") as f:
                return f.read()
    except Exception:
        pass
    return raw
'''
s=s.replace(anchor,anchor+preview_helper,1)

# V102 controls live in the final recipe section, so they apply to AI and Editor recipes.
old='''    if _show_final_flow:
        st.divider()
        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)

        _has_final=bool(
'''
new='''    if _show_final_flow:
        st.divider()
        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)

        # V102 — Hook intelligente: one source of truth for preview + final render.
        _v102_kind=str(_final_recipe.get("kind","") or "")
        _v102_start=float(_final_recipe.get("start",0.0) or 0.0)
        _v102_duration=float(_final_recipe.get("duration",15.0) or 15.0)
        _v102_identity=hashlib.sha1(
            f"{_v102_kind}|{_v102_start:.3f}|{_v102_duration:.3f}|"
            f"{_final_recipe.get('source_path','')}|{_final_recipe.get('master_token','')}".encode("utf-8")
        ).hexdigest()[:12]
        _v102_text_key=f"hook_text_v102_{_v102_identity}"
        _v102_toggle_key=f"hook_enabled_v102_{_v102_identity}"

        if _v102_kind=="auto":
            _v102_existing=str(_final_recipe.get("manual_hook","") or "")
            if _v102_existing==_GSF_HOOK_OFF_V102:
                _v102_existing=""
                _v102_existing_enabled=False
            else:
                _v102_existing_enabled=bool(_v102_existing)
        else:
            _v102_existing=str(
                (_final_recipe.get("render_kwargs") or {}).get("hook_text","") or ""
            )
            _v102_existing_enabled=bool(_v102_existing)

        _v102_auto=_gsf_auto_hook_for_start(_v102_start)
        if _v102_text_key not in st.session_state:
            st.session_state[_v102_text_key]=(_v102_existing or _v102_auto)
        if _v102_toggle_key not in st.session_state:
            st.session_state[_v102_toggle_key]=(
                _v102_existing_enabled if _v102_existing else bool(_v102_auto)
            )

        _v102_c1,_v102_c2=st.columns([0.24,0.76],gap="small")
        with _v102_c1:
            _v102_enabled=st.toggle(
                "Hook",
                key=_v102_toggle_key,
                help="Mostra o nasconde l’hook nel video finale."
            )
        with _v102_c2:
            _v102_text=st.text_input(
                "Testo hook",
                key=_v102_text_key,
                max_chars=70,
                disabled=not _v102_enabled,
                placeholder=(
                    "Nessun hook necessario"
                    if not _v102_auto else _v102_auto
                )
            )

        _v102_effective=(
            _gsf_clean_burnin_text(_v102_text)[:70]
            if _v102_enabled else ""
        )
        st.session_state["hook_testo"]=_v102_effective
        st.session_state["hook_enabled_v102"]=bool(_v102_enabled)

        _v102_changed=False
        if _v102_kind=="auto":
            _v102_recipe_hook=(
                _v102_effective if _v102_enabled else _GSF_HOOK_OFF_V102
            )
            if str(_final_recipe.get("manual_hook","") or "")!=_v102_recipe_hook:
                _final_recipe=dict(_final_recipe)
                _final_recipe["manual_hook"]=_v102_recipe_hook
                _v102_changed=True
        elif _v102_kind in ("main_editor","inline_editor"):
            _v102_kw=dict(_final_recipe.get("render_kwargs") or {})
            _v102_recipe_hook=(_v102_effective if _v102_enabled else "")
            if str(_v102_kw.get("hook_text","") or "")!=_v102_recipe_hook:
                _v102_kw["hook_text"]=_v102_recipe_hook
                _final_recipe=dict(_final_recipe)
                _final_recipe["render_kwargs"]=_v102_kw
                _v102_changed=True

        if _v102_changed:
            st.session_state["gsf_final_recipe"]=_final_recipe
            for _k in (
                "publication_final_bytes","publication_ready",
                "social_final_context_v53","social_final_context_v54"
            ):
                st.session_state.pop(_k,None)

        # Mini-preview uses the exact same ASS Hook renderer, position and duration.
        _v102_preview_source=(
            st.session_state.get("publication_preview_bytes")
            or st.session_state.get("preview_bytes")
            or st.session_state.get("inline_final_bytes")
        )
        if isinstance(_v102_preview_source,(bytes,bytearray)) and len(_v102_preview_source)>1024:
            _v102_preview_sig=hashlib.sha1(
                (
                    f"{_v102_identity}|{_v102_enabled}|{_v102_effective}|"
                    f"{len(_v102_preview_source)}"
                ).encode("utf-8")
                + bytes(_v102_preview_source[:4096])
                + bytes(_v102_preview_source[-4096:])
            ).hexdigest()[:16]
            if st.session_state.get("v102_hook_preview_sig")!=_v102_preview_sig:
                _v102_fmt=str(
                    (_final_recipe.get("render_kwargs") or {}).get("fmt","9:16 Short")
                    if _v102_kind in ("main_editor","inline_editor")
                    else "9:16 Short"
                )
                st.session_state["v102_hook_preview_bytes"]=_gsf_v102_hook_preview_bytes(
                    _v102_preview_source,_v102_effective,_v102_duration,fmt=_v102_fmt
                )
                st.session_state["v102_hook_preview_sig"]=_v102_preview_sig
            _v102_pb=st.session_state.get("v102_hook_preview_bytes")
            if isinstance(_v102_pb,(bytes,bytearray)) and len(_v102_pb)>1024:
                st.caption("ANTEPRIMA HOOK · stesso testo, posizione e durata del render finale")
                _v102_pp=_gsf_bytes_to_preview(
                    _v102_pb,f"v102_hook_{_v102_preview_sig}"
                )
                _gsf_v71_render_mini_player(
                    _v102_pp,f"v102_hook_{_v102_preview_sig}","Hook"
                )

        _has_final=bool(
'''
if old not in s:
    raise RuntimeError('V102 final-flow UI anchor missing')
s=s.replace(old,new,1)

# Make AI selection retain explicit OFF if the current project toggle is disabled.
old='''                            manual_hook=st.session_state.get(
                                "hook_testo",""
                            )
'''
new='''                            manual_hook=(
                                st.session_state.get("hook_testo","")
                                if st.session_state.get("hook_enabled_v102",True)
                                else _GSF_HOOK_OFF_V102
                            )
'''
if old not in s:
    raise RuntimeError('V102 auto recipe hook anchor missing')
s=s.replace(old,new,1)

marker='Gaming Shorts Factory · V101 Subtitle Refinement'
if marker not in s:
    raise RuntimeError('V102 marker source missing')
s=s.replace(marker,'Gaming Shorts Factory · V102 Smart Hook',1)

out.write_text(s,encoding='utf-8')
print(f'V102 Smart Hook applied: {out}')
