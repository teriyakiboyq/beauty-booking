/** Telegram WebApp SDK helpers */

export function getWebApp(): TelegramWebApp | null {
  return window.Telegram?.WebApp ?? null;
}

export function getInitData(): string {
  const wa = getWebApp();
  if (!wa?.initData) {
    // Local dev fallback (API will reject without valid signature)
    return import.meta.env.VITE_DEV_INIT_DATA ?? "";
  }
  return wa.initData;
}

export function initTelegramUI(): void {
  const wa = getWebApp();
  wa?.ready();
  wa?.expand();
}
