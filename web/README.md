# Math & Physics Playground — Web

A browser port of `spiral_art_generator/` and `equation_gallery/`: the exact
same verified equations and integration methods, reimplemented in
TypeScript + HTML5 Canvas instead of Python/pygame, so they run in a browser
with nothing to install.

## Run it

```bash
npm install
npm run dev
```

Then open `http://localhost:3000`.

## The demos

11 total — the same set as the desktop apps:

- **Art**: Spiral Art Generator
- **Math**: Mandelbrot Set, Fourier Epicycles, Euler's Identity, Golden
  Ratio Spiral, Lissajous Curves
- **Physics**: Double Pendulum (RK4), Orbital Mechanics (symplectic Euler),
  Simple Pendulum, Spring-Mass Oscillator, Projectile Motion

Each route (`src/app/demos/<slug>/page.tsx`) is a self-contained component
owning its own sliders and its own numerical integration — same "no shared
physics engine" philosophy as `equation_gallery/scenes/*.py`.

## Files

- `src/hooks/useCanvasLoop.ts` — the web equivalent of `common/scene.py`'s
  `Scene` contract: a canvas ref + a `requestAnimationFrame` loop, handling
  devicePixelRatio scaling.
- `src/components/Slider.tsx`, `Panel.tsx` — the web equivalent of
  `common/ui.py`'s `Slider`/`draw_hud`.
- `src/lib/theme.ts` — the same Chalkboard Lecture Hall palette as
  `common/theme.py`, so the web and desktop versions read as one visual
  identity.
- `src/lib/demos.ts` — the demo list driving the nav and landing page.

## Stack

Next.js (App Router, TypeScript) + Tailwind CSS + HTML5 Canvas 2D. No
animation library, no game engine — every demo is a plain
`requestAnimationFrame` loop drawing directly to a `<canvas>`.
