import type { Slot } from "../lib/api";

interface Props {
  slots: Slot[];
  selectedStart: string | null;
  onSelect: (slot: Slot) => void;
}

export function SlotPicker({ slots, selectedStart, onSelect }: Props) {
  if (slots.length === 0) {
    return (
      <p className="py-6 text-center text-slate-500">На этот день нет свободных слотов</p>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-2">
      {slots.map((slot) => (
        <button
          key={slot.start_time}
          type="button"
          onClick={() => onSelect(slot)}
          className={`rounded-lg border py-2 text-sm font-medium ${
            selectedStart === slot.start_time
              ? "border-violet-500 bg-violet-500 text-white"
              : "border-slate-200 bg-white"
          }`}
        >
          {slot.label_local}
        </button>
      ))}
    </div>
  );
}
