export function Panel({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-3 rounded-lg border border-[#5C4630]/60 bg-[#142019]/80 p-4">
      {children}
    </div>
  );
}

export function Hud({ lines }: { lines: string[] }) {
  return (
    <div className="space-y-1 font-mono text-sm text-[#7FB0CC]">
      {lines.map((line, i) => (
        <div key={i}>{line}</div>
      ))}
    </div>
  );
}
