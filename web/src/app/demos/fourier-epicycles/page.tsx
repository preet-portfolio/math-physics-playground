'use client';

import { useState, useRef } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;
const SCALE = 80;
const HISTORY_MAX = 300;
const ANCHOR_X = WIDTH * 0.28;
const ANCHOR_Y = HEIGHT * 0.5;

const DEFAULT_N = 5;
const DEFAULT_SPEED = 0.5;

export default function FourierEpicyclesDemo() {
  const [n, setN] = useState(DEFAULT_N);
  const [speed, setSpeed] = useState(DEFAULT_SPEED);
  const [thetaDisplay, setThetaDisplay] = useState(0);

  const thetaRef = useRef(0);
  const historyRef = useRef<number[]>([]);

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    thetaRef.current += speed * dt;
    const thetaBase = thetaRef.current;
    setThetaDisplay(thetaBase % (2 * Math.PI));

    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    let x = ANCHOR_X;
    let y = ANCHOR_Y;
    for (let k = 1; k <= 2 * n - 1; k += 2) {
      const amplitude = (4 / (Math.PI * k)) * SCALE;
      const angle = k * thetaBase;
      const nx = x + amplitude * Math.cos(angle);
      const ny = y + amplitude * Math.sin(angle);

      ctx.strokeStyle = COLORS.wood;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(x, y, amplitude, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = COLORS.chalkBlue;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(nx, ny);
      ctx.stroke();

      x = nx;
      y = ny;
    }

    ctx.fillStyle = COLORS.chalkGold;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();

    const hist = historyRef.current;
    hist.push(y - ANCHOR_Y);
    if (hist.length > HISTORY_MAX) hist.shift();

    const plotXStart = x;
    const plotXEnd = width * 0.95;
    const plotWidth = plotXEnd - plotXStart;

    ctx.strokeStyle = COLORS.chalkGold;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < hist.length; i++) {
      const px = plotXStart + (plotWidth * i) / HISTORY_MAX;
      const py = ANCHOR_Y + hist[hist.length - 1 - i];
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
  }, WIDTH, HEIGHT);

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Fourier Epicycles</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        f(t) = (4/&pi;) &sum;<sub>k odd</sub> sin(k&omega;t)/k — a square wave built from rotating circles.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider
              label="harmonics (N)"
              value={n}
              min={1}
              max={15}
              step={1}
              onChange={(v) => setN(Math.round(v))}
              format={(v) => v.toFixed(0)}
            />
            <Slider
              label="speed"
              value={speed}
              min={0.1}
              max={3}
              step={0.1}
              onChange={setSpeed}
              format={(v) => v.toFixed(2)}
            />
          </Panel>
          <Panel>
            <Hud
              lines={[
                `N = ${n} harmonics`,
                `speed = ${speed.toFixed(2)}`,
                `theta = ${thetaDisplay.toFixed(2)}`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
