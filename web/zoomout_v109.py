"""V109 native zoom-out filter builder.

For zoom >= 1 the mature renderer remains untouched. For zoom < 1 the full
native gameplay is scaled inside the output canvas and composited over a
low-cost blurred copy of itself in the same FFmpeg pass.
"""

def _f(value, fallback):
    try:
        return float(value)
    except Exception:
        return float(fallback)

def _escape_ass_path(path):
    text=str(path or "")
    return (
        text.replace("\\","\\\\")
            .replace(":","\\:")
            .replace("'","\\'")
            .replace(",","\\,")
    )

def build_zoomout_filter(
    fmt, zoom, x_pos, y_pos, brightness, contrast, speed, ass_file=None
):
    z=max(0.80,min(0.999,_f(zoom,0.8)))
    x=max(-100.0,min(100.0,_f(x_pos,0.0)))
    y=max(-100.0,min(100.0,_f(y_pos,0.0)))
    bri=max(-1.0,min(1.0,_f(brightness,0.0)))
    con=max(0.0,min(3.0,_f(contrast,1.0)))
    spd=max(0.5,min(2.0,_f(speed,1.0)))

    if str(fmt)=="9:16 Short":
        out_w,out_h=1080,1920
        bg_w,bg_h=540,960
    else:
        out_w,out_h=1920,1080
        bg_w,bg_h=960,540

    # Apply core look/timing before split so foreground/background stay in sync.
    pre=(
        f"eq=brightness={bri:.5f}:contrast={con:.5f},"
        f"setpts=PTS/{spd:.5f},split=2[gsfbg][gsffg]"
    )
    bg=(
        f"[gsfbg]scale={bg_w}:{bg_h}:force_original_aspect_ratio=increase,"
        f"crop={bg_w}:{bg_h},boxblur=20:1,scale={out_w}:{out_h},"
        "eq=brightness=-0.07000:saturation=0.86000[gsfbg2]"
    )
    if str(fmt)=="9:16 Short":
        # 1.00x must visually match the existing cover crop; 0.80x reaches
        # the complete native frame. Interpolate between those two geometries.
        t=max(0.0,min(1.0,(z-0.80)/0.20))
        factor=(
            f"(1+{t:.6f}*(max({out_w}/iw,{out_h}/ih)-1))"
        )
    else:
        # In a native 16:9 canvas zoom-out simply scales the complete frame.
        factor=f"{z:.6f}"
    fg=(
        f"[gsffg]scale={out_w}:{out_h}:force_original_aspect_ratio=decrease,"
        f"scale='trunc(iw*{factor}/2)*2':'trunc(ih*{factor}/2)*2'[gsffg2]"
    )
    overlay=(
        "[gsfbg2][gsffg2]overlay="
        f"x='(W-w)/2+({x:.5f}/100)*(W-w)/2':"
        f"y='(H-h)/2+({y:.5f}/100)*(H-h)/2'"
    )
    vf=";".join((pre,bg,fg,overlay))
    if ass_file:
        vf += ",ass='"+_escape_ass_path(ass_file)+"'"
    return vf
