#!/usr/bin/env python3
"""
Generate webversion/index.html and webversion/map.svg for deployment to
passwordscon.org/mailrequirements/ (WordPress site, static subfolder).

This produces a fully self-contained HTML page with all CSS and JS inlined.
Design: clean neutral / light theme.

Usage:
    python scripts/generate_webversion.py

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
OUTPUT_DIR = REPO_ROOT / "webversion"
OUTPUT_HTML = OUTPUT_DIR / "index.html"
OUTPUT_SVG = OUTPUT_DIR / "map.svg"

STANDARDS_ORDER = ["SPF", "DKIM", "DMARC", "DANE", "MTA-STS", "TLS-RPT", "BIMI", "STARTTLS"]

# Light-theme color scale (mandatory count → pastel-shifted colors)
LIGHT_COLORS = {
    "no_data": "#e8e8e8",
    0: "#c0392b",           # deep red — no requirements
    "rec_only": "#d35400",  # dark orange — recommendations only
    1: "#e67e22",
    2: "#f39c12",
    3: "#d4c000",
    4: "#a8c000",
    5: "#5cb85c",
    6: "#27ae60",
    7: "#1a9945",
    8: "#0e7a35",           # dark green — all mandatory
}


def score_color_light(mandatory_count, recommended_count, has_data):
    if not has_data:
        return LIGHT_COLORS["no_data"]
    if mandatory_count == 0 and recommended_count == 0:
        return LIGHT_COLORS[0]
    if mandatory_count == 0:
        return LIGHT_COLORS["rec_only"]
    count = min(mandatory_count, 8)
    return LIGHT_COLORS.get(count, LIGHT_COLORS[8])


def load_country_data():
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


def patch_svg_light(countries, scores):
    """Load basemap SVG and patch country fill colors for light theme."""
    if not BASEMAP_PATH.exists():
        print(f"ERROR: Basemap not found at {BASEMAP_PATH}")
        print("Run: python scripts/fetch_basemap.py")
        sys.exit(1)

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(BASEMAP_PATH), parser)
    root = tree.getroot()

    for path_el in root.iter("{http://www.w3.org/2000/svg}path"):
        code = path_el.get("id", "").upper()
        if not code or code == "_OCEAN":
            continue

        if code in countries:
            s = scores[code]
            color = score_color_light(s["mandatory"], s["recommended"], True)
            name = s["name"]
            tooltip = f"{name} | M:{s['mandatory']} R:{s['recommended']}"
        else:
            color = LIGHT_COLORS["no_data"]
            tooltip = path_el.get("data-name", code) + " | No data"

        path_el.set("fill", color)
        path_el.set("stroke", "#ffffff")
        path_el.set("stroke-width", "0.5")

        title_el = path_el.find("{http://www.w3.org/2000/svg}title")
        if title_el is None:
            title_el = etree.SubElement(path_el, "{http://www.w3.org/2000/svg}title")
        title_el.text = tooltip

    # Light background
    for rect in root.iter("{http://www.w3.org/2000/svg}rect"):
        if rect.get("id") == "_ocean":
            rect.set("fill", "#cce5ff")

    root.set("style", "background:#cce5ff")
    return tree


def load_svg_inline(path):
    with open(path, "rb") as f:
        content = f.read().decode("utf-8")
    if content.startswith("<?xml"):
        content = content[content.index("<svg"):]
    return content


def build_table_rows(countries, scores):
    STATUS_ICONS = {
        "mandatory": "✅",
        "recommended": "🔶",
        "informational": "ℹ️",
        "none": "➖",
        "unknown": "❓",
    }
    FLAG_EMOJI = {
        "NL": "🇳🇱", "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪",
        "AU": "🇦🇺", "FR": "🇫🇷", "CA": "🇨🇦", "EU": "🇪🇺",
    }

    rows = []
    for code in sorted(countries.keys()):
        data = countries[code]
        s = scores[code]
        name = data.get("country_name", code)
        flag = FLAG_EMOJI.get(code, "")
        display_name = f"{flag} {name}".strip()

        req_map = {r["standard"]: r for r in data.get("requirements", [])}

        cells = []
        for std in STANDARDS_ORDER:
            req = req_map.get(std)
            if req:
                icon = STATUS_ICONS.get(req.get("status", "unknown"), "❓")
                level = req.get("level", "")
                level_str = f" ({level})" if level and req.get("status") == "mandatory" else ""
                title_attr = req.get("status", "").capitalize() + level_str
                cells.append(
                    f'<td title="{title_attr}" class="status-{req.get("status", "unknown")}">'
                    f'{icon}</td>'
                )
            else:
                cells.append('<td class="status-unknown">❓</td>')

        authority_set = set()
        for req in data.get("requirements", []):
            if req.get("authority"):
                authority_set.add(req["authority"])
        authority_str = "; ".join(sorted(authority_set)) if authority_set else "—"

        applies_set = set()
        for req in data.get("requirements", []):
            for a in req.get("applies_to", []):
                applies_set.add(a.replace("_", " ").title())
        applies_str = ", ".join(sorted(applies_set)) if applies_set else "—"

        row = (
            f'<tr data-mandatory="{s["mandatory"]}" data-recommended="{s["recommended"]}">'
            f'<td><strong>{code}</strong></td>'
            f'<td>{display_name}</td>'
            f'<td>{authority_str}</td>'
            f"{''.join(cells)}"
            f'<td class="applies-col">{applies_str}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def generate_webversion_html(countries, scores, svg_content):
    table_rows = build_table_rows(countries, scores)
    std_header_cells = "".join(
        f'<th class="std-header">{s}</th>' for s in STANDARDS_ORDER
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Email Security World Requirements | passwordscon.org</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                   Ubuntu, Cantarell, sans-serif;
      background: #f8fafc;
      color: #1e293b;
      line-height: 1.6;
      font-size: 16px;
    }}
    .page-header {{
      background: #1e40af;
      color: white;
      padding: 2rem 1.5rem 1.5rem;
    }}
    .page-header h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }}
    .page-header p {{
      color: #bfdbfe;
      font-size: 0.95rem;
    }}
    .page-header a {{ color: #93c5fd; text-decoration: none; }}
    .page-header a:hover {{ text-decoration: underline; }}
    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
    }}
    section {{ margin-bottom: 3rem; }}
    h2 {{
      font-size: 1.1rem;
      font-weight: 600;
      color: #334155;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 0.5rem;
      margin-bottom: 1.25rem;
    }}
    .map-wrap {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }}
    .map-wrap svg {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .map-wrap svg path {{ transition: opacity 0.15s; }}
    .map-wrap svg path:hover {{ opacity: 0.7; cursor: pointer; }}
    .legend {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 1rem 1.25rem;
      margin-top: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }}
    .legend-title {{
      font-size: 0.8rem;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.6rem;
    }}
    .legend-scale {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 1rem;
      margin-bottom: 0.75rem;
    }}
    .legend-item {{ display: flex; align-items: center; gap: 0.35rem; font-size: 0.82rem; color: #475569; }}
    .swatch {{
      width: 14px; height: 14px;
      border-radius: 3px;
      border: 1px solid rgba(0,0,0,0.15);
      flex-shrink: 0;
    }}
    .legend-status {{
      display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem;
      font-size: 0.82rem; color: #475569;
    }}
    .controls {{
      display: flex;
      gap: 1rem;
      align-items: center;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }}
    .controls input[type="text"] {{
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 0.45rem 0.85rem;
      font-size: 0.9rem;
      color: #1e293b;
      min-width: 240px;
      background: white;
    }}
    .controls input[type="text"]:focus {{
      outline: none;
      border-color: #1e40af;
      box-shadow: 0 0 0 2px rgba(30,64,175,0.12);
    }}
    .controls label {{
      font-size: 0.85rem;
      color: #475569;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      cursor: pointer;
    }}
    .table-wrap {{
      overflow-x: auto;
      border-radius: 10px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      font-size: 0.875rem;
    }}
    thead th {{
      background: #f1f5f9;
      padding: 0.6rem 0.75rem;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #64748b;
      font-weight: 600;
      text-align: left;
      border-bottom: 2px solid #e2e8f0;
      white-space: nowrap;
      cursor: pointer;
      user-select: none;
    }}
    thead th:hover {{ background: #e8edf4; color: #334155; }}
    thead th.std-header {{ text-align: center; }}
    tbody tr {{ border-bottom: 1px solid #f1f5f9; }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: #f8fafc; }}
    tbody td {{ padding: 0.55rem 0.75rem; vertical-align: middle; }}
    td[class^="status-"] {{ text-align: center; }}
    .status-mandatory {{ color: #15803d; }}
    .status-recommended {{ color: #b45309; }}
    .status-informational {{ color: #64748b; }}
    .status-none {{ color: #94a3b8; }}
    .status-unknown {{ color: #cbd5e1; }}
    .applies-col {{ font-size: 0.8rem; color: #64748b; }}
    .std-ref-table {{ background: white; }}
    .std-ref-table td a {{ color: #1e40af; text-decoration: none; }}
    .std-ref-table td a:hover {{ text-decoration: underline; }}
    .page-footer {{
      text-align: center;
      padding: 1.5rem;
      font-size: 0.8rem;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
      background: white;
    }}
    .page-footer a {{ color: #1e40af; text-decoration: none; }}
    .hidden {{ display: none !important; }}
    @media (max-width: 768px) {{
      .container {{ padding: 1rem; }}
      table {{ font-size: 0.75rem; }}
      thead th, tbody td {{ padding: 0.4rem 0.5rem; }}
      .page-header h1 {{ font-size: 1.3rem; }}
    }}
  </style>
</head>
<body>
  <div class="page-header">
    <h1>Email Security World Requirements</h1>
    <p>
      Which countries require or recommend SPF, DKIM, DMARC, DANE, MTA-STS, TLS-RPT, BIMI &amp; STARTTLS?
      &nbsp;&middot;&nbsp;
      <a href="https://github.com/thorsheim/email-security-world-requirements" target="_blank">Contribute on GitHub</a>
      &nbsp;&middot;&nbsp;
      <a href="https://internet.nl" target="_blank">Test with internet.nl</a>
      &nbsp;&middot;&nbsp;
      <a href="https://passwordscon.org/mailcheck/" target="_blank">Test with Mailcheck</a>
    </p>
  </div>

  <div class="container">
    <section>
      <h2>World Overview</h2>
      <div class="map-wrap">
        {svg_content}
      </div>
      <div class="legend">
        <div class="legend-title">Map Legend — Mandatory Standards</div>
        <div class="legend-scale">
          <div class="legend-item"><span class="swatch" style="background:#0e7a35"></span> All standards mandatory</div>
          <div class="legend-item"><span class="swatch" style="background:#27ae60"></span> Most standards mandatory</div>
          <div class="legend-item"><span class="swatch" style="background:#5cb85c"></span> Several standards mandatory</div>
          <div class="legend-item"><span class="swatch" style="background:#f39c12"></span> Few standards mandatory</div>
          <div class="legend-item"><span class="swatch" style="background:#d35400"></span> Recommendations only</div>
          <div class="legend-item"><span class="swatch" style="background:#c0392b"></span> No requirements</div>
          <div class="legend-item"><span class="swatch" style="background:#e8e8e8"></span> No data</div>
        </div>
        <div class="legend-status">
          <span>✅ Mandatory</span>
          <span>🔶 Recommended</span>
          <span>ℹ️ Informational</span>
          <span>➖ None</span>
          <span>❓ Unknown / No data</span>
        </div>
      </div>
    </section>

    <section>
      <h2>Requirements Matrix</h2>
      <div class="controls">
        <input type="text" id="search" placeholder="Filter by country or authority…" oninput="filterTable()">
        <label>
          <input type="checkbox" id="hide-no-data" onchange="filterTable()">
          Hide countries with no data
        </label>
      </div>
      <div class="table-wrap">
        <table id="matrix-table">
          <thead>
            <tr>
              <th onclick="sortTable(0)">Code</th>
              <th onclick="sortTable(1)">Country</th>
              <th onclick="sortTable(2)">Authority</th>
              {std_header_cells}
              <th>Applies To</th>
            </tr>
          </thead>
          <tbody>
{table_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section>
      <h2>Standards Reference</h2>
      <div class="table-wrap">
        <table class="std-ref-table">
          <thead>
            <tr>
              <th>Standard</th>
              <th>Full Name</th>
              <th>RFC / Specification</th>
              <th>Key Testing Tools</th>
            </tr>
          </thead>
          <tbody>
            <tr><td><strong>SPF</strong></td><td>Sender Policy Framework</td><td><a href="https://datatracker.ietf.org/doc/html/rfc7208" target="_blank">RFC 7208</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/spf.aspx" target="_blank">MXToolbox</a>, <a href="https://passwordscon.org/mailcheck/" target="_blank">Mailcheck</a></td></tr>
            <tr><td><strong>DKIM</strong></td><td>DomainKeys Identified Mail</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6376" target="_blank">RFC 6376</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/dkim.aspx" target="_blank">MXToolbox</a>, <a href="https://passwordscon.org/mailcheck/" target="_blank">Mailcheck</a></td></tr>
            <tr><td><strong>DMARC</strong></td><td>Domain-based Message Authentication, Reporting and Conformance</td><td><a href="https://datatracker.ietf.org/doc/html/rfc7489" target="_blank">RFC 7489</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://dmarcian.com" target="_blank">dmarcian</a>, <a href="https://dmarc.postmarkapp.com" target="_blank">Postmark DMARC</a></td></tr>
            <tr><td><strong>DANE</strong></td><td>DNS-based Authentication of Named Entities</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6698" target="_blank">RFC 6698</a>, <a href="https://datatracker.ietf.org/doc/html/rfc7671" target="_blank">RFC 7671</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a></td></tr>
            <tr><td><strong>MTA-STS</strong></td><td>Mail Transfer Agent Strict Transport Security</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8461" target="_blank">RFC 8461</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://www.hardenize.com" target="_blank">Hardenize</a></td></tr>
            <tr><td><strong>TLS-RPT</strong></td><td>SMTP TLS Reporting</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8460" target="_blank">RFC 8460</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/TLSRpt.aspx" target="_blank">MXToolbox</a></td></tr>
            <tr><td><strong>BIMI</strong></td><td>Brand Indicators for Message Identification</td><td><a href="https://bimigroup.org" target="_blank">BIMI Group</a></td><td><a href="https://bimigroup.org/bimi-generator/" target="_blank">BIMI Checker</a>, <a href="https://mxtoolbox.com/bimi.aspx" target="_blank">MXToolbox</a></td></tr>
            <tr><td><strong>STARTTLS</strong></td><td>SMTP STARTTLS (Opportunistic TLS)</td><td><a href="https://datatracker.ietf.org/doc/html/rfc3207" target="_blank">RFC 3207</a>, <a href="https://datatracker.ietf.org/doc/html/rfc8314" target="_blank">RFC 8314</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://passwordscon.org/mailcheck/" target="_blank">Mailcheck</a></td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>

  <footer class="page-footer">
    <p>
      Data licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">CC-BY-4.0</a> &nbsp;&middot;&nbsp;
      <a href="https://github.com/thorsheim/email-security-world-requirements" target="_blank">Contribute on GitHub</a> &nbsp;&middot;&nbsp;
      Created by <a href="https://passwordscon.org" target="_blank">Per Thorsheim</a> &nbsp;&middot;&nbsp;
      Test your domain at <a href="https://internet.nl" target="_blank">internet.nl</a>
    </p>
  </footer>

  <script>
    function filterTable() {{
      const q = document.getElementById('search').value.toLowerCase();
      const hideNoData = document.getElementById('hide-no-data').checked;
      document.querySelectorAll('#matrix-table tbody tr').forEach(row => {{
        const text = row.textContent.toLowerCase();
        const mandatory = parseInt(row.dataset.mandatory || '0');
        const recommended = parseInt(row.dataset.recommended || '0');
        const noData = mandatory === 0 && recommended === 0;
        row.classList.toggle('hidden', (!q || !text.includes(q)) && q
          || (hideNoData && noData)
          || (q && !text.includes(q)));
      }});
    }}

    let sortDir = {{}};
    function sortTable(col) {{
      const table = document.getElementById('matrix-table');
      const tbody = table.tBodies[0];
      const rows = Array.from(tbody.rows);
      const asc = (sortDir[col] = !sortDir[col]);
      rows.sort((a, b) => {{
        const av = a.cells[col]?.textContent.trim() || '';
        const bv = b.cells[col]?.textContent.trim() || '';
        return asc ? av.localeCompare(bv) : bv.localeCompare(av);
      }});
      rows.forEach(r => tbody.appendChild(r));
    }}
  </script>
</body>
</html>
"""


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    countries = load_country_data()
    scores = compute_scores(countries)
    print(f"Loaded {len(countries)} country files.")

    # Generate light-theme SVG
    tree = patch_svg_light(countries, scores)
    tree.write(str(OUTPUT_SVG), xml_declaration=True, encoding="utf-8", pretty_print=True)
    print(f"Written: {OUTPUT_SVG}")

    # Load SVG for inlining
    svg_content = load_svg_inline(OUTPUT_SVG)

    # Generate HTML
    html = generate_webversion_html(countries, scores, svg_content)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written: {OUTPUT_HTML}")
    print(f"\nWebversion ready. Upload the contents of {OUTPUT_DIR}/ to your server.")


if __name__ == "__main__":
    main()
