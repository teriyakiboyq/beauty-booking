import { useEffect, useState } from "react";
import { api, type Service } from "../lib/api";
import { Loading } from "../components/Loading";
import { ServiceCard } from "../components/ServiceCard";

interface Props {
  onNext: (service: Service) => void;
}

export function ServicesPage({ onNext }: Props) {
  const [services, setServices] = useState<Service[]>([]);
  const [selected, setSelected] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getServices()
      .then(setServices)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="space-y-3">
      <h1 className="text-xl font-bold">Выберите услугу</h1>
      {services.map((s) => (
        <ServiceCard
          key={s.id}
          service={s}
          selected={selected?.id === s.id}
          onSelect={() => setSelected(s)}
        />
      ))}
      <button
        type="button"
        disabled={!selected}
        onClick={() => selected && onNext(selected)}
        className="mt-4 w-full rounded-xl bg-violet-600 py-3 font-medium text-white disabled:opacity-40"
      >
        Далее
      </button>
    </div>
  );
}
