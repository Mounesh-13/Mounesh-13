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


def test_readme_snake_header_caption():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "# 🐍 SNAKE" in t
    assert "SNAKE SHOW" not in t
    assert "theatre" not in t.lower() and "theater" not in t.lower()
    assert "He's hungry" not in t
    assert "*Eat. Grow. Repeat.*" in t


def test_readme_version_width_alt():
    t = Path("README.md").read_text(encoding="utf-8")
    assert 'width="600"' in t, "README img width must be 600"
    assert "?v=9" in t, "README must bump to ?v=9"
    assert t.count("?v=9") >= 2, "BOTH srcset and src must be ?v=9"
    assert "?v=8" not in t and "?v=7" not in t, "old version must be gone"
    assert "Snake game on loop" in t
    assert t.count("Snake game on loop") >= 2, "alt + title must both say Snake game on loop"
