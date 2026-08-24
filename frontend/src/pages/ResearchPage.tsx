import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, ChevronDown, CircleDot, Leaf, Search, Sparkles } from "lucide-react";
import { getApproval, resolveApproval } from "../api/approvals";
import { getEvents, getResult, getRun, startResearch } from "../api/research";
import { AgentActivity } from "../components/AgentActivity";
import { ApprovalPanel } from "../components/ApprovalPanel";
import { CachePanel } from "../components/CachePanel";
import { EvidencePanel } from "../components/EvidencePanel";
import { ResultView } from "../components/ResultView";
import { RetrievalPanel } from "../components/RetrievalPanel";
import { WorkflowTimeline } from "../components/WorkflowTimeline";
import { useResearchStore } from "../store";

export function ResearchPage() {
  const { query, setQuery, runId, setRunId } = useResearchStore();
  const [category, setCategory] = useState("Energy");
  const [yearFrom, setYearFrom] = useState("2024");
  const [yearTo, setYearTo] = useState("2026");
  const mutation = useMutation({ mutationFn: startResearch, onSuccess: (data) => setRunId(data.run_id) });
  const run = useQuery({ queryKey: ["run", runId], queryFn: () => getRun(runId!), enabled: !!runId, refetchInterval: runId ? 1200 : false });
  const result = useQuery({ queryKey: ["result", runId], queryFn: () => getResult(runId!), enabled: !!runId && run.data?.status === "completed" });
  const events = useQuery({ queryKey: ["events", runId], queryFn: () => getEvents(runId!), enabled: !!runId });
  const approval = useQuery({ queryKey: ["approval", runId], queryFn: () => getApproval(runId!), enabled: !!runId && !!result.data });
  const [approvalMessage, setApprovalMessage] = useState("");
  const [approvalResolved, setApprovalResolved] = useState(false);
  const approvalMutation = useMutation({ mutationFn: (body: unknown) => resolveApproval(runId!, body), onSuccess: (response: { decision?: string }) => { setApprovalMessage(`Decision recorded: ${response.decision ?? "resumed"}`); setApprovalResolved(true); }, onError: (error: Error) => setApprovalMessage(`Approval failed: ${error.message}`) });
  const activeStage = run.data?.current_node === "output_guardrail" ? 7 : Math.max(1, run.data?.progress.completed ?? 0);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    mutation.mutate({ query, filters: { category: category.toLowerCase(), year_from: Number(yearFrom), year_to: Number(yearTo) }, options: { use_rag: true, use_reranker: true, use_citations: true } });
  }

  function resolve(decision: "approve" | "reject" | "edit", filename?: string) {
    if (!approval.data) return;
    approvalMutation.mutate({ approval_id: approval.data.approval_id, decision, edited_payload: decision === "edit" ? { filename } : null });
  }

  return <main className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark"><Leaf size={18} /></span><span>Sustainability <strong>Intelligence</strong></span></div><div className="topbar-meta"><span className="live-dot" /> SYSTEM OPERATIONAL <span className="divider" /> <span className="model-tag">GEMINI 3.1 FLASH LITE</span></div></header>
    <section className="hero"><div className="eyebrow"><Sparkles size={14} /> GREEN TECH / RESEARCH CONSOLE</div><h1>Ask better questions<br /><em>of your sustainability data.</em></h1><p className="hero-copy">Evidence-backed answers across emissions, energy, water, and climate strategy. Every claim stays traceable.</p>
      <form className="query-card" onSubmit={submit}><div className="query-label"><Search size={15} /> RESEARCH QUERY <span>⌘ ↵</span></div><textarea value={query} onChange={(event) => setQuery(event.target.value)} rows={2} /><div className="form-footer"><div className="filters"><label>DOMAIN <select value={category} onChange={(event) => setCategory(event.target.value)}><option>Energy</option><option>Emissions</option><option>Water</option><option>Climate</option></select><ChevronDown size={13} /></label><label>WINDOW <input value={yearFrom} onChange={(event) => setYearFrom(event.target.value)} aria-label="Start year" /><span>→</span><input value={yearTo} onChange={(event) => setYearTo(event.target.value)} aria-label="End year" /></label></div><button className="ask-button" disabled={mutation.isPending}>{mutation.isPending ? "Thinking..." : "Run research"}<ArrowUpRight size={17} /></button></div></form>
    </section>
    <AnimatePresence>{runId && <motion.section className="workspace" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}><div className="run-header"><div><span className="section-kicker">ACTIVE INVESTIGATION</span><h2>Run <code>{runId}</code></h2></div><span className="status-pill"><CircleDot size={13} /> {run.data?.status?.toUpperCase() ?? "QUEUED"}</span></div>
      <div className="grid-layout"><div className="main-column"><WorkflowTimeline activeStage={activeStage} /><EvidencePanel citations={result.data?.citations} /></div><aside className="side-column"><RetrievalPanel retrieval={result.data?.retrieval} /><AgentActivity events={events.data?.events} /><CachePanel quota={result.data?.metadata.quota} cache={result.data?.cache} /></aside></div>
      {result.data && <ResultView result={result.data} />}
      {approval.data && !approvalResolved && <ApprovalPanel filename={approval.data.payload.filename} message={approvalMessage} onApprove={() => resolve("approve")} onReject={() => resolve("reject")} onEdit={(filename) => resolve("edit", filename)} />}
      {approvalResolved && <div className="decision-banner">{approvalMessage}</div>}
    </motion.section>}</AnimatePresence>
    <footer><span>GREEN TECH INDUSTRIES · INTERNAL KNOWLEDGE BASE</span><span>Built for accountable decisions <Leaf size={13} /></span></footer>
  </main>;
}
