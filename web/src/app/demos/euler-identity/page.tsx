'use client';

import { useState, useRef } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720, HEIGHT = 560;
const TWO_PI = Math.PI * 2;

export default function EulerIdentityDemo() {
  const [speed, setSpeed] = useState(1.0);
  const thetaRef = useRef(0);
  const [hud, setHud] = useState({ thetaDeg: 0, cos: 1, sin: 0 });

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    thetaRef.current += speed * dt;
    const theta = thetaRef.current;
    const cx = width * 0.35;
    const cy = height * 0.5;
    const radius = 150;

    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    // unit circle
    ctx.strokeStyle = COLORS.wood;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, TWO_PI);
    ctx.stroke();

    // axis crosshair
    ctx.beginPath();
    ctx.moveTo(cx - radius - 20, cy);
    ctx.lineTo(cx + radius + 20, cy);
    ctx.moveTo(cx, cy - radius - 20);
    ctx.lineTo(cx, cy + radius + 20);
    ctx.stroke();

    const cosT = Math.cos(theta);
    const sinT = Math.sin(theta);
    const tipX = cx + radius * cosT;
    const tipY = cy + radius * sinT;

    // projection lines
    ctx.strokeStyle = COLORS.chalkBlue; // sin / y projection
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(cx, tipY);
    ctx.stroke();

    ctx.strokeStyle = COLORS.chalkCoral; // cos / x projection
    ctx.beginPath();
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(tipX, cy);
    ctx.stroke();

    // vector
    ctx.strokeStyle = COLORS.chalk;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(tipX, tipY);
    ctx.stroke();

    // dot at tip
    ctx.fillStyle = COLORS.chalkGold;
    ctx.beginPath();
    ctx.arc(tipX, tipY, 6, 0, TWO_PI);
    ctx.fill();

    // e^(i*pi) + 1 = 0 callout when theta mod 2pi is within 0.03 of pi
    const thetaMod = ((theta % TWO_PI) + TWO_PI) % TWO_PI;
    if (Math.abs(thetaMod - Math.PI) < 0.03) {
      ctx.fillStyle = COLORS.chalkCoral;
      ctx.font = 'bold 20px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText('e^(i*pi) + 1 = 0', width - 20, 40);
      ctx.textAlign = 'left';
    }

    setHud({ thetaDeg: ((theta * 180) / Math.PI) % 360, cos: cosT, sin: sinT });
  }, WIDTH, HEIGHT);

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Euler&apos;s Identity</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        e^(i*theta) = cos(theta) + i*sin(theta) -- a unit vector rotating in the complex plane.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="speed (omega)" value={speed} min={-3} max={3} step={0.1} onChange={setSpeed} format={(v) => v.toFixed(1)} />
          </Panel>
          <Panel>
            <Hud
              lines={[
                `theta = ${hud.thetaDeg.toFixed(1)} deg`,
                `e^(i*theta) = ${hud.cos.toFixed(3)} ${hud.sin >= 0 ? '+' : '-'} ${Math.abs(hud.sin).toFixed(3)}i`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
