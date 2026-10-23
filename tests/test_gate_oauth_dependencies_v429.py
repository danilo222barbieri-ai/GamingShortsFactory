from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/v397-production-gate.yml"


def test_oauth_gate_does_not_install_ffmpeg_before_oauth_contracts():
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: OAuth session, signature and isolation contracts")
    end = text.index("- name: Build worker image", start)
    block = text[start:end]

    assert "python -m unittest discover -s tests -p test_social_oauth_v421.py" in block
    assert "cryptography==50.0.1" in block
    assert "apt-get install" not in block
    assert "ffmpeg" not in block.lower()
