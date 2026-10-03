from pathlib import Path
import re
import xml.etree.ElementTree as ET

FILES = [Path("assets/escape-light.svg"), Path("assets/escape-dark.svg")]
DARK_FLOW = ["#7C4DFF", "#F72585", "#4CC9F0"]
LIGHT_FLOW = ["#3A0CA3", "#C2185B", "#0077B6"]


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
        for bad in ['dur="2s"', 'dur="4s"', 'dur="24s"']:
            assert bad not in t, f"{p} still has old clock {bad}"


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


def test_theme_bg():
    light = _read(FILES[0])
    dark = _read(FILES[1])
    assert "#ffffff" in light, "light bg must be #ffffff"
    assert "#0d1117" in dark, "dark bg must be #0d1117"


def test_grid_visible():
    for p in FILES:
        t = _read(p)
        assert 'id="grid"' in t, f"{p} missing grid group"
        lines = re.findall(r'<line[^>]*>', t)
        vis = [ln for ln in lines
               if 'stroke-width="2"' in ln
               and re.search(r'opacit[y]*="([\d.]+)"', ln)
               and float(re.search(r'opacit[y]*="([\d.]+)"', ln).group(1)) >= 0.3]
        assert len(vis) >= 20, f"{p} need >=20 visible grid lines, found {len(vis)}"
    assert "#111111" in _read(FILES[0]) or "#111" in _read(FILES[0]), "light grid must be #111"
    assert "#FFFFFF" in _read(FILES[1]) or "#fff" in _read(FILES[1]).lower(), "dark grid must be #fff"


def test_snake_blocky_segments():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    for c in DARK_FLOW:
        assert c in dark, f"dark missing flow {c}"
    for c in LIGHT_FLOW:
        assert c in light, f"light missing jewel {c}"
    for p in FILES:
        t = _read(p)
        segs = re.findall(r'<rect[^>]*rx="8"[^>]*>', t)
        assert len(segs) >= 9, f"{p} need 8-10 blocky segments rx=8, found {len(segs)}"


def test_head_angry_eyes_fangs():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    assert "#FF3B30" in dark, "dark missing angry red eyes #FF3B30"
    assert "#D00000" in light, "light missing red eyes #D00000"
    for p in FILES:
        t = _read(p)
        assert 'id="head"' in t, f"{p} missing head group"
        assert "<polygon" in t, f"{p} missing fangs"


def test_snake_patrol_path():
    for p in FILES:
        t = _read(p)
        m = re.search(r'<g id="snake">.*?<animateTransform[^>]*type="translate"[^>]*values="([^"]+)"',
                      t, re.DOTALL)
        assert m, f"{p} snake missing patrol translate"
        pts = [s.strip() for s in m.group(1).split(";")]
        assert len(pts) >= 5, f"{p} patrol needs waypoints: {m.group(1)}"
        assert pts[0] == pts[-1], f"{p} patrol not seamless"


def test_apple_eaten_mid_loop():
    for p in FILES:
        t = _read(p)
        assert 'id="apple"' in t, f"{p} missing apple"
        assert "#E5383B" in t, f"{p} missing red apple square"
        assert "#2DC653" in t, f"{p} missing apple leaf"
        m = re.search(r'<g id="apple".*?type="scale"[^>]*values="([^"]+)"', t, re.DOTALL)
        assert m, f"{p} apple missing shrink scale"
        assert "0 0" in [s.strip() for s in m.group(1).split(";")], f"{p} apple must shrink to 0"


def test_score_ticks_up():
    for p in FILES:
        t = _read(p)
        assert "SCORE 08" in t and "SCORE 09" in t, f"{p} missing score texts"
        assert len(re.findall(r"SCORE \d+", t)) >= 2, f"{p} need 2-3 score texts"
        assert 'opacity' in t, f"{p} score needs opacity toggles"


def test_game_over_flash():
    for p in FILES:
        t = _read(p)
        assert "GAME OVER" in t, f"{p} missing GAME OVER"
        m = re.search(r'GAME OVER<animate[^>]*values="([^"]+)"', t)
        assert m, f"{p} game-over missing flash animate"
        assert "1" in [s.strip() for s in m.group(1).split(";")], f"{p} game-over never flashes"


def test_board_border():
    for p in FILES:
        t = _read(p)
        assert 'fill="none"' in t, f"{p} missing board border"


def test_identical_geometry_both_themes():
    light = _read(FILES[0])
    dark = _read(FILES[1])

    def strip_colors(s):
        s = re.sub(r'\sfill="[^"]*"', '', s)
        s = re.sub(r'\sstroke="[^"]*"', '', s)
        return s

    assert strip_colors(dark) == strip_colors(light), "geometry must be identical across themes (ignoring palette)"


def test_alt_title_match():
    for p in FILES:
        t = _read(p)
        assert 'aria-label="Snake game on loop"' in t, f"{p} aria-label wrong"
        assert "<title>Snake game on loop</title>" in t, f"{p} title wrong"
