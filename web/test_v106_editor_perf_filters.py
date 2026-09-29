from pathlib import Path
import sys

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V106_BETA_RC1.py")
s=app.read_text(encoding="utf-8")

checks=[
    ("V106 marker","Gaming Shorts Factory · V106.1 BETA RC1" in s),
    ("six filter presets",all(x in s for x in (
        "Originale","Gaming / Vibrante","Cinematico","Caldo","Freddo","Bianco e Nero"
    ))),
    ("CSS filter preview","_gsf_v106_css_filter" in s and "filter:{_v106_css_filter}" in s),
    ("FFmpeg one-pass filter","_gsf_v106_ffmpeg_filter" in s and 'vf=f"{vf},{_v106_final_fx}"' in s),
    ("cached editor probe","_gsf_v106_probe_display_size_cached" in s),
    ("render lock","_GSF_V106_RENDER_LOCK" in s and "GSF_EDITOR_RENDER_LOCK_START" in s),
    ("main adjustments stay clean",'["Volume","Velocità","Luminosità","Contrasto"]' in s),
    ("inline adjustments stay clean",'["Volume","Luminosità","Contrasto","Velocità"]' in s),
    ("prominent filter sections",s.count('"Filtri video"') >= 2 and s.count("segmented_control") >= 3),
    ("explicit color apply",all(x in s for x in (
        "apply_sub_text_color_v1061","apply_sub_active_color_v1061","apply_sub_outline_color_v1061",
        "inline_apply_txt_v1061","inline_apply_act_v1061","inline_apply_out_v1061"
    ))),
    ("approved 9:16 live size","(220,391,424)" in s),
    ("approved 16:9 live size","(520,293,332)" in s),
    ("single final encode path","colorbalance=" in s and "subprocess.run" in s),
    ("filter recipe propagation",'kind=="main_editor"' in s and "v106_last_inline_filter_preset" in s),
]
for label,ok in checks:
    if not ok:
        raise SystemExit("FAIL: "+label)
    print("PASS:",label)

compile(s,str(app),"exec")
print("V106 editor performance + filters contract: PASS")
