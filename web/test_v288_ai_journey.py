import sys
from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8")


def require(name, condition):
    status = "PASS" if condition else "FAIL"
    print(f"{status}: {name}")
    if not condition:
        raise AssertionError(name)


def main():
    if len(sys.argv) != 5:
        raise SystemExit(
            "usage: test_v288_ai_journey.py AI_HTML HOME_HTML EDITOR_HTML GENERATED_APP"
        )

    ai = read(sys.argv[1])
    home = read(sys.argv[2])
    editor = read(sys.argv[3])
    app = read(sys.argv[4])

    # AI page: engine choice is step 1; results become a real step 2 with an explicit fork.
    require("V288 AI marker", "V288 AI JOURNEY" in ai)
    require("AI search CTA copy", "TROVA I 3 MOMENTI MIGLIORI" in ai)
    require("journey progress", "1 Motore" in ai and "2 Momento" in ai and "3 Editor" in ai and "4 Crea Short" in ai and "5 Pronto" in ai)
    require("selected moment action panel", 'id="momentNextActions"' in ai)
    require("editor action from selected moment", 'id="editSelectedMoment"' in ai and 'send("open_editor"' in ai)
    require("direct short action from selected moment", 'id="createSelectedMoment"' in ai and 'send("create_short"' in ai)
    require("moment selection event", 'send("select_moment"' in ai)
    require("selection is explicit state", "selectedMoment" in ai)

    # Home bridge: selection is remembered and the exact preview is resolved before routing.
    require("V288 Home bridge marker", "V288 AI JOURNEY BRIDGE" in home)
    require("Home handles moment selection", 'action==="select_moment"' in home)
    require("Home remembers selected moment", "gsf_ai_selected_moment_v288" in home)
    require("Home resolves selected preview", "selectedPreview" in home and "previewData" in home)
    require("Home routes selected moment to Editor", 'shellNav("editor"' in home and "video_url" in home)
    require("Home routes selected moment direct to Short", 'action==="create_short"' in home and 'event:"create_short"' in home)

    # Editor: Done remains, but the journey now has a prominent and explicit final CTA.
    require("V288 Editor marker", "V288 EDITOR TO SHORT" in editor)
    require("Editor Create Short CTA", 'id="createShortFromEditor"' in editor and "HAI FINITO?" in editor and "CREA IL TUO SHORT" in editor)
    require("Editor next action payload", "payload.nextAction='create_short'" in editor)
    require("Editor still has Done", 'id="doneBtn"' in editor)

    # Persistent shell: consume selected preview on Editor open and persist state before final creation.
    require("V288 Editor shell marker", "V288 EDITOR JOURNEY BRIDGE" in app)
    require("shell accepts selected editor video", "selection.video_url" in app)
    require("shell consumes editor create_short action", "state.nextAction==='create_short'" in app)
    require("shell triggers existing final short control", "triggerCreateShort" in app and "crea short finale" in app)

    print("V288 AI Journey: PASS")


if __name__ == "__main__":
    main()
