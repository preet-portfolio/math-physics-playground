'use client';

import { useRef, useState } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;

const DEFAULT_ANGLE = 45;
const DEFAULT_V0 = 30;
const DEFAULT_G = 9.81;
const DEFAULT_DRAG = 0;

type ProjectileState = {
  t: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  landed: boolean;
  trajectory: { x: number; y: number }[];
  landedX: number | null;
};

export default function ProjectileMotionDemo() {
  const [angle, setAngle] = useState(DEFAULT_ANGLE);
  const [v0, setV0] = useState(DEFAULT_V0);
  const [g, setG] = useState(DEFAULT_G);
  const [drag, setDrag] = useState(DEFAULT_DRAG);

  // Initial value replicates what launch() would produce for the default
  // angle/v0, so no mount-only effect is needed just to kick off the first
  // flight (calling setState synchronously inside an effect body is flagged
  // by react-hooks/set-state-in-effect). useRef's initial argument is cheap
  // to recompute on every render (a plain object literal) and is only ever
  // used on the first one, so no memoization is needed here.
  const defaultAngleRad = (DEFAULT_ANGLE * Math.PI) / 180;
  const stateRef = useRef<ProjectileState>({
    t: 0, x: 0, y: 0,
    vx: DEFAULT_V0 * Math.cos(defaultAngleRad),
    vy: DEFAULT_V0 * Math.sin(defaultAngleRad),
    landed: false, trajectory: [{ x: 0, y: 0 }], landedX: null,
  });
  const [display, setDisplay] = useState<{ t: number; landed: boolean; landedX: number | null }>({
    t: 0, landed: false, landedX: null,
  });

  // Re-launches using whatever angle/v0 are currently set to -- called from
  // the Relaunch button's onClick, not on mount (initial state is set above).
  const launch = () => {
    const angleRad = (angle * Math.PI) / 180;
    const vx = v0 * Math.cos(angleRad);
    const vy = v0 * Math.sin(angleRad);
    stateRef.current = { t: 0, x: 0, y: 0, vx, vy, landed: false, trajectory: [{ x: 0, y: 0 }], landedX: null };
    setDisplay({ t: 0, landed: false, landedX: null });
  };

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    const state = stateRef.current;

    if (!state.landed) {
      if (drag === 0) {
        state.t += dt;
        state.x = state.vx * state.t;
        state.y = state.vy * state.t - 0.5 * g * state.t * state.t;
      } else {
        const substeps = 8;
        const dtSub = dt / substeps;
        for (let i = 0; i < substeps; i++) {
          const speed = Math.sqrt(state.vx * state.vx + state.vy * state.vy);
          const ax = -drag * speed * state.vx;
          const ay = -g - drag * speed * state.vy;
          state.vx += ax * dtSub;
          state.vy += ay * dtSub;
          state.x += state.vx * dtSub;
          state.y += state.vy * dtSub;
        }
        state.t += dt;
      }
      state.trajectory.push({ x: state.x, y: state.y });

      if (state.y < 0 && state.t > 0.01) {
        state.y = 0;
        state.landed = true;
        state.landedX = state.x;
      }

      setDisplay({ t: state.t, landed: state.landed, landedX: state.landedX });
    }

    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    const origin = { x: width * 0.08, y: height * 0.85 };
    const pxPerMeter = 2;

    // ground
    ctx.strokeStyle = COLORS.wood;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, origin.y);
    ctx.lineTo(width, origin.y);
    ctx.stroke();

    // full trajectory, not faded
    ctx.strokeStyle = COLORS.chalkBlue;
    ctx.lineWidth = 2;
    ctx.beginPath();
    state.trajectory.forEach((p, i) => {
      const sx = origin.x + p.x * pxPerMeter;
      const sy = origin.y - p.y * pxPerMeter;
      if (i === 0) ctx.moveTo(sx, sy);
      else ctx.lineTo(sx, sy);
    });
    ctx.stroke();

    // current / final position
    const cur = state.trajectory[state.trajectory.length - 1];
    const curX = origin.x + cur.x * pxPerMeter;
    const curY = origin.y - cur.y * pxPerMeter;
    ctx.fillStyle = COLORS.chalkGold;
    ctx.beginPath();
    ctx.arc(curX, curY, 6, 0, Math.PI * 2);
    ctx.fill();

    if (state.landed && state.landedX !== null) {
      const lx = origin.x + state.landedX * pxPerMeter;
      const ly = origin.y;
      ctx.strokeStyle = COLORS.chalkCoral;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(lx - 7, ly - 7);
      ctx.lineTo(lx + 7, ly + 7);
      ctx.moveTo(lx + 7, ly - 7);
      ctx.lineTo(lx - 7, ly + 7);
      ctx.stroke();
    }
  }, WIDTH, HEIGHT);

  const angleRad = (angle * Math.PI) / 180;
  const Ranalytic = (v0 * v0 * Math.sin(2 * angleRad)) / g;

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Projectile Motion</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        x = v0 cos(th) t, y = v0 sin(th) t - 0.5 g t^2 -- kinematics, with optional quadratic drag.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="Launch angle (deg)" value={angle} min={5} max={85} step={1} onChange={setAngle} format={(v) => v.toFixed(0)} />
            <Slider label="Launch speed v0 (m/s)" value={v0} min={5} max={60} step={0.1} onChange={setV0} format={(v) => v.toFixed(1)} />
            <Slider label="Gravity g (m/s^2)" value={g} min={2} max={20} step={0.01} onChange={setG} format={(v) => v.toFixed(2)} />
            <Slider label="Drag coefficient" value={drag} min={0} max={0.05} step={0.001} onChange={setDrag} format={(v) => v.toFixed(3)} />
            <button
              onClick={launch}
              className="w-full rounded-md border border-[#5C4630]/60 bg-[#1B2B22] px-3 py-1.5 text-sm text-[#EDEAE0] transition-colors hover:bg-[#1B2B22]/70"
            >
              Relaunch
            </button>
          </Panel>
          <Panel>
            <Hud
              lines={[
                `R_analytic (no drag) = v0^2*sin(2*angle)/g = ${Ranalytic.toFixed(2)} m`,
                display.landed && display.landedX !== null
                  ? `R_actual (landed) = ${display.landedX.toFixed(2)} m`
                  : `R_actual: (in flight...)`,
                `t = ${display.t.toFixed(2)} s   drag = ${drag.toFixed(3)}`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
