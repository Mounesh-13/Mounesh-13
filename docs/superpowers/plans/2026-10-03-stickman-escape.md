# Stick-Man Escape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build fresh Mounesh-13 profile README with single looping stick-man escape SVG and push live.

**Architecture:** Single self-contained SMIL SVG (800x400, 24s loop, 5 acts) + static centered README wrapper; no JS, no externals, transparent bg.

**Tech Stack:** GitHub Flavored Markdown, SVG 1.1 + SMIL (`<animate>`, `<animateTransform>`), Python 3.13 for verification scripts, git.

**Spec:** `docs/superpowers/specs/2026-10-03-stickman-escape-design.md`

## Global Constraints

- Workspace is `C:/Users/Nirmaan2/AppData/Local/Temp/opencode/stickman-escape/` — never write to `C:\Windows\System32`.
- `assets/escape.svg` must be <100KB, transparent background, no `<script>`, no `<foreignObject>`, no external hrefs/fonts.
- `README.md` must contain zero bio/skills/repos/badges/stats — only EMERGENCY BROADCAST header + single img + caption.
- SMIL loop total 24s, `repeatCount="indefinite"`, all begin offsets 0-24s.
- Python interpreter is `py -3.13` (not `python`/`python3`).
- Target remote `https://github.com/Mounesh-13/Mounesh-13.git`, branch `main`.

## Review Focus

- Transparent SVG invisible on white mode if strokes too thin — expect thick dark strokes with white halo visible both modes.
- GitHub image proxy caches old SVG — expect `?v=2` cache-bust or rename if update doesn't show.
- SMIL `begin` typo breaks whole loop silence — expect validator to catch missing `dur`/`repeatCount`.
- README img path case-sensitive `assets/escape.svg` — expect exact relative path `assets/escape.svg`.
- Mobile 375px overflow if width fixed — expect `width="600"` + SVG viewBox scales down without horizontal scroll.

---

### Task 1: Workspace scaffold + README wrapper

**Files:**
- Create: `README.md`
- Create: `assets/.gitkeep`
- Test: `tests/test_readme.py`

**Interfaces:**
- Consumes: none
- Produces: `README.md` with exact img path `assets/escape.svg` that Task 2-6 fill; `tests/test_readme.py::test_readme_*` helpers reused by Task 6.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_readme.py
from pathlib import Path
def test_readme_exists():
    assert Path("README.md").exists()
def test_readme_has_single_img():
    t = Path("README.md").read_text(encoding="utf-8")
    assert 'assets/escape.svg' in t
    assert t.count("<img") == 1
def test_readme_no_resume_leak():
    t = Path("README.md").read_text(encoding="utf-8").lower()
    for banned in ["shields.io", "github-readme-stats", "tech stack", "experience", "my skills"]:
        assert banned not in t, f"banned token {banned}"
def test_readme_has_broadcast():
    t = Path("README.md").read_text(encoding="utf-8")
    assert "EMERGENCY BROADCAST" in t
    assert "Don't look at him" in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.13 -m pytest tests/test_readme.py -v`
Expected: FAIL with "README.md does not exist" (no files yet).

- [ ] **Step 3: Write minimal implementation**

```markdown
<!-- Stick-man escape loop. Pure comedy, no bio. -->
<div align="center">

# 🚨 EMERGENCY BROADCAST 🚨

<img src="./assets/escape.svg" width="600" alt="Stickman tries to escape the README — knocks, smashes, leaks, spinner loop" title="Stickman tries to escape the README">

### *Don't look at him, he's trying to escape.*

</div>
```

Save as `README.md` in workspace root. Create empty `assets/.gitkeep`.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.13 -m pytest tests/test_readme.py -v`
Expected: PASS (4 passed). If `pytest` missing, run `py -3.13 -m pip install pytest` first.

- [ ] **Step 5: Commit**

```bash
git add README.md assets/.gitkeep tests/test_readme.py
git commit -m "feat: add README wrapper for stickman escape"
```

---

### Task 2: escape.svg skeleton + Act1 walk/slip

**Files:**
- Create: `assets/escape.svg`
- Test: `tests/test_svg.py`

**Interfaces:**
- Consumes: `README.md` img path from Task 1
- Produces: `assets/escape.svg` with `<svg viewBox="0 0 800 400">` + defs + Act1 group `id="act1"`; later tasks append `act2`..`act5`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_svg.py
from pathlib import Path
import re
def _svg():
    return Path("assets/escape.svg").read_text(encoding="utf-8")
def test_svg_exists_and_size():
    p = Path("assets/escape.svg")
    assert p.exists()
    assert p.stat().st_size < 100 * 1024, "must be <100KB"
def test_svg_no_js_or_external():
    t = _svg()
    assert "<script" not in t.lower()
    assert "foreignobject" not in t.lower()
    assert "http://" not in t and "https://" not in t
def test_svg_has_viewbox_and_loop():
    t = _svg()
    assert 'viewBox="0 0 800 400"' in t
    assert 'repeatCount="indefinite"' in t
def test_act1_present():
    t = _svg()
    assert 'id="act1"' in t
    assert 'id="walker"' in t
    assert 'id="banana"' in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.13 -m pytest tests/test_svg.py -v`
Expected: FAIL — `assets/escape.svg` missing.

- [ ] **Step 3: Write minimal implementation**

Create `assets/escape.svg` (full skeleton + Act1; later tasks insert before `<!-- ACT2 -->` marker):

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400" role="img" aria-label="Stickman escape loop">
<title>Stickman tries to escape</title>
<rect x="4" y="4" width="792" height="392" rx="18" fill="none" stroke="#111" stroke-width="6"/>
<!-- README margin frame -->
<g id="act1">
  <!-- floor -->
  <line x1="40" y1="330" x2="760" y2="330" stroke="#111" stroke-width="4" stroke-linecap="round"/>
  <!-- banana -->
  <g id="banana" transform="translate(430,318)">
    <path d="M0,0 Q20,12 42,2 Q22,18 0,0 Z" fill="#FFD23F" stroke="#111" stroke-width="3"/>
  </g>
  <!-- walker: simple stickman, walks 0-3s then slips -->
  <g id="walker">
    <animateTransform attributeName="transform" type="translate" from="60 0" to="420 0" begin="0s" dur="3s" fill="freeze" repeatCount="indefinite" />
    <!-- body parts offset so slip rotation looks right; keep simple -->
    <g id="stickbody" transform="translate(0,230)">
      <circle cx="0" cy="0" r="16" fill="none" stroke="#111" stroke-width="6"/>
      <circle cx="0" cy="0" r="16" fill="none" stroke="#fff" stroke-width="10" opacity="0.35"/>
      <line x1="0" y1="16" x2="0" y2="70" stroke="#111" stroke-width="6" stroke-linecap="round"/>
      <line x1="0" y1="34" x2="-20" y2="58" stroke="#111" stroke-width="5" stroke-linecap="round">
        <animate attributeName="x2" values="-20;20;-20" begin="0s" dur="1s" repeatCount="indefinite"/>
      </line>
      <line x1="0" y1="34" x2="20" y2="58" stroke="#111" stroke-width="5" stroke-linecap="round">
        <animate attributeName="x2" values="20;-20;20" begin="0s" dur="1s" repeatCount="indefinite"/>
      </line>
      <line x1="0" y1="70" x2="-18" y2="100" stroke="#111" stroke-width="5" stroke-linecap="round">
        <animate attributeName="x2" values="-18;18;-18" begin="0s" dur="1s" repeatCount="indefinite"/>
      </line>
      <line x1="0" y1="70" x2="18" y2="100" stroke="#111" stroke-width="5" stroke-linecap="round">
        <animate attributeName="x2" values="18;-18;18" begin="0s" dur="1s" repeatCount="indefinite"/>
      </line>
      <animateTransform attributeName="transform" type="rotate" values="0;0;-70;0" keyTimes="0;0.75;0.85;1" begin="0s" dur="4s" fill="freeze" repeatCount="indefinite" additive="sum"/>
    </g>
  </g>
</g>
<!-- ACT2 -->
<!-- ACT3 -->
<!-- ACT4 -->
<!-- ACT5 -->
</svg>
```

Note: white halo under head is behind-stroke trick for dark mode; keep strokes #111 thick.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.13 -m pytest tests/test_svg.py::test_svg_exists_and_size tests/test_svg.py::test_svg_no_js_or_external tests/test_svg.py::test_svg_has_viewbox_and_loop tests/test_svg.py::test_act1_present -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add assets/escape.svg tests/test_svg.py
git commit -m "feat: add escape.svg skeleton + Act1 walk/slip"
```

---

### Task 3: Act2 realization + screen knock

**Files:**
- Modify: `assets/escape.svg` (replace `<!-- ACT2 -->`)
- Test: `tests/test_svg.py` (append act2 test)

**Interfaces:**
- Consumes: `act1` timing (ends ~4s)
- Produces: `id="act2"` with `id="eyes-wide"`, `id="knock-ripple-1/2"`.

- [ ] **Step 1: Write the failing test**

```python
def test_act2_present():
    from pathlib import Path
    t = Path("assets/escape.svg").read_text(encoding="utf-8")
    assert 'id="act2"' in t
    assert 'id="eyes-wide"' in t
    assert 'knock-ripple' in t
    assert 'begin="4s"' in t
```

Append to `tests/test_svg.py`.

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.13 -m pytest tests/test_svg.py::test_act2_present -v`
Expected: FAIL — `id="act2"` not found.

- [ ] **Step 3: Write minimal implementation**

Replace `<!-- ACT2 -->` with:

```svg
<g id="act2" opacity="0">
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.9;1" begin="0s" dur="24s" repeatCount="indefinite"/>
  <!-- eyes widen at 4s -->
  <g id="eyes-wide" transform="translate(470,240)" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.2;0.25" begin="0s" dur="24s" repeatCount="indefinite"/>
    <circle cx="-8" cy="0" r="3" fill="#111"><animate attributeName="r" values="3;7;7;3" keyTimes="0;0.1;0.8;1" begin="4s" dur="4s" fill="freeze" repeatCount="indefinite"/></circle>
    <circle cx="8" cy="0" r="3" fill="#111"><animate attributeName="r" values="3;7;7;3" keyTimes="0;0.1;0.8;1" begin="4s" dur="4s" fill="freeze" repeatCount="indefinite"/></circle>
    <text x="0" y="-24" text-anchor="middle" font-size="22" font-family="sans-serif" fill="#111">!</text>
  </g>
  <!-- knock ripples at 6s and 6.6s -->
  <circle id="knock-ripple-1" cx="620" cy="180" r="6" fill="none" stroke="#111" stroke-width="3" opacity="0">
    <animate attributeName="opacity" values="0;1;0" begin="6s" dur="0.8s" repeatCount="indefinite"/>
    <animate attributeName="r" values="6;34" begin="6s" dur="0.8s" repeatCount="indefinite"/>
  </circle>
  <circle id="knock-ripple-2" cx="620" cy="180" r="6" fill="none" stroke="#111" stroke-width="3" opacity="0">
    <animate attributeName="opacity" values="0;1;0" begin="6.6s" dur="0.8s" repeatCount="indefinite"/>
    <animate attributeName="r" values="6;34" begin="6.6s" dur="0.8s" repeatCount="indefinite"/>
  </circle>
  <text x="620" y="120" text-anchor="middle" font-size="26" font-family="sans-serif" fill="#111" opacity="0">BONK!
    <animate attributeName="opacity" values="0;1;0" keyTimes="0;0.1;1" begin="6s" dur="2s" repeatCount="indefinite"/>
  </text>
</g>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.13 -m pytest tests/test_svg.py -v`
Expected: PASS (prior tests still pass).

- [ ] **Step 5: Commit**

```bash
git add assets/escape.svg tests/test_svg.py
git commit -m "feat: add Act2 realization and screen knock"
```

---

### Task 4: Act3 mallet smash + crack

**Files:**
- Modify: `assets/escape.svg` (replace `<!-- ACT3 -->`)
- Test: `tests/test_svg.py`

**Interfaces:**
- Consumes: `act2` knock at ~6s
- Produces: `id="act3"` with `id="mallet"`, `id="crack"`.

- [ ] **Step 1: Write the failing test**

```python
def test_act3_present():
    from pathlib import Path
    t = Path("assets/escape.svg").read_text(encoding="utf-8")
    assert 'id="act3"' in t
    assert 'id="mallet"' in t
    assert 'id="crack"' in t
    assert 'begin="8s"' in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.13 -m pytest tests/test_svg.py::test_act3_present -v`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Replace `<!-- ACT3 -->` with:

```svg
<g id="act3">
  <g id="mallet" transform="translate(560,250)" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.25;0.3" begin="0s" dur="24s" repeatCount="indefinite"/>
    <rect x="-14" y="-70" width="28" height="52" rx="6" fill="#E63946" stroke="#111" stroke-width="4"/>
    <rect x="-6" y="-18" width="12" height="58" fill="#8B5E34" stroke="#111" stroke-width="4"/>
    <animateTransform attributeName="transform" type="rotate" values="-30;45;-30" keyTimes="0;0.5;1" begin="8s" dur="2s" fill="freeze" repeatCount="indefinite" additive="replace"/>
  </g>
  <polyline id="crack" points="600,330 580,260 610,210 590,150 620,100" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round" stroke-dasharray="400" stroke-dashoffset="400" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.6;0.65" begin="0s" dur="24s" repeatCount="indefinite"/>
    <animate attributeName="stroke-dashoffset" from="400" to="0" begin="10s" dur="0.6s" fill="freeze" repeatCount="indefinite"/>
  </polyline>
  <text x="400" y="60" text-anchor="middle" font-size="34" font-family="sans-serif" font-weight="bold" fill="#E63946" opacity="0">CRACK!
    <animate attributeName="opacity" values="0;1;0" begin="10s" dur="1.2s" repeatCount="indefinite"/>
  </text>
</g>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.13 -m pytest tests/test_svg.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add assets/escape.svg tests/test_svg.py
git commit -m "feat: add Act3 mallet smash and crack"
```

---

### Task 5: Act4 leak + self-destruct button

**Files:**
- Modify: `assets/escape.svg` (replace `<!-- ACT4 -->`)
- Test: `tests/test_svg.py`

**Interfaces:**
- Consumes: `crack` at 10s
- Produces: `id="act4"` with `id="leak-drop"`, `id="big-red-button"`.

- [ ] **Step 1: Write the failing test**

```python
def test_act4_present():
    from pathlib import Path
    t = Path("assets/escape.svg").read_text(encoding="utf-8")
    assert 'id="act4"' in t
    assert 'leak-drop' in t
    assert 'big-red-button' in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.13 -m pytest tests/test_svg.py::test_act4_present -v`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Replace `<!-- ACT4 -->` with:

```svg
<g id="act4">
  <g id="leak" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.25;0.3" begin="0s" dur="24s" repeatCount="indefinite"/>
    <rect id="leak-drop" x="200" y="20" width="14" height="22" rx="7" fill="#4CC9F0" stroke="#111" stroke-width="3">
      <animate attributeName="y" values="20;300" begin="14s" dur="1s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="1;1;0" begin="14s" dur="1s" repeatCount="indefinite"/>
    </rect>
    <rect id="leak-drop-2" x="260" y="20" width="10" height="16" rx="5" fill="#4CC9F0" stroke="#111" stroke-width="3">
      <animate attributeName="y" values="20;300" begin="15s" dur="1s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="1;1;0" begin="15s" dur="1s" repeatCount="indefinite"/>
    </rect>
  </g>
  <g id="big-red-button" transform="translate(680,300)" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.2;0.25" begin="0s" dur="24s" repeatCount="indefinite"/>
    <rect x="-52" y="-18" width="104" height="36" rx="8" fill="#fff" stroke="#111" stroke-width="4"/>
    <circle cx="0" cy="0" r="12" fill="#E63946" stroke="#111" stroke-width="4">
      <animate attributeName="r" values="12;9;12" begin="17s" dur="0.6s" repeatCount="indefinite"/>
    </circle>
    <text x="0" y="-26" text-anchor="middle" font-size="13" font-family="sans-serif" fill="#111">DO NOT PRESS</text>
  </g>
</g>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -3.13 -m pytest tests/test_svg.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add assets/escape.svg tests/test_svg.py
git commit -m "feat: add Act4 leak and self-destruct button"
```

---

### Task 6: Act5 spinner reset + final verification

**Files:**
- Modify: `assets/escape.svg` (replace `<!-- ACT5 -->`)
- Test: `tests/test_svg.py`, `tests/test_readme.py`

**Interfaces:**
- Consumes: all acts 0-19s
- Produces: `id="act5"` with `id="spinner"`, seamless 24s loop; verified file sizes.

- [ ] **Step 1: Write the failing test**

```python
def test_act5_present():
    from pathlib import Path
    t = Path("assets/escape.svg").read_text(encoding="utf-8")
    assert 'id="act5"' in t
    assert 'id="spinner"' in t
    assert 'begin="19s"' in t
def test_no_placeholders():
    from pathlib import Path
    t = Path("assets/escape.svg").read_text(encoding="utf-8")
    assert "ACT2" not in t and "ACT3" not in t and "ACT4" not in t and "ACT5" not in t
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.13 -m pytest tests/test_svg.py::test_act5_present -v`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Replace `<!-- ACT5 -->` with:

```svg
<g id="act5">
  <g id="spinner" transform="translate(400,200)" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.2;0.25" begin="0s" dur="24s" repeatCount="indefinite"/>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" begin="19s" dur="1.6s" repeatCount="indefinite"/>
      <circle cx="0" cy="0" r="34" fill="none" stroke="#111" stroke-width="8" stroke-dasharray="40 30" stroke-linecap="round"/>
    </g>
    <text x="0" y="70" text-anchor="middle" font-size="16" font-family="sans-serif" fill="#111">loading…</text>
  </g>
  <rect x="0" y="0" width="800" height="400" fill="#111" opacity="0">
    <animate attributeName="opacity" values="0;0;0.9;0" keyTimes="0;0.9;0.95;1" begin="0s" dur="24s" repeatCount="indefinite"/>
  </rect>
</g>
```

- [ ] **Step 4: Run full verification**

Run: `py -3.13 -m pytest tests/ -v`
Expected: PASS all. Then run:

```bash
wc -c assets/escape.svg README.md
py -3.13 -c "from pathlib import Path; print(len(Path('assets/escape.svg').read_bytes()))"
```

Confirm <102400 bytes, open `assets/escape.svg` in browser to eyeball 24s loop.

- [ ] **Step 5: Commit**

```bash
git add assets/escape.svg tests/test_svg.py
git commit -m "feat: add Act5 spinner reset and seamless loop"
```

---

### Task 7: Go-live to Mounesh-13/Mounesh-13

**Files:**
- None (git remote + push only)

**Interfaces:**
- Consumes: committed README + assets from Tasks 1-6
- Produces: live profile at `https://github.com/Mounesh-13`.

- [ ] **Step 1: Confirm clean tree**

```bash
git status --short
py -3.13 -m pytest tests/ -q
```

Expected: no output from status, tests pass.

- [ ] **Step 2: Wire remote and push (ask user for auth first — never echo token)**

```bash
git branch -M main
git remote add origin https://github.com/Mounesh-13/Mounesh-13.git
git push -u origin main
```

If remote exists, use `git remote set-url origin https://github.com/Mounesh-13/Mounesh-13.git`. If push needs token, stop and ask user for PAT with `repo` scope, then push via credential helper — do not store token in files.

- [ ] **Step 3: Verify live**

Fetch `https://github.com/Mounesh-13` and confirm EMERGENCY BROADCAST + escape.svg renders. If cached, append `?v=2` to img src in follow-up commit.

- [ ] **Step 4: Final commit/tag if needed**

No code change — record push SHA in plan file footer.
