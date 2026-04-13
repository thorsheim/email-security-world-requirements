#!/usr/bin/env python3
"""
Inject the requirements matrix table and policy details table into README.md.

Sentinels:
    <!-- BEGIN_MATRIX --> ... <!-- END_MATRIX -->
    <!-- BEGIN_DETAILS --> ... <!-- END_DETAILS -->

Usage:
    python scripts/generate_readme_table.py

The tables are regenerated from data/countries/*.yaml on every run.
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES_DIR = REPO_ROOT / "data" / "countries"
README_PATH = REPO_ROOT / "README.md"

BEGIN_MATRIX = "<!-- BEGIN_MATRIX -->"
END_MATRIX = "<!-- END_MATRIX -->"
BEGIN_DETAILS = "<!-- BEGIN_DETAILS -->"
END_DETAILS = "<!-- END_DETAILS -->"

STANDARDS_ORDER = ["SPF", "DKIM", "DMARC", "STARTTLS", "DANE", "DNSSEC", "MTA-STS", "TLS-RPT", "CAA", "IPv6", "RPKI", "ASPA", "BIMI"]
STANDARDS_DOCS = {
    "SPF": "docs/standards/spf.md",
    "DKIM": "docs/standards/dkim.md",
    "DMARC": "docs/standards/dmarc.md",
    "STARTTLS": "docs/standards/starttls.md",
    "DANE": "docs/standards/dane.md",
    "DNSSEC": "docs/standards/dnssec.md",
    "MTA-STS": "docs/standards/mta-sts.md",
    "TLS-RPT": "docs/standards/tls-rpt.md",
    "CAA": "docs/standards/caa.md",
    "IPv6": "docs/standards/ipv6.md",
    "RPKI": "docs/standards/rpki.md",
    "ASPA": "docs/standards/aspa.md",
    "BIMI": "docs/standards/bimi.md",
}

STATUS_ICONS = {
    "mandatory": "✅ M",
    "recommended": "🔶 R",
    "informational": "ℹ️",
    "none": "➖",
    "unknown": "❓",
}

STATUS_PRIORITY = {
    "mandatory": 4,
    "recommended": 3,
    "informational": 2,
    "none": 1,
    "unknown": 0,
}

FLAG_EMOJI = {
    "NL": "🇳🇱", "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪",
    "AU": "🇦🇺", "FR": "🇫🇷", "CA": "🇨🇦", "EU": "🇪🇺",
    "NO": "🇳🇴",
    "NZ": "🇳🇿",
}


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


def best_req_per_standard(requirements):
    """For each standard, return the single requirement entry with the highest status.
    When two authorities cover the same standard, the highest status wins."""
    groups = {}
    for req in requirements:
        std = req.get("standard")
        if not std:
            continue
        if std not in groups:
            groups[std] = req
        else:
            existing_priority = STATUS_PRIORITY.get(groups[std].get("status", "unknown"), 0)
            new_priority = STATUS_PRIORITY.get(req.get("status", "unknown"), 0)
            if new_priority > existing_priority:
                groups[std] = req
    return groups


def link_authority(name, authority_urls):
    """Return a markdown link if a URL is available, otherwise plain text."""
    url = authority_urls.get(name)
    if url:
        return f"[{name}]({url})"
    return name


def build_authority_str(requirements, authority_urls):
    """Build a linked authority string showing all unique authorities for a country."""
    seen = []
    for req in requirements:
        auth = req.get("authority")
        if auth and auth not in seen:
            seen.append(auth)
    if not seen:
        return "—"
    return " · ".join(link_authority(a, authority_urls) for a in seen)


def build_matrix_table(countries):
    std_headers = " | ".join(
        f"[{s}]({STANDARDS_DOCS[s]})" for s in STANDARDS_ORDER
    )
    header = f"| Country | Authority | {std_headers} | Applies To |"

    sep_stds = " | ".join(":---:" for _ in STANDARDS_ORDER)
    separator = f"| :--- | :--- | {sep_stds} | :--- |"

    rows = [header, separator]

    for code in sorted(countries.keys()):
        data = countries[code]
        name = data.get("country_name", code)
        flag = FLAG_EMOJI.get(code, "")
        display_name = f"{flag} {name}".strip()
        authority_urls = data.get("authorities", {})

        best_map = best_req_per_standard(data.get("requirements", []))
        authority_str = build_authority_str(data.get("requirements", []), authority_urls)

        cells = []
        for std in STANDARDS_ORDER:
            req = best_map.get(std)
            if req:
                icon = STATUS_ICONS.get(req.get("status", "unknown"), "❓")
                level = req.get("level", "")
                if level and req.get("status") == "mandatory":
                    icon += f" ({level})"
            else:
                icon = "❓"
            cells.append(icon)

        applies_set = set()
        for req in data.get("requirements", []):
            for a in req.get("applies_to", []):
                applies_set.add(a.replace("_", " ").title())
        applies_str = ", ".join(sorted(applies_set)) if applies_set else "—"

        row = f"| {display_name} | {authority_str} | " + " | ".join(cells) + f" | {applies_str} |"
        rows.append(row)

    rows.append("")
    rows.append("### Legend")
    rows.append("")
    rows.append("**Status icons**")
    rows.append("")
    rows.append("| Icon | Status | Meaning |")
    rows.append("| :---: | :--- | :--- |")
    rows.append("| ✅ M | **Mandatory** | Legally or policy-required; non-compliance has consequences |")
    rows.append("| 🔶 R | **Recommended** | Official guidance or best-practice document published by a government body |")
    rows.append("| ℹ️ | **Informational** | Mentioned in an official document but no clear directive |")
    rows.append("| ➖ | **None** | Explicitly confirmed as not required |")
    rows.append("| ❓ | **Unknown** | No official data found |")
    rows.append("")
    rows.append("**Standards grouping**")
    rows.append("")
    rows.append("| Group | Standards | Purpose |")
    rows.append("| :--- | :--- | :--- |")
    rows.append("| Sender authentication | SPF · DKIM · DMARC | Verify who sent the message |")
    rows.append("| Transport security | STARTTLS · DANE · DNSSEC · MTA-STS · TLS-RPT | Encrypt and secure delivery |")
    rows.append("| Infrastructure | CAA · IPv6 | Certificate issuance restriction; dual-stack mail reachability |")
    rows.append("| Routing security | RPKI · ASPA | Protect against BGP hijacking and route leaks |")
    rows.append("| Emerging | BIMI | Visual brand verification |")
    rows.append("")
    rows.append("> DANE requires DNSSEC — if a country mandates DANE, DNSSEC is implicitly required too. "
                "ASPA extends RPKI ROA and is still in IETF standardization as of 2026.")

    return "\n".join(rows)


def truncate(text, max_len=140):
    """Truncate text to max_len characters, preserving word boundaries."""
    if not text:
        return ""
    text = " ".join(text.split())  # normalise whitespace
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return cut + "…"


def build_details_table(countries):
    """Build per-(country, authority, standard) details for mandatory/recommended entries."""

    rows = []
    rows.append("| Country | Authority | Standard | Status | Policy Document | Description | Source |")
    rows.append("| :--- | :--- | :--- | :---: | :--- | :--- | :--- |")

    for code in sorted(countries.keys()):
        data = countries[code]
        name = data.get("country_name", code)
        flag = FLAG_EMOJI.get(code, "")
        display_name = f"{flag} {name}".strip()
        authority_urls = data.get("authorities", {})

        first_row_for_country = True

        for req in data.get("requirements", []):
            status = req.get("status", "unknown")
            if status not in ("mandatory", "recommended"):
                continue

            authority = req.get("authority", "—")
            auth_linked = link_authority(authority, authority_urls)
            standard = req.get("standard", "")
            std_doc = STANDARDS_DOCS.get(standard, "")
            std_linked = f"[{standard}]({std_doc})" if std_doc else standard

            status_icon = STATUS_ICONS.get(status, "❓")
            level = req.get("level", "")
            if level and status == "mandatory":
                status_icon += f" ({level})"

            policy_doc = req.get("policy_document", "")

            notes = req.get("notes", "")
            description = truncate(notes) if notes else ""

            refs = req.get("references", [])
            if refs:
                first_ref = refs[0]
                ref_title = first_ref.get("title", "Source")
                ref_url = first_ref.get("url", "")
                source = f"[{ref_title}]({ref_url})" if ref_url else ref_title
            else:
                source = ""

            country_cell = display_name if first_row_for_country else ""
            first_row_for_country = False

            row = f"| {country_cell} | {auth_linked} | {std_linked} | {status_icon} | {policy_doc} | {description} | {source} |"
            rows.append(row)

    return "\n".join(rows)


def inject_section(content, begin_sentinel, end_sentinel, new_content):
    begin_idx = content.find(begin_sentinel)
    end_idx = content.find(end_sentinel)

    if begin_idx == -1 or end_idx == -1:
        print(f"WARNING: Could not find sentinels '{begin_sentinel}' / '{end_sentinel}' — skipping.")
        return content

    before = content[: begin_idx + len(begin_sentinel)]
    after = content[end_idx:]
    return before + "\n\n" + new_content + "\n\n" + after


def main():
    countries = load_country_data()
    print(f"Loaded {len(countries)} country files.")

    matrix = build_matrix_table(countries)
    details = build_details_table(countries)

    with open(README_PATH, encoding="utf-8") as f:
        readme = f.read()

    readme = inject_section(readme, BEGIN_MATRIX, END_MATRIX, matrix)
    readme = inject_section(readme, BEGIN_DETAILS, END_DETAILS, details)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"Updated matrix and details tables in {README_PATH}")


if __name__ == "__main__":
    main()
