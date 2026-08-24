import { Check } from "lucide-react";
import { Panel } from "./Panel";
const stages = ["Input guardrail", "Supervisor", "Query rewrite", "Hybrid retrieval", "Reranking", "Generation", "Grounding"];
export function WorkflowTimeline({ activeStage }: { activeStage: number }) { return <Panel title="Workflow trace" icon={<span>◌</span>}><div className="stages">{stages.map((stage, index) => <div className={`stage ${index < activeStage ? "done" : index === activeStage ? "active" : ""}`} key={stage}><span className="stage-icon">{index < activeStage ? <Check size={13} /> : index + 1}</span><span>{stage}</span>{index === activeStage - 1 && <span className="stage-now">NOW</span>}</div>)}</div></Panel>; }
