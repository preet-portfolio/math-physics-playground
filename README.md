# Fun Python: Physics & Math Playground

Small, real-time, interactive toys — each one built on an actual equation
(real rotational kinematics, real Lagrangian mechanics, real inverse-square
gravity), not just a decorative animation. Started as Python/pygame desktop
apps; `web/` is a browser port of the same verified math, playable without
installing anything.

## Projects

- **[spiral_art_generator/](spiral_art_generator/)** (Python/pygame) — a
  recreation of David Panik's CodePen
  [Spiral Art Generator](https://codepen.io/davidpanik/pen/myMrLx): rotating
  chords through a center point, uniform circular motion + phase offsets,
  fading trails turn rotation into spiral/moiré patterns.
- **[equation_gallery/](equation_gallery/)** (Python/pygame) — a sidebar
  gallery of 10 "greatest hits" interactive demos, 5 math + 5 physics:
  Mandelbrot set, Fourier epicycles, Euler's identity, the golden ratio
  spiral, Lissajous curves, the double pendulum (chaos), orbital mechanics,
  the simple pendulum, a spring-mass oscillator, and projectile motion.
  Chalkboard Lecture Hall visual theme — every demo opens with its formula
  handwritten across the board.
- **[web/](web/)** (Next.js + TypeScript + Canvas) — a browser port of all
  11 demos above (the 10-demo gallery + the spiral generator), reimplementing
  the exact same verified equations/integration methods for the web.
  **Live: [web-indol-delta-80.vercel.app](https://web-indol-delta-80.vercel.app)**

## Setup

**Python projects** (`spiral_art_generator/`, `equation_gallery/`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` installs `pygame-ce` (a drop-in `import pygame` build with
prebuilt wheels for newer Python versions) and `numpy` (used by the
Mandelbrot renderer).

**Web project** (`web/`):

```bash
cd web && npm install
```

## Running a project

```bash
python -m spiral_art_generator.main       # desktop, pygame window
python -m equation_gallery.main           # desktop, pygame window
cd web && npm run dev                     # browser, http://localhost:3000
```

## Repo layout

- `common/` — Python code shared across the pygame projects: `ui.py`
  (draggable `Slider`, `draw_hud`), `scene.py` (the `Scene` contract used by
  `equation_gallery`), and `theme.py` (the Chalkboard Lecture Hall
  palette/fonts/texture).
- `web/` — the browser port; `src/lib/theme.ts` mirrors the same Chalkboard
  palette so it reads as the same visual identity across desktop and web.
- One folder per project, each with its own `README.md` explaining its
  controls and the math behind it.
