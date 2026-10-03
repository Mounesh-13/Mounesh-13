from pathlib import Path
import re
import xml.etree.ElementTree as ET

FILES = [Path("assets/snake-light.svg"), Path("assets/snake-dark.svg")]
GONE = [Path("assets/escape-light.svg"), Path("assets/escape-dark.svg")]
DARK_FLOW = ["#7C4DFF", "#F72585", "#4CC9F0"]
LIGHT_FLOW = ["#3A0CA3", "#C2185B", "#0077B6"]


def _read(p):
    return p.read_text(encoding="utf-8")


def test_snake_themes_exist_and_size():
    for p in FILES:
        assert p.exists(), f"missing {p}"
        assert p.stat().st_size < 150 * 1024, f"{p} must be <150KB"


def test_escape_files_gone():
    for p in GONE:
        assert not p.exists(), f"stale file still present: {p}"


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


def test_viewbox_tall_canvas():
    for p in FILES:
        t = _read(p)
        assert 'viewBox="0 0 800 1600"' in t, f"{p} must be 800x1600 canvas"
        assert 'width="800"' in t and 'height="1600"' in t
        assert 'viewBox="0 0 800 400"' not in t, f"{p} still has old short board"


def test_master_clock_no_offset_begin():
    for p in FILES:
        t = _read(p)
        for m in re.finditer(r'begin="([\d.]+)s"', t):
            assert float(m.group(1)) == 0, f"{p} offset begin: {m.group(0)}"
        assert 'repeatCount="1"' not in t, f"{p} must not have one-shot repeatCount=1"


def test_every_animate_is_master_clock_12s():
    for p in FILES:
        t = _read(p)
        tags = re.findall(r'<animate(?:Transform)?[^>]*>', t)
        assert len(tags) >= 10, f"{p} too few animates: {len(tags)}"
        for tag in tags:
            assert 'begin="0s"' in tag, f"{p} missing begin=0s: {tag[:120]}"
            assert 'dur="12s"' in tag, f"{p} missing dur=12s: {tag[:120]}"
            assert 'repeatCount="indefinite"' in tag, f"{p} missing indefinite: {tag[:120]}"
        for bad in ['dur="8s"', 'dur="2s"', 'dur="4s"', 'dur="24s"']:
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


def test_grid_visible_full_height():
    for p in FILES:
        t = _read(p)
        assert 'id="grid"' in t, f"{p} missing grid group"
        lines = re.findall(r'<line[^>]*>', t)
        vis = [ln for ln in lines
               if 'stroke-width="2"' in ln
               and re.search(r'opacit[y]*="([\d.]+)"', ln)
               and float(re.search(r'opacit[y]*="([\d.]+)"', ln).group(1)) >= 0.3]
        assert len(vis) >= 40, f"{p} tall board needs >=40 grid lines, found {len(vis)}"
        assert "1600" in t, f"{p} grid must span full 1600 height"
    assert "#111111" in _read(FILES[0]) or "#111" in _read(FILES[0]), "light grid must be #111"
    assert "#FFFFFF" in _read(FILES[1]) or "#fff" in _read(FILES[1]).lower(), "dark grid must be #fff"


def test_snake_long_blocky_segments():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    for c in DARK_FLOW:
        assert c in dark, f"dark missing flow {c}"
    for c in LIGHT_FLOW:
        assert c in light, f"light missing jewel {c}"
    for p in FILES:
        t = _read(p)
        segs = re.findall(r'<rect[^>]*rx="8"[^>]*>', t)
        assert len(segs) >= 14, f"{p} need 14+ blocky segments rx=8, found {len(segs)}"
        assert 'id="tail"' in t, f"{p} missing tail"


def test_head_angry_eyes_fangs_tongue():
    dark = _read(FILES[1])
    light = _read(FILES[0])
    assert "#FF3B30" in dark, "dark missing angry red eyes #FF3B30"
    assert "#D00000" in light, "light missing red eyes #D00000"
    for p in FILES:
        t = _read(p)
        assert 'id="head"' in t, f"{p} missing head group"
        assert 'id="tongue"' in t, f"{p} missing tongue"
        assert t.count("<polygon") >= 3, f"{p} missing fangs + tongue polygons"


def _head_translate(p):
    t = _read(p)
    m = re.search(r'<g id="head">.*?<animateTransform[^>]*type="translate"[^>]*values="([^"]+)"[^>]*keyTimes="([^"]+)"',
                  t, re.DOTALL)
    assert m, f"{p} head missing grid-step translate"
    return m.group(1), m.group(2)


def _parse_pts(values):
    return [tuple(int(float(v)) for v in s.strip().split()) for s in values.split(";")]


def test_snake_closed_winding_circuit():
    for p in FILES:
        values, _ = _head_translate(p)
        pts = _parse_pts(values)
        assert len(pts) >= 20, f"{p} circuit needs 20+ waypoints, found {len(pts)}"
        assert pts[0] == pts[-1], f"{p} circuit not closed"
        for x, y in pts:
            assert 0 <= x <= 800 and 0 <= y <= 1600, f"{p} waypoint off-board: {(x, y)}"
        for need in ((600, 500), (200, 900), (600, 1300)):
            assert need in pts, f"{p} circuit must eat apple at {need}"
        diffs = {(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])}
        assert diffs <= {(40, 0), (-40, 0), (0, 40), (0, -40), (0, 0)}, f"{p} non-grid step: {diffs}"
        assert any(d[0] != 0 for d in diffs) and any(d[1] != 0 for d in diffs), f"{p} circuit must wind both axes"
        dirs = [d for d in
                [(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])] if d != (0, 0)]
        turns = sum(1 for a, b in zip(dirs, dirs[1:]) if a != b)
        assert turns >= 4, f"{p} boustrophedon needs 90-degree turns, found {turns}"


def test_head_grid_step_40px():
    for p in FILES:
        values, _ = _head_translate(p)
        pts = _parse_pts(values)
        assert pts[0] == pts[-1], f"{p} head not seamless"
        for a, b in zip(pts, pts[1:]):
            d = (b[0] - a[0], b[1] - a[1])
            assert d in {(40, 0), (-40, 0), (0, 40), (0, -40), (0, 0)}, f"{p} head step not 40px grid: {a}->{b}"


def test_head_keytimes_equal_spacing():
    for p in FILES:
        values, keytimes = _head_translate(p)
        n = len(values.split(";"))
        ks = [float(k) for k in keytimes.split(";")]
        assert len(ks) == n, f"{p} head keyTimes/values length mismatch: {len(ks)} vs {n}"
        assert ks[0] == 0 and ks[-1] == 1, f"{p} head keyTimes must span 0..1"
        step = 1 / (n - 1)
        for k, i in zip(ks, range(n)):
            assert abs(k - i * step) < 1e-3, f"{p} head keyTimes not equal spacing: {keytimes[:80]}"


def test_body_segments_timeshifted_circuit():
    for p in FILES:
        t = _read(p)
        head_values, _ = _head_translate(p)
        head = _parse_pts(head_values)
        cycle = head[:-1]
        assert len(cycle) >= 20
        grids = re.findall(
            r'<animateTransform[^>]*type="translate"[^>]*calcMode="linear"[^>]*values="([^"]+)"', t)
        assert len(grids) >= 15, f"{p} need head+14 segs+tail grid animates, found {len(grids)}"
        doubled = cycle + cycle
        for v in grids:
            pts = _parse_pts(v)
            assert pts[0] == pts[-1], f"{p} segment not seamless"
            assert len(pts) == len(head), f"{p} segment must reuse head waypoint list"
            cyc = pts[:-1]
            assert any(cyc == doubled[s:s + len(cycle)] for s in range(len(cycle))), \
                f"{p} segment must be time-shifted rotation of head circuit"


def test_three_apples_eaten_vertically():
    for p in FILES:
        t = _read(p)
        assert len(re.findall(r'id="apple', t)) == 3, f"{p} must have exactly 3 foods"
        assert "#E5383B" in t, f"{p} missing red apple square"
        assert "#2DC653" in t, f"{p} missing apple leaf"
        for aid in ("apple-1", "apple-2", "apple-3"):
            m = re.search(rf'<g id="{aid}".*?type="scale"[^>]*values="([^"]+)"', t, re.DOTALL)
            assert m, f"{p} {aid} missing shrink scale"
            assert "0 0" in [s.strip() for s in m.group(1).split(";")], f"{p} {aid} must shrink to 0"
        cy = [int(m.group(1)) for m in
              re.finditer(r'<g id="apple-\d" transform="translate\(\d+ (\d+)\)', t)]
        assert len(cy) == 3 and cy == sorted(cy), f"{p} apples must be spaced vertically: {cy}"
        assert max(cy) - min(cy) >= 500, f"{p} apples must span the tall board: {cy}"


def test_score_ticks_05_10_15_and_gulps():
    for p in FILES:
        t = _read(p)
        for s in ("SCORE 05", "SCORE 10", "SCORE 15"):
            assert s in t, f"{p} missing {s}"
        assert len(re.findall(r'id="gulp', t)) == 3, f"{p} must have 3 gulp pulses"
        assert 'opacity' in t, f"{p} score needs opacity toggles"


def test_board_border():
    for p in FILES:
        t = _read(p)
        assert 'fill="none"' in t, f"{p} missing board border"
        assert "1596" in t or "1600" in t, f"{p} border must fit tall board"


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
        assert 'aria-label="Long snake game"' in t, f"{p} aria-label wrong"
        assert "<title>Long snake game</title>" in t, f"{p} title wrong"
