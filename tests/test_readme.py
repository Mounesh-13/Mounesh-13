from pathlib import Path


def test_readme_exists():
    assert Path("README.md").exists()


def test_readme_has_picture_themes():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "<picture" in t
    assert "<source" in t
    assert "prefers-color-scheme: dark" in t
    assert "assets/escape-dark.svg" in t
    assert "assets/escape-light.svg" in t
    assert t.count("<img") == 1


def test_readme_no_single_svg():
    t = Path("README.md").read_text(encoding="utf-8")
    assert '"./assets/escape.svg"' not in t
    assert "'./assets/escape.svg'" not in t


def test_readme_no_resume_leak():
    t = Path("README.md").read_text(encoding="utf-8").lower()
    for banned in ["shields.io", "github-readme-stats", "tech stack", "experience", "my skills"]:
        assert banned not in t, f"banned token {banned}"


def test_readme_has_broadcast():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "STICKMAN SHOW" in t
    assert "Don't look at him" in t


def test_readme_dance_alt_title():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "Stickman hurrying like a mad man" in t
    assert "Stickman dancing on loop" not in t
