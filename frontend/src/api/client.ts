const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) throw new Error((await response.json()).detail?.message ?? "The request failed");
  return response.json() as Promise<T>;
}
