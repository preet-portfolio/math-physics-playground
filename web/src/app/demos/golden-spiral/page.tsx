'use client';

import { useState } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';
import { COLORS } from '@/lib/theme';

const WIDTH = 720;
const HEIGHT = 560;
const PHI = (1 + Math.sqrt(5)) / 2;

type Square = { x: number; y: number; side: number };

function buildSquares() {
  const fib = [1, 1];
  for (let i = 2; i < 10; i++) fib.push(fib[i - 1] + fib[i - 2]);
  const directions = ['left', 'below', 'right', 'above'] as const;
  const squares: Square[] = [{ x: 0, y: 0, side: fib[0] }];
  let left = 0, top = 0, right = fib[0], bottom = fib[0];
  for (let i = 1; i < 10; i++) {
    const side = fib[i];
    const d = directions[(i - 1) % 4];
    let nx = 0, ny = 0;
    if (d === 'left') { nx = left - side; ny = top; left -= side; }
    else if (d === 'below') { nx = left; ny = bottom; bottom += side; }
    else if (d === 'right') { nx = right; ny = top; right += side; }
    else { nx = left; ny = top - side; top -= side; }
    squares.push({ x: nx, y: ny, side });
  }
  return { squares, left, top, right, bottom };
}

const { squares, left, top, right, bottom } = buildSquares();
const FIB0 = squares[0].side; // 1

export default function GoldenSpiralDemo() {
  const [growth, setGrowth] = useState(PHI);

  const canvasRef = useCanvasLoop((ctx, _dt, width, height) => {
    ctx.fillStyle = COLORS.board;
    ctx.fillRect(0, 0, width, height);

    const bboxW = right - left;
    const bboxH = bottom - top;
    const pxScale = Math.min((width * 0.5) / bboxW, (height * 0.7) / bboxH);
    const originX = width * 0.42 - (left + bboxW / 2) * pxScale;
    const originY = height * 0.5 - (top + bboxH / 2) * pxScale;

    ctx.strokeStyle = COLORS.wood;
    ctx.lineWidth = 1;
    for (const sq of squares) {
      ctx.strokeRect(
        originX + sq.x * pxScale,
        originY + sq.y * pxScale,
        sq.side * pxScale,
        sq.side * pxScale,
      );
    }

    const b = Math.pow(growth, 2 / Math.PI);
    const r0 = 4;
    const originLocalX = 0;
    const originLocalY = FIB0; // (left, bottom) corner of square 0 = local (0, fib[0])

    ctx.strokeStyle = COLORS.chalkGold;
    ctx.lineWidth = 2;
    ctx.beginPath();
    const steps = 200;
    for (let i = 0; i <= steps; i++) {
      const theta = (4 * Math.PI * i) / steps;
      const r = r0 * Math.pow(b, theta);
      const localX = originLocalX + r * Math.cos(theta);
      const localY = originLocalY + r * Math.sin(theta);
      const px = originX + localX * pxScale;
      const py = originY + localY * pxScale;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
  }, WIDTH, HEIGHT);

  const b = Math.pow(growth, 2 / Math.PI);
  const isGolden = Math.abs(growth - 1.618033988749895) < 0.01;

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Golden Ratio Spiral</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        r(&theta;) = r0 &middot; growth^(2&theta;/&pi;) — a logarithmic spiral overlaid on the Fibonacci square tiling.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas ref={canvasRef} className="rounded-lg border border-[#5C4630]/60" />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider
              label="growth"
              value={growth}
              min={1.0}
              max={2.5}
              step={0.001}
              onChange={setGrowth}
              format={(v) => v.toFixed(3)}
            />
          </Panel>
          <Panel>
            <Hud lines={[`growth = ${growth.toFixed(3)}`, `b = growth^(2/pi) = ${b.toFixed(3)}`]} />
            {isGolden && (
              <div className="font-mono text-sm text-[#D97757]">== golden ratio (phi)!</div>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
