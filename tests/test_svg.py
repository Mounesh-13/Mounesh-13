from pathlib import Path
import re
import xml.etree.ElementTree as ET

FILES = [Path("assets/escape-light.svg"), Path("assets/escape-dark.svg")]
BANNED_IDS = ["hurry", "dancer", "dance", "banana", "curtain",
              "spinner", "blackout", "knock", "mallet", "crack", "leak"]


def _read(p):
    return p.read_text(encoding="utf-8")


def test_both_themes_exist_and_size():
    for p in FILES:
        assert p.exists(), f"missing {p}"
        assert p.stat().st_size < 100 * 1024, f"{p} must be <100KB"


def test_both_valid_xml():
    for p in FILES:
        ET.fromstring(_read(p))


def test_no_js_or_external():
    for p in FILES:
        t = _read(p)
        assert "<script" not in t.lower()
        assert "foreignobject" not in t.lower()
        t_no_ns = t.replace('xmlns="http://www.w3.org/2000/svg"', "")
        assert "http://" not in t_no_ns and "https://" not in t_no_ns


def test_viewbox_and_loop():
    for p in FILES:
        t = _read(p)
        assert 'viewBox="0 0 800 400"' in t
        assert 'repeatCount="indefinite"' in t


def test_master_clock_no_offset_begin():
    for p in FILES:
        t = _read(p)
        for m in re.finditer(r'begin="([\d.]+)s"', t):
            assert float(m.group(1)) == 0, f"{p} offset begin: {m.group(0)}"
        assert 'repeatCount="1"' not in t, f"{p} must not have one-shot repeatCount=1"


def test_every_animate_is_master_clock_8s():
    for p in FILES:
        t = _read(p)
        tags = re.findall(r'<animate(?:Transform)?[^>]*>', t)
        assert len(tags) >= 10, f"{p} too few animates: {len(tags)}"
        for tag in tags:
            assert 'begin="0s"' in tag, f"{p} missing begin=0s: {tag[:120]}"
            assert 'dur="8s"' in tag, f"{p} missing dur=8s: {tag[:120]}"
            assert 'repeatCount="indefinite"' in tag, f"{p} missing indefinite: {tag[:120]}"
        assert 'dur="2s"' not in t, f"{p} still has old 2s clock"
        assert 'dur="4s"' not in t, f"{p} still has old 4s clock"
        assert 'dur="24s"' not in t, f"{p} still has old 24s clock"


def test_keytimes_range_and_monotonic():
    for p in FILES:
        t = _read(p)
        gates = re.findall(r'keyTimes="([^"]+)"', t)
        assert gates, f"{p} no keyTimes"
        for g in gates:
            ks = [float(k) for k in g.split(";")]
            assert all(0 <= k <= 1 for k in ks), f"{p} keyTimes out of range: {g}"
            assert ks == sorted(ks), f"{p} keyTimes not monotonic: {g}"
            assert ks[0] == 0 and ks[-1] == 1, f"{p} keyTimes must span 0..1: {g}"


def test_seamless_values_first_equals_last():
    for p in FILES:
        t = _read(p)
        vals = re.findall(r'values="([^"]+)"', t)
        assert vals, f"{p} no values lists"
        for v in vals:
            parts = [s.strip() for s in v.split(";")]
            assert len(parts) >= 2, f"{p} values too short: {v}"
            assert parts[0] == parts[-1], f"{p} not seamless: {v}"


def test_no_banned_ids():
    for p in FILES:
        t = _read(p)
        for b in BANNED_IDS:
            assert b not in t, f"{p} still contains banned id {b}"
        assert 'id="hurry"' not in t, f"{p} still has hurry"
        assert 'id="banana"' not in t, f"{p} still has banana"


def test_no_banana_or_notes():
    for p in FILES:
        t = _read(p)
        assert "banana" not in t.lower(), f"{p} still has banana"
        assert "#FFD23F" not in t, f"{p} still has banana yellow #FFD23F"
        assert "♪" not in t, f"{p} still has music notes"


def test_no_banned_text_or_effects():
    for p in FILES:
        t = _read(p)
        low = t.lower()
        assert "loading" not in low, f"{p} still has loading"
        for w in ["BONK", "CRACK", "PHEW"]:
            assert w not in t, f"{p} still has {w}"
        assert 'stroke-dasharray="40 30"' not in t


def test_arcade_rainbow_segments():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    for c in ["#F72585", "#4CC9F0", "#FFE700", "#0B0F1A", "#7C4DFF", "#00F5FF"]:
        assert c in dark, f"dark missing neon {c}"
    for c in ["#3A0CA3", "#C2185B", "#0077B6"]:
        assert c in light, f"light missing jewel {c}"
    for p in FILES:
        t = _read(p)
        seg = re.findall(r'<circle[^>]*r="(2[6-9]|30)"', t)
        assert len(seg) >= 10, f"{p} need ~10 big segment circles r26-30, found {len(seg)}"
        assert 'stroke-width="3"' in t, f"{p} missing segment outlines"


def test_arcade_grid_floor():
    for p in FILES:
        t = _read(p)
        assert 'id="grid"' in t, f"{p} missing grid pattern"
        assert "patternUnits" in t, f"{p} grid must be a pattern"
        assert 'fill="url(#grid)"' in t, f"{p} grid not applied"


def test_scary_head_fangs_eyes():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    assert "#0B0F1A" in dark, "dark missing navy head #0B0F1A"
    assert "#FF3B30" in dark, "dark missing glowing red eyes #FF3B30"
    assert "#1A1A2E" in light, "light missing head #1A1A2E"
    assert "#D00000" in light, "light missing red eyes #D00000"
    for p in FILES:
        t = _read(p)
        assert "<polygon" in t, f"{p} missing white fangs"
        assert 'id="tongue"' in t, f"{p} missing tongue"
        assert t.count("<circle") >= 10, f"{p} need segments + head + glints"


def test_head_lunge_and_gulp_pulse():
    for p in FILES:
        t = _read(p)
        assert "1.15 1.15" in t, f"{p} missing head lunge scale 1.15"
        assert 'id="gulp"' in t, f"{p} missing gulp bulge"
        m = re.search(r'<ellipse id="gulp".*?attributeName="rx"[^>]*values="([^"]+)"', t, re.DOTALL)
        assert m, f"{p} gulp missing rx pulse"
        assert "28" in m.group(1), f"{p} gulp must pulse wide: {m.group(1)}"


def test_snake_slither_travel():
    for p in FILES:
        t = _read(p)
        m = re.search(r'<g id="snake".*?<animateTransform[^>]*type="translate"[^>]*values="([^"]+)"', t, re.DOTALL)
        assert m, f"{p} snake missing travel translate"
        assert m.group(1) == "-350 0;450 0;-350 0", f"{p} snake travel must be -350/450 loop: {m.group(1)}"


def test_food_apple_and_gulp():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    assert "#FFE700" in dark, "dark missing legendary gold apple #FFE700"
    assert "#9A7B00" in light, "light missing deep gold apple #9A7B00"
    for p in FILES:
        t = _read(p)
        assert 'id="food"' in t, f"{p} missing food group"
        assert 'id="gulp"' in t, f"{p} missing gulp bulge"
        m = re.search(r'<g id="food".*?type="scale"[^>]*values="([^"]+)"', t, re.DOTALL)
        assert m, f"{p} food missing shrink scale"
        parts = [s.strip() for s in m.group(1).split(";")]
        assert "0 0" in parts, f"{p} food must shrink to 0: {m.group(1)}"


def test_theme_bg():
    light = _read(FILES[0])
    dark = _read(FILES[1])
    assert "#ffffff" in light, "light bg must be #ffffff"
    assert "#0d1117" in dark, "dark bg must be #0d1117"


def test_identical_geometry_both_themes():
    light = _read(FILES[0])
    dark = _read(FILES[1])

    def strip_colors(s):
        s = re.sub(r'\sfill="[^"]*"', '', s)
        s = re.sub(r'\sstroke="[^"]*"', '', s)
        return s

    assert strip_colors(dark) == strip_colors(light), "geometry must be identical across themes (ignoring palette)"


def test_readme_snake_show():
    r = Path("README.md").read_text(encoding="utf-8")
    assert 'width="600"' in r, "README img width must stay 600"
    assert "?v=7" in r, "README must bump to ?v=7"
    assert r.count("?v=7") >= 2, "BOTH srcset and src must be ?v=7"
    assert "?v=6" not in r, "old ?v=6 must be gone"
    assert "SNAKE SHOW" in r
    assert "🐍" in r
    assert "*He's hungry.*" in r
    assert 'alt="Giant snake eats and leaves"' in r
    assert 'title="Giant snake eats and leaves"' in r
    assert "<picture>" in r


def test_alt_title_match():
    for p in FILES:
        t = _read(p)
        assert 'aria-label="Giant snake eats and leaves"' in t, f"{p} aria-label wrong"
        assert "<title>Giant snake eats and leaves</title>" in t, f"{p} title wrong"
