import type { ReactNode } from "react";
import { Activity, Database, FileSearch, Leaf, Settings2 } from "lucide-react";

const links = [
  { href: "/", label: "Research", icon: FileSearch },
  { href: "/agents", label: "Agents", icon: Activity },
  { href: "/knowledge", label: "Knowledge base", icon: Database },
];

export function AppLayout({ children }: { children: ReactNode }) {
  const currentPath = window.location.pathname;
  return <div className="app-frame">
    <aside className="sidebar">
      <a className="sidebar-brand" href="/"><span className="brand-mark"><Leaf size={18} /></span><span>GREEN<span>TECH</span></span></a>
      <div className="sidebar-section-label">WORKSPACE</div>
      <nav className="sidebar-nav">{links.map(({ href, label, icon: Icon }) => <a className={currentPath === href ? "active" : ""} href={href} key={href}><Icon size={16} /><span>{label}</span>{label === "Agents" && <b>6</b>}</a>)}</nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-status"><span className="live-dot" /><div><strong>All systems nominal</strong><small>API · DB · REDIS · OTEL</small></div></div>
      <a className="sidebar-settings" href="/settings"><Settings2 size={16} /><span>Workspace settings</span></a>
    </aside>
    <div className="app-content">{children}</div>
  </div>;
}
