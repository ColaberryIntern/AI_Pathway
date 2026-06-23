"""Trust Before Intelligence (TBI) status + dashboard.

Aggregates the trust signals this system was instrumented with into one view:
INPACT scorecard, the 7-layer health grid, and GOALS (Governance, Observability,
Availability, Lexicon, Solid). Recorded signals (INPACT scores, last drift result,
test count, layer annotations) come from app/data/tbi_status.json; live signals
(metrics, RAG availability, gate config) are merged at request time.

build_tbi_status() -> dict      (the /tbi JSON)
render_dashboard_html(status)   (the self-contained /tbi/dashboard page)
"""
from __future__ import annotations

import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[1] / "data" / "tbi_status.json"


def build_tbi_status(trends: dict | None = None) -> dict:
    recorded = json.loads(_DATA.read_text(encoding="utf-8"))

    from app.config import get_settings
    s = get_settings()
    governance = {
        "gate_enabled": s.judge_gate_enabled,
        "gate_mode": s.judge_gate_mode,
        "judge_model": s.judge_model,
        "ensemble_k": s.judge_ensemble_k,
    }
    try:
        from app.metrics import snapshot
        observability = snapshot()
    except Exception as e:  # never let one signal break the view
        observability = {"error": str(e)}
    try:
        from app.services.rag.retriever import get_rag_status
        rag = get_rag_status()
    except Exception as e:
        rag = {"available": False, "reason": str(e)}

    return {
        "framework": "Trust Before Intelligence",
        "as_of": recorded.get("as_of"),
        "inpact": recorded.get("inpact", {}),
        "layers": recorded.get("layers", []),
        "goals": {
            "governance": governance,
            "observability": observability,
            "availability": {"status": "healthy", "rag": rag},
            "lexicon": recorded.get("goals_recorded", {}).get("lexicon", {}),
            "solid": recorded.get("goals_recorded", {}).get("solid", {}),
        },
        "trends": trends or {},
    }


# --- HTML dashboard (self-contained, no external assets/CDN) ---

_CSS = """
<style>
  :root { --navy:#1a365d; --blue:#2b6cb0; --green:#38a169; --amber:#d69e2e;
          --red:#e53e3e; --bg:#f7fafc; --card:#fff; --border:#e2e8f0; --text:#2d3748; --muted:#718096; }
  * { box-sizing:border-box; }
  body { font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         background:var(--bg); color:var(--text); margin:0; padding:32px; }
  .wrap { max-width:980px; margin:0 auto; }
  h1 { color:var(--navy); font-size:24px; margin:0 0 4px; }
  .sub { color:var(--muted); font-size:13px; margin-bottom:24px; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:10px;
          padding:20px 22px; margin-bottom:20px; box-shadow:0 1px 2px rgba(0,0,0,.04); }
  .card h2 { color:var(--navy); font-size:15px; text-transform:uppercase; letter-spacing:.04em;
             margin:0 0 16px; }
  .score-head { display:flex; align-items:baseline; gap:12px; margin-bottom:16px; }
  .score-big { font-size:40px; font-weight:700; color:var(--navy); }
  .score-line { font-size:13px; color:var(--muted); }
  .dim { margin-bottom:12px; }
  .dim-top { display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px; }
  .dim-name { font-weight:600; }
  .track { background:#edf2f7; border-radius:6px; height:10px; overflow:hidden; }
  .fill { height:100%; border-radius:6px; }
  .dim-basis { font-size:11px; color:var(--muted); margin-top:3px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }
  .tile { border:1px solid var(--border); border-radius:8px; padding:12px 14px; }
  .tile .k { font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }
  .tile .v { font-size:13px; margin-top:4px; }
  .pill { display:inline-block; padding:1px 8px; border-radius:999px; font-size:11px; font-weight:600; }
  .ok { background:#f0fff4; color:var(--green); } .degraded { background:#fffaf0; color:var(--amber); }
  .bad { background:#fff5f5; color:var(--red); }
  table { width:100%; border-collapse:collapse; font-size:12px; }
  th,td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--border); }
  th { color:var(--muted); font-weight:600; text-transform:uppercase; font-size:10px; letter-spacing:.04em; }
  .foot { color:var(--muted); font-size:11px; margin-top:8px; }
</style>
"""


def _color(score: int) -> str:
    return "var(--green)" if score >= 5 else ("var(--amber)" if score >= 3 else "var(--red)")


def _status_pill(status: str) -> str:
    cls = {"ok": "ok", "degraded": "degraded"}.get(status, "bad")
    return f'<span class="pill {cls}">{status}</span>'


_SPARK = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float], lo: float = 0.0, hi: float = 1.0) -> str:
    """Render a list of 0..1 values as unicode block sparkline chars."""
    if not values:
        return ""
    span = (hi - lo) or 1.0
    out = []
    for v in values:
        idx = int(round((max(lo, min(hi, v)) - lo) / span * (len(_SPARK) - 1)))
        out.append(_SPARK[idx])
    return "".join(out)


def render_dashboard_html(status: dict) -> str:
    inpact = status.get("inpact", {})
    maxp = inpact.get("max_per", 6)
    dims = inpact.get("dimensions", [])
    dim_html = ""
    for d in dims:
        pct = round(d["score"] / maxp * 100)
        dim_html += (
            f'<div class="dim"><div class="dim-top">'
            f'<span class="dim-name">{d["name"]}</span><span>{d["score"]}/{maxp}</span></div>'
            f'<div class="track"><div class="fill" style="width:{pct}%;background:{_color(d["score"])}"></div></div>'
            f'<div class="dim-basis">{d.get("basis","")}</div></div>'
        )

    g = status.get("goals", {})
    gov = g.get("governance", {})
    avail = g.get("availability", {})
    rag = avail.get("rag", {})
    lex = g.get("lexicon", {})
    solid = g.get("solid", {})
    rag_pill = _status_pill("ok" if rag.get("available") else "degraded")
    tiles = (
        f'<div class="tile"><div class="k">Governance</div><div class="v">gate '
        f'<b>{"on" if gov.get("gate_enabled") else "off"}</b> / {gov.get("gate_mode","?")}<br>'
        f'judge {gov.get("judge_model","?")} &middot; ensemble k={gov.get("ensemble_k","?")}</div></div>'
        f'<div class="tile"><div class="k">Availability</div><div class="v">api <span class="pill ok">healthy</span><br>'
        f'RAG {rag_pill}</div></div>'
        f'<div class="tile"><div class="k">Lexicon (judge calibration)</div><div class="v">'
        f'{lex.get("result","?")} &middot; drift {lex.get("role_fit_drift","?")}<br>'
        f'<span class="dim-basis">last check {lex.get("last_drift_check","?")}</span></div></div>'
        f'<div class="tile"><div class="k">Solid (tests)</div><div class="v">'
        f'{solid.get("tests_passing","?")} passing &middot; {solid.get("golden_cases","?")} golden</div></div>'
    )

    obs = g.get("observability", {})
    if obs and "error" not in obs:
        rows = ""
        for cat, m in obs.items():
            lat = m.get("latency_ms", {})
            rows += (
                f'<tr><td>{cat}</td><td>{m.get("count",0)}</td>'
                f'<td>{round(m.get("success_rate",0)*100)}%</td>'
                f'<td>{m.get("retry_count",0)}</td>'
                f'<td>{lat.get("p50","-")}/{lat.get("p95","-")}/{lat.get("p99","-")}</td></tr>'
            )
        obs_html = (
            '<table><tr><th>category</th><th>count</th><th>success</th><th>retries</th>'
            '<th>latency p50/p95/p99 (ms)</th></tr>' + (rows or
            '<tr><td colspan="5" class="foot">no traffic in the rolling window yet</td></tr>') + '</table>'
        )
    else:
        obs_html = '<div class="foot">metrics unavailable</div>'

    trends = status.get("trends", {}) or {}
    if trends:
        trows = ""
        for cat, series in trends.items():
            srates = [p.get("success_rate", 0.0) for p in series]
            spark = _sparkline(srates)
            latest = series[-1] if series else {}
            trows += (
                f'<tr><td>{cat}</td><td style="font-family:monospace;font-size:15px">{spark}</td>'
                f'<td>{round((latest.get("success_rate") or 0) * 100)}%</td>'
                f'<td>{latest.get("p95","-")}</td><td>{len(series)}</td></tr>'
            )
        trends_html = (
            '<table><tr><th>category</th><th>success-rate trend</th><th>latest</th>'
            '<th>latest p95 (ms)</th><th>samples</th></tr>' + trows + '</table>'
        )
    else:
        trends_html = ('<div class="foot">No persisted history yet - the background '
                       'task records a sample every few minutes once there is traffic.</div>')

    layers_html = ""
    for ly in status.get("layers", []):
        layers_html += (
            f'<tr><td><b>{ly["layer"]}</b></td><td>{_status_pill(ly.get("status","?"))}</td>'
            f'<td>{ly.get("note","")}</td></tr>'
        )

    pct = inpact.get("pct", 0)
    line = inpact.get("production_line", 80)
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Trust Before Intelligence - System Status</title>" + _CSS + "</head><body><div class='wrap'>"
        "<h1>Trust Before Intelligence &mdash; System Status</h1>"
        f"<div class='sub'>AI Pathway &middot; as of {status.get('as_of','?')} &middot; live signals refresh on load</div>"
        "<div class='card'><h2>INPACT readiness</h2>"
        f"<div class='score-head'><span class='score-big'>{pct}%</span>"
        f"<span class='score-line'>{inpact.get('total','?')}/{inpact.get('max','?')} &middot; "
        f"production line {line}% &middot; {'ABOVE' if pct>=line else 'below'} the line</span></div>"
        + dim_html + "</div>"
        "<div class='card'><h2>GOALS</h2><div class='grid'>" + tiles + "</div></div>"
        "<div class='card'><h2>Observability (rolling 24h)</h2>" + obs_html + "</div>"
        "<div class='card'><h2>Trends (persisted history)</h2>" + trends_html + "</div>"
        "<div class='card'><h2>7-layer architecture</h2><table>"
        "<tr><th>layer</th><th>status</th><th>note</th></tr>" + layers_html + "</table></div>"
        "<div class='foot'>INPACT scores + layer status are recorded (app/data/tbi_status.json); "
        "Governance, Availability and Observability tiles are live. Refresh after a redeploy or a "
        "judge_drift_check / pytest run to update the recorded signals.</div>"
        "</div></body></html>"
    )
