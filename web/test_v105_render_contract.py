#!/usr/bin/env python3
import v105_render_benchmark as bench

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

profiles=bench.PROFILES
need(set(profiles)=={"medium_crf14_t1","medium_crf14_t2","fast_crf14_t2"},
     "benchmark exposes exactly the three V105 render candidates")

for name,cfg in profiles.items():
    need(cfg["crf"]==14,f"{name} keeps CRF 14")
    need(cfg["pix_fmt"]=="yuv420p",f"{name} keeps yuv420p")
    need(cfg["profile"]=="high",f"{name} keeps H.264 High")
    need(cfg["level"]=="4.2",f"{name} keeps level 4.2")
    need(cfg["audio_bitrate"]=="192k",f"{name} keeps AAC 192k")
    need(cfg["audio_rate"]==48000,f"{name} keeps 48 kHz audio")
    need(cfg["audio_channels"]==2,f"{name} keeps stereo audio")
    need(cfg["fpsmax"]==60,f"{name} caps at 60 fps")

need(profiles["medium_crf14_t1"]["preset"]=="medium","baseline uses medium preset")
need(profiles["medium_crf14_t1"]["threads"]==1,"baseline uses one thread")
need(profiles["medium_crf14_t2"]["preset"]=="medium","two-thread candidate uses medium preset")
need(profiles["medium_crf14_t2"]["threads"]==2,"two-thread candidate uses two threads")
need(profiles["fast_crf14_t2"]["preset"]=="fast","fast candidate uses fast preset")
need(profiles["fast_crf14_t2"]["threads"]==2,"fast candidate uses two threads")

fixture=bench.synthetic_fixture_command("fixture.mp4",duration=15)
need("1920x1080" in " ".join(fixture),"synthetic fixture starts from landscape 1080p")
need("60" in " ".join(fixture),"synthetic fixture exercises 60 fps")
need(hasattr(bench,"probe_master"),"benchmark validates rendered social master")
need(hasattr(bench,"run_benchmark"),"benchmark exposes measured runner")

need(hasattr(bench,"long_fixture_command"),"benchmark exposes memory-light long-fixture builder")
long_cmd=bench.long_fixture_command("seed15.mp4","fixture30.mp4",30)
joined=" ".join(long_cmd)
need("-stream_loop" in joined,"long fixture reuses encoded seed instead of regenerating raw 1080p60")
need("-c copy" in joined,"long fixture extension uses stream copy")

print("V105 render benchmark contract: PASS")
