# Stick-Man Escape Profile README — Design Spec
Date: 2026-10-03
Target: Mounesh-13/Mounesh-13 (fresh repo, no migration of old LONG WAY DOWN assets)
Path choice: Architectural (new asset + README + publish)

## 1. Intent & Success Criteria
- Outcome: GitHub profile README that is 100% slapstick comedy, zero bio/skills/repos/badges/stats.
- Audience: profile visitors, dark + light mode.
- Success: single looping animation plays instantly, funny on first 5s, loops seamlessly, file <100KB, renders on github.com + mobile.
- Constraints: GitHub README sanitizer — pure SMIL SVG only, no JS, no external calls/fonts, transparent bg.

## 2. Architecture & Files (Approved)
- Workspace: `C:/Users/Nirmaan2/AppData/Local/Temp/opencode/stickman-escape/` (avoid C:\Windows\System32).
- Fresh git init in workspace, no clone/archive (user renamed old repo).
- Files:
  - `README.md` — centered wrapper, EMERGENCY BROADCAST header, single img, caption.
  - `assets/escape.svg` — 800x400 viewBox, transparent bg, all acts in one SMIL timeline.
- README shape:
```markdown
<div align="center">

# 🚨 EMERGENCY BROADCAST 🚨

<img src="./assets/escape.svg" width="600" alt="Stickman tries to escape the README">
### *Don't look at him, he's trying to escape.*

</div>
```
- Plus HTML comment noting loop, alt/title for a11y.

## 3. Components — 5 Acts, 24s Loop (Approved with knock-then-break)
- Canvas 800x400, stickman stroke #111 thick (visible both modes), accents: yellow banana, red mallet + self-destruct button, blue leak water, gray spinner.
- Act1 0-4s Curtain up: walk in from left (animateTransform translate), slip on banana peel (rotate fall), bump README margin border.
- Act2 4-8s Realization + Knock: freeze, dot-eyes scale up, head turns to viewer, walks to front glass, two knocks (circle ripple opacity anim + bonk stars), confused shrug.
- Act3 8-14s Attempt / Break: pulls giant mallet (scale in), wind-up, SMASH bottom border + front glass, crack polyline draws (stroke-dashoffset anim), shards wobble.
- Act4 14-19s Consequence: water drips/leak from top (rects falling, opacity), panic run, finger-plug (pause), then curiosity → hits red self-destruct button.
- Act5 19-24s Reset: alarm flash, sucked into loading spinner (scale down + rotate into center), 0.5s black, spit back to Act1 start pose — dur indefinite repeat.
- All timing via SMIL `begin="Xs"` offsets on master 24s loop, `repeatCount="indefinite"`.

## 4. Data Flow & README Embed (Author's choice — approved to decide)
- Self-contained SVG: no `<script>`, no `<foreignObject>`, no `xlink:href` externals.
- Master loop implicit via all anims `dur="24s" repeatCount="indefinite"` with begin offsets; no build step.
- README static: div center → img loads SVG → SMIL autoplays Acts1-5 → seamless restart.
- Alt text describes gag for a11y, title mirrors it.

## 5. Fallbacks, Verification & Go-Live (Author's choice — approved to decide)
- Dark/light: transparent bg, thick dark strokes with white halo (paint-order stroke) so visible both modes; avoid pure-white fills that vanish in light mode.
- Size: target <100KB (aim <50KB), no raster embeds.
- Tests:
  1. Open `assets/escape.svg` directly in Chrome/Edge — confirm 24s loop, no console errors.
  2. Preview README (600px width, mobile 375px) — no overflow, caption visible.
  3. Grep README for banned tokens: skill, stack, repo stats, badges, `shields.io`, `github-readme-stats`.
  4. Check file size via `wc -c`.
- Go-live: `git init`, commit README+assets, add remote `https://github.com/Mounesh-13/Mounesh-13.git`, push to `main` when user supplies auth. Rollback = revert commit.
- No-resume audit before push.

## 6. Out of Scope
- GIF export, CSS/JS interactivity, multi-file strip, old asset migration, profile stats, contribution snakes.
