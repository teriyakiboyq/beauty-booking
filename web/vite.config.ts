import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: true,
    // Ngrok / Telegram WebApp: иначе Vite блокирует Host из туннеля
    allowedHosts: [
      "galleria-scoop-deferred.ngrok-free.dev",
      ".ngrok-free.dev",
      ".ngrok-free.app",
      ".ngrok.io",
    ],
    // Один ngrok на :5173 — запросы /api уходят на локальный FastAPI :8000
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
