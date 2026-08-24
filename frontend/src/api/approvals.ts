import { api } from "./client";
export const getApproval = (runId: string) => api<{ approval_id: string; action: string; risk_level: string; payload: { filename: string } }>(`/api/v1/runs/${runId}/approval`);
export const resolveApproval = (runId: string, body: unknown) => api<{ decision?: string; status?: string }>(`/api/v1/runs/${runId}/approval`, { method: "POST", body: JSON.stringify(body) });
