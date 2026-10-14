#!/usr/bin/env python3
"""Deterministic integration patch for Game Editor V403.

Default mode patches app.py in-place. --check only validates that the expected
anchors are present (or that the patch is already installed) and never writes.
This lets CI validate compatibility while app.py is protected by another claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path

APP = Path("app.py")
MARKER = "GSF GAME EDITOR V403"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"V403 anchor missing: {label}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"V403 expected exactly one {label} anchor, found {count}")
    return text.replace(old, new, 1)


def validate(text: str) -> None:
    if MARKER in text:
        require(text, "from gsf_editor_v403 import (", "V403 import")
        require(text, "editor-v403-shell", "V403 shell")
        require(text, "editor_v403_active_tool", "V403 toolbar")
        require(text, "gsf-v403-timeline", "V403 timeline")
        require(text, '"safeZones":bool(safe_zones)', "V403 safe-zone data")
        require(text, '"compareMode":str(compare_mode)', "V403 compare data")
        return

    require(text, "from faster_whisper import WhisperModel\n", "Whisper import")
    require(text, "# ===== EDITOR STUDIO: timeline + player + tools in one compact workspace =====", "editor shell")
    require(text, '        editor_trim_key = "editor_trim_" + str(\n            st.session_state.get("editor_ai_token", "manual")\n        )\n', "editor trim key")
    require(text, '        info3.caption(f"DURATA · **{editor_len:.1f}s**")\n', "editor timeline info")
    require(text, '        studio_player, studio_side = st.columns([.22,.78],gap="medium")', "editor columns")
    require(text, "        with studio_side:\n", "inspector start")
    require(text, '        st.markdown("#### 🎞️ Crea video")', "inspector end")
    require(text, '<div class="gsf-live-subs"></div>', "V2 player HTML")
    require(text, 'const box = parentElement.querySelector(".gsf-live-subs");', "V2 player JS")
    require(text, '            "textColor":tc,"activeColor":ac,"outlineColor":oc,', "V2 player data")


def patch(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_once(
        text,
        "from faster_whisper import WhisperModel\n",
        "from faster_whisper import WhisperModel\n"
        "from gsf_editor_v403 import (\n"
        "    apply_all_director_suggestions, apply_director_suggestion,\n"
        "    game_director_suggestions, normalize_editor_state,\n"
        "    normalize_timeline_markers, push_history, redo_state, undo_state,\n"
        ")\n",
        "editor support import",
    )

    text = replace_once(
        text,
        '<div class="gsf-live-subs"></div>',
        '<div class="gsf-live-subs"></div>\n            <div class="gsf-live-safe"><span class="safe-top"></span><span class="safe-bottom"></span></div>',
        "safe-zone HTML",
    )
    text = replace_once(
        text,
        "        .gsf-live-subs .active{display:inline-block;transform:scale(1.10)}\n",
        "        .gsf-live-subs .active{display:inline-block;transform:scale(1.10)}\n"
        "        .gsf-live-safe{display:none;position:absolute;z-index:3;inset:7%;border:1px dashed rgba(255,255,255,.62);border-radius:13px;pointer-events:none}\n"
        "        .gsf-live-safe:after{content:'SAFE';position:absolute;right:7px;top:6px;color:rgba(255,255,255,.76);font:700 9px Arial;letter-spacing:.12em}\n"
        "        .gsf-live-safe .safe-bottom{position:absolute;left:0;right:0;bottom:11%;border-top:1px dashed rgba(255,255,255,.42)}\n",
        "safe-zone CSS",
    )
    text = replace_once(
        text,
        '          const box = parentElement.querySelector(".gsf-live-subs");\n          if (!v || !vp || !box) return;\n',
        '          const box = parentElement.querySelector(".gsf-live-subs");\n'
        '          const safe = parentElement.querySelector(".gsf-live-safe");\n'
        '          if (!v || !vp || !box) return;\n',
        "safe-zone JS query",
    )
    text = replace_once(
        text,
        "          const zoom = Number(d.zoom ?? 1);\n          const tx = Number(d.x ?? 0) * .35;\n          const ty = Number(d.y ?? 0) * .35;\n          v.style.transform = `translate(${tx}%, ${ty}%) scale(${zoom})`;\n          v.style.filter = `brightness(${Math.max(0,1+Number(d.brightness ?? 0))}) contrast(${Math.max(0,Number(d.contrast ?? 1))})`;\n",
        "          const originalMode = String(d.compareMode || 'EDITED') === 'ORIGINAL';\n"
        "          const zoom = originalMode ? 1 : Number(d.zoom ?? 1);\n"
        "          const tx = originalMode ? 0 : Number(d.x ?? 0) * .35;\n"
        "          const ty = originalMode ? 0 : Number(d.y ?? 0) * .35;\n"
        "          v.style.transform = `translate(${tx}%, ${ty}%) scale(${zoom})`;\n"
        "          v.style.filter = originalMode ? 'brightness(1) contrast(1)' : `brightness(${Math.max(0,1+Number(d.brightness ?? 0))}) contrast(${Math.max(0,Number(d.contrast ?? 1))})`;\n"
        "          if (safe) safe.style.display = d.safeZones ? 'block' : 'none';\n"
        "          badge.textContent = (originalMode ? 'ORIGINALE · ' : 'LIVE · ') + (d.format || '');\n",
        "compare mode JS",
    )
    text = replace_once(
        text,
        "    text_color=None, active_color=None, outline_color=None\n):",
        "    text_color=None, active_color=None, outline_color=None,\n"
        "    safe_zones=False, compare_mode=\"EDITED\"\n):",
        "live player signature",
    )
    text = replace_once(
        text,
        '            "textColor":tc,"activeColor":ac,"outlineColor":oc,\n',
        '            "textColor":tc,"activeColor":ac,"outlineColor":oc,\n'
        '            "safeZones":bool(safe_zones),"compareMode":str(compare_mode),\n',
        "live player V403 data",
    )

    old_shell = '''        # ===== EDITOR STUDIO: timeline + player + tools in one compact workspace =====\n        st.markdown("#### ✂️ Editor")\n'''
    new_shell = '''        # ===== GSF GAME EDITOR V403 — creator-first shell over persistent V2 player =====\n        st.markdown("""\n        <style>\n        .editor-v403-shell{margin:.25rem 0 .7rem;padding:15px 18px;border:1px solid rgba(155,190,214,.28);\n          border-radius:22px;background:linear-gradient(145deg,rgba(17,25,34,.96),rgba(30,43,55,.94));\n          color:#f5fbff;box-shadow:0 18px 44px rgba(9,20,31,.18)}\n        .editor-v403-kicker{font-size:.72rem;letter-spacing:.14em;font-weight:800;color:#9edcff;text-transform:uppercase}\n        .editor-v403-title{font-size:1.42rem;font-weight:800;letter-spacing:-.025em;margin-top:2px}\n        .editor-v403-sub{font-size:.82rem;color:rgba(235,247,255,.72);margin-top:2px}\n        .gsf-v403-timeline{position:relative;height:54px;border-radius:16px;background:linear-gradient(90deg,#17222e,#223444);\n          border:1px solid rgba(160,204,233,.18);overflow:hidden;margin:.25rem 0 .55rem}\n        .gsf-v403-timeline:before{content:'';position:absolute;left:0;right:0;top:26px;height:2px;background:rgba(182,222,247,.22)}\n        .gsf-v403-marker{position:absolute;top:10px;transform:translateX(-50%);width:8px;height:34px;border-radius:8px;background:#b9e9ff;\n          box-shadow:0 0 16px rgba(127,211,255,.42)}\n        .gsf-v403-marker.cut{height:38px;top:8px;background:#fff}\n        .gsf-v403-marker.speech{height:20px;top:17px;background:#d9c9ff}\n        .gsf-v403-marker.action_peak,.gsf-v403-marker.kill,.gsf-v403-marker.hook{background:#ffe08a}\n        .gsf-v403-legend{display:flex;gap:7px;flex-wrap:wrap;margin:-.15rem 0 .55rem}\n        .gsf-v403-chip{font-size:.69rem;padding:4px 7px;border-radius:999px;background:rgba(102,153,187,.12);border:1px solid rgba(130,184,218,.18)}\n        @media(max-width:780px){\n          .editor-v403-shell{border-radius:18px;padding:12px 13px}.editor-v403-title{font-size:1.16rem}\n          .gsf-v403-timeline{height:48px}\n          div[data-testid='stHorizontalBlock']{gap:.35rem}\n        }\n        </style>\n        <div class="editor-v403-shell">\n          <div class="editor-v403-kicker">GAME EDITOR · V403</div>\n          <div class="editor-v403-title">La scena al centro. Gli strumenti solo quando servono.</div>\n          <div class="editor-v403-sub">Editing non distruttivo · Smart Timeline · Game Director · preview LIVE persistente</div>\n        </div>\n        """,unsafe_allow_html=True)\n'''
    text = replace_once(text, old_shell, new_shell, "V403 shell")

    trim_anchor = '''        editor_trim_key = "editor_trim_" + str(\n            st.session_state.get("editor_ai_token", "manual")\n        )\n'''
    toolbar = '''\n        # V403 project state is a non-destructive decision document mirrored to existing widget keys.\n        st.session_state.setdefault("editor_v403_history",[])\n        st.session_state.setdefault("editor_v403_future",[])\n        st.session_state.setdefault("editor_v403_active_tool","FRAME")\n        st.session_state.setdefault("editor_v403_focus_mode",False)\n        st.session_state.setdefault("editor_v403_safe_zones",True)\n        st.session_state.setdefault("editor_v403_compare_mode","EDITED")\n\n        def _v403_state_from_session():\n            _tr=st.session_state.get(editor_trim_key,trim_default)\n            if not isinstance(_tr,(tuple,list)) or len(_tr)!=2: _tr=trim_default\n            return normalize_editor_state({\n                "start":_tr[0],"end":_tr[1],\n                "format":st.session_state.get("editor_format","9:16 Short"),\n                "zoom":st.session_state.get("editor_zoom",1.0),\n                "x":st.session_state.get("editor_x",0),"y":st.session_state.get("editor_y",0),\n                "volume":st.session_state.get("editor_volume",100),\n                "speed":st.session_state.get("editor_speed",1.0),\n                "brightness":st.session_state.get("editor_brightness",0.0),\n                "contrast":st.session_state.get("editor_contrast",1.0),\n                "subtitles_enabled":st.session_state.get("editor_sub_mode","Automatici")!="Nessuno",\n                "subtitle_y":st.session_state.get("subtitle_y_v18",st.session_state.get("subtitle_y",78)),\n                "safe_zones":st.session_state.get("editor_v403_safe_zones",True),\n                "focus_mode":st.session_state.get("editor_v403_focus_mode",False),\n                "compare_mode":st.session_state.get("editor_v403_compare_mode","EDITED"),\n                "active_tool":st.session_state.get("editor_v403_active_tool","FRAME"),\n            },editor_duration)\n\n        def _v403_write_state(_state):\n            _s=normalize_editor_state(_state,editor_duration)\n            st.session_state[editor_trim_key]=(_s["start"],_s["end"])\n            for _key in ["editor_format","editor_zoom","editor_x","editor_y","editor_volume","editor_speed","editor_brightness","editor_contrast"]:\n                st.session_state[_key]=_s[_key.replace("editor_","")]\n            st.session_state["editor_v403_safe_zones"]=_s["safe_zones"]\n            st.session_state["editor_v403_focus_mode"]=_s["focus_mode"]\n            st.session_state["editor_v403_compare_mode"]=_s["compare_mode"]\n            st.session_state["editor_v403_active_tool"]=_s["active_tool"]\n            st.session_state["subtitle_y_v18"]=_s["subtitle_y"]\n            st.session_state["subtitle_y"]=_s["subtitle_y"]\n            return _s\n\n        _v403_current=_v403_state_from_session()\n        _v403_pending=st.session_state.pop("editor_v403_pending_patch",None)\n        if _v403_pending:\n            st.session_state["editor_v403_history"]=push_history(st.session_state.get("editor_v403_history",[]),_v403_current)\n            st.session_state["editor_v403_future"]=[]\n            _v403_current=_v403_write_state({**_v403_current,**dict(_v403_pending)})\n            st.session_state["editor_v403_last_state"]=_v403_current\n\n        _v403_guard=bool(st.session_state.pop("editor_v403_history_guard",False))\n        _v403_last=st.session_state.get("editor_v403_last_state")\n        if _v403_last and _v403_last!=_v403_current and not _v403_guard:\n            st.session_state["editor_v403_history"]=push_history(st.session_state.get("editor_v403_history",[]),_v403_last)\n            st.session_state["editor_v403_future"]=[]\n        st.session_state["editor_v403_last_state"]=_v403_current\n\n        _undo_col,_redo_col,_focus_col,_safe_col,_compare_col=st.columns([.13,.13,.22,.22,.30],gap="small")\n        with _undo_col:\n            if st.button("↶",key="editor_v403_undo",help="Annulla ultima modifica",use_container_width=True,disabled=not bool(st.session_state.get("editor_v403_history"))):\n                _restored,_past,_future=undo_state(st.session_state.get("editor_v403_history",[]),_v403_current,st.session_state.get("editor_v403_future",[]))\n                st.session_state["editor_v403_history"]=_past; st.session_state["editor_v403_future"]=_future\n                _v403_write_state(_restored); st.session_state["editor_v403_history_guard"]=True; st.rerun()\n        with _redo_col:\n            if st.button("↷",key="editor_v403_redo",help="Ripeti modifica",use_container_width=True,disabled=not bool(st.session_state.get("editor_v403_future"))):\n                _restored,_past,_future=redo_state(st.session_state.get("editor_v403_history",[]),_v403_current,st.session_state.get("editor_v403_future",[]))\n                st.session_state["editor_v403_history"]=_past; st.session_state["editor_v403_future"]=_future\n                _v403_write_state(_restored); st.session_state["editor_v403_history_guard"]=True; st.rerun()\n        with _focus_col:\n            st.toggle("Focus",key="editor_v403_focus_mode",help="Nasconde l'inspector e lascia spazio al video")\n        with _safe_col:\n            st.toggle("Safe zone",key="editor_v403_safe_zones",help="Mostra l'area sicura per Shorts/Reels/TikTok")\n        with _compare_col:\n            st.segmented_control("Confronto",["EDITED","ORIGINAL"],key="editor_v403_compare_mode",label_visibility="collapsed")\n\n        _v403_active_tool=st.segmented_control(\n            "Strumenti",["FRAME","CAPTION","LOOK","AUDIO","AI"],\n            key="editor_v403_active_tool",label_visibility="collapsed"\n        ) or "FRAME"\n'''
    text = replace_once(text, trim_anchor, trim_anchor + toolbar, "V403 toolbar")

    timeline_anchor = '        info3.caption(f"DURATA · **{editor_len:.1f}s**")\n'
    timeline = '''\n\n        # Smart Timeline: only boundaries and events that really exist upstream.\n        _v403_events=[\n            {"time":editor_start,"type":"CUT","label":"IN","score":1.0},\n            {"time":editor_end,"type":"CUT","label":"OUT","score":1.0},\n        ]\n        for _score,_sec in st.session_state.get("ai_director_scores",[]) or []:\n            try: _v403_events.append({"time":float(_sec),"type":"ACTION_PEAK","label":"AI peak","score":float(_score)})\n            except Exception: pass\n        _speech_words=st.session_state.get("editor_sub_words",[]) or []\n        if _speech_words:\n            for _group in _gsf_subtitle_groups(_speech_words)[:8]:\n                if _group: _v403_events.append({"time":float(_group[0]["start"]),"type":"SPEECH","label":"Voce","score":.7})\n        _v403_markers=normalize_timeline_markers(_v403_events,editor_start,editor_end)\n        _marker_html="".join(\n            f'<span class="gsf-v403-marker {m["type"].lower()}" style="left:{m["position_pct"]:.2f}%" title="{m["label"]} · {m["time"]:.1f}s"></span>'\n            for m in _v403_markers\n        )\n        st.markdown(f'<div class="gsf-v403-timeline">{_marker_html}</div>',unsafe_allow_html=True)\n        _types=[]\n        for _m in _v403_markers:\n            if _m["type"] not in _types: _types.append(_m["type"])\n        st.markdown('<div class="gsf-v403-legend">'+''.join(f'<span class="gsf-v403-chip">{t.replace("_"," ")}</span>' for t in _types)+'</div>',unsafe_allow_html=True)\n'''
    text = replace_once(text, timeline_anchor, timeline_anchor + timeline, "Smart Timeline")

    text = replace_once(
        text,
        '        studio_player, studio_side = st.columns([.22,.78],gap="medium")',
        '        _v403_focus=bool(st.session_state.get("editor_v403_focus_mode",False))\n'
        '        studio_player, studio_side = st.columns(([.92,.08] if _v403_focus else [.58,.42]),gap="medium")',
        "V403 player ratio",
    )

    call_anchor = '''                reset_id=st.session_state.get("editor_reset_id",0),\n                clip_start_override=editor_start\n            )\n'''
    call_new = '''                reset_id=st.session_state.get("editor_reset_id",0),\n                clip_start_override=editor_start,\n                safe_zones=bool(st.session_state.get("editor_v403_safe_zones",True)),\n                compare_mode=st.session_state.get("editor_v403_compare_mode","EDITED")\n            )\n'''
    text = replace_once(text, call_anchor, call_new, "V403 player call")

    side_start = text.index("        with studio_side:\n", text.index(MARKER))
    side_end = text.index('        st.markdown("#### 🎞️ Crea video")', side_start)
    new_side = '''        with studio_side:\n            if _v403_focus:\n                st.caption("FOCUS · usa la barra sopra per tornare agli strumenti")\n            else:\n                st.markdown(f"##### {_v403_active_tool} · Inspector")\n                st.caption("Solo i controlli utili al lavoro che stai facendo adesso.")\n\n                if _v403_active_tool=="FRAME":\n                    st.session_state.setdefault("editor_format","9:16 Short")\n                    editor_format=st.segmented_control("Formato",["9:16 Short","16:9 Originale"],key="editor_format") or "9:16 Short"\n                    editor_zoom=st.slider("Zoom",1.0,2.0,float(st.session_state.get("editor_zoom",1.0)),.05,key="editor_zoom")\n                    _xc,_yc=st.columns(2,gap="small")\n                    with _xc: editor_x=st.slider("↔ X",-100,100,int(st.session_state.get("editor_x",0)),5,key="editor_x")\n                    with _yc: editor_y=st.slider("↕ Y",-100,100,int(st.session_state.get("editor_y",0)),5,key="editor_y")\n                    st.caption("Game Vision usa i marker reali della scena: nessun evento viene inventato.")\n\n                elif _v403_active_tool=="CAPTION":\n                    _modes=["Nessuno","Automatici","Manuali"]\n                    _current_mode=st.session_state.get("editor_sub_mode","Automatici")\n                    if _current_mode not in _modes: _current_mode="Automatici"\n                    st.session_state.setdefault("editor_sub_mode_v403",_current_mode)\n                    editor_sub_mode=st.segmented_control("Sottotitoli",_modes,key="editor_sub_mode_v403",label_visibility="collapsed") or _current_mode\n                    st.session_state["editor_sub_mode"]=editor_sub_mode\n                    st.session_state["project_subtitles_enabled"]=(editor_sub_mode!="Nessuno")\n                    st.session_state["project_subtitles_mode"]=editor_sub_mode\n                    if editor_sub_mode=="Manuali":\n                        if not st.session_state.get("editor_sub_words"):\n                            if st.button("TRASCRIVI LA SCENA",use_container_width=True,key="editor_v403_transcribe"):\n                                with st.spinner("Trascrivo la scena..."):\n                                    _words,_err=_gsf_transcribe_editor_scene(editor_input,editor_start,editor_len)\n                                if _err: st.warning(f"Trascrizione non disponibile: {_err}")\n                                else:\n                                    st.session_state["editor_sub_words"]=list(_words); st.session_state["editor_sub_live_words"]=list(_words)\n                                    st.session_state["editor_sub_text"]=" ".join(w["text"] for w in _words); st.rerun()\n                        else:\n                            _edited=st.text_area("Testo",value=st.session_state.get("editor_sub_text",""),height=118,key="editor_v403_caption_text")\n                            if st.button("✓ APPLICA TESTO",use_container_width=True,key="editor_v403_caption_apply"):\n                                st.session_state["editor_sub_text"]=_edited\n                                _tokens=_edited.split(); _timed=st.session_state.get("editor_sub_words",[])\n                                st.session_state["editor_sub_live_words"]=[{**w,"text":_tokens[i]} for i,w in enumerate(_timed) if i<len(_tokens)]\n                                st.rerun()\n                        _fonts=_gsf_windows_fonts(); _font=st.session_state.get("editor_sub_font_v18","Arial")\n                        if _font not in _fonts: _font="Arial"\n                        st.selectbox("Font",_fonts,index=_fonts.index(_font),key="editor_sub_font_v18",on_change=_gsf_sync_main_subtitle_font)\n                        st.slider("Dimensione",48,140,int(st.session_state.get("editor_sub_size_v18",92)),2,key="editor_sub_size_v18")\n                        _pc1,_pc2=st.columns(2,gap="small")\n                        with _pc1: st.slider("↔ X",5,95,int(st.session_state.get("subtitle_x_v18",50)),1,key="subtitle_x_v18")\n                        with _pc2: st.slider("↕ Y",5,95,int(st.session_state.get("subtitle_y_v18",78)),1,key="subtitle_y_v18")\n                        _cc1,_cc2,_cc3=st.columns(3,gap="small")\n                        with _cc1: st.color_picker("Testo",st.session_state.get("subtitle_text_color_v18","#FFFFFF"),key="subtitle_text_color_v18")\n                        with _cc2: st.color_picker("Attiva",st.session_state.get("subtitle_active_color_v18","#FFD400"),key="subtitle_active_color_v18")\n                        with _cc3: st.color_picker("Bordo",st.session_state.get("subtitle_outline_color_v18","#000000"),key="subtitle_outline_color_v18")\n\n                elif _v403_active_tool=="LOOK":\n                    editor_brightness=st.slider("Luminosità",-.30,.30,float(st.session_state.get("editor_brightness",0.0)),.05,key="editor_brightness")\n                    editor_contrast=st.slider("Contrasto",.70,1.50,float(st.session_state.get("editor_contrast",1.0)),.05,key="editor_contrast")\n                    _lp1,_lp2,_lp3=st.columns(3,gap="small")\n                    with _lp1:\n                        if st.button("NEUTRO",use_container_width=True,key="editor_v403_look_neutral"):\n                            st.session_state["editor_v403_pending_patch"]={"brightness":0.0,"contrast":1.0}; st.rerun()\n                    with _lp2:\n                        if st.button("POP",use_container_width=True,key="editor_v403_look_pop"):\n                            st.session_state["editor_v403_pending_patch"]={"brightness":.03,"contrast":1.12}; st.rerun()\n                    with _lp3:\n                        if st.button("NIGHT",use_container_width=True,key="editor_v403_look_night"):\n                            st.session_state["editor_v403_pending_patch"]={"brightness":-.05,"contrast":1.18}; st.rerun()\n\n                elif _v403_active_tool=="AUDIO":\n                    editor_volume=st.slider("Volume",0,200,int(st.session_state.get("editor_volume",100)),5,key="editor_volume")\n                    editor_speed=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state.get("editor_speed",1.0)),key="editor_speed")\n                    st.caption("Preview immediata; il render finale continua a usare la pipeline GSF esistente.")\n\n                else:\n                    _director_state=normalize_editor_state({**_v403_state_from_session(),"start":editor_start,"end":editor_end},editor_duration)\n                    _director=game_director_suggestions(_director_state,_v403_markers)\n                    if not _director:\n                        st.success("✓ Nessuna correzione evidente per questa scena.")\n                    else:\n                        st.markdown(f"**{len(_director)} correzioni consigliate**")\n                        if st.button("✦ APPLICA TUTTO",type="primary",use_container_width=True,key="editor_v403_ai_all"):\n                            _all=apply_all_director_suggestions(_director_state,_director,editor_duration)\n                            st.session_state["editor_v403_pending_patch"]={k:_all[k] for k in ["start","end","zoom","x","y","volume","subtitle_y","safe_zones"]}\n                            st.rerun()\n                        for _suggestion in _director:\n                            with st.container(border=True):\n                                st.markdown(f"**{_suggestion['category']} · {_suggestion['title']}**")\n                                st.caption(_suggestion["reason"])\n                                if st.button("APPLICA",key=f"editor_v403_ai_{_suggestion['id']}",use_container_width=True):\n                                    st.session_state["editor_v403_pending_patch"]=dict(_suggestion["patch"]); st.rerun()\n\n                with st.expander("Dettagli progetto",expanded=False):\n                    _detail=_v403_state_from_session()\n                    st.caption(f"{_detail['format']} · {_detail['end']-_detail['start']:.1f}s · zoom {_detail['zoom']:.2f}× · audio {_detail['volume']}%")\n                    if st.button("↶ RESET TUTTO",use_container_width=True,key="reset_main_all_v403",on_click=_gsf_reset_main_all):\n                        st.session_state["editor_v403_history"]=[]; st.session_state["editor_v403_future"]=[]\n\n'''
    text = text[:side_start] + new_side + text[side_end:]
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = APP.read_text(encoding="utf-8")
    validate(text)
    if args.check:
        print("V403 anchors OK" if MARKER not in text else "V403 already installed")
        return
    changed = patch(text)
    validate(changed)
    if changed == text:
        print("V403 already installed; no changes")
        return
    APP.write_text(changed, encoding="utf-8")
    print("V403 Game Editor integration applied")


if __name__ == "__main__":
    main()
