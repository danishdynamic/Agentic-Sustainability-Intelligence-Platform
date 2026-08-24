import { useEffect, useMemo, useState } from "react";
import { BrainCircuit, Check, Circle, FileSearch, GitBranch, LoaderCircle, ShieldCheck, Sparkles, Users } from "lucide-react";
import type { Result } from "../api/research";
import { Panel } from "./Panel";

type AgentEvent = { agent: string; message: string; node?: string; type?: string };
type Agent = { name: string; role: string; icon: typeof Users; color: string; match: string[] };

const agents: Agent[] = [
  { name: "Supervisor", role: "Plans the investigation", icon: Users, color: "sage", match: ["supervisor"] },
  { name: "Query Agent", role: "Rewrites the question", icon: BrainCircuit, color: "amber", match: ["query_agent"] },
  { name: "Researcher", role: "Retrieves and ranks evidence", icon: FileSearch, color: "blue", match: ["vector_search", "bm25_search", "researcher"] },
  { name: "Analyst", role: "Generates the answer", icon: Sparkles, color: "violet", match: ["analyst"] },
  { name: "Critic", role: "Verifies grounding", icon: ShieldCheck, color: "rose", match: ["critic"] },
  { name: "Report Agent", role: "Gates external actions", icon: GitBranch, color: "teal", match: ["report_agent", "output_guardrail"] },
];

export function AgentPipeline({ events = [], result, running = false }: { events?: AgentEvent[]; result?: Result; running?: boolean }) {
  const [visibleCount, setVisibleCount] = useState(0);
  useEffect(() => {
    setVisibleCount(0);
    if (!events.length) return;
    const timer = window.setInterval(() => setVisibleCount((count) => Math.min(count + 1, events.length)), 520);
    return () => window.clearInterval(timer);
  }, [events]);
  const visibleEvents = events.slice(0, visibleCount);
  const progress = events.length ? Math.round((visibleCount / events.length) * 100) : 0;
  const processing = running || (events.length > 0 && visibleCount < events.length);
  const statuses = useMemo(() => agents.map((agent, index) => { const matches = visibleEvents.filter((event) => agent.match.some((name) => event.agent.toLowerCase().includes(name))); const isCurrent = !matches.length && visibleCount > 0 && index === agents.findIndex((candidate) => candidate.match.some((name) => events[Math.max(visibleCount - 1, 0)]?.agent.toLowerCase().includes(name))); return { matches, isCurrent }; }), [events, visibleEvents, visibleCount]);
  return <Panel title="Live agent pipeline" icon={<GitBranch size={17} />}><div className="pipeline-summary"><div><span>RUN STATE</span><strong>{processing ? "PROCESSING" : progress === 100 ? "PROCESSED" : "READY"}</strong></div><div><span>PIPELINE PROGRESS</span><strong>{progress}%</strong></div>{result && <div><span>GROUNDING</span><strong>{Math.round(result.grounding.score * 100)}%</strong></div>}</div><div className="pipeline-bar"><i style={{ width: `${progress}%` }} /></div><div className="pipeline-stages">{agents.map((agent, index) => { const status = statuses[index]; const completed = status.matches.length > 0; const current = !completed && (status.isCurrent || (processing && index === 0 && visibleCount === 0)); const Icon = agent.icon; return <article className={`pipeline-agent ${agent.color} ${completed ? "completed" : ""} ${current ? "processing" : ""}`} key={agent.name}><div className="pipeline-agent-head"><span className="pipeline-icon"><Icon size={18} /></span><span className="pipeline-state">{completed ? <><Check size={12} /> DONE</> : current ? <><LoaderCircle className="spin" size={12} /> WORKING</> : <><Circle size={9} /> WAITING</>}</span></div><strong>{index + 1}. {agent.name}</strong><small>{agent.role}</small>{status.matches.length > 0 && <p>{status.matches[status.matches.length - 1].message}</p>}</article>; })}</div></Panel>;
}
