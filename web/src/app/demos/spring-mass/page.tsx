'use client';

import { useEffect, useRef, useState } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;

const DEFAULT_K = 10;
const DEFAULT_M = 1;
const DEFAULT_C = 0.3;
const DEFAULT_X0 = 1.5;

type SpringState = {
  x: number;
  v: number;
};

export default function SpringMassDemo() {
  const [k, setK] = useState(DEFAULT_K);
  const [m, setM] = useState(DEFAULT_M);
  const [damping, setDamping] = useState(DEFAULT_C);
  const [x0, setX0] = useState(DEFAULT_X0);

  const stateRef = useRef<SpringState>({ x: 0, v: 0 });
  const maxEnergyRef = useRef(0);

  const reset = () => {
    stateRef.current = { x: x0, v: 0 };
    maxEnergyRef.current = 0.5 * k * x0 * x0;
  };

  useEffect(() => {
    reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    const state = stateRef.current;

    const substeps = 8;
    const dtSub = dt / substeps;
    for (let i = 0; i < substeps; i++) {
      const a = -(k / m) * state.x - (damping / m) * state.v;
      state.v += a * dtSub;
      state.x += state.v * dtSub;
    }

    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    const anchor = { x: width * 0.15, y: height * 0.35 };
    const equilibriumGap = 150;
    const pxPerUnit = 120;
    const blockX = anchor.x + equilibriumGap + state.x * pxPerUnit;
    const blockY = anchor.y;

    // wall hatch
    ctx.strokeStyle = COLORS.wood;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(anchor.x, anchor.y - 30);
    ctx.lineTo(anchor.x, anchor.y + 30);
    ctx.stroke();

    // zigzag spring: 7 segments alternating +-18px vertical offset
    const springEndX = blockX - 20;
    const nSeg = 7;
    const points: { x: number; y: number }[] = [];
    for (let i = 0; i <= nSeg; i++) {
      const t = i / nSeg;
      const px = anchor.x + (springEndX - anchor.x) * t;
      const py = i === 0 || i === nSeg ? anchor.y : anchor.y + (i % 2 === 1 ? -18 : 18);
      points.push({ x: px, y: py });
    }
    ctx.strokeStyle = COLORS.chalk;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) ctx.lineTo(points[i].x, points[i].y);
    ctx.stroke();

    // block
    ctx.fillStyle = COLORS.chalkGold;
    ctx.fillRect(blockX - 20, blockY - 20, 40, 40);

    // energy bars (fixed screen position, clear of the block's oscillation range)
    const ke = 0.5 * m * state.v * state.v;
    const pe = 0.5 * k * state.x * state.x;
    const maxEnergy = maxEnergyRef.current > 1e-9 ? maxEnergyRef.current : 1e-9;
    const barMaxHeight = 160;
    const barBaseY = anchor.y + 180;
    const keBarX = width * 0.72;
    const peBarX = keBarX + 50;
    const barWidth = 24;

    const keHeight = Math.min(1, ke / maxEnergy) * barMaxHeight;
    const peHeight = Math.min(1, pe / maxEnergy) * barMaxHeight;

    ctx.fillStyle = COLORS.chalkBlue;
    ctx.fillRect(keBarX, barBaseY - keHeight, barWidth, keHeight);
    ctx.fillStyle = COLORS.chalkCoral;
    ctx.fillRect(peBarX, barBaseY - peHeight, barWidth, peHeight);

    ctx.fillStyle = COLORS.chalk;
    ctx.font = '12px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('KE', keBarX + barWidth / 2, barBaseY + 16);
    ctx.fillText('PE', peBarX + barWidth / 2, barBaseY + 16);
    ctx.textAlign = 'start';
  }, WIDTH, HEIGHT);

  const omega0 = Math.sqrt(k / m);
  const period = (2 * Math.PI) / omega0;
  const zeta = damping / (2 * Math.sqrt(m * k));
  const regime = zeta < 0.999 ? 'underdamped' : zeta > 1.001 ? 'overdamped' : 'critically damped';

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Spring-Mass Oscillator</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        m*x&apos;&apos; = -k*x - c*x&apos; -- Hooke&apos;s law with damping, live KE/PE energy bars.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="Spring constant k" value={k} min={1} max={50} step={0.1} onChange={setK} format={(v) => v.toFixed(1)} />
            <Slider label="Mass m" value={m} min={0.5} max={5} step={0.01} onChange={setM} format={(v) => v.toFixed(2)} />
            <Slider label="Damping c" value={damping} min={0} max={5} step={0.01} onChange={setDamping} format={(v) => v.toFixed(2)} />
            <Slider label="Initial displacement x0" value={x0} min={-2} max={2} step={0.01} onChange={setX0} format={(v) => v.toFixed(2)} />
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
                `omega0 = sqrt(k/m) = ${omega0.toFixed(2)} rad/s`,
                `period = 2*pi/omega0 = ${period.toFixed(2)} s`,
                `zeta = c/(2*sqrt(mk)) = ${zeta.toFixed(3)} (${regime})`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
