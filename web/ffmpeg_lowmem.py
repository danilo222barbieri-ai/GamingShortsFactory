#!/usr/bin/env python3
import os
import sys

REAL="/usr/bin/ffmpeg"
args=sys.argv[1:]

# Informational FFmpeg invocations should remain untouched.
if not args or any(flag in args for flag in ("-version","-formats","-encoders","-decoders","-filters","-h","-help")):
    os.execv(REAL,[REAL]+args)

# Railway beta has ~1 GB RAM. Limit filter and codec worker threads so libx264
# + libass do not peak at the container memory ceiling after Whisper.
prefix=[REAL,"-filter_threads","1","-filter_complex_threads","1"]

# Gaming Shorts Factory conversion commands use the final argument as output.
# Keep explicit encoder thread budgets (final HQ render asks for 2); otherwise
# retain the conservative one-thread default for analysis/transcode jobs.
if len(args)>=1:
    if "-threads" in args:
        cmd=prefix+args
    else:
        cmd=prefix+args[:-1]+["-threads","1"]+[args[-1]]
else:
    cmd=prefix+args

os.execv(REAL,cmd)
