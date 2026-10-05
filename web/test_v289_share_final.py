import sys
from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8")


def require(name, condition):
    print(("PASS" if condition else "FAIL") + ": " + name)
    if not condition:
        raise AssertionError(name)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: test_v289_share_final.py SHARE_HTML STRUCTURAL_HOME_SOURCE")

    share = read(sys.argv[1])
    shell = read(sys.argv[2])
    visible = share.split("<script>", 1)[0].lower()

    require("V289 final-share marker", "V289 SHARE FINAL" in share)
    require("GSF final title", "Condividi o scarica" in share and "Il tuo Short è pronto" in share)
    require("four social publishing cards", all(f'data-card="{name}"' in share for name in ("youtube", "tiktok", "instagram", "facebook")))
    require("social actions remain functional", all(f'data-platform="{name}"' in share for name in ("youtube", "tiktok", "instagram", "facebook")))
    require("download area exists", "Scarica il tuo Short" in share and "Scarica video" in share)
    require("quality strip exists", all(label in share for label in ("1080×1920", "H.264", "60 FPS", "AAC", "Qualità massima")))
    require("no visible video reader", "<video" not in visible and "player" not in visible and "video-preview" not in visible)
    require("no social mini players", "cardpreview" not in visible and "mini-player" not in visible)
    require("GSF pastel final layout", "gsfFinalSurface" in share and "gsfFinalGrid" in share)
    require("mobile final layout", "V289 SHARE MOBILE" in share)
    require("share iframe cache bumped", '/share-v156/?v=289' in shell)

    print("V289 Share Final: PASS")


if __name__ == "__main__":
    main()
