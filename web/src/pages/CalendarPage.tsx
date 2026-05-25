import { useEffect, useState } from "react";
import { api, type Service, type Slot } from "../lib/api";
import { Loading } from "../components/Loading";
import { SlotPicker } from "../components/SlotPicker";

interface Props {
  service: Service;
  onBack: () => void;
  onNext: (slot: Slot) => void;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function CalendarPage({ service, onBack, onNext }: Props) {
  const [date, setDate] = useState(todayIso());
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selected, setSelected] = useState<Slot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setSelected(null);
    api
      .getSlots(service.id, date)
      .then(setSlots)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [service.id, date]);

  return (
    <div className="space-y-4">
      <button type="button" onClick={onBack} className="text-sm text-violet-600">
        ← Назад
      </button>
      <h1 className="text-xl font-bold">{service.name}</h1>
      <input
        type="date"
        value={date}
        min={todayIso()}
        onChange={(e) => setDate(e.target.value)}
        className="w-full rounded-lg border border-slate-200 px-3 py-2"
      />
      {loading && <Loading />}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <SlotPicker
          slots={slots}
          selectedStart={selected?.start_time ?? null}
          onSelect={setSelected}
        />
      )}
      <button
        type="button"
        disabled={!selected}
        onClick={() => selected && onNext(selected)}
        className="w-full rounded-xl bg-violet-600 py-3 font-medium text-white disabled:opacity-40"
      >
        Подтвердить время
      </button>
    </div>
  );
}
