import { create } from "zustand";

type State = { runId: string | null; query: string; setRunId: (runId: string | null) => void; setQuery: (query: string) => void };
const savedRunId = typeof window !== "undefined" ? window.localStorage.getItem("sustainability:last-run") : null;
export const useResearchStore = create<State>((set) => ({ runId: savedRunId, query: "How has our renewable energy target changed from 2024 to 2026?", setRunId: (runId) => { if (runId) window.localStorage.setItem("sustainability:last-run", runId); set({ runId }); }, setQuery: (query) => set({ query }) }));
