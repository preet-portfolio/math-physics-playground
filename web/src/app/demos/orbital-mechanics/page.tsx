'use client';

import { useEffect, useRef, useState } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;

const GM = 4_500_000; // fixed, not slider-controlled
const R0 = 200; // initial orbital radius (px; 1 unit = 1 px)
const V_CIRCULAR = Math.sqrt(GM / R0); // ~150.0
const V_ESCAPE = Math.sqrt((2 * GM) / R0); // ~212.1

const SUBSTEPS = 4;
const TRAIL_MAXLEN = 5000;
const EPSILON_BAND = 1.0;

type State = { x: number; y: number; vx: number; vy: number };

export default function OrbitalMechanicsDemo() {
  const [v0, setV0] = useState(V_CIRCULAR);

  const stateRef = useRef<State>({ x: R0, y: 0, vx: 0, vy: -V_CIRCULAR });
  const trailRef = useRef<{ x: number; y: number }[]>([{ x: R0, y: 0 }]);
  const [display, setDisplay] = useState({ speed: V_CIRCULAR, r: R0, epsilon: 0 });

  const reset = () => {
    stateRef.current = { x: R0, y: 0, vx: 0, vy: -v0 };
    trailRef.current = [{ x: R0, y: 0 }];
  };

  useEffect(() => {
    reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    const state = stateRef.current;
    const dtSub = dt / SUBSTEPS;
    for (let i = 0; i < SUBSTEPS; i++) {
      const r = Math.hypot(state.x, state.y);
      const ax = (-GM * state.x) / (r * r * r);
      const ay = (-GM * state.y) / (r * r * r);
      // Symplectic (semi-implicit) Euler: velocity from the *current* position
      // first, then position from the *new* velocity -- order matters.
      state.vx += ax * dtSub;
      state.vy += ay * dtSub;
      state.x += state.vx * dtSub;
      state.y += state.vy * dtSub;
    }
    const trail = trailRef.current;
    trail.push({ x: state.x, y: state.y });
    if (trail.length > TRAIL_MAXLEN) trail.shift();

    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    const center = { x: width * 0.55, y: height * 0.5 };

    ctx.fillStyle = COLORS.chalkGold;
    ctx.beginPath();
    ctx.arc(center.x, center.y, 14, 0, Math.PI * 2);
    ctx.fill();

    if (trail.length >= 2) {
      ctx.strokeStyle = COLORS.chalkBlue;
      ctx.lineWidth = 1;
      ctx.beginPath();
      trail.forEach((p, i) => {
        const sx = center.x + p.x;
        const sy = center.y + p.y;
        if (i === 0) ctx.moveTo(sx, sy);
        else ctx.lineTo(sx, sy);
      });
      ctx.stroke();
    }

    ctx.fillStyle = COLORS.chalk;
    ctx.beginPath();
    ctx.arc(center.x + state.x, center.y + state.y, 8, 0, Math.PI * 2);
    ctx.fill();

    const r = Math.hypot(state.x, state.y);
    const speed = Math.hypot(state.vx, state.vy);
    const epsilon = 0.5 * speed * speed - GM / r;
    setDisplay({ speed, r, epsilon });
  }, WIDTH, HEIGHT);

  const classification =
    display.epsilon < -EPSILON_BAND
      ? 'elliptical/circular orbit'
      : display.epsilon <= EPSILON_BAND
        ? 'parabolic (near escape threshold)'
        : 'hyperbolic (escaping)';

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Orbital Mechanics</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        a = -GM * r_hat / r&sup2; -- real inverse-square gravity, symplectic integration.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="v0 tangential speed" value={v0} min={0} max={320} step={1} onChange={setV0} format={(v) => v.toFixed(1)} />
            <button
              onClick={reset}
              className="w-full rounded-md border border-[#5C4630]/60 bg-[#1B2B22] px-3 py-1.5 text-sm text-[#EDEAE0] transition-colors hover:bg-[#1B2B22]/70"
            >
              Reset
            </button>
          </Panel>
          <Panel>
            <Hud
              lines={[
                `v_circular = sqrt(GM/r0) = ${V_CIRCULAR.toFixed(1)}`,
                `v_escape = sqrt(2GM/r0) = ${V_ESCAPE.toFixed(1)}`,
                `speed = ${display.speed.toFixed(1)}   r = ${display.r.toFixed(1)}`,
                `epsilon = ${display.epsilon.toFixed(2)}`,
                classification,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
