import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ResearchPage } from "./pages/ResearchPage";
import { AgentsPage } from "./pages/AgentsPage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { AppLayout } from "./components/AppLayout";
import "./styles.css";

const queryClient = new QueryClient();
const page = window.location.pathname === "/agents" ? <AgentsPage /> : window.location.pathname === "/knowledge" ? <KnowledgePage /> : <ResearchPage />;
createRoot(document.getElementById("root")!).render(<StrictMode><QueryClientProvider client={queryClient}><AppLayout>{page}</AppLayout></QueryClientProvider></StrictMode>);
