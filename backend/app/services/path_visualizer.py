"""Path Visualizer — generates a standalone HTML report.

Given a completed analysis result, produces a self-contained HTML page
showing the user profile, top-10 skill breakdowns (current vs target),
gap analysis, and an interactive ontology path chart (D3.js).

The HTML is entirely self-contained (inline CSS/JS, CDN D3) so it can
be opened in any browser for verification.
"""

from __future__ import annotations

import html
import json
from typing import Any

from app.services.ontology import OntologyService, get_ontology_service


class PathVisualizer:
    """Generate standalone HTML visualizations of learning paths."""

    def __init__(self, ontology_service: OntologyService | None = None) -> None:
        self._ontology = ontology_service or get_ontology_service()

    def generate_html(self, analysis_result: dict[str, Any]) -> str:
        """Generate a complete HTML page from an analysis result dict.

        Parameters
        ----------
        analysis_result : dict
            The ``result`` field from the orchestrator output, containing
            ``profile_analysis``, ``jd_parsing``, ``gap_analysis``,
            ``learning_path``, ``top_10_current_skills``,
            ``top_10_target_skills``, and ``summary``.

        Returns
        -------
        str
            Self-contained HTML string.
        """
        summary = analysis_result.get("summary", {})
        top10_current = analysis_result.get("top_10_current_skills", [])
        top10_target = analysis_result.get("top_10_target_skills", [])
        top10_gaps = analysis_result.get("top_10_skill_gaps", [])
        gaps = analysis_result.get("gap_analysis", {}).get("gaps", [])
        chapters = analysis_result.get("learning_path", {}).get("chapters", [])
        profile_analysis = analysis_result.get("profile_analysis", {})
        journey_roadmap = analysis_result.get("journey_roadmap", {})
        all_skill_gaps = analysis_result.get("all_skill_gaps", [])
        full_journey = analysis_result.get("full_journey_estimate", {})

        # Build graph data for D3
        graph_data = self._build_graph_data(
            top10_current, top10_target, gaps, chapters, top10_gaps,
        )

        return self._render_html(
            summary=summary,
            top10_current=top10_current,
            top10_target=top10_target,
            gaps=gaps,
            chapters=chapters,
            profile_summary=profile_analysis.get("profile_summary", ""),
            graph_data=graph_data,
            journey_roadmap=journey_roadmap,
            top10_gaps=top10_gaps,
            all_skill_gaps=all_skill_gaps,
            full_journey=full_journey,
        )

    # ------------------------------------------------------------------
    # Graph data builder
    # ------------------------------------------------------------------

    def _build_graph_data(
        self,
        top10_current: list[dict],
        top10_target: list[dict],
        gaps: list[dict],
        chapters: list[dict],
        top10_gaps: list[dict] | None = None,
    ) -> dict:
        """Build nodes & links for the D3 ontology path chart."""
        domains = self._ontology.domains
        layers = self._ontology.layers

        # Collect skill IDs by role
        current_skill_ids = {s["skill_id"] for s in top10_current}
        target_skill_ids = {s["skill_id"] for s in top10_target}
        gap_skill_ids = {g["skill_id"] for g in gaps}
        chapter_skill_ids = {
            ch.get("skill_id") or ch.get("primary_skill_id", "")
            for ch in chapters
        }
        # Remaining: skills in top-10 gaps but not in this path
        remaining_skill_ids = {
            g["skill_id"] for g in (top10_gaps or [])
            if g.get("gap", 0) > 0
            and g["skill_id"] not in chapter_skill_ids
        }

        # Build layer color map
        layer_colors: dict[str, str] = {}
        for layer in layers:
            layer_colors[layer["id"]] = layer.get("color", "#6b7280")

        # Collect relevant domain IDs
        all_relevant_skills = (
            current_skill_ids | target_skill_ids
            | gap_skill_ids | chapter_skill_ids
            | remaining_skill_ids
        )
        relevant_domains: set[str] = set()
        for sid in all_relevant_skills:
            skill = self._ontology.get_skill(sid)
            if skill:
                relevant_domains.add(skill["domain"])

        # Build domain nodes
        domain_nodes: list[dict] = []
        for d in domains:
            if d["id"] in relevant_domains:
                domain_nodes.append({
                    "id": d["id"],
                    "label": d["label"],
                    "layer": d.get("layer", ""),
                    "color": layer_colors.get(d.get("layer", ""), "#6b7280"),
                    "type": "domain",
                })

        # Build skill nodes (only relevant ones)
        skill_nodes: list[dict] = []
        for sid in sorted(all_relevant_skills):
            skill = self._ontology.get_skill(sid)
            if not skill:
                continue
            state = "neutral"
            if sid in chapter_skill_ids:
                state = "chapter"
            elif sid in remaining_skill_ids:
                state = "remaining"
            elif sid in gap_skill_ids:
                state = "gap"
            elif sid in target_skill_ids:
                state = "target"
            elif sid in current_skill_ids:
                state = "current"

            skill_nodes.append({
                "id": sid,
                "label": skill["name"],
                "domain": skill["domain"],
                "level": skill["level"],
                "state": state,
                "type": "skill",
            })

        # Build links: skill → domain
        links: list[dict] = []
        for sn in skill_nodes:
            links.append({
                "source": sn["domain"],
                "target": sn["id"],
                "type": sn["state"],
            })

        # Build chapter flow links (1 → 2 → 3 → 4 → 5)
        last_chapter_sid = ""
        for i, ch in enumerate(chapters):
            sid = ch.get("skill_id") or ch.get("primary_skill_id", "")
            if i > 0:
                prev_sid = chapters[i - 1].get("skill_id") or chapters[i - 1].get("primary_skill_id", "")
                if prev_sid and sid:
                    links.append({
                        "source": prev_sid,
                        "target": sid,
                        "type": "path",
                    })
            last_chapter_sid = sid

        # Connect last chapter to remaining skills (future path hint)
        if last_chapter_sid:
            for rsid in sorted(remaining_skill_ids):
                links.append({
                    "source": last_chapter_sid,
                    "target": rsid,
                    "type": "future",
                })

        return {
            "nodes": domain_nodes + skill_nodes,
            "links": links,
            "chapters": [
                {
                    "num": ch.get("chapter_number", i + 1),
                    "skill_id": ch.get("skill_id") or ch.get("primary_skill_id", ""),
                    "skill_name": ch.get("skill_name", ""),
                    "current_level": ch.get("current_level", 0),
                    "target_level": ch.get("target_level", 0),
                }
                for i, ch in enumerate(chapters)
            ],
        }

    # ------------------------------------------------------------------
    # HTML renderer
    # ------------------------------------------------------------------

    def _render_html(
        self,
        summary: dict,
        top10_current: list[dict],
        top10_target: list[dict],
        gaps: list[dict],
        chapters: list[dict],
        profile_summary: str,
        graph_data: dict,
        journey_roadmap: dict | None = None,
        top10_gaps: list[dict] | None = None,
        all_skill_gaps: list[dict] | None = None,
        full_journey: dict | None = None,
    ) -> str:
        """Render the full HTML page."""
        e = html.escape  # shorthand

        # --- Profile summary table ---
        fj = full_journey or {}
        profile_rows = ""
        for key, label in [
            ("profile_summary", "Profile"),
            ("target_role", "Target Role"),
            ("total_gaps_identified", "Gaps Identified"),
            ("total_chapters", "Chapters"),
            ("estimated_learning_hours", "Est. Hours"),
        ]:
            val = summary.get(key, "")
            if val:
                profile_rows += f"<tr><td class='label'>{e(label)}</td><td>{e(str(val))}</td></tr>\n"

        # --- Full journey summary (expandable) ---
        summary_extra_rows = ""
        all_skills_table = ""
        if fj:
            summary_extra_rows += f"<tr><td class='label'>Total Skills with Gaps</td><td>{fj.get('total_skills_with_gaps', 0)}</td></tr>\n"
            summary_extra_rows += f"<tr><td class='label'>Total Gap-Levels</td><td>{fj.get('total_gap_levels', 0)}</td></tr>\n"
            summary_extra_rows += f"<tr><td class='label'>Total Est. Chapters</td><td>{fj.get('total_estimated_chapters', 0)}</td></tr>\n"
            summary_extra_rows += f"<tr><td class='label'>Total Est. Hours</td><td>{fj.get('total_estimated_hours', 0)}</td></tr>\n"
            summary_extra_rows += f"<tr><td class='label'>Est. Paths to Complete</td><td>~{fj.get('total_estimated_paths', 1)}</td></tr>\n"
            # Build all-skills table
            for g in (all_skill_gaps or []):
                all_skills_table += f"""<tr>
                    <td><span class='skill-id'>{e(g.get('skill_id',''))}</span><br>{e(g.get('skill_name',''))}</td>
                    <td>{e(g.get('domain',''))}</td>
                    <td class='level'>L{g.get('current_level',0)}</td>
                    <td class='level'>L{g.get('target_level',0)}</td>
                    <td class='delta'>+{g.get('gap',0)}</td>
                </tr>\n"""

        summary_toggle_html = ""
        if fj:
            summary_toggle_html = """<button class="toggle-btn" id="summary-toggle" onclick="toggleSummary()">Show Full Journey Details</button>"""

        # --- Skill matching: compute overlap between current and target ---
        current_skill_ids = {s.get("skill_id", "") for s in top10_current}
        target_skill_ids = {s.get("skill_id", "") for s in top10_target}
        # Build lookup: target skill_id -> required_level
        target_level_lookup = {s.get("skill_id", ""): s.get("required_level", 0) for s in top10_target}
        # Build lookup: current skill_id -> current_level
        current_level_lookup = {s.get("skill_id", ""): s.get("current_level", 0) for s in top10_current}

        # --- Top 10 current skills ---
        current_rows = ""
        for s in top10_current:
            sid = s.get("skill_id", "")
            in_target = sid in target_skill_ids
            row_class = "match-row" if in_target else ""
            match_badge = f"<span class='match-badge target-match'>Target: L{target_level_lookup.get(sid, 0)}</span>" if in_target else ""
            current_rows += f"""<tr class='{row_class}'>
                <td class='rank'>{s.get('rank','')}</td>
                <td><span class='skill-id'>{e(sid)}</span><br>{e(s.get('skill_name',''))}{match_badge}</td>
                <td><span class='domain-badge'>{e(s.get('domain_label','') or s.get('domain',''))}</span></td>
                <td class='level'>L{s.get('current_level',0)}</td>
                <td class='rationale'>{e(s.get('rationale',''))}</td>
            </tr>\n"""

        # --- Top 10 target skills ---
        target_rows = ""
        for s in top10_target:
            sid = s.get("skill_id", "")
            imp = s.get("importance", "")
            imp_class = "imp-critical" if imp == "critical" else "imp-high" if imp == "high" else "imp-med"
            in_current = sid in current_skill_ids
            row_class = "match-row" if in_current else ""
            match_badge = f"<span class='match-badge current-match'>You: L{current_level_lookup.get(sid, 0)}</span>" if in_current else ""
            target_rows += f"""<tr class='{row_class}'>
                <td class='rank'>{s.get('rank','')}</td>
                <td><span class='skill-id'>{e(sid)}</span><br>{e(s.get('skill_name',''))}{match_badge}</td>
                <td><span class='domain-badge'>{e(s.get('domain_label','') or s.get('domain',''))}</span></td>
                <td class='level'>L{s.get('required_level',0)}</td>
                <td><span class='{imp_class}'>{e(imp)}</span></td>
                <td class='rationale'>{e(s.get('rationale',''))}</td>
            </tr>\n"""

        # --- Gap table (default: scaffold-aligned gaps; expandable: all gaps) ---
        all_gaps = all_skill_gaps or []
        default_gap_ids = {g.get('skill_id', '') for g in gaps}

        gap_rows_default = ""
        for g in gaps:
            required = g.get('target_level', g.get('required_level', 0))
            delta = g.get('gap', g.get('delta', 0))
            priority = g.get('priority', g.get('priority_score', ''))
            gap_rows_default += f"""<tr>
                <td><span class='skill-id'>{e(g.get('skill_id',''))}</span><br>{e(g.get('skill_name',''))}</td>
                <td>{e(g.get('domain',''))}</td>
                <td class='level'>L{g.get('current_level',0)}</td>
                <td class='level'>L{required}</td>
                <td class='delta'>+{delta}</td>
                <td>{priority}</td>
            </tr>\n"""

        gap_rows_extra = ""
        for g in all_gaps:
            if g.get('skill_id', '') in default_gap_ids:
                continue
            gap_rows_extra += f"""<tr>
                <td><span class='skill-id'>{e(g.get('skill_id',''))}</span><br>{e(g.get('skill_name',''))}</td>
                <td>{e(g.get('domain',''))}</td>
                <td class='level'>L{g.get('current_level',0)}</td>
                <td class='level'>L{g.get('target_level',0)}</td>
                <td class='delta'>+{g.get('gap',0)}</td>
                <td></td>
            </tr>\n"""

        extra_gap_count = len(all_gaps) - len(default_gap_ids)
        total_gap_count = len(all_gaps)
        gap_toggle_html = ""
        if extra_gap_count > 0:
            gap_toggle_html = f"""<button class="toggle-btn" id="gap-toggle" onclick="toggleGaps()">Show All {total_gap_count} Gaps</button>"""

        # --- Chapter rows (default: this path; expandable: full journey) ---
        chapter_rows = ""
        for ch in chapters:
            chapter_rows += f"""<tr>
                <td class='rank'>{ch.get('chapter_number','')}</td>
                <td><span class='skill-id'>{e(ch.get('skill_id','') or ch.get('primary_skill_id',''))}</span><br>
                    {e(ch.get('skill_name','') or ch.get('title',''))}</td>
                <td class='level'>L{ch.get('current_level',0)}</td>
                <td class='arrow'>→</td>
                <td class='level level-target'>L{ch.get('target_level',0)}</td>
            </tr>\n"""

        # Build projected future chapters from all_skill_gaps not in Path 1
        chapter_skill_ids = {
            ch.get('skill_id') or ch.get('primary_skill_id', '')
            for ch in chapters
        }
        future_skills = [
            g for g in all_gaps
            if g.get('skill_id', '') not in chapter_skill_ids
        ]
        path_extra_rows = ""
        if future_skills:
            path_num = 2
            ch_in_path = 0
            for g in future_skills:
                if ch_in_path == 0:
                    path_extra_rows += f"""<tr class='path-header'>
                        <td colspan='5'>Path {path_num} (projected)</td>
                    </tr>\n"""
                gap_val = g.get('gap', 0)
                cur = g.get('current_level', 0)
                tgt = g.get('target_level', 0)
                # Each chapter = +1 level, so show incremental steps
                for step in range(gap_val):
                    from_lvl = cur + step
                    to_lvl = from_lvl + 1
                    ch_in_path += 1
                    path_extra_rows += f"""<tr class='projected-row'>
                        <td class='rank'>{ch_in_path}</td>
                        <td><span class='skill-id'>{e(g.get('skill_id',''))}</span><br>
                            {e(g.get('skill_name',''))}</td>
                        <td class='level'>L{from_lvl}</td>
                        <td class='arrow'>→</td>
                        <td class='level level-target'>L{to_lvl}</td>
                    </tr>\n"""
                    if ch_in_path >= 5:
                        ch_in_path = 0
                        path_num += 1

        path_toggle_html = ""
        if future_skills:
            remaining_count = sum(g.get('gap', 0) for g in future_skills)
            path_toggle_html = f"""<button class="toggle-btn" id="path-toggle" onclick="togglePath()">Show Full Journey (+{remaining_count} more chapters)</button>"""

        graph_json = json.dumps(graph_data)

        # --- Journey progress section ---
        jr = journey_roadmap or {}
        total_gaps = jr.get("total_gap_levels", 0)
        path_closes = jr.get("path_closes_levels", 0)
        est_paths = jr.get("estimated_total_paths", 1)
        pct = round(path_closes / total_gaps * 100) if total_gaps else 0
        skills_addressed = jr.get("skills_addressed", [])
        skills_remaining = jr.get("skills_remaining", [])

        # Build addressed rows
        addressed_rows = ""
        for s in skills_addressed:
            addressed_rows += (
                f"<div class='jp-skill'>"
                f"<span class='skill-id'>{html.escape(s.get('skill_id', ''))}</span> "
                f"{html.escape(s.get('skill_name', ''))}"
                f"<span class='jp-level'>L{s.get('current_level', 0)} → "
                f"L{s.get('after_path_level', 0)}</span>"
                f"</div>\n"
            )

        # Build remaining rows (includes partial badges)
        remaining_rows = ""
        remaining_total_levels = sum(s.get('gap', 0) for s in skills_remaining)
        for s in skills_remaining:
            partial_badge = ""
            if s.get("partial"):
                partial_badge = " <span class='partial-badge'>+1 this path</span>"
            remaining_rows += (
                f"<div class='jp-skill'>"
                f"<span class='skill-id'>{html.escape(s.get('skill_id', ''))}</span> "
                f"{html.escape(s.get('skill_name', ''))}{partial_badge}"
                f"<span class='jp-level'>L{s.get('current_level', 0)} → "
                f"L{s.get('required_level', 0)} (+{s.get('gap', 0)})</span>"
                f"</div>\n"
            )

        journey_section = ""
        if total_gaps > 0:
            journey_section = f"""
    <h2>Journey Progress</h2>
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <span style="font-weight:700;font-size:15px">Path 1 of ~{est_paths} estimated</span>
            <span style="font-weight:600;color:var(--primary)">{path_closes} of {total_gaps} gap-levels ({pct}%)</span>
        </div>
        <div style="width:100%;height:10px;background:#e2e8f0;border-radius:6px;overflow:hidden;margin-bottom:16px">
            <div style="width:{pct}%;height:100%;background:var(--primary);border-radius:6px"></div>
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">
            This path: +{path_closes} levels &nbsp;|&nbsp; Remaining: {remaining_total_levels} gap-levels &nbsp;|&nbsp; Total: {total_gaps} gap-levels
        </div>
        <div class="grid-2">
            <div>
                <h3 style="color:#f59e0b">This Path ({len(skills_addressed)} skills, +1 level each)</h3>
                {addressed_rows}
            </div>
            <div>
                <h3 style="color:#8b5cf6">Remaining ({len(skills_remaining)} entries, {remaining_total_levels} gap-levels)</h3>
                {remaining_rows}
            </div>
        </div>
    </div>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Pathway — Ontology Path Visualization</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
:root {{
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --border: #e2e8f0;
    --text: #1e293b;
    --text-muted: #64748b;
    --primary: #4f46e5;
    --green: #16a34a;
    --red: #dc2626;
    --amber: #d97706;
    --cyan: #0891b2;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 24px; }}
.container {{ max-width: 1400px; margin: 0 auto; }}
h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 4px; color: var(--primary); }}
h2 {{ font-size: 18px; font-weight: 600; margin: 24px 0 12px; color: var(--text); border-bottom: 2px solid var(--primary); padding-bottom: 6px; }}
h3 {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; }}
.subtitle {{ color: var(--text-muted); font-size: 14px; margin-bottom: 24px; }}
.card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th {{ background: #f1f5f9; text-align: left; padding: 8px 10px; font-weight: 600; border-bottom: 2px solid var(--border); }}
td {{ padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
td.label {{ font-weight: 600; color: var(--text-muted); width: 140px; }}
td.rank {{ width: 32px; text-align: center; font-weight: 700; color: var(--primary); }}
td.level {{ font-weight: 700; text-align: center; width: 48px; }}
td.level-target {{ color: var(--green); }}
td.delta {{ font-weight: 700; color: var(--red); }}
td.arrow {{ text-align: center; width: 24px; color: var(--text-muted); }}
td.rationale {{ font-style: italic; color: var(--text-muted); font-size: 12px; max-width: 400px; }}
.skill-id {{ font-family: monospace; font-size: 11px; color: var(--cyan); }}
.domain-badge {{ background: #e0e7ff; color: var(--primary); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; white-space: nowrap; }}
.imp-critical {{ background: #fee2e2; color: var(--red); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
.imp-high {{ background: #fef3c7; color: var(--amber); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
.imp-med {{ background: #f1f5f9; color: var(--text-muted); padding: 2px 8px; border-radius: 4px; font-size: 11px; }}
tr.match-row {{ background: #f0fdf4; }}
.match-badge {{ display: inline-block; margin-left: 6px; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
.target-match {{ background: #dbeafe; color: #2563eb; }}
.current-match {{ background: #dcfce7; color: #16a34a; }}
#graph-container {{ width: 100%; height: 800px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: #fafbfc; }}
.legend {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0; font-size: 12px; }}
.legend-item {{ display: flex; align-items: center; gap: 4px; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
.print-btn {{ background: var(--primary); color: white; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }}
.print-btn:hover {{ opacity: 0.9; }}
@media print {{ .print-btn {{ display: none; }} }}
.jp-skill {{ display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
.jp-level {{ font-weight: 600; font-size: 12px; color: var(--text-muted); flex-shrink: 0; margin-left: 8px; }}
.toggle-btn {{ background: var(--primary); color: white; border: none; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; margin-top: 12px; }}
.toggle-btn:hover {{ opacity: 0.85; }}
.partial-badge {{ background: #fef3c7; color: #d97706; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 6px; }}
tr.projected-row {{ background: #faf5ff; }}
tr.projected-row td {{ color: var(--text-muted); }}
tr.path-header {{ background: #f1f5f9; }}
tr.path-header td {{ font-weight: 600; color: var(--primary); font-size: 13px; padding: 6px 10px; }}
@media print {{ .toggle-btn {{ display: none; }} }}
</style>
</head>
<body>
<div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>AI Pathway — Ontology Path Visualization</h1>
            <p class="subtitle">Skills assessment, gap analysis, and learning path through the GenAI Skills Ontology</p>
        </div>
        <button class="print-btn" onclick="window.print()">Print / Save PDF</button>
    </div>

    <!-- Profile Summary -->
    <div class="card">
        <h3>Profile Summary</h3>
        <table>{profile_rows}</table>
        {summary_toggle_html}
        <div id="summary-extra" style="display:none;margin-top:16px">
            <h3 style="margin-top:12px;color:var(--primary)">Full Journey Estimate</h3>
            <table>{summary_extra_rows}</table>
            <h3 style="margin-top:16px">All Skills Needing Improvement</h3>
            <table>
                <thead><tr><th>Skill</th><th>Domain</th><th>Current</th><th>Target</th><th>Gap</th></tr></thead>
                <tbody>{all_skills_table}</tbody>
            </table>
        </div>
    </div>

    <!-- Top 10 Skills Breakdown -->
    <h2>Skills Assessment Breakdown</h2>
    <div class="grid-2">
        <div class="card">
            <h3>Your Current Skills (Top 10)</h3>
            <table>
                <thead><tr><th>#</th><th>Skill</th><th>Domain</th><th>Level</th><th>Rationale</th></tr></thead>
                <tbody>{current_rows}</tbody>
            </table>
        </div>
        <div class="card">
            <h3>Target Role Skills (Top 10)</h3>
            <table>
                <thead><tr><th>#</th><th>Skill</th><th>Domain</th><th>Level</th><th>Imp.</th><th>Rationale</th></tr></thead>
                <tbody>{target_rows}</tbody>
            </table>
        </div>
    </div>

    <!-- Gap Analysis -->
    <h2>Gap Analysis</h2>
    <div class="card">
        <table>
            <thead><tr><th>Skill</th><th>Domain</th><th>Current</th><th>Required</th><th>Gap</th><th>Priority</th></tr></thead>
            <tbody>{gap_rows_default}</tbody>
            <tbody id="gap-extra" style="display:none">{gap_rows_extra}</tbody>
        </table>
        {gap_toggle_html}
    </div>

    <!-- Learning Path -->
    <h2>Learning Path ({len(chapters)} Chapters)</h2>
    <div class="card">
        <table>
            <thead><tr><th>Ch</th><th>Skill</th><th>From</th><th></th><th>To</th></tr></thead>
            <tbody>{chapter_rows}</tbody>
            <tbody id="path-extra" style="display:none">{path_extra_rows}</tbody>
        </table>
        {path_toggle_html}
    </div>

    {journey_section}

    <!-- Ontology Path Graph -->
    <h2>Ontology Path Visualization</h2>
    <div class="legend">
        <div class="legend-item"><div class="legend-dot" style="background:#16a34a"></div> Current Skills</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div> This Path (Chapters)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#8b5cf6;border:2px dashed #7c3aed"></div> Future Paths</div>
        <div class="legend-item"><div class="legend-dot" style="background:#6b7280;border:2px solid #374151"></div> Domains</div>
    </div>
    <div class="card">
        <div id="graph-container"></div>
    </div>
</div>

<script>
const graphData = {graph_json};

const container = document.getElementById('graph-container');
const width = container.clientWidth;
const height = container.clientHeight || 800;

const svg = d3.select('#graph-container')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

// Color mapping for skill states
const stateColors = {{
    current: '#16a34a',
    target: '#3b82f6',
    chapter: '#f59e0b',
    remaining: '#8b5cf6',
    gap: '#ef4444',
    neutral: '#94a3b8',
}};

const linkColors = {{
    current: '#bbf7d0',
    target: '#bfdbfe',
    chapter: '#fef08a',
    remaining: '#ddd6fe',
    gap: '#fecaca',
    path: '#f59e0b',
    future: '#a78bfa',
    neutral: '#e2e8f0',
}};

// Create arrow markers for path and future links
const defs = svg.append('defs');
defs.selectAll('marker')
    .data([{{ id: 'path', color: '#f59e0b' }}, {{ id: 'future', color: '#8b5cf6' }}])
    .enter().append('marker')
    .attr('id', d => 'arrow-' + d.id)
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 28)
    .attr('refY', 0)
    .attr('markerWidth', 8)
    .attr('markerHeight', 8)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', d => d.color);

// Force simulation
const simulation = d3.forceSimulation(graphData.nodes)
    .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(d => d.type === 'path' ? 160 : d.type === 'future' ? 180 : 120))
    .force('charge', d3.forceManyBody().strength(d => d.type === 'domain' ? -600 : -250))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => d.type === 'domain' ? 80 : 40));

// Draw links
const link = svg.append('g')
    .selectAll('line')
    .data(graphData.links)
    .enter().append('line')
    .attr('stroke', d => linkColors[d.type] || '#e2e8f0')
    .attr('stroke-width', d => d.type === 'path' ? 3.5 : d.type === 'future' ? 2 : 2)
    .attr('stroke-dasharray', d => d.type === 'path' ? '8,4' : d.type === 'future' ? '4,4' : 'none')
    .attr('marker-end', d => d.type === 'path' ? 'url(#arrow-path)' : d.type === 'future' ? 'url(#arrow-future)' : '')
    .attr('opacity', d => d.type === 'future' ? 0.6 : 1);

// Draw nodes
const node = svg.append('g')
    .selectAll('g')
    .data(graphData.nodes)
    .enter().append('g')
    .call(d3.drag()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded));

// Domain nodes — dynamic width based on label length
node.filter(d => d.type === 'domain').each(function(d) {{
    const charWidth = 8.5;  // approx px per char at 14px font-weight 600
    const padding = 24;
    const w = Math.min(240, Math.max(120, d.label.length * charWidth + padding));
    d._rectW = w;  // store for collision reference
    d3.select(this).append('rect')
        .attr('width', w)
        .attr('height', 40)
        .attr('x', -w / 2)
        .attr('y', -20)
        .attr('rx', 10)
        .attr('fill', d.color || '#6b7280')
        .attr('opacity', 0.85)
        .attr('stroke', d.color || '#6b7280')
        .attr('stroke-width', 2);
    d3.select(this).append('text')
        .text(d.label)
        .attr('text-anchor', 'middle')
        .attr('dy', 5)
        .attr('fill', 'white')
        .attr('font-size', '13px')
        .attr('font-weight', '600');
}});

// Skill nodes (circles)
node.filter(d => d.type === 'skill')
    .append('circle')
    .attr('r', d => d.state === 'chapter' ? 22 : d.state === 'remaining' ? 18 : 16)
    .attr('fill', d => stateColors[d.state] || '#94a3b8')
    .attr('stroke', d => d.state === 'remaining' ? '#7c3aed' : d.state === 'chapter' ? '#d97706' : '#fff')
    .attr('stroke-width', d => d.state === 'remaining' ? 3 : d.state === 'chapter' ? 3 : 2)
    .attr('stroke-dasharray', d => d.state === 'remaining' ? '4,3' : 'none')
    .attr('opacity', 0.9)
    .attr('filter', d => d.state === 'chapter' ? 'drop-shadow(0 2px 4px rgba(245,158,11,0.4))' : 'none');

// Chapter numbers on chapter nodes
node.filter(d => d.type === 'skill' && d.state === 'chapter')
    .append('text')
    .text(d => {{
        const ch = graphData.chapters.find(c => c.skill_id === d.id);
        return ch ? ch.num : '';
    }})
    .attr('text-anchor', 'middle')
    .attr('dy', 5)
    .attr('fill', 'white')
    .attr('font-size', '13px')
    .attr('font-weight', '700');

// Skill labels (skill name instead of ID for readability)
node.filter(d => d.type === 'skill')
    .append('text')
    .text(d => d.label)
    .attr('dy', -24)
    .attr('text-anchor', 'middle')
    .attr('fill', '#334155')
    .attr('font-size', '12px')
    .attr('font-weight', '500');

// Skill ID (smaller, below the name)
node.filter(d => d.type === 'skill')
    .append('text')
    .text(d => d.id)
    .attr('dy', d => d.state === 'chapter' ? 34 : 30)
    .attr('text-anchor', 'middle')
    .attr('fill', '#94a3b8')
    .attr('font-size', '10px')
    .attr('font-family', 'monospace');

// Tooltip
node.append('title')
    .text(d => d.type === 'domain' ? d.label : d.id + ': ' + d.label);

// Simulation tick — clamp nodes within bounds to prevent label clipping
const MARGIN = 120;
simulation.on('tick', () => {{
    graphData.nodes.forEach(d => {{
        d.x = Math.max(MARGIN, Math.min(width - MARGIN, d.x));
        d.y = Math.max(MARGIN, Math.min(height - MARGIN, d.y));
    }});
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
}});

function dragStarted(event, d) {{
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}}
function dragged(event, d) {{
    d.fx = event.x;
    d.fy = event.y;
}}
function dragEnded(event, d) {{
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}}

// --- Toggle functions for Show More buttons ---
function toggleGaps() {{
    const extra = document.getElementById('gap-extra');
    const btn = document.getElementById('gap-toggle');
    if (!extra) return;
    if (extra.style.display === 'none') {{
        extra.style.display = '';
        btn.textContent = 'Show Less';
    }} else {{
        extra.style.display = 'none';
        btn.textContent = 'Show All {total_gap_count} Gaps';
    }}
}}
function togglePath() {{
    const extra = document.getElementById('path-extra');
    const btn = document.getElementById('path-toggle');
    if (!extra) return;
    if (extra.style.display === 'none') {{
        extra.style.display = '';
        btn.textContent = 'Show Current Path Only';
    }} else {{
        extra.style.display = 'none';
        btn.textContent = btn.dataset.label || 'Show Full Journey';
    }}
}}
function toggleSummary() {{
    const extra = document.getElementById('summary-extra');
    const btn = document.getElementById('summary-toggle');
    if (!extra) return;
    if (extra.style.display === 'none') {{
        extra.style.display = '';
        btn.textContent = 'Show Less';
    }} else {{
        extra.style.display = 'none';
        btn.textContent = 'Show Full Journey Details';
    }}
}}
</script>
</body>
</html>"""
