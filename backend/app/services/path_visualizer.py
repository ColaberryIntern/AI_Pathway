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
        gaps = analysis_result.get("gap_analysis", {}).get("gaps", [])
        chapters = analysis_result.get("learning_path", {}).get("chapters", [])
        profile_analysis = analysis_result.get("profile_analysis", {})

        # Build graph data for D3
        graph_data = self._build_graph_data(
            top10_current, top10_target, gaps, chapters
        )

        return self._render_html(
            summary=summary,
            top10_current=top10_current,
            top10_target=top10_target,
            gaps=gaps,
            chapters=chapters,
            profile_summary=profile_analysis.get("profile_summary", ""),
            graph_data=graph_data,
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

        # Build layer color map
        layer_colors: dict[str, str] = {}
        for layer in layers:
            layer_colors[layer["id"]] = layer.get("color", "#6b7280")

        # Collect relevant domain IDs
        all_relevant_skills = current_skill_ids | target_skill_ids | gap_skill_ids | chapter_skill_ids
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

        # Build chapter flow links
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
    ) -> str:
        """Render the full HTML page."""
        e = html.escape  # shorthand

        # --- Profile summary table ---
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

        # --- Top 10 current skills ---
        current_rows = ""
        for s in top10_current:
            current_rows += f"""<tr>
                <td class='rank'>{s.get('rank','')}</td>
                <td><span class='skill-id'>{e(s.get('skill_id',''))}</span><br>{e(s.get('skill_name',''))}</td>
                <td><span class='domain-badge'>{e(s.get('domain_label','') or s.get('domain',''))}</span></td>
                <td class='level'>L{s.get('current_level',0)}</td>
                <td class='rationale'>{e(s.get('rationale',''))}</td>
            </tr>\n"""

        # --- Top 10 target skills ---
        target_rows = ""
        for s in top10_target:
            imp = s.get("importance", "")
            imp_class = "imp-critical" if imp == "critical" else "imp-high" if imp == "high" else "imp-med"
            target_rows += f"""<tr>
                <td class='rank'>{s.get('rank','')}</td>
                <td><span class='skill-id'>{e(s.get('skill_id',''))}</span><br>{e(s.get('skill_name',''))}</td>
                <td><span class='domain-badge'>{e(s.get('domain_label','') or s.get('domain',''))}</span></td>
                <td class='level'>L{s.get('required_level',0)}</td>
                <td><span class='{imp_class}'>{e(imp)}</span></td>
                <td class='rationale'>{e(s.get('rationale',''))}</td>
            </tr>\n"""

        # --- Gap table ---
        gap_rows = ""
        for g in gaps[:15]:
            gap_rows += f"""<tr>
                <td><span class='skill-id'>{e(g.get('skill_id',''))}</span><br>{e(g.get('skill_name',''))}</td>
                <td>{e(g.get('domain',''))}</td>
                <td class='level'>L{g.get('current_level',0)}</td>
                <td class='level'>L{g.get('required_level',0)}</td>
                <td class='delta'>+{g.get('delta',0)}</td>
                <td>{g.get('priority_score','')}</td>
            </tr>\n"""

        # --- Chapter rows ---
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

        graph_json = json.dumps(graph_data)

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
#graph-container {{ width: 100%; height: 500px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: #fafbfc; }}
.legend {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0; font-size: 12px; }}
.legend-item {{ display: flex; align-items: center; gap: 4px; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
.print-btn {{ background: var(--primary); color: white; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }}
.print-btn:hover {{ opacity: 0.9; }}
@media print {{ .print-btn {{ display: none; }} }}
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
            <tbody>{gap_rows}</tbody>
        </table>
    </div>

    <!-- Learning Path -->
    <h2>Learning Path ({len(chapters)} Chapters)</h2>
    <div class="card">
        <table>
            <thead><tr><th>Ch</th><th>Skill</th><th>From</th><th></th><th>To</th></tr></thead>
            <tbody>{chapter_rows}</tbody>
        </table>
    </div>

    <!-- Ontology Path Graph -->
    <h2>Ontology Path Visualization</h2>
    <div class="legend">
        <div class="legend-item"><div class="legend-dot" style="background:#16a34a"></div> Current Skills</div>
        <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div> Target Skills</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div> Learning Path</div>
        <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div> Skill Gaps</div>
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
const height = container.clientHeight || 500;

const svg = d3.select('#graph-container')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

// Color mapping for skill states
const stateColors = {{
    current: '#16a34a',
    target: '#3b82f6',
    chapter: '#f59e0b',
    gap: '#ef4444',
    neutral: '#94a3b8',
}};

const linkColors = {{
    current: '#bbf7d0',
    target: '#bfdbfe',
    chapter: '#fef08a',
    gap: '#fecaca',
    path: '#f59e0b',
    neutral: '#e2e8f0',
}};

// Create arrow markers for path links
svg.append('defs').selectAll('marker')
    .data(['path'])
    .enter().append('marker')
    .attr('id', d => 'arrow-' + d)
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 20)
    .attr('refY', 0)
    .attr('markerWidth', 8)
    .attr('markerHeight', 8)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#f59e0b');

// Force simulation
const simulation = d3.forceSimulation(graphData.nodes)
    .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(d => d.type === 'path' ? 120 : 80))
    .force('charge', d3.forceManyBody().strength(d => d.type === 'domain' ? -400 : -150))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => d.type === 'domain' ? 40 : 20));

// Draw links
const link = svg.append('g')
    .selectAll('line')
    .data(graphData.links)
    .enter().append('line')
    .attr('stroke', d => linkColors[d.type] || '#e2e8f0')
    .attr('stroke-width', d => d.type === 'path' ? 3 : 1.5)
    .attr('stroke-dasharray', d => d.type === 'path' ? '8,4' : 'none')
    .attr('marker-end', d => d.type === 'path' ? 'url(#arrow-path)' : '');

// Draw nodes
const node = svg.append('g')
    .selectAll('g')
    .data(graphData.nodes)
    .enter().append('g')
    .call(d3.drag()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded));

// Domain nodes (larger rectangles)
node.filter(d => d.type === 'domain')
    .append('rect')
    .attr('width', 100)
    .attr('height', 32)
    .attr('x', -50)
    .attr('y', -16)
    .attr('rx', 8)
    .attr('fill', d => d.color || '#6b7280')
    .attr('opacity', 0.85)
    .attr('stroke', d => d.color || '#6b7280')
    .attr('stroke-width', 2);

node.filter(d => d.type === 'domain')
    .append('text')
    .text(d => d.label)
    .attr('text-anchor', 'middle')
    .attr('dy', 4)
    .attr('fill', 'white')
    .attr('font-size', '11px')
    .attr('font-weight', '600');

// Skill nodes (circles)
node.filter(d => d.type === 'skill')
    .append('circle')
    .attr('r', d => d.state === 'chapter' ? 14 : 10)
    .attr('fill', d => stateColors[d.state] || '#94a3b8')
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .attr('opacity', 0.9);

// Chapter numbers on chapter nodes
node.filter(d => d.type === 'skill' && d.state === 'chapter')
    .append('text')
    .text(d => {{
        const ch = graphData.chapters.find(c => c.skill_id === d.id);
        return ch ? ch.num : '';
    }})
    .attr('text-anchor', 'middle')
    .attr('dy', 4)
    .attr('fill', 'white')
    .attr('font-size', '10px')
    .attr('font-weight', '700');

// Skill labels
node.filter(d => d.type === 'skill')
    .append('text')
    .text(d => d.id)
    .attr('dy', -14)
    .attr('text-anchor', 'middle')
    .attr('fill', '#64748b')
    .attr('font-size', '9px')
    .attr('font-family', 'monospace');

// Tooltip
node.append('title')
    .text(d => d.type === 'domain' ? d.label : d.id + ': ' + d.label);

// Simulation tick
simulation.on('tick', () => {{
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
</script>
</body>
</html>"""
