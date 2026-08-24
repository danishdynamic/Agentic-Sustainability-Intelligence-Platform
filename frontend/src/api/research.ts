import { api } from "./client";
export type ResearchResponse = { run_id: string; status: string };
export type Result = { answer: string; citations: { document_id: string; document_name: string; chunk_id: string; section: string; text: string; relevance_score: number }[]; retrieval: { vector_count: number; lexical_count: number; reranked_count: number; selected_count: number }; grounding: { passed: boolean; score: number; status: string }; cache: { semantic_hit: boolean; embedding_hit: boolean; retrieval_hit: boolean; response_hit: boolean }; metadata: { rag_retries: number; model: string; quota: { rpm: number; tpm: number; rpd: number } } };
export const startResearch = (body: unknown) => api<ResearchResponse>("/api/v1/research", { method: "POST", body: JSON.stringify(body) });
export const getResult = (id: string) => api<Result>(`/api/v1/runs/${id}/result`);
export const getRun = (id: string) => api<{ status: string; current_node: string; progress: { completed: number; total: number } }>(`/api/v1/runs/${id}`);
export const getEvents = (id: string) => api<{ events: { type: string; agent: string; message: string; node?: string }[] }>(`/api/v1/runs/${id}/events`);
