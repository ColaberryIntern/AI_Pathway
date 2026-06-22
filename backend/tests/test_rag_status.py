"""Tests for RAG availability reporting (Observability for the Semantic layer).

Verifies the no-op fallback is no longer silent: get_rag_status() reports whether
RAG actually initialized and why not, the rag_enabled switch gives an explicit
no-op, and the no-op retriever degrades safely. Four mandatory types covered.
No real Vertex: RAGRetriever construction is controlled via monkeypatch.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app.services.rag.retriever as rr  # noqa: E402


def _setup(monkeypatch, rag_enabled=True, raises=False):
    monkeypatch.setattr(rr, "_retriever_instance", None)
    monkeypatch.setattr(rr, "_rag_unavailable_reason", None)
    monkeypatch.setattr("app.config.get_settings",
                        lambda: type("S", (), {"rag_enabled": rag_enabled})())

    class FakeRAG:
        def __init__(self):
            if raises:
                raise RuntimeError("vertex ADC missing")

    monkeypatch.setattr(rr, "RAGRetriever", FakeRAG)


# --- happy path: RAG initializes ---

def test_status_available_when_init_succeeds(monkeypatch):
    _setup(monkeypatch, rag_enabled=True, raises=False)
    status = rr.get_rag_status()
    assert status["available"] is True
    assert status["reason"] is None
    assert status["retriever"] != "_NoOpRetriever"


# --- failure path: init raises (the real-world ADC-missing case) ---

def test_status_degraded_with_reason_when_init_fails(monkeypatch):
    _setup(monkeypatch, rag_enabled=True, raises=True)
    status = rr.get_rag_status()
    assert status["available"] is False
    assert status["retriever"] == "_NoOpRetriever"
    assert "RuntimeError" in status["reason"] and "ADC" in status["reason"]


# --- explicit "remove": disabled by config ---

def test_status_disabled_by_config(monkeypatch):
    _setup(monkeypatch, rag_enabled=False)
    status = rr.get_rag_status()
    assert status["available"] is False
    assert "disabled by config" in status["reason"]


# --- boundary: the no-op retriever degrades safely (returns []) ---

def test_noop_retriever_returns_empty():
    noop = rr._NoOpRetriever()
    assert asyncio.run(noop.retrieve_skills("q")) == []
    assert asyncio.run(noop.retrieve_learning_content("SK.A", "Tech")) == []
    assert asyncio.run(noop.retrieve_similar_paths("summary")) == []


# --- idempotency: status is stable across calls (singleton cached) ---

def test_status_idempotent(monkeypatch):
    _setup(monkeypatch, rag_enabled=True, raises=True)
    assert rr.get_rag_status() == rr.get_rag_status()
