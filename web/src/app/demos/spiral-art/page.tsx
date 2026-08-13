'use client';

import { useState, useRef } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720, HEIGHT = 560;

export default function SpiralArtDemo() {
  const [numLines, setNumLines] = useState(12);
  const [lineWidth, setLineWidth] = useState(2);
  const [speed, setSpeed] = useState(1.0);
  const [rotationDeg, setRotationDeg] = useState(30);
  const theta0Ref = useRef(0);

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    theta0Ref.current += speed * dt;
    const theta0 = theta0Ref.current;
    const deltaPhi = (rotationDeg * Math.PI) / 180;
    const N = Math.round(numLines);
    const R = Math.max(width, height);
    const cx = width / 2;
    const cy = height / 2;

    // Low-alpha refill instead of clearRect -- fades old chords into a trail.
    ctx.fillStyle = 'rgba(27,43,34,0.08)';
    ctx.fillRect(0, 0, width, height);

    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = COLORS.chalkGold;
    for (let i = 0; i < N; i++) {
      const theta = theta0 + i * deltaPhi;
      const dx = R * Math.cos(theta);
      const dy = R * Math.sin(theta);
      ctx.beginPath();
      ctx.moveTo(cx - dx, cy - dy);
      ctx.lineTo(cx + dx, cy + dy);
      ctx.stroke();
    }
  }, WIDTH, HEIGHT);

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Spiral Art Generator</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        theta_i(t) = theta0(t) + i * delta_phi -- N rotating chords through a center point.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="lines (N)" value={numLines} min={2} max={60} step={1} onChange={setNumLines} format={(v) => `${Math.round(v)}`} />
            <Slider label="line width" value={lineWidth} min={1} max={10} step={1} onChange={setLineWidth} format={(v) => `${Math.round(v)}`} />
            <Slider label="speed (omega)" value={speed} min={-5} max={5} step={0.1} onChange={setSpeed} format={(v) => v.toFixed(1)} />
            <Slider label="rotation (delta_phi, deg)" value={rotationDeg} min={0} max={180} step={1} onChange={setRotationDeg} format={(v) => `${v.toFixed(0)}°`} />
          </Panel>
          <Panel>
            <Hud
              lines={[
                `N = ${Math.round(numLines)}`,
                `delta_phi = ${rotationDeg.toFixed(0)} deg`,
                `omega = ${speed.toFixed(2)} rad/s`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
