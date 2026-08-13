'use client';

import { useRef, useState } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;

// Fixed (non-slider) physical parameters -- abstract units, scaled to pixels separately.
const M1 = 1.0;
const M2 = 1.0;
const L1 = 1.2;
const L2 = 1.2;
const PX_PER_LENGTH = 150;

const DEFAULT_G = 9.81;
const DEFAULT_DELTA_THETA0 = 0.01;
const DEFAULT_TIME_SCALE = 0.4;

const SUBSTEPS = 6;
const THETA1_0 = (120 * Math.PI) / 180;
const THETA2_0 = (-10 * Math.PI) / 180;

const COLOR_A = COLORS.chalkBlue;
const COLOR_B = COLORS.chalkCoral;

type State = [number, number, number, number]; // theta1, theta2, omega1, omega2

function derivatives(state: State, g: number): State {
  const [theta1, theta2, omega1, omega2] = state;
  const delta = theta1 - theta2;

  const denom = L1 * (2 * M1 + M2 - M2 * Math.cos(2 * theta1 - 2 * theta2));
  const theta1dd =
    (-g * (2 * M1 + M2) * Math.sin(theta1) -
      M2 * g * Math.sin(theta1 - 2 * theta2) -
      2 * Math.sin(delta) * M2 * (omega2 * omega2 * L2 + omega1 * omega1 * L1 * Math.cos(delta))) /
    denom;

  const denom2 = L2 * (2 * M1 + M2 - M2 * Math.cos(2 * theta1 - 2 * theta2));
  const theta2dd =
    (2 *
      Math.sin(delta) *
      (omega1 * omega1 * L1 * (M1 + M2) +
        g * (M1 + M2) * Math.cos(theta1) +
        omega2 * omega2 * L2 * M2 * Math.cos(delta))) /
    denom2;

  return [omega1, omega2, theta1dd, theta2dd];
}

function addScaled(state: State, deriv: State, factor: number): State {
  return [
    state[0] + deriv[0] * factor,
    state[1] + deriv[1] * factor,
    state[2] + deriv[2] * factor,
    state[3] + deriv[3] * factor,
  ];
}

function rk4Step(state: State, g: number, dt: number): State {
  const k1 = derivatives(state, g);
  const k2 = derivatives(addScaled(state, k1, dt / 2), g);
  const k3 = derivatives(addScaled(state, k2, dt / 2), g);
  const k4 = derivatives(addScaled(state, k3, dt), g);
  return [
    state[0] + (dt / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
    state[1] + (dt / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
    state[2] + (dt / 6) * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]),
    state[3] + (dt / 6) * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3]),
  ];
}

function bobPositions(state: State, pivot: { x: number; y: number }) {
  const [theta1, theta2] = state;
  const l1px = L1 * PX_PER_LENGTH;
  const l2px = L2 * PX_PER_LENGTH;
  const bob1 = { x: pivot.x + l1px * Math.sin(theta1), y: pivot.y + l1px * Math.cos(theta1) };
  const bob2 = { x: bob1.x + l2px * Math.sin(theta2), y: bob1.y + l2px * Math.cos(theta2) };
  return { bob1, bob2 };
}

export default function DoublePendulumDemo() {
  const [g, setG] = useState(DEFAULT_G);
  const [deltaTheta0, setDeltaTheta0] = useState(DEFAULT_DELTA_THETA0);
  const [timeScale, setTimeScale] = useState(DEFAULT_TIME_SCALE);

  const stateARef = useRef<State>([THETA1_0, THETA2_0, 0, 0]);
  const stateBRef = useRef<State>([THETA1_0 + DEFAULT_DELTA_THETA0, THETA2_0, 0, 0]);
  const simTimeRef = useRef(0);
  const prevBob2ARef = useRef<{ x: number; y: number } | null>(null);
  const prevBob2BRef = useRef<{ x: number; y: number } | null>(null);
  const [simTimeDisplay, setSimTimeDisplay] = useState(0);

  // Initial refs above already match what reset() computes at mount time
  // (deltaTheta0 starts at DEFAULT_DELTA_THETA0), so no mount-only effect is
  // needed just to initialize state (calling setState synchronously inside
  // an effect body is flagged by react-hooks/set-state-in-effect). reset()
  // is only called from the Reset button's onClick from here on.
  const reset = () => {
    stateARef.current = [THETA1_0, THETA2_0, 0, 0];
    stateBRef.current = [THETA1_0 + deltaTheta0, THETA2_0, 0, 0];
    simTimeRef.current = 0;
    prevBob2ARef.current = null;
    prevBob2BRef.current = null;
    setSimTimeDisplay(0);
  };

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    const dtSub = (dt * timeScale) / SUBSTEPS;
    for (let i = 0; i < SUBSTEPS; i++) {
      stateARef.current = rk4Step(stateARef.current, g, dtSub);
      stateBRef.current = rk4Step(stateBRef.current, g, dtSub);
    }
    simTimeRef.current += dt * timeScale;

    // fade the trail toward transparent instead of a hard clear
    ctx.fillStyle = 'rgba(27,43,34,0.06)';
    ctx.fillRect(0, 0, width, height);

    const pivot = { x: width * 0.5, y: height * 0.22 };
    const { bob1: bob1A, bob2: bob2A } = bobPositions(stateARef.current, pivot);
    const { bob1: bob1B, bob2: bob2B } = bobPositions(stateBRef.current, pivot);

    if (prevBob2ARef.current) {
      ctx.strokeStyle = COLOR_A;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(prevBob2ARef.current.x, prevBob2ARef.current.y);
      ctx.lineTo(bob2A.x, bob2A.y);
      ctx.stroke();
    }
    if (prevBob2BRef.current) {
      ctx.strokeStyle = COLOR_B;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(prevBob2BRef.current.x, prevBob2BRef.current.y);
      ctx.lineTo(bob2B.x, bob2B.y);
      ctx.stroke();
    }
    prevBob2ARef.current = bob2A;
    prevBob2BRef.current = bob2B;

    for (const [bob1, bob2, color] of [
      [bob1A, bob2A, COLOR_A],
      [bob1B, bob2B, COLOR_B],
    ] as const) {
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(pivot.x, pivot.y);
      ctx.lineTo(bob1.x, bob1.y);
      ctx.lineTo(bob2.x, bob2.y);
      ctx.stroke();
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(bob1.x, bob1.y, 7, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(bob2.x, bob2.y, 10, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = COLORS.wood;
    ctx.beginPath();
    ctx.arc(pivot.x, pivot.y, 4, 0, Math.PI * 2);
    ctx.fill();

    setSimTimeDisplay(simTimeRef.current);
  }, WIDTH, HEIGHT);

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Double Pendulum</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        The classic chaos demo: two nearly-identical pendulums, integrated with RK4, visibly diverge.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="Gravity g" value={g} min={2} max={20} step={0.01} onChange={setG} format={(v) => v.toFixed(2)} />
            <Slider
              label="delta_theta0 (rad)"
              value={deltaTheta0}
              min={0.0001}
              max={0.1}
              step={0.0001}
              onChange={setDeltaTheta0}
              format={(v) => v.toFixed(4)}
            />
            <Slider label="Time scale" value={timeScale} min={0.1} max={1.0} step={0.01} onChange={setTimeScale} format={(v) => v.toFixed(2)} />
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
                `delta_theta0 = ${deltaTheta0.toFixed(4)} rad (${((deltaTheta0 * 180) / Math.PI).toFixed(3)} deg)`,
                `t_sim = ${simTimeDisplay.toFixed(2)} s`,
                'watch the paths diverge -- this is chaos',
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
