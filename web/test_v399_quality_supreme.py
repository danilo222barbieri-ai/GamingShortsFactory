#!/usr/bin/env python3
from pathlib import Path

from quality_supreme_v399 import encoder_args, quality_profile


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


baseline = quality_profile({})
need(baseline["preset"] == "medium", "V399 baseline keeps x264 medium")
need(int(baseline["crf"]) == 14, "V399 baseline keeps CRF 14")
need(baseline["codec"] == "libx264", "V399 keeps CPU libx264")
need(baseline["profile"] == "high", "V399 keeps H.264 High")
need(baseline["pix_fmt"] == "yuv420p", "V399 keeps mobile-safe yuv420p")
need(int(baseline["fpsmax"]) == 60, "V399 keeps 60 fps cap")
need(int(baseline["width"]) == 1080 and int(baseline["height"]) == 1920,
     "V399 keeps the 1080x1920 vertical master")

high_motion = quality_profile({"motion": 0.96, "detail": 0.90, "action_peak": 0.95})
need(12 <= int(high_motion["crf"]) <= 14,
     "high-complexity scenes never receive less quality than CRF 14")
need(high_motion["preset"] == "medium",
     "high-complexity scenes never switch to a slower or lower-efficiency preset")
need(float(high_motion["aq_strength"]) >= float(baseline["aq_strength"]),
     "high-complexity scenes receive at least baseline adaptive quantization")

low_source = quality_profile({"motion": 0.15, "detail": 0.20, "source_width": 720, "source_height": 1280})
need(int(low_source["crf"]) == 14,
     "low-resolution input does not waste bitrate pretending to invent detail")
need(not bool(low_source["sharpen"]),
     "low-resolution input is not aggressively sharpened")

args = encoder_args(high_motion, has_audio=True)
joined = " ".join(args)
need("libx264" in joined and "-preset medium" in joined,
     "shared V399 encoder args use libx264 medium")
need("-profile:v high" in joined and "-pix_fmt yuv420p" in joined,
     "shared V399 encoder args keep the social-master codec contract")
need("h264_qsv" not in joined and "libx265" not in joined,
     "V399 never reintroduces QSV or HEVC")
need("-c:a aac" in joined and "-ar 48000" in joined and "-ac 2" in joined,
     "V399 keeps AAC 48 kHz stereo when audio must be encoded")

for payload in (None, "bad", [], {"motion": "nan", "detail": object()}):
    p = quality_profile(payload)
    need(p["preset"] == "medium" and 12 <= int(p["crf"]) <= 14,
         "malformed or absent metadata falls back safely")

# The two post-master re-encoders must share V399 instead of silently degrading
# the master with independent fast/CRF15 tails.
director = Path("web/director_render_exec_v143.py").read_text(encoding="utf-8")
privacy = Path("web/privacy_cleanup_v149.py").read_text(encoding="utf-8")
need("quality_supreme_v399" in director,
     "Director V143 consumes the shared V399 quality policy")
need("quality_supreme_v399" in privacy,
     "Privacy V149 consumes the shared V399 quality policy")
need('"-preset","fast"' not in director,
     "Director V143 no longer downgrades AI-edited Shorts to x264 fast")
need('"-preset","fast"' not in privacy and '"-crf","15"' not in privacy,
     "Privacy V149 no longer downgrades masked Shorts to fast/CRF15")

print("V399 Quality Supreme contract: PASS")
