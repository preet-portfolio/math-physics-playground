# Spiral Art Generator

A Python/pygame recreation of David Panik's CodePen
[Spiral Art Generator](https://codepen.io/davidpanik/pen/myMrLx) — rebuilt as
real rotational kinematics instead of a straight visual port (CodePen blocked
fetching the original source, so this is a from-scratch, math-first take on
the same idea).

## Run it

From the repo root (`Fun_Python_CS/`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spiral_art_generator.main
```

`requirements.txt` installs `pygame-ce` (a drop-in, community-maintained
build of pygame) since plain `pygame` 2.6.1 has no prebuilt wheel for newer
Python versions yet.

## Controls

- Drag the sliders: **Lines (N)**, **Width**, **Speed (ω)**, **Rotation (Δφ)**
- `R` — reset all sliders to defaults
- `Esc` / close the window — quit

## The math

The pattern is `N` straight chords through a fixed center point. Each line's
angle is:

```
theta_i(t) = theta0(t) + i * delta_phi        for i = 0 .. N-1
theta0(t)  = theta0(t - dt) + omega * dt       (uniform circular motion)
```

- **ω (omega / "Speed")** is the angular velocity the whole pattern spins at,
  in radians/second. Integrating it each frame (`theta0 += omega * dt`) is
  literally simulating uniform circular motion — negative values spin the
  pattern the other way.
- **Δφ (delta-phi / "Rotation")** is the fixed angular offset between one
  line and the next. At `delta_phi = 360°/N` the lines are evenly spaced into
  a perfectly symmetric radial star. Detune it away from that value and the
  symmetry breaks — combined with the fading trail, the rotating pattern
  traces out drifting spiral and moiré shapes. This is the toy's "aha" — try
  nudging Rotation just a few degrees off `360/N` while it's spinning.
- **The trail** isn't a physics quantity, just a rendering trick: instead of
  clearing the screen every frame, a near-transparent black rectangle is
  blitted over it first. Each old frame's brightness decays by a constant
  fraction every tick — an exponential decay, the same shape as an RC-circuit
  discharge — which is what turns a spinning line pattern into a persistent
  spiral trace.
- The live HUD shows `ω`, `Δφ`, and the current `theta0(t) mod 360°` so the
  equations driving the picture are always visible, not hidden behind slider
  labels.

## Files

- `spiral.py` — all the math: `SpiralField` integrates `theta0` and computes
  each line's angle/endpoints. No pygame drawing logic beyond drawing the
  lines themselves.
- `main.py` — wiring: window/event loop, slider → field parameter updates,
  trail compositing, HUD.
- `../common/ui.py` — generic, spiral-agnostic widgets (`Slider`, `draw_hud`)
  shared with other projects in this repo (e.g. `equation_gallery/`).
