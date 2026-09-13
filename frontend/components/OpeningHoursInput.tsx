"use client";

import { useEffect, useState } from "react";

const DAY_PRESETS = [
  { label: "Every day", value: "Mon-Sun" },
  { label: "Weekdays", value: "Mon-Fri" },
  { label: "Weekends", value: "Sat-Sun" },
  { label: "Tue–Sun", value: "Tue-Sun" },
  { label: "Wed–Sun", value: "Wed-Sun" },
];

interface Props {
  label?: string;
  value: string; // e.g. "Mon-Sun 11:00-22:00"
  onChange: (value: string) => void;
}

function parseValue(value: string) {
  const match = value.match(/^(\S+)\s+(\d{2}:\d{2})-(\d{2}:\d{2})$/);
  if (match) return { days: match[1], start: match[2], end: match[3] };
  return { days: "Mon-Sun", start: "11:00", end: "22:00" };
}

export function OpeningHoursInput({ label = "Opening hours", value, onChange }: Props) {
  const initial = parseValue(value);
  const [days, setDays] = useState(initial.days);
  const [start, setStart] = useState(initial.start);
  const [end, setEnd] = useState(initial.end);

  useEffect(() => {
    onChange(`${days} ${start}-${end}`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [days, start, end]);

  return (
    <div className="flex flex-col gap-2 text-sm">
      <span className="text-ink/70">{label}</span>

      <div className="flex flex-wrap gap-2">
        {DAY_PRESETS.map((preset) => (
          <button
            key={preset.value}
            type="button"
            onClick={() => setDays(preset.value)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-150 active:scale-95 ${
              days === preset.value
                ? "bg-teal text-paper shadow-[0_0_0_3px_rgba(23,73,74,0.25)]"
                : "bg-paper border border-line text-ink/70 hover:border-teal-soft"
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <input
          type="time"
          value={start}
          onChange={(e) => setStart(e.target.value)}
          className="px-3 py-2 rounded-xl border border-line bg-paper focus:bg-paper-raised outline-none transition-colors focus:border-teal"
        />
        <span className="text-ink/40">to</span>
        <input
          type="time"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
          className="px-3 py-2 rounded-xl border border-line bg-paper focus:bg-paper-raised outline-none transition-colors focus:border-teal"
        />
      </div>

      <p className="text-xs text-ink/45">Preview: {days} {start}–{end}</p>
    </div>
  );
}