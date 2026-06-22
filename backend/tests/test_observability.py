"""Tests for the observability layer: JSON log formatter, correlation context,
and the correlation/telemetry middleware. Covers happy, failure, boundary,
idempotency.
"""
import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.correlation import (  # noqa: E402
    get_correlation_id, new_correlation_id, set_correlation_id, reset_correlation_id,
)
from app.observability import (  # noqa: E402
    JsonLogFormatter, configure_logging, CorrelationIdMiddleware, CORRELATION_HEADER,
)


def _record(msg="event_x", **extra):
    rec = logging.LogRecord(name="app.x", level=logging.INFO, pathname=__file__,
                            lineno=1, msg=msg, args=(), exc_info=None)
    for k, v in extra.items():
        setattr(rec, k, v)
    return rec


# --- correlation context ---

def test_correlation_set_get_reset():
    assert get_correlation_id() is None  # boundary: unset
    token = set_correlation_id("abc")
    assert get_correlation_id() == "abc"
    reset_correlation_id(token)
    assert get_correlation_id() is None


def test_new_correlation_id_unique():
    a, b = new_correlation_id(), new_correlation_id()
    assert a != b and len(a) == 32 and a.isalnum()


# --- formatter: happy path ---

def test_formatter_required_fields_and_extras():
    out = json.loads(JsonLogFormatter().format(_record("hello", provider="openai", attempt=2)))
    assert out["event"] == "hello" and out["level"] == "INFO" and out["module"] == "app.x"
    assert "timestamp" in out and "correlation_id" in out
    assert out["provider"] == "openai" and out["attempt"] == 2


def test_formatter_includes_bound_correlation_id():
    token = set_correlation_id("cid-123")
    try:
        out = json.loads(JsonLogFormatter().format(_record()))
        assert out["correlation_id"] == "cid-123"
    finally:
        reset_correlation_id(token)


def test_formatter_no_correlation_is_null():  # boundary
    out = json.loads(JsonLogFormatter().format(_record()))
    assert out["correlation_id"] is None


# --- formatter: failure path (exception) ---

def test_formatter_captures_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        rec = logging.LogRecord("app.x", logging.ERROR, __file__, 1, "failed", (), sys.exc_info())
    out = json.loads(JsonLogFormatter().format(rec))
    assert out["error_class"] == "ValueError" and "boom" in out["exc_info"]


def test_formatter_output_is_valid_json_for_nonserializable():  # boundary
    out = JsonLogFormatter().format(_record(obj=object()))
    json.loads(out)  # must not raise (default=str fallback)


# --- configure_logging: idempotency ---

def test_configure_logging_idempotent():
    root = logging.getLogger()
    saved = list(root.handlers)
    saved_level = root.level
    try:
        configure_logging(logging.INFO)
        configure_logging(logging.INFO)
        json_handlers = [h for h in root.handlers if h.get_name() == "json_stdout"]
        assert len(json_handlers) == 1  # no duplicate handlers
    finally:
        for h in list(root.handlers):
            root.removeHandler(h)
        for h in saved:
            root.addHandler(h)
        root.setLevel(saved_level)


# --- middleware integration ---

def _client():
    fastapi = pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    app = fastapi.FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/x")
    async def x():
        return {"cid": get_correlation_id()}

    @app.get("/boom")
    async def boom():
        raise RuntimeError("kaboom")

    return TestClient(app, raise_server_exceptions=False)


def test_middleware_generates_and_binds_correlation_id():
    r = _client().get("/x")
    assert r.status_code == 200
    cid = r.headers.get(CORRELATION_HEADER)
    assert cid and r.json()["cid"] == cid  # bound for the whole request


def test_middleware_echoes_supplied_correlation_id():
    r = _client().get("/x", headers={CORRELATION_HEADER: "supplied-123"})
    assert r.headers.get(CORRELATION_HEADER) == "supplied-123"
    assert r.json()["cid"] == "supplied-123"


def test_middleware_context_cleared_after_request():  # idempotency / no leak
    _client().get("/x")
    assert get_correlation_id() is None
