from pathlib import Path

src=Path('/app/GamingShortsFactory_V103_FINAL_QUALITY.py')
out=Path('/app/GamingShortsFactory_V103_1_CLEAN_HOOK_PIXFMT.py')
s=src.read_text(encoding='utf-8')

# 1) Remove the V102 hook UI/player from the final creation area.
start_marker='        # V102 — Hook intelligente: one source of truth for preview + final render.\n'
end_marker='        _has_final=bool(\n'
start=s.find(start_marker)
if start<0:
    raise RuntimeError('V103.1 hook UI start marker not found')
end=s.find(end_marker,start)
if end<0:
    raise RuntimeError('V103.1 hook UI end marker not found')

replacement='''        # V103.1 — Hook temporarily disabled.
        # Keep the engine code available, but do not show Hook UI/player and
        # do not burn an automatic/manual hook into the final export.
        _v103_hook_kind=str(_final_recipe.get("kind","") or "")
        _v103_hook_changed=False
        if _v103_hook_kind=="auto":
            if str(_final_recipe.get("manual_hook","") or "")!=_GSF_HOOK_OFF_V102:
                _final_recipe=dict(_final_recipe)
                _final_recipe["manual_hook"]=_GSF_HOOK_OFF_V102
                _v103_hook_changed=True
        elif _v103_hook_kind in ("main_editor","inline_editor"):
            _v103_kw=dict(_final_recipe.get("render_kwargs") or {})
            if str(_v103_kw.get("hook_text","") or ""):
                _v103_kw["hook_text"]=""
                _final_recipe=dict(_final_recipe)
                _final_recipe["render_kwargs"]=_v103_kw
                _v103_hook_changed=True

        st.session_state["hook_enabled_v102"]=False
        st.session_state["hook_testo"]=""
        st.session_state.pop("v102_hook_preview_bytes",None)
        st.session_state.pop("v102_hook_preview_sig",None)

        if _v103_hook_changed:
            st.session_state["gsf_final_recipe"]=_final_recipe
            for _k in (
                "publication_final_bytes","publication_ready",
                "social_final_context_v53","social_final_context_v54"
            ):
                st.session_state.pop(_k,None)

'''
s=s[:start]+replacement+s[end:]

# 2) Relax only the post-render validator for the full-range 4:2:0 alias.
old='''    if str(video.get("pix_fmt","")).lower()!="yuv420p":
        errors.append("pixel format non yuv420p")
'''
new='''    pix_fmt=str(video.get("pix_fmt","")).lower()
    if pix_fmt not in ("yuv420p","yuvj420p"):
        errors.append(
            "pixel format non 4:2:0 8-bit compatibile "
            f"({video.get('pix_fmt') or 'sconosciuto'})"
        )
'''
if old not in s:
    raise RuntimeError('V103.1 pixel-format validator anchor not found')
s=s.replace(old,new,1)

marker='Gaming Shorts Factory · V103 Final Quality'
if marker not in s:
    raise RuntimeError('V103.1 version marker not found')
s=s.replace(marker,'Gaming Shorts Factory · V103.1 Clean Final',1)

out.write_text(s,encoding='utf-8')
print(f'V103.1 clean hook/pixfmt patch applied: {out}')
