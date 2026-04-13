#!/usr/bin/env python3
"""
Generate docs/index.html (interactive GitHub Pages page) from data/countries/*.yaml.

Usage:
    python scripts/generate_map.py

Requirements: pyyaml
"""

import html as _html
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES_DIR = REPO_ROOT / "data" / "countries"
STANDARDS_PATH = REPO_ROOT / "data" / "standards.yaml"
OUTPUT_HTML = REPO_ROOT / "docs" / "index.html"

STANDARDS_ORDER = ["SPF", "DKIM", "DMARC", "STARTTLS", "DANE", "DNSSEC", "MTA-STS", "TLS-RPT", "CAA", "IPv6", "RPKI", "ASPA", "BIMI"]

_SAFE_SCHEMES = {"http", "https"}


def h(s) -> str:
    """HTML-escape a value before insertion into an HTML context."""
    return _html.escape(str(s), quote=True)


def safe_url(url: str) -> str:
    """Return url only if scheme is http/https, else empty string."""
    try:
        scheme = urlparse(url).scheme.lower()
    except Exception:
        return ""
    return url if scheme in _SAFE_SCHEMES else ""


def truncate(text, max_len=140) -> str:
    """Truncate to max_len chars on a word boundary."""
    if not text:
        return ""
    text = " ".join(str(text).split())
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


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
    """For each country, compute mandatory and recommended counts.
    When multiple authorities cover the same standard, only the highest status counts."""
    scores = {}
    for code, data in countries.items():
        mandatory = 0
        recommended = 0
        for req in best_req_per_standard(data.get("requirements", [])).values():
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



STATUS_PRIORITY = {
    "mandatory": 4,
    "recommended": 3,
    "informational": 2,
    "none": 1,
    "unknown": 0,
}


def best_req_per_standard(requirements):
    """For each standard return the entry with the highest status."""
    groups = {}
    for req in requirements:
        std = req.get("standard")
        if not std:
            continue
        if std not in groups:
            groups[std] = req
        else:
            if STATUS_PRIORITY.get(req.get("status", "unknown"), 0) > STATUS_PRIORITY.get(groups[std].get("status", "unknown"), 0):
                groups[std] = req
    return groups


def link_authority_html(name, authority_urls):
    url = safe_url(authority_urls.get(name, ""))
    if url:
        return f'<a href="{h(url)}" target="_blank">{h(name)}</a>'
    return h(name)


def build_table_rows_html(countries, scores):
    """Build HTML table rows for the interactive page."""
    STATUS_ICONS = {
        "mandatory": "✅",
        "recommended": "🟡",
        "informational": "ℹ️",
        "none": "➖",
        "unknown": "✗",
    }

    rows = []
    for code in sorted(countries.keys()):
        data = countries[code]
        s = scores[code]
        name = data.get("country_name", code)
        authority_urls = data.get("authorities", {})

        best_map = best_req_per_standard(data.get("requirements", []))

        cells = []
        for std in STANDARDS_ORDER:
            req = best_map.get(std)
            if req:
                icon = STATUS_ICONS.get(req.get("status", "unknown"), "❓")
                level = req.get("level", "")
                level_str = f" ({level})" if level else ""
                status_label = h(req.get("status", "unknown").capitalize() + level_str)
                cells.append(
                    f'<td title="{status_label}" class="status-{req.get("status", "unknown")}">'
                    f'{icon}</td>'
                )
            else:
                cells.append('<td class="status-unknown">✗</td>')

        applies_set = set()
        for req in data.get("requirements", []):
            for a in req.get("applies_to", []):
                applies_set.add(h(a.replace("_", " ").title()))
        applies_str = ", ".join(sorted(applies_set)) if applies_set else "—"

        # Collect unique authorities in order of appearance, linked
        seen_auths = list(dict.fromkeys(
            req.get("authority") for req in data.get("requirements", [])
            if req.get("authority")
        ))
        authority_str = " · ".join(link_authority_html(a, authority_urls) for a in seen_auths) if seen_auths else "—"

        row = (
            f'<tr data-mandatory="{s["mandatory"]}" data-recommended="{s["recommended"]}">'
            f'<td><strong>{h(code)}</strong></td>'
            f'<td>{h(name)}</td>'
            f'<td>{authority_str}</td>'
            f"{''.join(cells)}"
            f'<td>{applies_str}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def build_details_rows_html(countries):
    """Build HTML rows for the per-(country, authority, standard) details table."""
    STATUS_LABELS = {
        "mandatory": ("✅ Mandatory", "status-mandatory"),
        "recommended": ("🟡 Recommended", "status-recommended"),
    }
    rows = []
    for code in sorted(countries.keys()):
        data = countries[code]
        name = data.get("country_name", code)
        authority_urls = data.get("authorities", {})
        first = True

        for req in data.get("requirements", []):
            status = req.get("status", "unknown")
            if status not in ("mandatory", "recommended"):
                continue

            authority = req.get("authority", "—")
            auth_html = link_authority_html(authority, authority_urls)
            standard = req.get("standard", "")
            level = req.get("level", "")
            scope = req.get("scope", "")
            label, css = STATUS_LABELS[status]
            if level and status == "mandatory":
                label += f" ({level})"
            elif scope:
                label += f" ({scope})"
            policy = h(req.get("policy_document", ""))
            notes = h(truncate(req.get("notes", "") or ""))

            refs = req.get("references", [])
            if refs:
                r0 = refs[0]
                rtitle = h(r0.get("title", "Source"))
                rurl = safe_url(r0.get("url", ""))
                source_html = f'<a href="{h(rurl)}" target="_blank">{rtitle}</a>' if rurl else rtitle
            else:
                source_html = "—"

            country_cell = f"<strong>{h(code)}</strong> {h(name)}" if first else ""
            first = False

            rows.append(
                f'<tr>'
                f'<td>{country_cell}</td>'
                f'<td>{auth_html}</td>'
                f'<td>{h(standard)}</td>'
                f'<td class="{css}">{h(label)}</td>'
                f'<td>{policy}</td>'
                f'<td class="details-notes">{notes}</td>'
                f'<td>{source_html}</td>'
                f'</tr>'
            )
    return "\n".join(rows)


def generate_index_html(countries, scores):
    """Generate the GitHub Pages index.html."""

    table_rows = build_table_rows_html(countries, scores)
    details_rows = build_details_rows_html(countries)

    std_header_cells = "".join(
        f'<th class="std-header" title="{s}">{s}</th>' for s in STANDARDS_ORDER
    )

    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Email Security World Requirements</title>
  <script>
    // Restore saved theme before first paint to avoid flash
    (function() {{
      const t = localStorage.getItem('theme');
      if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t;
    }})();
  </script>
  <style>
    /* ── Dark theme (default) ── */
    :root, html[data-theme="dark"] {{
      --bg:               #0f1117;
      --surface:          #1a1a2e;
      --surface-alt:      #0f1117;
      --border:           #2e3050;
      --text:             #e2e8f0;
      --text-muted:       #94a3b8;
      --text-heading:     #00e676;
      --blue:             #60a5fa;
      --hover-bg:         rgba(255,255,255,0.04);
      --color-mandatory:  #4ade80;
      --color-recommended:#fbbf24;
      --color-info:       #94a3b8;
      --color-none:       #475569;
      --color-unknown:    #f87171;
      --btn-bg:           #2e3050;
      --btn-text:         #e2e8f0;
      --btn-border:       #4a4f7a;
      --btn-hover-bg:     #3d4270;
    }}

    /* ── Light theme ── */
    html[data-theme="light"] {{
      --bg:               #f0f4f8;
      --surface:          #ffffff;
      --surface-alt:      #e8edf3;
      --border:           #c8d3df;
      --text:             #1e293b;
      --text-muted:       #4a5568;
      --text-heading:     #1a5c96;
      --blue:             #1d4ed8;
      --hover-bg:         rgba(0,0,0,0.03);
      --color-mandatory:  #15803d;
      --color-recommended:#92400e;
      --color-info:       #475569;
      --color-none:       #94a3b8;
      --color-unknown:    #b91c1c;
      --btn-bg:           #ffffff;
      --btn-text:         #1e293b;
      --btn-border:       #c8d3df;
      --btn-hover-bg:     #e8edf3;
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
      padding: 1.25rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .header-text h1 {{ font-size: 1.5rem; color: var(--text-heading); margin-bottom: 0.2rem; }}
    .header-text p {{ color: var(--text-muted); font-size: 0.875rem; }}
    header a {{ color: var(--blue); text-decoration: none; }}
    header a:hover {{ text-decoration: underline; }}
    #theme-btn {{
      flex-shrink: 0;
      background: var(--btn-bg);
      border: 1px solid var(--btn-border);
      color: var(--btn-text);
      border-radius: 6px;
      padding: 0.4rem 0.85rem;
      font-size: 0.85rem;
      cursor: pointer;
      white-space: nowrap;
      transition: background 0.15s;
    }}
    #theme-btn:hover {{ background: var(--btn-hover-bg); }}
    main {{ padding: 2rem; max-width: 1600px; margin: 0 auto; }}
    section {{ margin-bottom: 3rem; }}
    h2 {{ font-size: 1.1rem; color: var(--text-muted); text-transform: uppercase;
          letter-spacing: 0.08em; margin-bottom: 1rem; border-bottom: 1px solid var(--border);
          padding-bottom: 0.5rem; }}
    .controls {{
      display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center;
    }}
    .controls input[type="text"] {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      padding: 0.4rem 0.8rem;
      font-size: 0.9rem;
      min-width: 220px;
    }}
    .controls input[type="text"]::placeholder {{ color: var(--text-muted); }}
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
      background: var(--surface-alt);
      padding: 0.6rem 0.75rem;
      text-align: left;
      font-size: 0.72rem;
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
    tbody tr:hover {{ background: var(--hover-bg); }}
    tbody td {{ padding: 0.55rem 0.75rem; vertical-align: middle; }}
    tbody td.std-header, td[class^="status-"] {{ text-align: center; }}
    .status-mandatory    {{ color: var(--color-mandatory); }}
    .status-recommended  {{ color: var(--color-recommended); }}
    .status-informational {{ color: var(--color-info); }}
    .status-none         {{ color: var(--color-none); }}
    .status-unknown      {{ color: var(--color-unknown); }}
    .matrix-legend {{
      display: flex; flex-wrap: wrap; gap: 0.4rem 1.5rem;
      font-size: 0.82rem; margin-bottom: 0.75rem;
      padding: 0.6rem 1rem;
      background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
    }}
    .matrix-legend span {{ white-space: nowrap; }}
    .details-notes {{ font-size: 0.8rem; color: var(--text-muted); max-width: 320px; }}
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
      header {{ padding: 1rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-text">
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
    </div>
    <button id="theme-btn" onclick="toggleTheme()" aria-label="Toggle light/dark theme">☀️ Light</button>
  </header>

  <main>
    <section id="table-section">
      <h2>Requirements Matrix</h2>
      <div class="matrix-legend">
        <span class="status-mandatory">✅ Mandatory</span>
        <span class="status-recommended">🟡 Recommended</span>
        <span class="status-informational">ℹ️ Informational</span>
        <span class="status-none">➖ None confirmed</span>
        <span class="status-unknown">✗ No data found</span>
      </div>
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

    <section id="details-section">
      <h2>Policy Details — Mandatory &amp; Recommended</h2>
      <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1rem">
        Per-country, per-authority breakdown of each mandatory or recommended standard with policy document names and direct source links.
        Where multiple authorities cover the same standard, each entry is listed separately.
      </p>
      <table id="details-table">
        <thead>
          <tr>
            <th>Country</th>
            <th>Authority</th>
            <th>Standard</th>
            <th>Status</th>
            <th>Policy Document</th>
            <th>Description</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
{details_rows}
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
          <tr><td><a href="standards/ipv6.md">IPv6</a></td><td>IPv6 Support for Email</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8200" target="_blank">RFC 8200</a>, <a href="https://datatracker.ietf.org/doc/html/rfc3596" target="_blank">RFC 3596</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a></td></tr>
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
    // ── Theme toggle ──
    function updateThemeBtn() {{
      const dark = document.documentElement.dataset.theme === 'dark';
      document.getElementById('theme-btn').textContent = dark ? '☀️ Light' : '🌙 Dark';
    }}
    function toggleTheme() {{
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      localStorage.setItem('theme', next);
      updateThemeBtn();
    }}
    updateThemeBtn();

    // ── Filter ──
    function filterTable() {{
      const q = document.getElementById('search').value.toLowerCase();
      const hideNoData = document.getElementById('hide-no-data').checked;
      document.querySelectorAll('#matrix-table tbody tr').forEach(row => {{
        const text = row.textContent.toLowerCase();
        const noData = parseInt(row.dataset.mandatory || '0') === 0
                    && parseInt(row.dataset.recommended || '0') === 0;
        row.classList.toggle('hidden', (q && !text.includes(q)) || (hideNoData && noData));
      }});
    }}

    // ── Sort ──
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

    html = generate_index_html(countries, scores)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
