import type { ReactNode } from "react";
export function Panel({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) { return <section className="panel"><div className="panel-title">{icon}<span>{title}</span><span className="panel-rule" /></div>{children}</section>; }
