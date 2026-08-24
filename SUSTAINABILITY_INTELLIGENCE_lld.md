# Frontend + Backend LLD / Build Specification

> Creating a Multi agent architecture into a RAG system with hybrid retrieval, reranking, corrective RAG, citations, guardrails, MCP, HITL, Redis caching, semantic caching, RAGAS, and OpenTelemetry.


---

# 1. What the final application does

The user asks a sustainability question such as:

> "How has GreenTech's renewable energy target changed from 2024 to 2026?"

The system:

```text
User
  ↓
Input Guardrail
  ↓
LangGraph Supervisor
  ↓
Query Analysis / Rewriting
  ↓
Hybrid RAG
  ├── pgvector semantic search
  └── lexical/BM25 search
  ↓
Merge candidates
  ↓
Reranker
  ↓
Evidence selection
  ↓
Gemini
  ↓
Grounding / citation verification
  ├── PASS → final answer
  └── FAIL → corrective RAG → retry
  ↓
Output Guardrail
  ↓
Frontend
```

For actions such as saving or publishing a report:

```text
Agent
  ↓
Risk Gate
  ↓
interrupt()
  ↓
Frontend Approval UI
  ├── Approve
  ├── Edit & Approve
  └── Reject
  ↓
LangGraph resumes from checkpoint
```

---

# 2. Domain

Use a fictional organization such as:

**GreenTech Industries**

The knowledge base contains only `.md` and `.txt` files initially.

Example:

```text
knowledge/
├── climate/
├── emissions/
├── energy/
├── water/
├── waste/
├── sustainability/
└── supply-chain/
```

Example files:

```text
scope-1.md
scope-2.md
scope-3.md
renewable-energy.md
water-management.md
waste-management.md
circular-economy.md
sustainability-strategy-2024.md
sustainability-strategy-2025.md
sustainability-strategy-2026.md
```

Start with roughly **10–20 documents**.

---

# 3. High-level repository

```text
project-2/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── graph/
│   │   ├── rag/
│   │   ├── guardrails/
│   │   ├── mcp/
│   │   ├── cache/
│   │   ├── evaluation/
│   │   ├── observability/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── migrations/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── types/
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
│
├── knowledge/
│   ├── climate/
│   ├── emissions/
│   ├── energy/
│   ├── water/
│   ├── waste/
│   └── sustainability/
│
├── evaluation/
│   ├── datasets/
│   └── results/
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 4. Docker Compose

Docker Compose must provide at least:

```text
PostgreSQL + pgvector
Redis
Backend
Frontend
```

Recommended:

```text
services:

  postgres:
    PostgreSQL with pgvector

  redis:
    Redis

  backend:
    FastAPI + LangGraph

  frontend:
    React
```

Do not add unnecessary infrastructure initially.

OpenTelemetry and RAGAS can start as application dependencies rather than separate containers.

Later, if useful, add an observability backend such as Jaeger/OTel Collector.

---

# 5. Environment variables

Create `.env.example`.

```env
# Application
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# Gemini
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_EMBEDDING_MODEL=

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=sustainability
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

DATABASE_URL=

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=

# RAG
RETRIEVAL_TOP_K=20
RERANK_TOP_K=8
MAX_RAG_RETRIES=2
CHUNK_SIZE=
CHUNK_OVERLAP=

# Cache
CACHE_TTL_SECONDS=
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_THRESHOLD=

# Guardrails
MAX_INPUT_LENGTH=
MAX_OUTPUT_LENGTH=

# Observability
OTEL_ENABLED=true
OTEL_SERVICE_NAME=sustainability-agent
OTEL_EXPORTER_OTLP_ENDPOINT=

# Application
CHECKPOINT_ENABLED=true
```

Never commit real API keys.

---

# 6. Backend layers

Keep responsibilities separated.

```text
API
 ↓
Application Services
 ↓
LangGraph
 ↓
Agents / RAG / MCP
 ↓
Infrastructure
 ↓
PostgreSQL / Redis
```

The API layer should not contain agent logic.

---

# 7. Core backend modules

Recommended structure:

```text
backend/app/

api/
    routes/
        health.py
        research.py
        runs.py
        documents.py
        approvals.py
        evaluations.py

agents/
    supervisor.py
    query_agent.py
    researcher.py
    analyst.py
    critic.py
    report_agent.py

graph/
    state.py
    workflow.py
    nodes.py
    routing.py
    checkpoints.py

rag/
    ingestion.py
    loaders.py
    chunking.py
    embeddings.py
    vector_store.py
    lexical_search.py
    hybrid_search.py
    reranker.py
    query_rewriter.py
    corrective_rag.py
    citation.py
    grounding.py

guardrails/
    input.py
    output.py
    action.py
    pii.py
    injection.py

mcp/
    knowledge_server.py
    sustainability_data_server.py
    report_server.py
    client.py

cache/
    redis.py
    embedding_cache.py
    retrieval_cache.py
    semantic_cache.py
    response_cache.py

db/
    session.py
    repositories/

models/
    document.py
    chunk.py
    run.py
    event.py
    approval.py

schemas/
    research.py
    run.py
    document.py
    approval.py
    result.py

evaluation/
    ragas_runner.py
    datasets.py

observability/
    tracing.py
    metrics.py

services/
    research_service.py
    document_service.py
    approval_service.py

config/
    settings.py
```

---

# 8. Database design

Use PostgreSQL with pgvector.

## documents

```text
id
name
path
content_hash
category
topic
source_type
year
region
created_at
updated_at
```

## chunks

```text
id
document_id
chunk_index
content
embedding
metadata
created_at
```

`embedding` uses pgvector.

Metadata should support filtering.

Example:

```json
{
  "category": "emissions",
  "topic": "scope_2",
  "year": 2026,
  "region": "global"
}
```

## runs

```text
id
query
status
current_node
created_at
updated_at
completed_at
```

## events

```text
id
run_id
timestamp
event_type
agent
node
task_id
message
metadata
```

## approvals

```text
id
run_id
action
risk_level
payload
status
edited_payload
created_at
resolved_at
```

LangGraph checkpoint storage should also be persistent.

---

# 9. Document ingestion API

Endpoint:

```http
POST /api/v1/documents/ingest
```

Request:

```json
{
  "path": "knowledge/emissions/scope-2.md",
  "category": "emissions",
  "topic": "scope_2",
  "year": 2026,
  "region": "global"
}
```

Response:

```json
{
  "document_id": "doc_123",
  "status": "indexed",
  "chunks_created": 18
}
```

Ingestion flow:

```text
file
 ↓
read
 ↓
clean
 ↓
hash
 ↓
metadata
 ↓
chunk
 ↓
embedding
 ↓
pgvector
```

If the content hash already exists, do not re-embed unnecessarily.

---

# 10. Document listing API

```http
GET /api/v1/documents
```

Optional filters:

```text
category
topic
year
region
```

Response:

```json
{
  "documents": [
    {
      "id": "doc_123",
      "name": "scope-2.md",
      "category": "emissions",
      "topic": "scope_2",
      "year": 2026
    }
  ]
}
```

---

# 11. Main research API

## Start research

```http
POST /api/v1/research
```

Request:

```json
{
  "query": "How has our renewable energy target changed from 2024 to 2026?",
  "filters": {
    "category": "energy",
    "year_from": 2024,
    "year_to": 2026
  },
  "options": {
    "use_rag": true,
    "use_reranker": true,
    "use_citations": true
  }
}
```

Response:

```json
{
  "run_id": "run_123",
  "status": "queued"
}
```

The frontend uses the `run_id` for subsequent requests.

---

# 12. Run status API

```http
GET /api/v1/runs/{run_id}
```

Response:

```json
{
  "run_id": "run_123",
  "status": "running",
  "current_node": "reranker",
  "progress": {
    "completed": 4,
    "total": 7
  }
}
```

Possible statuses:

```text
queued
running
awaiting_approval
completed
failed
cancelled
```

---

# 13. Run events API

```http
GET /api/v1/runs/{run_id}/events
```

Response:

```json
{
  "events": [
    {
      "timestamp": "...",
      "type": "agent_started",
      "agent": "query_agent",
      "message": "Analyzing query"
    },
    {
      "timestamp": "...",
      "type": "retrieval",
      "agent": "researcher",
      "message": "Hybrid retrieval started"
    },
    {
      "timestamp": "...",
      "type": "mcp_call",
      "server": "knowledge",
      "tool": "search_knowledge"
    }
  ]
}
```

Polling is sufficient initially.

Do not build WebSockets/SSE until the core system works.

---

# 14. Run result API

```http
GET /api/v1/runs/{run_id}/result
```

Response:

```json
{
  "answer": "GreenTech increased its renewable electricity target from 50% in 2024 to 90% in 2026.",
  "citations": [
    {
      "document_id": "doc_2024",
      "document_name": "sustainability-strategy-2024.md",
      "chunk_id": "chunk_10",
      "section": "Renewable Energy",
      "text": "..."
    },
    {
      "document_id": "doc_2026",
      "document_name": "sustainability-strategy-2026.md",
      "chunk_id": "chunk_18",
      "section": "Energy Targets",
      "text": "..."
    }
  ],
  "grounding": {
    "status": "passed",
    "score": 0.94
  }
}
```

---

# 15. LangGraph architecture

The graph should look roughly like:

```text
START
  ↓
Input Guardrail
  ↓
Supervisor
  ↓
Query Analysis
  ↓
Query Rewriter
  ↓
Parallel Retrieval
  ├── Vector Retrieval
  └── Lexical Retrieval
  ↓
Merge
  ↓
Reranker
  ↓
Evidence Evaluator
  ↓
Generate Answer
  ↓
Grounding / Citation Check
  │
  ├── PASS → Output Guardrail → END
  │
  └── FAIL → Corrective RAG
                  ↓
              Query Rewrite
                  ↓
              Retrieval
```


---

# 16. LangGraph state

Example conceptual state:

```python
class ResearchState(TypedDict):
    run_id: str
    query: str
    rewritten_queries: list[str]

    filters: dict

    retrieval_results: list
    reranked_results: list
    evidence: list

    answer: str
    citations: list

    grounding_score: float
    grounding_passed: bool

    rag_retry_count: int

    pending_action: dict | None
    approval_result: dict | None

    events: list
```

Keep state explicit.

Do not hide important workflow state inside random global variables.

---

# 17. Hybrid retrieval

Implement two retrieval paths:

```text
Query
 ├── Vector search
 │      ↓
 │   pgvector
 │
 └── Lexical search
        ↓
      BM25
```

Then:

```text
vector results
      +
BM25 results
      ↓
deduplicate
      ↓
candidate pool
      ↓
reranker
```

Parameters:

```text
vector_top_k = 20
bm25_top_k = 20
rerank_top_k = 8
```

Keep them configurable.

---

# 18. Query rewriting

The Query Agent should return structured output.

Example:

```json
{
  "original_query": "How did our renewable energy strategy change?",
  "queries": [
    "renewable energy strategy 2024",
    "renewable electricity target 2025",
    "renewable energy target 2026"
  ],
  "filters": {
    "category": "energy",
    "year_from": 2024,
    "year_to": 2026
  }
}
```

Use a schema rather than parsing arbitrary LLM text.

---

# 19. Reranking

The retrieval pipeline:

```text
40 candidates
     ↓
reranker
     ↓
8 strongest chunks
     ↓
Gemini
```

Do not send all retrieval candidates to the LLM.

Record:

```text
retrieval_count
rerank_count
selected_count
```

for observability.

---

# 20. Corrective RAG

The system must not blindly accept every generated answer.

Flow:

```text
Generate
  ↓
Grounding evaluator
  ↓
Is every important claim supported?
  ├── yes → continue
  └── no
       ↓
   rewrite query
       ↓
   retrieve again
       ↓
   rerank
       ↓
   generate
```

Maximum retries:

```text
MAX_RAG_RETRIES=2
```

If still unsuccessful:

```text
"I could not find enough evidence in the knowledge base to answer reliably."
```

Do not fabricate evidence.

---

# 21. Citations

Every factual answer should preserve evidence references.

A citation object:

```json
{
  "document_id": "...",
  "document_name": "...",
  "chunk_id": "...",
  "section": "...",
  "relevance_score": 0.91
}
```

The frontend should make citations clickable/expandable.

---

# 22. Guardrails

Implement three levels.

## Input

Check:

```text
maximum length
prompt injection
PII
malformed requests
```

Example:

```text
User input
 ↓
Input Guardrail
 ↓
safe → graph
unsafe → reject
```

## Output

Check:

```text
schema
grounding
citations
unsafe content
```

## Action

Risk tiers:

```text
LOW
    read/search
    automatic

MEDIUM
    create/save report
    approval recommended

HIGH
    publish/send/delete/external side effect
    mandatory HITL
```

---

# 23. MCP servers

Use at least 2–3 MCP servers.

## Knowledge MCP

Tools:

```text
search_knowledge()
get_document()
list_documents()
```

## Sustainability Data MCP

Initially use deterministic mock data.

Tools:

```text
get_emissions_data()
get_energy_data()
get_water_data()
```

Example:

```json
{
  "year": 2026,
  "energy_consumption_mwh": 12000,
  "renewable_percentage": 90
}
```

## Report MCP

Tools:

```text
create_report()
save_report()
```

The report action should demonstrate risk-tiered gating and HITL.

---

# 24. HITL API

When LangGraph calls:

```python
interrupt(...)
```

the run becomes:

```text
awaiting_approval
```

Frontend:

```http
GET /api/v1/runs/{run_id}/approval
```

Response:

```json
{
  "approval_id": "approval_123",
  "action": "save_report",
  "risk_level": "MEDIUM",
  "payload": {
    "filename": "sustainability-report.md"
  },
  "options": [
    "approve",
    "edit",
    "reject"
  ]
}
```

Submit:

```http
POST /api/v1/runs/{run_id}/approval
```

Request:

```json
{
  "approval_id": "approval_123",
  "decision": "approve",
  "edited_payload": null
}
```

For edit:

```json
{
  "approval_id": "approval_123",
  "decision": "edit",
  "edited_payload": {
    "filename": "final-sustainability-report.md"
  }
}
```

The backend resumes the same checkpointed graph.

---

# 25. Redis caching

Use Redis for multiple cache layers.

## Embedding cache

Key:

```text
embedding:{content_hash}
```

Value:

```text
embedding vector
```

Avoid re-embedding unchanged text.

## Retrieval cache

Key should include normalized query + filters:

```text
retrieval:{hash(query + filters)}
```

Value:

```text
retrieval candidates
```

## Response cache

Key:

```text
response:{hash(normalized_query + filters + relevant_version)}
```

Value:

```text
final structured response
```

Be careful with invalidation when documents change.

---

# 26. Semantic cache

Add a semantic cache for repeated or near-duplicate questions.

Example:

```text
"What is our renewable energy target?"
```

and:

```text
"How much renewable electricity are we targeting?"
```

may be semantically similar.

Flow:

```text
User query
   ↓
query embedding
   ↓
semantic cache search
   ↓
similar cached query?
   ├── yes + similarity >= threshold
   │       ↓
   │   return cached result
   │
   └── no
           ↓
        full RAG
```

Important:

Do not return cached answers blindly.

The semantic cache key should account for:

```text
query
metadata filters
knowledge-base version
model/version if relevant
```

Use a conservative threshold initially.

Example configuration:

```env
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_THRESHOLD=0.92
```

The exact threshold should be tuned experimentally.

---

# 27. Cache architecture

Overall:

```text
                   Query
                     │
                     ▼
              Semantic Cache
               /          \
            HIT            MISS
             │              │
             ▼              ▼
          Answer        Query Rewrite
                            │
                            ▼
                       Retrieval Cache
                            │
                            ▼
                         RAG
                            │
                            ▼
                       Gemini
                            │
                            ▼
                      Response Cache
```

Embedding cache happens during ingestion/query embedding.

---

# 28. OpenTelemetry

Trace the complete request.

At minimum create spans for:

```text
HTTP request
LangGraph run
agent invocation
query rewrite
embedding
vector retrieval
BM25 retrieval
hybrid merge
reranking
Gemini call
grounding evaluation
MCP call
cache lookup
cache hit/miss
HITL interruption
```

Useful attributes:

```text
run_id
agent
node
model
latency_ms
token_usage
cache_hit
retrieval_count
rerank_count
rag_retry_count
```

Do not log secrets or raw PII.

---

# 29. RAGAS

Create an evaluation dataset.

Example:

```json
{
  "question": "What was the renewable energy target in 2024?",
  "ground_truth": "50%",
  "expected_documents": [
    "sustainability-strategy-2024.md"
  ]
}
```

Start with 20–30 questions.

Eventually target 50+.

Measure:

```text
faithfulness
answer relevance
context relevance
context recall
```

Run evaluations after changing:

```text
chunk size
chunk overlap
retrieval top-k
reranker
query rewriting
prompt
model
```

Keep results so you can compare versions.

---

# 30. Frontend

Keep the frontend minimal.

```text
frontend/src/

api/
    client.ts
    research.ts
    documents.ts
    runs.ts
    approvals.ts

components/
    QueryForm.tsx
    RunStatus.tsx
    WorkflowTimeline.tsx
    RetrievalPanel.tsx
    EvidencePanel.tsx
    AgentActivity.tsx
    MCPActivity.tsx
    ApprovalPanel.tsx
    ResultView.tsx
    CachePanel.tsx

pages/
    ResearchPage.tsx
```

One primary page is enough.

---

# 31. Frontend screen

The final UI should roughly contain:

```text
┌────────────────────────────────────────────────────────────┐
│ 🌱 Sustainability Intelligence                             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Ask a sustainability question                              │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ How did renewable energy targets change from 2024-26? │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ Filters:                                                   │
│ Category [Energy]  Year [2024] → [2026]                   │
│                                                            │
│                     [ Ask ]                               │
├────────────────────────────────────────────────────────────┤
│ RUN run_123                     ● RUNNING                   │
│                                                            │
│ ✓ Input Guardrail                                          │
│ ✓ Supervisor                                               │
│ ✓ Query Rewrite                                            │
│ ● Hybrid Retrieval                                         │
│ ○ Reranking                                                │
│ ○ Generation                                               │
│ ○ Grounding                                                │
├────────────────────────────────────────────────────────────┤
│ RETRIEVAL                                                  │
│                                                            │
│ Vector Search             20 candidates                    │
│ BM25                      20 candidates                    │
│ Reranked                  8 chunks                         │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ EVIDENCE                                                   │
│                                                            │
│ 📄 sustainability-strategy-2024.md                         │
│ 📄 sustainability-strategy-2025.md                         │
│ 📄 sustainability-strategy-2026.md                         │
├────────────────────────────────────────────────────────────┤
│ AGENT ACTIVITY                                             │
│                                                            │
│ Supervisor → Query Agent                                   │
│ Query Agent → Knowledge MCP                                │
│ Researcher → Hybrid Retrieval                              │
│ Researcher → Reranker                                      │
│ Critic → Grounding check                                   │
├────────────────────────────────────────────────────────────┤
│ CACHE                                                      │
│                                                            │
│ Semantic cache: MISS                                       │
│ Embedding cache: HIT                                       │
│ Retrieval cache: MISS                                      │
├────────────────────────────────────────────────────────────┤
│ RESULT                                                     │
│                                                            │
│ GreenTech increased its renewable electricity target       │
│ from 50% in 2024 to 90% in 2026.                           │
│                                                            │
│ [1] 2024 strategy   [2] 2026 strategy                     │
│                                                            │
│ Grounding: ✓ PASSED                                       │
└────────────────────────────────────────────────────────────┘
```

---

# 32. Approval UI

When a risky action occurs:

```text
┌────────────────────────────────────────────────────────────┐
│ ⚠ HUMAN APPROVAL REQUIRED                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Action: Save sustainability report                          │
│ Risk: MEDIUM                                               │
│                                                            │
│ Filename                                                   │
│ [ sustainability-report.md______________________________ ] │
│                                                            │
│ [ Reject ]       [ Edit & Approve ]       [ Approve ]      │
└────────────────────────────────────────────────────────────┘
```

This must be driven by backend state, not frontend assumptions.

---

# 33. Final answer contract

The backend should return structured data.

Conceptually:

```json
{
  "answer": "...",
  "citations": [],
  "retrieval": {
    "vector_count": 20,
    "lexical_count": 20,
    "reranked_count": 8
  },
  "grounding": {
    "passed": true,
    "score": 0.94
  },
  "cache": {
    "semantic_hit": false,
    "embedding_hit": true,
    "retrieval_hit": false,
    "response_hit": false
  },
  "metadata": {
    "rag_retries": 0,
    "model": "..."
  }
}
```

This allows the frontend to remain simple.

---

# 34. Important API relationships

The main lifecycle:

```text
POST /research
       │
       ▼
    run_id
       │
       ├───────────────┐
       ▼               ▼
GET /runs/{id}    GET /runs/{id}/events
       │
       │
       ├── status=running
       │
       ├── status=awaiting_approval
       │              │
       │              ▼
       │       GET /approval
       │              │
       │              ▼
       │       POST /approval
       │              │
       │              ▼
       │        graph resumes
       │
       └── status=completed
                      │
                      ▼
             GET /result
```

Document lifecycle:

```text
POST /documents/ingest
        ↓
parse
        ↓
chunk
        ↓
embed
        ↓
pgvector
        ↓
available to RAG
```

---

# 35. Error handling

Every API should return predictable errors.

Example:

```json
{
  "error": {
    "code": "RUN_NOT_FOUND",
    "message": "Run does not exist"
  }
}
```

Useful error codes:

```text
INVALID_REQUEST
INPUT_GUARDRAIL_FAILED
RUN_NOT_FOUND
DOCUMENT_NOT_FOUND
INGESTION_FAILED
RETRIEVAL_FAILED
LLM_FAILED
MCP_FAILED
GROUNDING_FAILED
APPROVAL_NOT_FOUND
APPROVAL_REQUIRED
RUN_FAILED
```

Do not expose stack traces to the frontend.

Log detailed errors server-side.


---


# 36. Final architecture target

```text
                         ┌─────────────┐
                         │   React     │
                         └──────┬──────┘
                                │
                              REST
                                │
                         ┌──────▼──────┐
                         │   FastAPI   │
                         └──────┬──────┘
                                │
                    ┌───────────▼───────────┐
                    │      LangGraph        │
                    │                       │
                    │ Supervisor            │
                    │ Query Agent            │
                    │ Researcher             │
                    │ Analyst                │
                    │ Critic                │
                    │ Report Agent           │
                    └───────┬───────┬───────┘
                            │       │
                    ┌───────▼───┐ ┌─▼────────────┐
                    │    RAG    │ │     MCP      │
                    │           │ │              │
                    │ Rewrite   │ │ Knowledge    │
                    │ Hybrid    │ │ Data         │
                    │ Rerank    │ │ Report       │
                    │ Ground    │ │              │
                    └─────┬─────┘ └──────────────┘
                          │
                 ┌────────▼─────────┐
                 │    PostgreSQL    │
                 │    + pgvector    │
                 └──────────────────┘

                 ┌──────────────────┐
                 │      Redis       │
                 │                  │
                 │ embedding cache  │
                 │ retrieval cache  │
                 │ response cache   │
                 │ semantic cache   │
                 └──────────────────┘

                 ┌──────────────────┐
                 │ OpenTelemetry    │
                 └──────────────────┘

                 ┌──────────────────┐
                 │      RAGAS       │
                 └──────────────────┘
```
