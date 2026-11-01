'use client';

import { useState, useRef, type MouseEvent } from 'react';
import { useCanvasLoop } from '@/hooks/useCanvasLoop';
import { Slider } from '@/components/Slider';
import { Panel, Hud } from '@/components/Panel';

const WIDTH = 720;
const HEIGHT = 560;
const RENDER_SCALE = 0.5;
const RENDER_WIDTH = Math.round(WIDTH * RENDER_SCALE);
const RENDER_HEIGHT = Math.round(HEIGHT * RENDER_SCALE);

const DEFAULT_CX = -0.5;
const DEFAULT_CY = 0.0;
const DEFAULT_ZOOM = 1;
const DEFAULT_MAX_ITER = 80;

function computeMandelbrot(
  width: number,
  height: number,
  cx: number,
  cy: number,
  span: number,
  maxIter: number,
): Uint8ClampedArray<ArrayBuffer> {
  const spanY = (span * height) / width;
  const data = new Uint8ClampedArray(width * height * 4) as Uint8ClampedArray<ArrayBuffer>;
  for (let py = 0; py < height; py++) {
    const y0 = cy - spanY + (2 * spanY * py) / height;
    for (let px = 0; px < width; px++) {
      const x0 = cx - span + (2 * span * px) / width;
      let x = 0, y = 0, iter = 0;
      while (x * x + y * y <= 4 && iter < maxIter) {
        const xtemp = x * x - y * y + x0;
        y = 2 * x * y + y0;
        x = xtemp;
        iter++;
      }
      const idx = (py * width + px) * 4;
      if (iter === maxIter) {
        // COLORS.board (#1B2B22) = rgb(27,43,34), the "inside the set" color
        data[idx] = 27;
        data[idx + 1] = 43;
        data[idx + 2] = 34;
      } else {
        const t = iter / maxIter;
        data[idx] = (Math.sin(t * 6.0 + 0.0) * 0.5 + 0.5) * 255;
        data[idx + 1] = (Math.sin(t * 6.0 + 2.0) * 0.5 + 0.5) * 255;
        data[idx + 2] = (Math.sin(t * 6.0 + 4.0) * 0.5 + 0.5) * 255;
      }
      data[idx + 3] = 255;
    }
  }
  return data;
}

export default function MandelbrotDemo() {
  const [cx, setCx] = useState(DEFAULT_CX);
  const [cy, setCy] = useState(DEFAULT_CY);
  const [zoom, setZoom] = useState(DEFAULT_ZOOM);
  const [maxIter, setMaxIter] = useState(DEFAULT_MAX_ITER);

  const offscreenRef = useRef<HTMLCanvasElement | null>(null);
  const lastParamsRef = useRef<{ cx: number; cy: number; span: number; maxIter: number } | null>(null);

  const canvasRef = useCanvasLoop((ctx, _dt, width, height) => {
    const span = 1.6 / zoom;
    const last = lastParamsRef.current;
    const changed =
      !last || last.cx !== cx || last.cy !== cy || last.span !== span || last.maxIter !== maxIter;

    if (!offscreenRef.current) {
      offscreenRef.current = document.createElement('canvas');
      offscreenRef.current.width = RENDER_WIDTH;
      offscreenRef.current.height = RENDER_HEIGHT;
    }
    const off = offscreenRef.current;

    if (changed) {
      const octx = off.getContext('2d');
      if (octx) {
        const data = computeMandelbrot(RENDER_WIDTH, RENDER_HEIGHT, cx, cy, span, maxIter);
        octx.putImageData(new ImageData(data, RENDER_WIDTH, RENDER_HEIGHT), 0, 0);
      }
      lastParamsRef.current = { cx, cy, span, maxIter };
    }

    ctx.drawImage(off, 0, 0, width, height);
  }, WIDTH, HEIGHT);

  function handleClick(e: MouseEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    // On narrow screens the canvas is shown smaller than WIDTH x HEIGHT.
    const px = ((e.clientX - rect.left) * WIDTH) / rect.width;
    const py = ((e.clientY - rect.top) * HEIGHT) / rect.height;
    const span = 1.6 / zoom;
    const spanY = (span * HEIGHT) / WIDTH;
    setCx(cx - span + (2 * span * px) / WIDTH);
    setCy(cy - spanY + (2 * spanY * py) / HEIGHT);
  }

  const span = 1.6 / zoom;

  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-2xl font-semibold text-[#EDEAE0]">Mandelbrot Set</h1>
      <p className="mt-2 text-[#EDEAE0]/70">
        z = z&sup2; + c — escape-time fractal, recomputed only when the view changes.
      </p>
      <div className="mt-6 flex flex-wrap gap-6">
        <canvas
          ref={canvasRef}
          onClick={handleClick}
          className="cursor-crosshair rounded-lg border border-[#5C4630]/60"
        />
        <div className="w-64 shrink-0 space-y-4">
          <Panel>
            <Slider
              label="max iterations"
              value={maxIter}
              min={20}
              max={300}
              step={1}
              onChange={(v) => setMaxIter(Math.round(v))}
              format={(v) => v.toFixed(0)}
            />
            <Slider
              label="zoom"
              value={zoom}
              min={1}
              max={200}
              step={1}
              onChange={(v) => setZoom(Math.round(v))}
              format={(v) => v.toFixed(0)}
            />
          </Panel>
          <Panel>
            <Hud
              lines={[
                `c = ${cx.toFixed(4)} + ${cy.toFixed(4)}i`,
                `zoom = ${zoom.toFixed(0)}x`,
                `span = ${span.toFixed(5)}`,
                `max iter = ${maxIter}`,
                'click canvas to recenter',
              ]}
            />
          </Panel>
        </div>
      </div>
    </div>
  );
}
