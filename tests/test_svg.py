from pathlib import Path
import re
import xml.etree.ElementTree as ET

FILES = [Path("assets/escape-light.svg"), Path("assets/escape-dark.svg")]
BANNED_IDS = ["dancer", "dance", "banana", "act2", "act3", "act4", "act5",
              "spinner", "blackout", "knock-ripple", "mallet", "crack",
              "leak-drop", "big-red-button"]


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


def test_every_animate_is_master_clock_4s():
    for p in FILES:
        t = _read(p)
        tags = re.findall(r'<animate(?:Transform)?[^>]*>', t)
        assert len(tags) >= 10, f"{p} too few animates: {len(tags)}"
        for tag in tags:
            assert 'begin="0s"' in tag, f"{p} missing begin=0s: {tag[:120]}"
            assert 'dur="4s"' in tag, f"{p} missing dur=4s: {tag[:120]}"
            assert 'repeatCount="indefinite"' in tag, f"{p} missing indefinite: {tag[:120]}"
        assert 'dur="2s"' not in t, f"{p} still has old 2s clock"
        assert 'dur="8s"' not in t, f"{p} still has old 8s clock"
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
        assert 'id="act1"' not in t, f"{p} still has act1"
        assert 'id="dancer"' not in t, f"{p} still has dancer"
        assert 'id="spinner"' not in t
        assert 'id="blackout"' not in t


def test_no_banana():
    for p in FILES:
        t = _read(p)
        assert "banana" not in t.lower(), f"{p} still has banana"
        assert "#FFD23F" not in t, f"{p} still has banana yellow #FFD23F"
        assert 'id="banana"' not in t, f"{p} still has banana prop"


def test_no_dance_notes():
    for p in FILES:
        t = _read(p)
        assert "♪" not in t, f"{p} still has music notes"
        assert "-8;8;-8" not in t, f"{p} still has old dance lean"
        assert "0 -14" not in t, f"{p} still has old dance bounce"


def test_hurry_present():
    for p in FILES:
        t = _read(p)
        assert 'id="hurry"' in t, f"{p} missing hurry group"
        assert 'translate(400,210)' in t, f"{p} hurry not center-stage"
        assert 'r="16"' in t, f"{p} head r16 missing"
        assert "stroke-linecap" in t, f"{p} round linecaps missing"


def test_hurry_frantic_details():
    for p in FILES:
        t = _read(p)
        low = t.lower()
        assert "speed" in low, f"{p} missing speed lines"
        assert "sweat" in low, f"{p} missing sweat drops"
        # rapid leg pump: x2 values with 8+ entries
        x2_vals = re.findall(r'attributeName="x2" values="([^"]+)"', t)
        assert x2_vals, f"{p} no leg/arm x2 animation"
        assert any(len(v.split(";")) >= 8 for v in x2_vals), f"{p} need 8+ entry x2 pump: {x2_vals}"
        # forward lean ~15deg
        assert "15;" in t or ";15" in t or "rotate(15" in t or "values=\"15" in t, f"{p} missing ~15deg forward lean"
        # mad face: eyes + shouting mouth
        assert "<ellipse" in t, f"{p} missing shouting mouth ellipse"
        assert t.count("<circle") >= 3, f"{p} need head + 2 eyes (+sweat)"


def test_no_banned_text_or_effects():
    for p in FILES:
        t = _read(p)
        low = t.lower()
        assert "loading" not in low, f"{p} still has loading"
        for w in ["BONK", "CRACK", "PHEW"]:
            assert w not in t, f"{p} still has {w}"
        assert 'stroke-dasharray="40 30"' not in t


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


def test_stage_curtains_present():
    for p in FILES:
        t = _read(p)
        assert 'id="curtain-left"' in t, f"{p} missing curtain-left"
        assert 'id="curtain-right"' in t, f"{p} missing curtain-right"
        assert 'id="curtain-top"' in t, f"{p} missing curtain-top"
        assert "#C1121F" in t, f"{p} missing curtain red #C1121F"
        assert t.count("#C1121F") >= 2, f"{p} need red in curtains+valance"
        assert "#780000" in t, f"{p} missing fold stripe #780000"


def test_stage_opening_kept():
    for p in FILES:
        t = _read(p)
        assert "curtain-left" in t
        assert t.count("#C1121F") >= 2
        for cid in ["curtain-left", "curtain-right", "curtain-top"]:
            m = re.search(rf'<g id="{cid}".*?</g>', t, re.DOTALL)
            assert m, f"{p} missing {cid} group"
            g = m.group(0)
            assert "<animate" not in g, f"{p} {cid} must be static (no animate)"
            for rm in re.finditer(r'<rect[^>]*>', g):
                tag = rm.group(0)
                xm = re.search(r'x="([\d.]+)"', tag)
                wm = re.search(r'width="([\d.]+)"', tag)
                ym = re.search(r'y="([\d.]+)"', tag)
                hm = re.search(r'height="([\d.]+)"', tag)
                if xm and wm and ym and hm:
                    x, w, y, h = map(float, (xm.group(1), wm.group(1), ym.group(1), hm.group(1)))
                    covers = (x < 600 and x + w > 200 and y < 200 and y + h > 200)
                    assert not covers, f"{p} {cid} rect blocks stage: {tag[:120]}"
        assert "H92" in t or "H90" in t, f"{p} left curtain width ~90px missing"
        assert "H708" in t or "H710" in t, f"{p} right curtain width ~90px missing"


def test_curtains_order_and_readme_big_screen():
    for p in FILES:
        t = _read(p)
        assert t.index('id="curtain-left"') < t.index('id="hurry"'), f"{p} curtains must be before hurry"
        assert t.index('id="curtain-top"') < t.index('id="hurry"'), f"{p} valance must be before hurry"
    r = Path("README.md").read_text(encoding="utf-8")
    assert 'width="600"' in r, "README img width must stay 600"
    assert "?v=5" in r, "README must bump to ?v=5"
    assert r.count("?v=5") >= 2, "BOTH srcset and src must be ?v=5"
    assert "?v=4" not in r, "old ?v=4 must be gone"
    assert "?v=3" not in r, "old ?v=3 must be gone"
    assert "?v=2" not in r, "old ?v=2 must be gone"
    assert "STICKMAN SHOW" in r
    assert 'alt="Stickman hurrying like a mad man"' in r
    assert 'title="Stickman hurrying like a mad man"' in r


def test_hurry_lateral_travel():
    for p in FILES:
        t = _read(p)
        m = re.search(r'<g id="hurry".*?<animateTransform[^>]*type="translate"[^>]*values="([^"]+)"', t, re.DOTALL)
        assert m, f"{p} hurry missing lateral translate shuttle"
        parts = [s.strip() for s in m.group(1).split(";")]
        assert len(parts) >= 4, f"{p} hurry travel needs there-and-back: {m.group(1)}"
        xs = [float(s.split()[0]) for s in parts]
        assert max(xs) - min(xs) >= 250, f"{p} hurry travel span too small: {m.group(1)}"


def test_limbs_shake_many_entries():
    for p in FILES:
        t = _read(p)
        x2_vals = re.findall(r'attributeName="x2" values="([^"]+)"', t)
        assert x2_vals, f"{p} no limb x2 animation"
        assert any(len(v.split(";")) >= 8 for v in x2_vals), f"{p} limbs must shake 8+ entries: {x2_vals}"
        assert any(len(v.split(";")) >= 10 for v in x2_vals), f"{p} limbs must shake 10+ extremes: {x2_vals}"
