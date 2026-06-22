"""Structured logging + request telemetry (Trust Before Intelligence - Observability).

- JsonLogFormatter: one JSON event per line to stdout, with the required fields
  (timestamp, level, event, correlation_id, module) plus any structured `extra`
  fields a caller attached. Logs-as-event-streams per the 12-factor adaptation.
- configure_logging(): installs the JSON formatter on the root logger.
- CorrelationIdMiddleware: generates (or accepts via X-Correlation-ID) a correlation
  id at request entry, binds it to the context for every downstream log line,
  returns it in the response header, and emits one http_request telemetry line
  (method, path, status_code, duration_ms) per request - including on error.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app import metrics
from app.correlation import (
    get_correlation_id,
    new_correlation_id,
    reset_correlation_id,
    set_correlation_id,
)

CORRELATION_HEADER = "X-Correlation-ID"

# LogRecord attributes that are NOT custom `extra` fields.
_RESERVED = set(vars(logging.makeLogRecord({}))) | {"taskName"}


class JsonLogFormatter(logging.Formatter):
    """Render a LogRecord as a single JSON line with the required fields + extras."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            "module": record.name,
            "correlation_id": get_correlation_id(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["error_class"] = record.exc_info[0].__name__ if record.exc_info[0] else None
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: int | str = logging.INFO) -> None:
    """Install the JSON formatter on the root logger (idempotent)."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    handler.set_name("json_stdout")
    root = logging.getLogger()
    # Replace any prior handlers so we don't double-log in plain + JSON.
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(level)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Bind a correlation id per request and emit one telemetry line per request."""

    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get(CORRELATION_HEADER) or new_correlation_id()
        token = set_correlation_id(cid)
        logger = logging.getLogger("request")
        started = time.monotonic()
        try:
            try:
                response = await call_next(request)
            except Exception as exc:
                # Log with the correlation id still bound (finally resets it last).
                dur = round((time.monotonic() - started) * 1000, 1)
                logger.exception(
                    "http_request",
                    extra={"method": request.method, "path": request.url.path,
                           "status_code": 500, "status": "error", "duration_ms": dur},
                )
                metrics.record("http_request", "failure", dur, type(exc).__name__)
                raise
            response.headers[CORRELATION_HEADER] = cid
            dur = round((time.monotonic() - started) * 1000, 1)
            status = "success" if response.status_code < 500 else "failure"
            logger.info(
                "http_request",
                extra={"method": request.method, "path": request.url.path,
                       "status_code": response.status_code, "status": status,
                       "duration_ms": dur},
            )
            metrics.record("http_request", status, dur,
                           None if status == "success" else f"HTTP_{response.status_code}")
            return response
        finally:
            reset_correlation_id(token)
