import { useState } from "react";
import { useTelegram } from "./hooks/useTelegram";
import type { Service, Slot } from "./lib/api";
import { ServicesPage } from "./pages/ServicesPage";
import { CalendarPage } from "./pages/CalendarPage";
import { ConfirmPage } from "./pages/ConfirmPage";

type Step = "services" | "calendar" | "confirm";

export default function App() {
  useTelegram();
  const [step, setStep] = useState<Step>("services");
  const [service, setService] = useState<Service | null>(null);
  const [slot, setSlot] = useState<Slot | null>(null);

  return (
    <main className="mx-auto min-h-screen max-w-md p-4">
      {step === "services" && (
        <ServicesPage
          onNext={(s) => {
            setService(s);
            setStep("calendar");
          }}
        />
      )}
      {step === "calendar" && service && (
        <CalendarPage
          service={service}
          onBack={() => setStep("services")}
          onNext={(s) => {
            setSlot(s);
            setStep("confirm");
          }}
        />
      )}
      {step === "confirm" && service && slot && (
        <ConfirmPage
          service={service}
          slot={slot}
          onBack={() => setStep("calendar")}
        />
      )}
    </main>
  );
}
