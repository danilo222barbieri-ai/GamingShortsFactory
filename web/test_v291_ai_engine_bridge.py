from pathlib import Path
import sys


def need(ok, msg):
    print(('PASS: ' if ok else 'FAIL: ') + msg)
    if not ok:
        raise AssertionError(msg)


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: test_v291_ai_engine_bridge.py HOME_HTML GENERATED_APP')

    home = Path(sys.argv[1]).read_text(encoding='utf-8')
    app = Path(sys.argv[2]).read_text(encoding='utf-8')

    need('V291 DIRECT AI ENGINE BRIDGE' in home, 'Home V291 marker present')
    need('value({event:"create_ai",duration:nextDuration,engine:nextEngine})' in home,
         'AI create command emits engine and duration directly')

    create_block = home.split('if(action==="create"){', 1)[1].split('}', 1)[0]
    need('parentClick(' not in create_block,
         'AI create command no longer clicks hidden Streamlit button')

    need('# V291 DIRECT AI ENGINE BRIDGE' in app, 'App V291 marker present')
    for ui_engine, profile in (
        ('auto', 'auto'),
        ('best', 'director'),
        ('action', 'action'),
        ('reaction', 'reaction'),
    ):
        need(f'"{ui_engine}":"{profile}"' in app,
             f'{ui_engine} maps to backend profile {profile}')

    need('st.session_state["gsf_v291_ai_request"]' in app,
         'create_ai event arms backend request')
    need('st.session_state["gsf_v291_requested_duration"]' in app,
         '15s/30s duration is persisted for backend execution')
    need('_gsf_v291_direct_create' in app and 'or _gsf_v291_direct_create' in app,
         'real AI backend starts without browser click race')
    need('modalita="🚀 AUTO TOTALE"' in app,
         'all four UI engines enter the proven whole-video scan path')
    need('_v291_forced_profile' in app and '_profile=_v291_forced_profile' in app,
         'Game Brain ranker consumes authoritative engine profile')
    need('("auto","director","action","reaction")' in app,
         'all four backend profiles are explicitly accepted')

    compile(app, '<v291-generated-app>', 'exec')
    print('V291 AI engine bridge: PASS')


if __name__ == '__main__':
    main()
