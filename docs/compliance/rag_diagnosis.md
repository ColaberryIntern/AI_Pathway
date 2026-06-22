# RAG (Vertex) auth diagnosis + fix plan (Phase 2, item 10)

**Symptom:** the Semantic/Intelligence layers run on a no-op fallback - all RAG
retrieval returns `[]`, so `content_curator` and any retrieval-augmented agent get
no real context.

## Root cause (traced)

```
RAGRetriever.__init__
  -> get_vector_store()                       # vector_store.py
       -> VectorStore.__init__
            -> get_embedding_service()        # embeddings.py
                 -> EmbeddingService.__init__
                      -> vertexai.init(project, region)          # supplies PROJECT only
                      -> TextEmbeddingModel.from_pretrained("text-embedding-004")
```

`vertexai.init(...)` sets the project/region but does **not** supply credentials - it
relies on Google **Application Default Credentials (ADC)**. In an environment without
ADC (no `GOOGLE_APPLICATION_CREDENTIALS` service-account key, no workload identity,
no `gcloud auth application-default login`), the embedding call raises an auth error.

`get_retriever()` catches that and installs `_NoOpRetriever` - **silently** (one
WARNING line, then every retrieval returns `[]` forever). That silent, permanent
capability loss is the compliance gap (Observability + Contextual).

Compounding factor: `main.py`'s lifespan only loads the ontology into the vector
store when `GOOGLE_APPLICATION_CREDENTIALS` **or** `GOOGLE_CLOUD_PROJECT` is set. If
ADC is provided another way (workload identity) those vars may be unset, so RAG could
authenticate yet still query empty collections because the ontology was never loaded.

## Fix paths

### A. Make it real (NEEDS GCP CREDENTIALS - owner/infra action)
1. Provide ADC to the backend container: mount a service-account key and set
   `GOOGLE_APPLICATION_CREDENTIALS`, or attach a workload identity with Vertex AI
   User on project `ai-pathway-486221`.
2. Load the ontology into the vector store at startup whenever RAG is available
   (decouple the load gate from the specific env-var check; key it off real RAG
   availability instead).
3. Verify with the new `get_rag_status()` health probe (below) reporting
   `available: true`, then confirm `content_curator` returns non-empty resources.
   **Verification requires the credentials**, so it cannot be done from this repo
   checkout alone.

### B. Decouple the embedding provider (STRATEGIC - escalate, do NOT do autonomously)
Swap Vertex `text-embedding-004` for a credential-free embedding (ChromaDB's default
local model, or OpenAI embeddings) so RAG works without GCP. This is an **AI
model-class change** per the Autonomy Model and changes retrieval semantics, so it is
a Strategic Decision that must be escalated, not taken autonomously.

### C. Cred-free hardening shipped in this PR (Observability + explicit control)
Even without credentials, the silent-degradation half of the gap is closed:
- `get_retriever()` now **captures the init failure** (error_class + message) instead
  of discarding it, and logs it as a structured event.
- `get_rag_status()` reports `{available, retriever, reason}` so callers/ops can see
  RAG is degraded and why.
- `/health` now includes a `rag` block, so degradation is visible on every health
  check instead of hidden.
- `settings.rag_enabled` makes the no-op an **explicit, intentional** choice ("remove"
  cleanly) rather than an accidental side effect of a missing credential.

## Recommendation
Ship C now (done). Do A when credentials are provisioned - it is the only path that
makes retrieval real, and it is an infra/credentials task the owner must drive.
Escalate B separately if running RAG without GCP is desired.
