'use client';

import { useRef, useState } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;

const DEFAULT_L = 1.5;
const DEFAULT_G = 9.81;
const DEFAULT_DAMPING = 0.1;
const DEFAULT_THETA0 = 60;

type PendulumState = {
  theta: number;
  omega: number;
};

export default function SimplePendulumDemo() {
  const [length, setLength] = useState(DEFAULT_L);
  const [g, setG] = useState(DEFAULT_G);
  const [damping, setDamping] = useState(DEFAULT_DAMPING);
  const [theta0, setTheta0] = useState(DEFAULT_THETA0);

  // Lazy initializers run once, so no mount-only effect is needed just to
  // set the initial simulation state (calling setState synchronously inside
  // an effect body is flagged by react-hooks/set-state-in-effect).
  const stateRef = useRef<PendulumState>({ theta: (DEFAULT_THETA0 * Math.PI) / 180, omega: 0 });
  const [display, setDisplay] = useState<PendulumState>(() => ({
    theta: (DEFAULT_THETA0 * Math.PI) / 180,
    omega: 0,
  }));

  // Re-launches from whatever theta0 is currently set to -- called from the
  // Reset button's onClick, not on mount (initial state is set above).
  const reset = () => {
    const theta = (theta0 * Math.PI) / 180;
    stateRef.current = { theta, omega: 0 };
    setDisplay({ theta, omega: 0 });
  };

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    const state = stateRef.current;

    const substeps = 8;
    const dtSub = dt / substeps;
    for (let i = 0; i < substeps; i++) {
      const alpha = -(g / length) * Math.sin(state.theta) - damping * state.omega;
      state.omega += alpha * dtSub;
      state.theta += state.omega * dtSub;
    }

    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    const pivot = { x: width * 0.5, y: height * 0.2 };
    const rodLenPx = length * 150;
    const bob = {
      x: pivot.x + rodLenPx * Math.sin(state.theta),
      y: pivot.y + rodLenPx * Math.cos(state.theta),
    };

    ctx.strokeStyle = COLORS.chalk;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pivot.x, pivot.y);
    ctx.lineTo(bob.x, bob.y);
    ctx.stroke();

    ctx.fillStyle = COLORS.chalkGold;
    ctx.beginPath();
    ctx.arc(bob.x, bob.y, 14, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = COLORS.wood;
    ctx.beginPath();
    ctx.arc(pivot.x, pivot.y, 4, 0, Math.PI * 2);
    ctx.fill();

    setDisplay({ theta: state.theta, omega: state.omega });
  }, WIDTH, HEIGHT);

  const Tsmall = 2 * Math.PI * Math.sqrt(length / g);
  const thetaDeg = (display.theta * 180) / Math.PI;

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Simple Pendulum</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        theta&apos;&apos; = -(g/L) sin(theta) - b*theta&apos; -- the real nonlinear pendulum, not the
        small-angle approximation.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="Length L (m)" value={length} min={0.5} max={3} step={0.01} onChange={setLength} format={(v) => v.toFixed(2)} />
            <Slider label="Gravity g (m/s^2)" value={g} min={2} max={20} step={0.01} onChange={setG} format={(v) => v.toFixed(2)} />
            <Slider label="Damping b" value={damping} min={0} max={2} step={0.01} onChange={setDamping} format={(v) => v.toFixed(2)} />
            <Slider label="Initial angle theta0 (deg)" value={theta0} min={10} max={170} step={1} onChange={setTheta0} format={(v) => v.toFixed(0)} />
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
                `T_small = 2*pi*sqrt(L/g) = ${Tsmall.toFixed(2)} s (small-angle approx)`,
                `theta = ${thetaDeg.toFixed(1)} deg`,
                `omega = ${display.omega.toFixed(2)} rad/s`,
                `at large theta0 the real period exceeds T_small`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
