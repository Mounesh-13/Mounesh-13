from pathlib import Path
import re
import xml.etree.ElementTree as ET

FILES = [Path("assets/escape-light.svg"), Path("assets/escape-dark.svg")]


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
        # no begin="Ns" with N > 0
        for m in re.finditer(r'begin="([\d.]+)s"', t):
            assert float(m.group(1)) == 0, f"{p} offset begin: {m.group(0)}"
        assert 'repeatCount="1"' not in t, f"{p} must not have one-shot repeatCount=1"


def test_every_animate_is_master_clock():
    for p in FILES:
        t = _read(p)
        tags = re.findall(r'<animate(?:Transform)?[^>]*>', t)
        assert len(tags) >= 10, f"{p} too few animates: {len(tags)}"
        for tag in tags:
            assert 'begin="0s"' in tag, f"{p} missing begin=0s: {tag[:120]}"
            assert 'dur="24s"' in tag, f"{p} missing dur=24s: {tag[:120]}"
            assert 'repeatCount="indefinite"' in tag, f"{p} missing indefinite: {tag[:120]}"


def test_keytimes_range_and_monotonic():
    for p in FILES:
        t = _read(p)
        gates = re.findall(r'keyTimes="([^"]+)"', t)
        assert gates, f"{p} no keyTimes"
        for g in gates:
            ks = [float(k) for k in g.split(";")]
            assert all(0 <= k <= 1 for k in ks), f"{p} keyTimes out of range: {g}"
            assert ks == sorted(ks), f"{p} keyTimes not monotonic: {g}"


def test_act_windows():
    for p in FILES:
        t = _read(p)
        gates = re.findall(r'keyTimes="([\d.;]+)"[^>]*dur="24s"', t)
        for g in ['0;0.16;0.33;0.37', '0;0.33;0.54;0.58',
                  '0;0.58;0.79;0.83', '0;0.83;0.85;0.93;0.97;1']:
            assert g in gates, f"{p} missing gate {g}"
        for g in ['0;0.02;0.15;0.19', '0;0.79;0.96;1', '0;0.94;0.97;1']:
            assert g not in gates, f"{p} stale gated window still present: {g}"


def test_ids_present():
    for p in FILES:
        t = _read(p)
        for i in ['id="act1"', 'id="walker"', 'id="banana"', 'id="act2"',
                  'id="eyes-wide"', 'knock-ripple', 'id="act3"', 'id="mallet"',
                  'id="crack"', 'id="act4"', 'leak-drop', 'big-red-button',
                  'id="act5"']:
            assert i in t, f"{p} missing {i}"


def test_no_spinner_loading_blackout():
    for p in FILES:
        t = _read(p)
        assert 'id="spinner"' not in t, f"{p} still has spinner"
        assert "loading" not in t.lower(), f"{p} still has loading text"
        assert 'id="blackout"' not in t, f"{p} still has blackout"
        assert 'stroke-dasharray="40 30"' not in t, f"{p} still has spinner dasharray"


def test_walker_patrol_no_spinner():
    for p in FILES:
        t = _read(p)
        assert 'id="walker"' in t, f"{p} missing walker"
        assert 'values="60 0;420 0;560 0;560 0;60 0"' in t
        assert 'keyTimes="0;0.125;0.33;0.9;1"' in t
        assert 'dur="24s"' in t
        assert 'PHEW!' in t
        assert 'values="0;0;1;1;0;0"' in t
        assert 'keyTimes="0;0.83;0.85;0.93;0.97;1"' in t
        assert 'values="0;0;360;360"' not in t
        assert 'fill="#000"' not in t


def test_theme_bg_and_stick():
    light = _read(FILES[0])
    dark = _read(FILES[1])
    assert 'x="0" y="0" width="800" height="400"' in light
    assert 'x="0" y="0" width="800" height="400"' in dark
    assert "#ffffff" in light, "light bg must be #ffffff"
    assert "#111" in light, "light stick/frame must be #111"
    assert "#0d1117" in dark, "dark bg must be #0d1117"
    assert "#fff" in dark, "dark stick/frame must be #fff"


def test_no_placeholders():
    for p in FILES:
        t = _read(p)
        assert "ACT2" not in t and "ACT3" not in t and "ACT4" not in t and "ACT5" not in t
