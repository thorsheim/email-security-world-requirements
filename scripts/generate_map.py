#!/usr/bin/env python3
"""
Generate docs/map.svg (static dark-themed map) and docs/index.html
(interactive GitHub Pages page) from data/countries/*.yaml.

Usage:
    python scripts/generate_map.py

Requirements: pyyaml, lxml
"""

import os
import sys
from pathlib import Path

import yaml

try:
    from lxml import etree
except ImportError:
    print("ERROR: 'lxml' not installed. Run: pip install lxml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
BASEMAP_PATH = REPO_ROOT / "assets" / "world-110m.svg"
COUNTRIES_DIR = REPO_ROOT / "data" / "countries"
STANDARDS_PATH = REPO_ROOT / "data" / "standards.yaml"
OUTPUT_SVG = REPO_ROOT / "docs" / "map.svg"
OUTPUT_HTML = REPO_ROOT / "docs" / "index.html"

STANDARDS_ORDER = ["SPF", "DKIM", "DMARC", "STARTTLS", "DANE", "DNSSEC", "MTA-STS", "TLS-RPT", "CAA", "RPKI", "ASPA", "BIMI"]

# Dark-theme color scale (mandatory count, scale 0–12)
DARK_COLORS = {
    "no_data": "#2a2a3e",
    0: "#7f0000",           # dark red — no requirements
    "rec_only": "#994400",  # orange-red — recommendations only
    1: "#b04000",
    2: "#c05000",
    3: "#d07000",
    4: "#b8a000",
    5: "#88bb00",
    6: "#55aa00",
    7: "#33cc33",
    8: "#00dd55",
    9: "#00ee77",
    10: "#00ff88",
    11: "#00ffaa",
    12: "#00ffcc",          # bright green — all mandatory
}


def score_color_dark(mandatory_count, recommended_count, has_data):
    if not has_data:
        return DARK_COLORS["no_data"]
    if mandatory_count == 0 and recommended_count == 0:
        return DARK_COLORS[0]
    if mandatory_count == 0:
        return DARK_COLORS["rec_only"]
    count = min(mandatory_count, 12)
    return DARK_COLORS.get(count, DARK_COLORS[12])


def load_country_data():
    """Load all country YAML files and build a dict keyed by country_code."""
    countries = {}
    for path in sorted(COUNTRIES_DIR.glob("*.yaml")):
        if path.stem == "_template":
            continue
        with open(path) as f:
            data = yaml.safe_load(f)
        code = data.get("country_code", "").upper()
        if code:
            countries[code] = data
    return countries


def compute_scores(countries):
    """For each country, compute mandatory and recommended counts."""
    scores = {}
    for code, data in countries.items():
        mandatory = 0
        recommended = 0
        for req in data.get("requirements", []):
            s = req.get("status", "")
            if s == "mandatory":
                mandatory += 1
            elif s == "recommended":
                recommended += 1
        scores[code] = {
            "mandatory": mandatory,
            "recommended": recommended,
            "name": data.get("country_name", code),
        }
    return scores


def build_tooltip(code, data, scores):
    s = scores.get(code, {})
    name = s.get("name", code)
    mandatory = s.get("mandatory", 0)
    recommended = s.get("recommended", 0)

    lines = [name]
    if mandatory:
        lines.append(f"Mandatory: {mandatory} standard(s)")
    if recommended:
        lines.append(f"Recommended: {recommended} standard(s)")
    if not mandatory and not recommended:
        lines.append("No requirements/recommendations found")

    applies_set = set()
    for req in data.get("requirements", []):
        for a in req.get("applies_to", []):
            applies_set.add(a.replace("_", " ").title())
    if applies_set:
        lines.append("Applies to: " + ", ".join(sorted(applies_set)))

    return " | ".join(lines)


def patch_svg_dark(countries, scores):
    """Load basemap SVG and patch country fill colors for dark theme."""
    if not BASEMAP_PATH.exists():
        print(f"ERROR: Basemap not found at {BASEMAP_PATH}")
        print("Run: python scripts/fetch_basemap.py")
        sys.exit(1)

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(BASEMAP_PATH), parser)
    root = tree.getroot()

    ns = {"svg": "http://www.w3.org/2000/svg"}

    for path_el in root.iter("{http://www.w3.org/2000/svg}path"):
        code = path_el.get("id", "").upper()
        if not code or code == "_OCEAN":
            continue

        if code in countries:
            data = countries[code]
            s = scores[code]
            color = score_color_dark(s["mandatory"], s["recommended"], True)
            tooltip = build_tooltip(code, data, scores)
        else:
            color = DARK_COLORS["no_data"]
            tooltip = path_el.get("data-name", code) + " | No data"

        path_el.set("fill", color)
        path_el.set("data-mandatory", str(scores.get(code, {}).get("mandatory", 0)))
        path_el.set("data-recommended", str(scores.get(code, {}).get("recommended", 0)))

        # Update or create title element
        title_el = path_el.find("{http://www.w3.org/2000/svg}title")
        if title_el is None:
            title_el = etree.SubElement(path_el, "{http://www.w3.org/2000/svg}title")
        title_el.text = tooltip

    # Update background rect
    for rect in root.iter("{http://www.w3.org/2000/svg}rect"):
        if rect.get("id") == "_ocean":
            rect.set("fill", "#1a1a2e")

    root.set("style", "background:#1a1a2e")
    return tree


def write_svg(tree, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_path), xml_declaration=True, encoding="utf-8", pretty_print=True)
    print(f"Written: {output_path}")


def build_table_rows_html(countries, scores):
    """Build HTML table rows for the interactive page."""
    STATUS_ICONS = {
        "mandatory": "✅",
        "recommended": "🔶",
        "informational": "ℹ️",
        "none": "➖",
        "unknown": "❓",
    }

    rows = []
    for code in sorted(countries.keys()):
        data = countries[code]
        s = scores[code]
        name = data.get("country_name", code)

        # Build per-standard cells
        req_map = {r["standard"]: r for r in data.get("requirements", [])}
        cells = []
        for std in STANDARDS_ORDER:
            req = req_map.get(std)
            if req:
                icon = STATUS_ICONS.get(req.get("status", "unknown"), "❓")
                level = req.get("level", "")
                level_str = f" ({level})" if level else ""
                status_label = req.get("status", "unknown").capitalize() + level_str
                cells.append(
                    f'<td title="{status_label}" class="status-{req.get("status", "unknown")}">'
                    f'{icon}</td>'
                )
            else:
                cells.append('<td class="status-unknown">❓</td>')

        # Applies-to summary
        applies_set = set()
        for req in data.get("requirements", []):
            for a in req.get("applies_to", []):
                applies_set.add(a.replace("_", " ").title())
        applies_str = ", ".join(sorted(applies_set)) if applies_set else "—"

        authority_set = set()
        for req in data.get("requirements", []):
            if req.get("authority"):
                authority_set.add(req["authority"])
        authority_str = "; ".join(sorted(authority_set)) if authority_set else "—"

        row = (
            f'<tr data-mandatory="{s["mandatory"]}" data-recommended="{s["recommended"]}">'
            f'<td><strong>{code}</strong></td>'
            f'<td>{name}</td>'
            f'<td>{authority_str}</td>'
            f"{''.join(cells)}"
            f'<td>{applies_str}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def load_svg_inline(path):
    """Load SVG file content as a string for inlining."""
    with open(path, "rb") as f:
        content = f.read().decode("utf-8")
    # Remove XML declaration for inlining
    if content.startswith("<?xml"):
        content = content[content.index("<svg"):]
    return content


def generate_index_html(countries, scores, svg_content):
    """Generate the GitHub Pages index.html."""

    table_rows = build_table_rows_html(countries, scores)

    std_header_cells = "".join(
        f'<th class="std-header" title="{s}">{s}</th>' for s in STANDARDS_ORDER
    )

    legend_html = """
        <div class="legend">
          <h3>Map Legend — Mandatory Standards Count (out of 12)</h3>
          <div class="legend-grid">
            <div class="legend-item"><span class="swatch" style="background:#00ffcc"></span> 12 — All mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#00ffaa"></span> 11 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#00ff88"></span> 10 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#00ee77"></span> 9 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#00dd55"></span> 8 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#33cc33"></span> 7 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#55aa00"></span> 6 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#88bb00"></span> 5 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#b8a000"></span> 4 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#d07000"></span> 3 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#c05000"></span> 2 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#b04000"></span> 1 mandatory</div>
            <div class="legend-item"><span class="swatch" style="background:#994400"></span> Recommendations only</div>
            <div class="legend-item"><span class="swatch" style="background:#7f0000"></span> No requirements</div>
            <div class="legend-item"><span class="swatch" style="background:#2a2a3e"></span> No data</div>
          </div>
          <div class="status-legend">
            <span class="status-mandatory">✅ Mandatory</span>
            <span class="status-recommended">🔶 Recommended</span>
            <span class="status-informational">ℹ️ Informational</span>
            <span class="status-none">➖ None</span>
            <span class="status-unknown">❓ Unknown / No data</span>
          </div>
          <p style="margin-top:0.75rem;font-size:0.8rem;color:var(--text-muted)">
            Standards: SPF · DKIM · DMARC · STARTTLS · DANE · DNSSEC · MTA-STS · TLS-RPT · CAA · RPKI · ASPA · BIMI
          </p>
        </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Email Security World Requirements</title>
  <style>
    :root {{
      --bg: #0f1117;
      --surface: #1a1a2e;
      --border: #2e3050;
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --green: #00ff88;
      --yellow: #fbbf24;
      --red: #f87171;
      --blue: #60a5fa;
      --accent: #7c3aed;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}
    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1.5rem 2rem;
    }}
    header h1 {{ font-size: 1.6rem; color: var(--green); margin-bottom: 0.25rem; }}
    header p {{ color: var(--text-muted); font-size: 0.9rem; }}
    header a {{ color: var(--blue); text-decoration: none; }}
    header a:hover {{ text-decoration: underline; }}
    main {{ padding: 2rem; max-width: 1600px; margin: 0 auto; }}
    section {{ margin-bottom: 3rem; }}
    h2 {{ font-size: 1.2rem; color: var(--text-muted); text-transform: uppercase;
          letter-spacing: 0.1em; margin-bottom: 1rem; border-bottom: 1px solid var(--border);
          padding-bottom: 0.5rem; }}
    .map-container {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      padding: 1rem;
    }}
    .map-container svg {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .map-container svg path:hover {{
      opacity: 0.75;
      cursor: pointer;
    }}
    .legend {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.5rem;
      margin-top: 1rem;
    }}
    .legend h3 {{ font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem; }}
    .legend-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 1.5rem;
      margin-bottom: 0.75rem;
    }}
    .legend-item {{ display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; }}
    .swatch {{
      display: inline-block;
      width: 14px; height: 14px;
      border-radius: 3px;
      border: 1px solid rgba(255,255,255,0.2);
      flex-shrink: 0;
    }}
    .status-legend {{ display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.85rem; }}
    .controls {{
      display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center;
    }}
    .controls input {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      padding: 0.4rem 0.8rem;
      font-size: 0.9rem;
      min-width: 220px;
    }}
    .controls label {{ font-size: 0.85rem; color: var(--text-muted); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }}
    thead th {{
      background: #0f1117;
      padding: 0.6rem 0.75rem;
      text-align: left;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}
    thead th:hover {{ color: var(--text); }}
    thead th.std-header {{ text-align: center; }}
    tbody tr {{ border-bottom: 1px solid var(--border); }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: rgba(255,255,255,0.03); }}
    tbody td {{ padding: 0.55rem 0.75rem; vertical-align: middle; }}
    tbody td.std-header, td[class^="status-"] {{ text-align: center; }}
    .status-mandatory {{ color: #4ade80; }}
    .status-recommended {{ color: #fbbf24; }}
    .status-informational {{ color: #94a3b8; }}
    .status-none {{ color: #475569; }}
    .status-unknown {{ color: #64748b; }}
    footer {{
      text-align: center;
      padding: 2rem;
      color: var(--text-muted);
      font-size: 0.8rem;
      border-top: 1px solid var(--border);
    }}
    footer a {{ color: var(--blue); text-decoration: none; }}
    .hidden {{ display: none; }}
    @media (max-width: 768px) {{
      main {{ padding: 1rem; }}
      table {{ font-size: 0.75rem; }}
      thead th, tbody td {{ padding: 0.4rem 0.5rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Email Security World Requirements</h1>
    <p>
      Which countries require or recommend SPF, DKIM, DMARC, DANE, MTA-STS, TLS-RPT, BIMI, STARTTLS, RPKI, and ASPA?
      &nbsp;·&nbsp;
      <a href="https://github.com/thorsheim/email-security-world-requirements">GitHub</a>
      &nbsp;·&nbsp;
      <a href="https://internet.nl">Test with internet.nl</a>
      &nbsp;·&nbsp;
      <a href="https://passwordscon.org/mailcheck/">Test with Mailcheck</a>
    </p>
  </header>

  <main>
    <section id="map-section">
      <h2>World Overview</h2>
      <div class="map-container" id="map-container">
        {svg_content}
      </div>
      {legend_html}
    </section>

    <section id="table-section">
      <h2>Requirements Matrix</h2>
      <div class="controls">
        <input type="text" id="search" placeholder="Filter by country or authority…" oninput="filterTable()">
        <label>
          <input type="checkbox" id="hide-no-data" onchange="filterTable()">
          Hide countries with no data
        </label>
      </div>
      <table id="matrix-table">
        <thead>
          <tr>
            <th onclick="sortTable(0)">Code ↕</th>
            <th onclick="sortTable(1)">Country ↕</th>
            <th onclick="sortTable(2)">Authority ↕</th>
            {std_header_cells}
            <th>Applies To</th>
          </tr>
        </thead>
        <tbody>
{table_rows}
        </tbody>
      </table>
    </section>

    <section id="standards-section">
      <h2>Standards Reference</h2>
      <table>
        <thead>
          <tr>
            <th>Standard</th>
            <th>Full Name</th>
            <th>RFC / Spec</th>
            <th>Key Testing Tools</th>
          </tr>
        </thead>
        <tbody>
          <tr><td><a href="standards/spf.md">SPF</a></td><td>Sender Policy Framework</td><td><a href="https://datatracker.ietf.org/doc/html/rfc7208" target="_blank">RFC 7208</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/spf.aspx" target="_blank">MXToolbox</a></td></tr>
          <tr><td><a href="standards/dkim.md">DKIM</a></td><td>DomainKeys Identified Mail</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6376" target="_blank">RFC 6376</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/dkim.aspx" target="_blank">MXToolbox</a></td></tr>
          <tr><td><a href="standards/dmarc.md">DMARC</a></td><td>Domain-based Message Authentication, Reporting and Conformance</td><td><a href="https://datatracker.ietf.org/doc/html/rfc7489" target="_blank">RFC 7489</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://dmarcian.com" target="_blank">dmarcian</a></td></tr>
          <tr><td><a href="standards/starttls.md">STARTTLS</a></td><td>SMTP STARTTLS (Opportunistic TLS)</td><td><a href="https://datatracker.ietf.org/doc/html/rfc3207" target="_blank">RFC 3207</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://passwordscon.org/mailcheck/" target="_blank">Mailcheck</a></td></tr>
          <tr><td><a href="standards/dane.md">DANE</a></td><td>DNS-based Authentication of Named Entities</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6698" target="_blank">RFC 6698</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a></td></tr>
          <tr><td><a href="standards/dnssec.md">DNSSEC</a></td><td>DNS Security Extensions</td><td><a href="https://datatracker.ietf.org/doc/html/rfc4033" target="_blank">RFC 4033–4035</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://dnsviz.net" target="_blank">DNSViz</a></td></tr>
          <tr><td><a href="standards/mta-sts.md">MTA-STS</a></td><td>Mail Transfer Agent Strict Transport Security</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8461" target="_blank">RFC 8461</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://www.hardenize.com" target="_blank">Hardenize</a></td></tr>
          <tr><td><a href="standards/tls-rpt.md">TLS-RPT</a></td><td>SMTP TLS Reporting</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8460" target="_blank">RFC 8460</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/TLSRpt.aspx" target="_blank">MXToolbox</a></td></tr>
          <tr><td><a href="standards/caa.md">CAA</a></td><td>Certification Authority Authorization</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8659" target="_blank">RFC 8659</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/caa.aspx" target="_blank">MXToolbox</a></td></tr>
          <tr><td><a href="standards/rpki.md">RPKI</a></td><td>Resource Public Key Infrastructure</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6480" target="_blank">RFC 6480 / 9582</a></td><td><a href="https://rpki.cloudflare.com" target="_blank">Cloudflare RPKI</a>, <a href="https://rpki-validator.ripe.net" target="_blank">RIPE NCC</a></td></tr>
          <tr><td><a href="standards/aspa.md">ASPA</a></td><td>Autonomous System Provider Authorization</td><td><a href="https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-profile/" target="_blank">IETF SIDROPS draft</a></td><td><a href="https://rpki-validator.ripe.net" target="_blank">RIPE NCC RPKI</a></td></tr>
          <tr><td><a href="standards/bimi.md">BIMI</a></td><td>Brand Indicators for Message Identification</td><td><a href="https://bimigroup.org" target="_blank">BIMI Group</a></td><td><a href="https://bimigroup.org/bimi-generator/" target="_blank">BIMI Checker</a></td></tr>
        </tbody>
      </table>
    </section>
  </main>

  <footer>
    <p>
      Data: <a href="https://creativecommons.org/licenses/by/4.0/">CC-BY-4.0</a> &nbsp;·&nbsp;
      Code: <a href="https://opensource.org/licenses/MIT">MIT</a> &nbsp;·&nbsp;
      Created by <a href="https://passwordscon.org">Per Thorsheim</a> &nbsp;·&nbsp;
      <a href="https://github.com/thorsheim/email-security-world-requirements">Contribute on GitHub</a>
    </p>
  </footer>

  <script>
    function filterTable() {{
      const q = document.getElementById('search').value.toLowerCase();
      const hideNoData = document.getElementById('hide-no-data').checked;
      const rows = document.querySelectorAll('#matrix-table tbody tr');
      rows.forEach(row => {{
        const text = row.textContent.toLowerCase();
        const mandatory = parseInt(row.dataset.mandatory || '0');
        const recommended = parseInt(row.dataset.recommended || '0');
        const noData = mandatory === 0 && recommended === 0;
        const matchesSearch = !q || text.includes(q);
        const matchesFilter = !hideNoData || !noData;
        row.classList.toggle('hidden', !matchesSearch || !matchesFilter);
      }});
    }}

    let sortDir = {{}};
    function sortTable(col) {{
      const table = document.getElementById('matrix-table');
      const tbody = table.tBodies[0];
      const rows = Array.from(tbody.rows);
      const dir = (sortDir[col] = !(sortDir[col]));
      rows.sort((a, b) => {{
        const av = a.cells[col]?.textContent.trim() || '';
        const bv = b.cells[col]?.textContent.trim() || '';
        return dir ? av.localeCompare(bv) : bv.localeCompare(av);
      }});
      rows.forEach(r => tbody.appendChild(r));
    }}
  </script>
</body>
</html>
"""
    return html


def main():
    countries = load_country_data()
    scores = compute_scores(countries)

    print(f"Loaded {len(countries)} country files.")

    # Generate dark-theme SVG map
    tree = patch_svg_dark(countries, scores)
    write_svg(tree, OUTPUT_SVG)

    # Load the SVG content for inlining in HTML
    svg_content = load_svg_inline(OUTPUT_SVG)

    # Generate interactive HTML
    html = generate_index_html(countries, scores, svg_content)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
