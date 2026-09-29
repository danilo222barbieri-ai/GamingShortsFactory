#!/usr/bin/env python3
import v105_stress_matrix as stress

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

expected={
    "landscape_1080p30_48k_stereo",
    "landscape_1080p60_44k_mono",
    "landscape_1440p60_no_audio",
    "portrait_1080x1920_60",
    "rotated_iphone_1080p60",
    "vfr_1080p",
}
need(set(stress.CASES)==expected,"stress matrix covers all six source classes")
need(hasattr(stress,"build_source"),"stress matrix can build each source")
need(hasattr(stress,"probe_source"),"stress matrix probes input metadata")
need(hasattr(stress,"run_matrix"),"stress matrix exposes runtime runner")
for name,cfg in stress.CASES.items():
    need(float(cfg["duration"])<=5.0,f"{name} fixture stays short enough for 1 GB staging")
need(stress.RENDER_PROFILE=="medium_crf14_t1","stress matrix uses measured render winner")

print("V105 stress matrix contract: PASS")
