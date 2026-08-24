import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Activity, BrainCircuit, CheckCircle2, Circle, Database, FileSearch, GitBranch, ShieldCheck, Sparkles, Users } from "lucide-react";
import { getEvents, getResult, startResearch } from "../api/research";
import { AgentPipeline } from "../components/AgentPipeline";
import { Panel } from "../components/Panel";
import { useResearchStore } from "../store";

const roster = [
  { name: "Supervisor", role: "Orchestrates the investigation", icon: Users, color: "sage", status: "Ready" },
  { name: "Query Agent", role: "Analyzes and rewrites questions", icon: BrainCircuit, color: "amber", status: "Ready" },
  { name: "Researcher", role: "Runs hybrid retrieval and reranking", icon: FileSearch, color: "blue", status: "Ready" },
  { name: "Analyst", role: "Synthesizes evidence into an answer", icon: Sparkles, color: "violet", status: "Ready" },
  { name: "Critic", role: "Checks grounding and citations", icon: ShieldCheck, color: "rose", status: "Ready" },
  { name: "Report Agent", role: "Prepares gated report actions", icon: GitBranch, color: "teal", status: "HITL gated" },
];

export function AgentsPage() {
  const { runId, setRunId, query } = useResearchStore();
  const [message, setMessage] = useState("");
  const runMutation = useMutation({ mutationFn: () => startResearch({ query, filters: {}, options: { use_rag: true, use_reranker: true, use_citations: true, use_cache: false } }), onSuccess: (data) => { setRunId(data.run_id); setMessage("Pipeline started. Watch each agent take its turn below."); }, onError: (error: Error) => setMessage(`Could not start pipeline: ${error.message}`) });
  const events = useQuery({ queryKey: ["agent-events", runId], queryFn: () => getEvents(runId!), enabled: !!runId, refetchInterval: runId ? 1200 : false });
  const result = useQuery({ queryKey: ["agent-result", runId], queryFn: () => getResult(runId!), enabled: !!runId });
  return <main className="page-shell"><header className="topbar"><div className="brand"><span className="brand-mark"><Activity size={17} /></span><span>Agent <strong>Control Room</strong></span></div><div className="topbar-meta"><span className="live-dot" /> GRAPH RUNTIME / {runId ?? "NO ACTIVE RUN"}</div></header><section className="page-heading"><span className="eyebrow"><Activity size={14} /> MULTI-AGENT WORKSPACE</span><h1>Watch the team think.</h1><p>Start a research run and follow the handoff from planning to retrieval, synthesis, critique, and completion.</p><button type="button" className="pipeline-button" onClick={() => runMutation.mutate()} disabled={runMutation.isPending}><Activity size={16} /> {runMutation.isPending ? "Starting pipeline..." : "Run agent pipeline"}</button>{message && <small className="pipeline-message">{message}</small>}</section>{runId && <AgentPipeline events={events.data?.events} result={result.data} running={!result.data} />}<section className="agent-grid">{roster.map(({ name, role, icon: Icon, color, status }, index) => <article className={`agent-card ${color}`} key={name}><div className="agent-card-top"><span className="agent-icon"><Icon size={21} /></span><span className={status === "HITL gated" ? "agent-status gated" : "agent-status"}><Circle size={8} /> {status}</span></div><div><span className="agent-index">0{index + 1}</span><h2>{name}</h2><p>{role}</p></div><div className="agent-card-footer"><span>NODE / {name.toLowerCase().replace(" ", "_")}</span><CheckCircle2 size={15} /></div></article>)}</section><div className="agent-lower"><Panel title="Latest handoffs" icon={<GitBranch size={17} />}><div className="handoff-list">{events.data?.events.slice().reverse().map((item, index) => <div className="handoff" key={`${item.agent}-${item.message}-${index}`}><span className="handoff-line" /><div><strong>{item.agent}</strong><p>{item.message}</p></div><small>{item.node ?? "workflow"}</small></div>) ?? <div className="empty-state">Start the agent pipeline to see handoffs here.</div>}</div></Panel><Panel title="Runtime services" icon={<Database size={17} />}><div className="runtime-list"><div><span><Database size={15} /> PostgreSQL / pgvector</span><b>CONNECTED</b></div><div><span><Activity size={15} /> LangGraph checkpoint</span><b>READY</b></div><div><span><Sparkles size={15} /> Gemini generation</span><b>CONFIGURED</b></div></div></Panel></div></main>;
}
