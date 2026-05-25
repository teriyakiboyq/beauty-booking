import { useState } from "react";
import { api, type Service, type Slot } from "../lib/api";

interface Props {
  service: Service;
  slot: Slot;
  onBack: () => void;
}

export function ConfirmPage({ service, slot, onBack }: Props) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const book = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.createAppointment(service.id, slot.start_time);
      setDone(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка записи");
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <p className="py-12 text-center text-lg font-medium text-green-700">
        Вы записаны! ✅
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={onBack} className="text-sm text-violet-600">
        ← Назад
      </button>
      <h1 className="text-xl font-bold">Подтверждение</h1>
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <p className="font-semibold">{service.name}</p>
        <p className="mt-2 text-slate-600">
          Время: <strong>{slot.label_local}</strong>
        </p>
        <p className="text-slate-600">
          Стоимость: <strong>{service.price} ₽</strong>
        </p>
      </div>
      {error && <p className="text-red-600">{error}</p>}
      <button
        type="button"
        disabled={loading}
        onClick={book}
        className="w-full rounded-xl bg-violet-600 py-3 font-medium text-white disabled:opacity-40"
      >
        {loading ? "Запись…" : "Записаться"}
      </button>
    </div>
  );
}
