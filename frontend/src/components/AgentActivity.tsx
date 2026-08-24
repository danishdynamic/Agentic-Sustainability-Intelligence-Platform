import { Zap } from "lucide-react";
import { Panel } from "./Panel";
export function AgentActivity({ events = [] }: { events?: { agent: string; message: string }[] }) { return <Panel title="Agent activity" icon={<Zap size={17} />}><div className="activity-list">{events.map((item) => <div className="activity" key={`${item.agent}-${item.message}`}><span className="activity-dot" /><span><strong>{item.agent}</strong><small>{item.message}</small></span></div>)}</div></Panel>; }
