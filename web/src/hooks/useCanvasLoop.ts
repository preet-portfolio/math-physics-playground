'use client';

import { useEffect, useLayoutEffect, useRef } from 'react';

export type DrawFn = (ctx: CanvasRenderingContext2D, dt: number, width: number, height: number) => void;

/**
 * The web equivalent of common/scene.py's Scene contract: a canvas ref plus
 * a requestAnimationFrame loop that calls `draw(ctx, dt, width, height)`
 * every frame, handling devicePixelRatio scaling so rendering stays crisp
 * on Retina displays. `draw` owns all per-frame state (position, angle,
 * etc.) via closures/refs in the calling component -- this hook only owns
 * timing and the canvas backing store.
 */
export function useCanvasLoop(draw: DrawFn, width: number, height: number) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawRef = useRef(draw);

  // Refs must not be mutated during render -- update it in a layout effect,
  // which runs synchronously after commit but before the browser paints, so
  // the next animation frame always sees the latest `draw` closure.
  useLayoutEffect(() => {
    drawRef.current = draw;
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    // Full size where there's room; on narrower screens the canvas shrinks to
    // fit and keeps its shape, while drawing still happens in width x height.
    canvas.style.width = `${width}px`;
    canvas.style.maxWidth = '100%';
    canvas.style.aspectRatio = `${width} / ${height}`;
    ctx.scale(dpr, dpr);

    let rafId = 0;
    let last = performance.now();

    function frame(now: number) {
      const dt = Math.min((now - last) / 1000, 1 / 15); // clamp huge gaps (tab backgrounded)
      last = now;
      if (ctx) drawRef.current(ctx, dt, width, height);
      rafId = requestAnimationFrame(frame);
    }

    rafId = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(rafId);
  }, [width, height]);

  return canvasRef;
}
