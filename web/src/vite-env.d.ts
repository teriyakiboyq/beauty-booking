/// <reference types="vite/client" />

interface TelegramWebApp {
  initData: string;
  ready: () => void;
  expand: () => void;
  close: () => void;
  MainButton: {
    text: string;
    show: () => void;
    hide: () => void;
    onClick: (cb: () => void) => void;
    offClick: (cb: () => void) => void;
    showProgress: (leaveActive?: boolean) => void;
    hideProgress: () => void;
  };
  themeParams: Record<string, string>;
}

interface TelegramWindow {
  WebApp: TelegramWebApp;
}

interface Window {
  Telegram?: TelegramWindow;
}
