# Equation Gallery

A pygame app collecting 10 "greatest hits" interactive math and physics
demos — five of each, each one built on a real equation rather than just a
pretty animation. Visual theme: **Chalkboard Lecture Hall** — every demo
opens with its formula handwritten across the board.

## Run it

From the repo root (`Fun_Python_CS/`), with the shared venv active:

```bash
python -m equation_gallery.main
```

## Controls

- **Sidebar** (always visible, left side): click a row, or press `1`-`5` for
  a math demo / `6`-`9` and `0` for a physics demo, to switch instantly — no
  menu round-trip. Demo instances are cached, so switching back to one you've
  already visited resumes exactly where it was (a running double-pendulum
  trail, a Mandelbrot zoom, ...).
- **In a scene:** drag the sliders to change parameters live — the handle
  fills solid gold while held. `R` resets the current scene to its initial
  conditions.
- `Esc`, or closing the window, quits.

## The demos

### Math

1. **Mandelbrot Set** — `z = z^2 + c`, escape-time coloring, numpy-vectorized
   over the pixel grid. Sliders: max iterations, zoom. Click anywhere on the
   fractal to recenter there. Recomputes only when a parameter actually
   changes (not while a slider is mid-drag), so dragging stays smooth.
2. **Fourier Epicycles** — a square wave built from its own Fourier series,
   `f(t) = (4/pi) * sum[k odd] sin(k*omega*t)/k`, drawn as a chain of rotating
   circles whose tip traces the wave on a scrolling plot. Slider `N` sets how
   many harmonics are summed — watch the plotted wave sharpen toward a true
   square wave (with the classic Gibbs-phenomenon overshoot) as `N` grows.
3. **Euler's Identity** — a unit vector `e^(i*theta)` rotating in the complex
   plane, `theta` integrated from a speed slider exactly like the spiral
   generator's rotation. Highlights `e^(i*pi) + 1 = 0` whenever `theta`
   crosses `pi`.
4. **Golden Ratio Spiral** — the classic flush Fibonacci square tiling (fixed,
   since perfect flush tiling only works for the true Fibonacci recurrence)
   overlaid with a smooth logarithmic spiral curve whose growth-per-quarter-turn
   *is* a slider — set it to `phi = 1.618...` and it hugs the square
   construction; detune it and watch it drift away.
5. **Lissajous Curves** — `x = A*sin(a*t + delta)`, `y = B*sin(b*t)`, the
   classic oscilloscope XY figures. Sliders for the frequency ratio `a:b` and
   phase `delta`.

### Physics

6. **Double Pendulum** — the textbook chaos demo. Real Lagrangian double-
   pendulum equations of motion, integrated with RK4 (plain Euler diverges on
   this system). Two pendulums are launched a tiny slider-controlled angle
   apart and visibly diverge over time — sensitive dependence on initial
   conditions, made visible.
7. **Orbital Mechanics** — one body orbiting a fixed mass under real
   inverse-square gravity, integrated with semi-implicit (symplectic) Euler
   so orbits don't artificially drift. The velocity slider sweeps from
   sub-orbital fall-in through circular, elliptical, and hyperbolic escape;
   the HUD classifies the orbit from the sign of its specific orbital energy.
8. **Simple Pendulum** — the real nonlinear pendulum ODE,
   `theta'' = -(g/L)*sin(theta) - b*theta'` (not the small-angle
   approximation). The HUD shows the small-angle reference period next to the
   actual swing, so you can see the approximation break down at large angles.
9. **Spring-Mass Oscillator** — Hooke's law, `m*x'' = -k*x - c*x'`, with live
   kinetic/potential energy bars showing conservation (or decay, once damping
   is added) and a damping-ratio classification (under/critically/over-damped).
10. **Projectile Motion** — closed-form kinematics with an optional quadratic
    drag term that switches the scene to numerical integration. The HUD
    compares the analytic no-drag range against the actual simulated landing
    point — they match at zero drag and diverge as drag increases.

## Files

- `main.py` — the sidebar + game loop. Reaches the 1000x750 content area
  scenes are built against via a pygame subsurface (`screen.subsurface`),
  so scene code never has to know a sidebar exists; translates window-
  absolute mouse coordinates to content-local ones before forwarding events
  to the active scene.
- `scenes/` — one file per demo, each a `common.scene.Scene` subclass owning
  its own sliders and its own numerical integration (no shared "physics
  engine" — the equations are all different shapes).
- `../common/scene.py` — the `Scene` contract (`reset`/`handle_event`/
  `update`/`draw`) every demo implements, plus `draw_panel_backing()`
  (shared translucent panel behind each scene's sliders).
- `../common/ui.py` — the shared `Slider` and `draw_hud` widgets, also used
  by `spiral_art_generator`.
- `../common/theme.py` — the Chalkboard Lecture Hall palette, fonts
  (Chalkduster for the big formula headline, Chalkboard SE for everything
  else, both real macOS system fonts), and the chalk-dust texture.
