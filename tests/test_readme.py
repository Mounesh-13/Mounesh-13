from pathlib import Path


def test_readme_exists():
    assert Path("README.md").exists()


def test_readme_has_picture_themes():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "<picture" in t
    assert "<source" in t
    assert "prefers-color-scheme: dark" in t
    assert "prefers-color-scheme: light" in t
    assert t.count("<source") == 2
    assert "assets/snake-dark.svg" in t
    assert "assets/snake-light.svg" in t
    assert t.count("<img") == 1


def test_readme_fresh_filenames_no_query_string():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "?v=" not in t, "fresh snake-* filenames bust cache, no query string allowed"
    assert "escape-" not in t, "stale escape-* filenames must be gone"


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


def test_readme_full_width_alt():
    t = Path("README.md").read_text(encoding="utf-8")
    assert 'width="100%"' in t, "README img must be full width 100%"
    assert 'width="600"' not in t, "old fixed width must be gone"
    assert "Long snake game" in t
    assert t.count("Long snake game") >= 2, "alt + title must both say Long snake game"
