# Fun Python: Physics & Math Playground

Small, real-time, interactive Python toys — each one built on an actual
equation (real rotational kinematics, real Lagrangian mechanics, real
inverse-square gravity), not just a decorative animation. Pygame + sliders +
a live HUD showing the math driving what's on screen.

## Projects

- **[spiral_art_generator/](spiral_art_generator/)** — a recreation of David
  Panik's CodePen [Spiral Art Generator](https://codepen.io/davidpanik/pen/myMrLx):
  rotating chords through a center point, uniform circular motion + phase
  offsets, fading trails turn rotation into spiral/moiré patterns.
- **[equation_gallery/](equation_gallery/)** — a menu of 10 "greatest hits"
  interactive demos, 5 math + 5 physics: Mandelbrot set, Fourier epicycles,
  Euler's identity, the golden ratio spiral, Lissajous curves, the double
  pendulum (chaos), orbital mechanics, the simple pendulum, a spring-mass
  oscillator, and projectile motion.

## Setup (shared across all projects)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` installs `pygame-ce` (a drop-in `import pygame` build with
prebuilt wheels for newer Python versions) and `numpy` (used by the
Mandelbrot renderer).

## Running a project

Every project is a package run as a module from this directory:

```bash
python -m spiral_art_generator.main
python -m equation_gallery.main
```

## Repo layout

- `common/` — code shared across projects: `ui.py` (draggable `Slider`,
  `draw_hud`) and `scene.py` (the `Scene` contract used by `equation_gallery`).
- One folder per project, each with its own `README.md` explaining its
  controls and the math behind it.
