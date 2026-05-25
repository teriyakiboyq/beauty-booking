import { useEffect } from "react";
import { initTelegramUI } from "../lib/telegram";

export function useTelegram() {
  useEffect(() => {
    initTelegramUI();
  }, []);
}
