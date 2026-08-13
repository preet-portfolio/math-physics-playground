'use client';

import { useState, useRef } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720, HEIGHT = 560;

export default function LissajousDemo() {
  const [aFreq, setAFreq] = useState(3);
  const [bFreq, setBFreq] = useState(2);
  const [delta, setDelta] = useState(Math.PI / 2);
  const [speed, setSpeed] = useState(1.0);
  const tRef = useRef(0);
  const prevPointRef = useRef<{ x: number; y: number } | null>(null);

  const canvasRef = useCanvasLoop((ctx, dt, width, height) => {
    tRef.current += speed * dt;
    const t = tRef.current;
    const a = Math.round(aFreq);
    const b = Math.round(bFreq);
    const cx = width * 0.5;
    const cy = height * 0.5;
    const amp = Math.min(width, height) * 0.35;

    const x = cx + amp * Math.sin(a * t + delta);
    const y = cy + amp * Math.sin(b * t);

    // Low-alpha refill instead of clearRect -- traced curve is the point.
    ctx.fillStyle = 'rgba(27,43,34,0.08)';
    ctx.fillRect(0, 0, width, height);

    const prev = prevPointRef.current;
    if (prev) {
      ctx.strokeStyle = COLORS.chalkBlue;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(prev.x, prev.y);
      ctx.lineTo(x, y);
      ctx.stroke();
    }
    prevPointRef.current = { x, y };

    ctx.fillStyle = COLORS.chalkGold;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  }, WIDTH, HEIGHT);

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Lissajous Curves</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        x = A sin(at+d), y = A sin(bt) -- two perpendicular sinusoids at different frequencies.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider label="a (x-freq)" value={aFreq} min={1} max={10} step={1} onChange={setAFreq} format={(v) => `${Math.round(v)}`} />
            <Slider label="b (y-freq)" value={bFreq} min={1} max={10} step={1} onChange={setBFreq} format={(v) => `${Math.round(v)}`} />
            <Slider label="delta (phase)" value={delta} min={0} max={Math.PI * 2} step={0.01} onChange={setDelta} format={(v) => v.toFixed(2)} />
            <Slider label="speed" value={speed} min={0.1} max={4} step={0.1} onChange={setSpeed} format={(v) => v.toFixed(1)} />
          </Panel>
          <Panel>
            <Hud
              lines={[
                `a = ${Math.round(aFreq)}, b = ${Math.round(bFreq)}`,
                `delta = ${delta.toFixed(2)} rad`,
                `speed = ${speed.toFixed(2)}`,
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
