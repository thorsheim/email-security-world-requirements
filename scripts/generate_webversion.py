#!/usr/bin/env python3
"""
Generate webversion/index.html for deployment to
passwordscon.org/mailrequirements/ (WordPress site, static subfolder).

This produces a fully self-contained HTML page with all CSS and JS inlined.
Design: clean neutral / light theme.

Usage:
    python scripts/generate_webversion.py

Requirements: pyyaml
"""

import html as _html
from pathlib import Path
from urllib.parse import urlparse

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES_DIR = REPO_ROOT / "data" / "countries"
STANDARDS_PATH = REPO_ROOT / "data" / "standards.yaml"
OUTPUT_DIR = REPO_ROOT / "webversion"
OUTPUT_HTML = OUTPUT_DIR / "index.html"

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


def compute_scores(countries):
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



FLAG_EMOJI = {
    "NL": "🇳🇱", "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪",
    "AU": "🇦🇺", "FR": "🇫🇷", "CA": "🇨🇦", "EU": "🇪🇺",
    "NO": "🇳🇴",
    "NZ": "🇳🇿",
}


def build_table_rows(countries, scores):
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
        flag = FLAG_EMOJI.get(code, "")
        display_name = f"{flag} {name}".strip()
        authority_urls = data.get("authorities", {})

        best_map = best_req_per_standard(data.get("requirements", []))

        cells = []
        for std in STANDARDS_ORDER:
            req = best_map.get(std)
            if req:
                icon = STATUS_ICONS.get(req.get("status", "unknown"), "❓")
                level = req.get("level", "")
                level_str = f" ({level})" if level and req.get("status") == "mandatory" else ""
                title_attr = h(req.get("status", "").capitalize() + level_str)
                cells.append(
                    f'<td title="{title_attr}" class="status-{req.get("status", "unknown")}">'
                    f'{icon}</td>'
                )
            else:
                cells.append('<td class="status-unknown">❓</td>')

        seen_auths = list(dict.fromkeys(
            req.get("authority") for req in data.get("requirements", [])
            if req.get("authority")
        ))
        authority_str = " · ".join(link_authority_html(a, authority_urls) for a in seen_auths) if seen_auths else "—"

        applies_set = set()
        for req in data.get("requirements", []):
            for a in req.get("applies_to", []):
                applies_set.add(h(a.replace("_", " ").title()))
        applies_str = ", ".join(sorted(applies_set)) if applies_set else "—"

        row = (
            f'<tr data-mandatory="{s["mandatory"]}" data-recommended="{s["recommended"]}">'
            f'<td><strong>{h(code)}</strong></td>'
            f'<td>{h(display_name)}</td>'
            f'<td>{authority_str}</td>'
            f"{''.join(cells)}"
            f'<td class="applies-col">{applies_str}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def build_details_rows(countries):
    """Build HTML rows for the per-(country, authority, standard) details table."""
    STATUS_LABELS = {
        "mandatory": ("✅ Mandatory", "status-mandatory"),
        "recommended": ("🔶 Recommended", "status-recommended"),
    }
    rows = []
    for code in sorted(countries.keys()):
        data = countries[code]
        name = data.get("country_name", code)
        flag = FLAG_EMOJI.get(code, "")
        display_name = f"{flag} {name}".strip()
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

            country_cell = f"<strong>{h(display_name)}</strong>" if first else ""
            first = False

            rows.append(
                f'<tr>'
                f'<td class="details-country">{country_cell}</td>'
                f'<td>{auth_html}</td>'
                f'<td><strong>{h(standard)}</strong></td>'
                f'<td class="{css}">{h(label)}</td>'
                f'<td class="details-policy">{policy}</td>'
                f'<td class="details-notes">{notes}</td>'
                f'<td>{source_html}</td>'
                f'</tr>'
            )
    return "\n".join(rows)


def generate_webversion_html(countries, scores):
    table_rows = build_table_rows(countries, scores)
    details_rows = build_details_rows(countries)
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
    .details-country {{ font-weight: 600; white-space: nowrap; }}
    .details-policy {{ font-size: 0.8rem; color: #475569; white-space: nowrap; }}
    .details-notes {{ font-size: 0.8rem; color: #64748b; max-width: 320px; }}
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
      <h2>Policy Details — Mandatory &amp; Recommended</h2>
      <p style="font-size:0.875rem;color:#64748b;margin-bottom:1rem">
        Each mandatory or recommended entry by country and authority, with the specific policy document,
        a description, and a direct link to the source. Where multiple agencies cover the same standard,
        each is listed on its own row.
      </p>
      <div class="table-wrap">
        <table>
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
            <tr><td><strong>STARTTLS</strong></td><td>SMTP STARTTLS (Opportunistic TLS)</td><td><a href="https://datatracker.ietf.org/doc/html/rfc3207" target="_blank">RFC 3207</a>, <a href="https://datatracker.ietf.org/doc/html/rfc8314" target="_blank">RFC 8314</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://passwordscon.org/mailcheck/" target="_blank">Mailcheck</a></td></tr>
            <tr><td><strong>DANE</strong></td><td>DNS-based Authentication of Named Entities</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6698" target="_blank">RFC 6698</a>, <a href="https://datatracker.ietf.org/doc/html/rfc7671" target="_blank">RFC 7671</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a></td></tr>
            <tr><td><strong>DNSSEC</strong></td><td>DNS Security Extensions</td><td><a href="https://datatracker.ietf.org/doc/html/rfc4033" target="_blank">RFC 4033–4035</a>, <a href="https://datatracker.ietf.org/doc/html/rfc9364" target="_blank">RFC 9364</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://dnsviz.net" target="_blank">DNSViz</a>, <a href="https://dnssec-analyzer.verisignlabs.com" target="_blank">Verisign Analyzer</a></td></tr>
            <tr><td><strong>MTA-STS</strong></td><td>Mail Transfer Agent Strict Transport Security</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8461" target="_blank">RFC 8461</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://www.hardenize.com" target="_blank">Hardenize</a></td></tr>
            <tr><td><strong>TLS-RPT</strong></td><td>SMTP TLS Reporting</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8460" target="_blank">RFC 8460</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/TLSRpt.aspx" target="_blank">MXToolbox</a></td></tr>
            <tr><td><strong>CAA</strong></td><td>Certification Authority Authorization</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8659" target="_blank">RFC 8659</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a>, <a href="https://mxtoolbox.com/caa.aspx" target="_blank">MXToolbox</a>, <a href="https://sslmate.com/caa/" target="_blank">SSLMate CAA Gen</a></td></tr>
            <tr><td><strong>IPv6</strong></td><td>IPv6 Support for Email</td><td><a href="https://datatracker.ietf.org/doc/html/rfc8200" target="_blank">RFC 8200</a>, <a href="https://datatracker.ietf.org/doc/html/rfc3596" target="_blank">RFC 3596</a></td><td><a href="https://internet.nl" target="_blank">internet.nl</a></td></tr>
            <tr><td><strong>RPKI</strong></td><td>Resource Public Key Infrastructure</td><td><a href="https://datatracker.ietf.org/doc/html/rfc6480" target="_blank">RFC 6480 / 9582</a></td><td><a href="https://rpki.cloudflare.com" target="_blank">Cloudflare RPKI</a>, <a href="https://rpki-validator.ripe.net" target="_blank">RIPE NCC RPKI</a></td></tr>
            <tr><td><strong>ASPA</strong></td><td>Autonomous System Provider Authorization</td><td><a href="https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-profile/" target="_blank">IETF SIDROPS draft</a></td><td><a href="https://rpki-validator.ripe.net" target="_blank">RIPE NCC RPKI</a></td></tr>
            <tr><td><strong>BIMI</strong></td><td>Brand Indicators for Message Identification</td><td><a href="https://bimigroup.org" target="_blank">BIMI Group</a></td><td><a href="https://bimigroup.org/bimi-generator/" target="_blank">BIMI Checker</a>, <a href="https://mxtoolbox.com/bimi.aspx" target="_blank">MXToolbox</a></td></tr>
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
        row.classList.toggle('hidden', (q && !text.includes(q)) || (hideNoData && noData));
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

    html = generate_webversion_html(countries, scores)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written: {OUTPUT_HTML}")
    print(f"\nWebversion ready. Upload {OUTPUT_HTML} to your server.")


if __name__ == "__main__":
    main()
