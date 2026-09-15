"use client";

import { LEVELS } from "@/lib/levels";
import { pillClass } from "@/lib/ui";

type Props = {
  value: string | null;
  onChange: (level: string | null) => void;
  allowAll?: boolean;
};

export function LevelSwitcher({ value, onChange, allowAll = true }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {allowAll && (
        <button onClick={() => onChange(null)} className={pillClass(value === null)}>
          Все уровни
        </button>
      )}
      {LEVELS.map((l) => (
        <button key={l} onClick={() => onChange(l)} className={pillClass(value === l)}>
          {l}
        </button>
      ))}
    </div>
  );
}
