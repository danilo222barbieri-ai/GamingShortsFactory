from pathlib import Path

src=Path('/app/GamingShortsFactory_V105_PERF_TELEMETRY.py')
out=Path('/app/GamingShortsFactory_V105_1_NO_AUDIO_MASTER.py')
s=src.read_text(encoding='utf-8')

helper=r'''def _gsf_source_has_audio(path):
    """Return True when the source exposes at least one audio stream."""
    probe=shutil.which("ffprobe") or "ffprobe"
    try:
        r=subprocess.run(
            [
                probe,"-v","error",
                "-select_streams","a:0",
                "-show_entries","stream=index",
                "-of","csv=p=0",
                str(path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )
        return r.returncode==0 and bool((r.stdout or "").strip())
    except Exception:
        # Preserve the historical path if probing is unavailable.
        return True


'''
anchor='def _gsf_render_core('
if anchor not in s:
    raise RuntimeError('V105.1 render core anchor missing')
s=s.replace(anchor,helper+anchor,1)

old="base = [FFMPEG_PATH, '-y', '-ss', str(start), '-i', str(source_path), '-t', str(duration), '-vf', vf, '-af', af]"
new="""_gsf_has_audio = _gsf_source_has_audio(source_path)
        base = [FFMPEG_PATH, '-y', '-ss', str(start), '-i', str(source_path)]
        if not _gsf_has_audio:
            base += [
                '-f','lavfi','-i',
                'anullsrc=channel_layout=stereo:sample_rate=48000',
            ]
        base += ['-t', str(duration), '-vf', vf]
        if _gsf_has_audio:
            base += ['-af', af]
        else:
            base += ['-map', '0:v:0', '-map', '1:a:0', '-af', af]"""
if old not in s:
    raise RuntimeError('V105.1 base render command anchor missing')
s=s.replace(old,new,1)

s=s.replace(
    'Gaming Shorts Factory · V105 Performance Telemetry',
    'Gaming Shorts Factory · V105.1 No-Audio Master',
    1,
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.1 no-audio master applied: {out}')
