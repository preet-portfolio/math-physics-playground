'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { demos } from '@/lib/demos';

const CATEGORY_LABEL: Record<string, string> = { art: 'ART', math: 'MATH', physics: 'PHYSICS' };
const CATEGORY_COLOR: Record<string, string> = {
  art: '#E8B94D',
  math: '#E8B94D',
  physics: '#7FB0CC',
};

export function Nav() {
  const pathname = usePathname();
  // Below md the nav is a top bar and the demo list folds behind a button,
  // so it doesn't squeeze the page into the space beside it.
  const [open, setOpen] = useState(false);
  const groups: Record<string, typeof demos> = { art: [], math: [], physics: [] };
  for (const demo of demos) groups[demo.category].push(demo);

  return (
    <nav className="shrink-0 overflow-y-auto border-b border-[#5C4630]/60 bg-[#142019] p-4 md:w-64 md:border-r md:border-b-0">
      <div className="flex items-center justify-between gap-4 md:mb-6">
        <Link
          href="/"
          onClick={() => setOpen(false)}
          className="block text-lg font-semibold tracking-tight text-[#EDEAE0]"
        >
          Math &amp; Physics Playground
        </Link>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls="demo-list"
          className="shrink-0 rounded-md border border-[#5C4630]/60 bg-[#1B2B22] px-3 py-1.5 text-sm text-[#EDEAE0] transition-colors hover:bg-[#1B2B22]/70 md:hidden"
        >
          {open ? 'Close' : 'Demos'}
        </button>
      </div>
      <div id="demo-list" className={`${open ? 'mt-4' : 'hidden'} md:mt-0 md:block`}>
        {(['art', 'math', 'physics'] as const).map((cat) =>
          groups[cat].length ? (
            <div key={cat} className="mb-4">
              <p className="mb-1 text-xs font-semibold tracking-wide" style={{ color: CATEGORY_COLOR[cat] }}>
                {CATEGORY_LABEL[cat]}
              </p>
              <ul className="space-y-1">
                {groups[cat].map((demo) => {
                  const href = `/demos/${demo.slug}`;
                  const active = pathname === href;
                  return (
                    <li key={demo.slug}>
                      <Link
                        href={href}
                        onClick={() => setOpen(false)}
                        className={`block rounded-md px-3 py-1.5 text-sm transition-colors ${
                          active
                            ? 'bg-white/10 font-medium text-[#EDEAE0]'
                            : 'text-[#EDEAE0]/60 hover:bg-white/5 hover:text-[#EDEAE0]'
                        }`}
                      >
                        {demo.title}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null,
        )}
      </div>
    </nav>
  );
}
