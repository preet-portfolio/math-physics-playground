'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { demos } from '@/lib/demos';

const CATEGORY_LABEL: Record<string, string> = { art: 'ART', math: 'MATH', physics: 'PHYSICS' };
const CATEGORY_COLOR: Record<string, string> = {
  art: '#E8B94D',
  math: '#E8B94D',
  physics: '#7FB0CC',
};

export function Nav() {
  const pathname = usePathname();
  const groups: Record<string, typeof demos> = { art: [], math: [], physics: [] };
  for (const demo of demos) groups[demo.category].push(demo);

  return (
    <nav className="w-64 shrink-0 overflow-y-auto border-r border-[#5C4630]/60 bg-[#142019] p-4">
      <Link href="/" className="mb-6 block text-lg font-semibold tracking-tight text-[#EDEAE0]">
        Math &amp; Physics Playground
      </Link>
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
    </nav>
  );
}
