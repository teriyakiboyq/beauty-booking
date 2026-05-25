/**
 * HTTP client for FastAPI backend.
 * Sends Telegram initData on every request for auth.
 */

import { getInitData } from "./telegram";

// С ngrok: оставьте /api (тот же хост, что и Mini App) или полный https://xxx.ngrok.app/api
const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("X-Telegram-Init-Data", getInitData());
  if (options.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? response.statusText);
  }
  return response.json() as Promise<T>;
}

export interface Service {
  id: string;
  name: string;
  price: number;
  duration: number;
  description?: string;
}

export interface Slot {
  start_time: string;
  end_time: string;
  label_local: string;
}

export interface Appointment {
  id: string;
  service_id: string;
  start_time: string;
  end_time: string;
  status: string;
}

export const api = {
  getServices: () => request<Service[]>("/services"),
  getSlots: (serviceId: string, date: string) =>
    request<Slot[]>(`/slots?service_id=${serviceId}&date=${date}`),
  createAppointment: (serviceId: string, startTime: string) =>
    request<Appointment>("/appointments", {
      method: "POST",
      body: JSON.stringify({ service_id: serviceId, start_time: startTime }),
    }),
  getMyAppointments: () => request<Appointment[]>("/appointments/my"),
};
