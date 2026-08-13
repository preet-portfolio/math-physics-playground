'use client';

type SliderProps = {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  format?: (value: number) => string;
};

export function Slider({ label, value, min, max, step = 0.01, onChange, format }: SliderProps) {
  const display = format ? format(value) : value.toFixed(2);
  return (
    <label className="block text-sm">
      <span className="text-[#EDEAE0]/80">{label}</span>{' '}
      <span className="font-mono font-semibold text-[#E8B94D]">{display}</span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-1 block w-full accent-[#E8B94D]"
      />
    </label>
  );
}
