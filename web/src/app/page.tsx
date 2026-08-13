import Link from 'next/link';
import { demos } from '@/lib/demos';

const CATEGORY_COLOR: Record<string, string> = { art: '#E8B94D', math: '#E8B94D', physics: '#7FB0CC' };

export default function Home() {
  return (
    <div className="mx-auto max-w-4xl px-8 py-12">
      <h1 className="text-3xl font-semibold tracking-tight text-[#EDEAE0]">Math &amp; Physics Playground</h1>
      <p className="mt-3 max-w-2xl text-[#EDEAE0]/70">
        Real equations, not decoration: rotational kinematics, RK4 chaos, symplectic
        orbital mechanics, escape-time fractals. The web port of a set of Python/pygame
        desktop apps built earlier — same math, reimplemented for the browser.
      </p>

      <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {demos.map((demo) => (
          <Link
            key={demo.slug}
            href={`/demos/${demo.slug}`}
            className="rounded-lg border border-[#5C4630]/60 bg-[#142019] p-4 transition-colors hover:border-[#5C4630]"
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-[#EDEAE0]">{demo.title}</span>
              <span
                className="text-xs font-semibold uppercase tracking-wide"
                style={{ color: CATEGORY_COLOR[demo.category] }}
              >
                {demo.category}
              </span>
            </div>
            <p className="mt-1 text-sm text-[#EDEAE0]/60">{demo.blurb}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
