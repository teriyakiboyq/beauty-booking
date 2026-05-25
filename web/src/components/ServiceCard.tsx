import type { Service } from "../lib/api";

interface Props {
  service: Service;
  selected: boolean;
  onSelect: () => void;
}

export function ServiceCard({ service, selected, onSelect }: Props) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full rounded-xl border p-4 text-left transition ${
        selected
          ? "border-violet-500 bg-violet-50"
          : "border-slate-200 bg-white hover:border-violet-300"
      }`}
    >
      <div className="font-semibold">{service.name}</div>
      <div className="mt-1 text-sm text-slate-600">
        {service.duration} мин · {service.price} ₽
      </div>
      {service.description && (
        <p className="mt-2 text-sm text-slate-500">{service.description}</p>
      )}
    </button>
  );
}
