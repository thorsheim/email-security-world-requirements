#!/usr/bin/env python3
"""
Inject the requirements matrix table into README.md between sentinel comments:
    <!-- BEGIN_MATRIX -->
    <!-- END_MATRIX -->

Usage:
    python scripts/generate_readme_table.py

The table is regenerated from data/countries/*.yaml on every run.
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES_DIR = REPO_ROOT / "data" / "countries"
README_PATH = REPO_ROOT / "README.md"

BEGIN_SENTINEL = "<!-- BEGIN_MATRIX -->"
END_SENTINEL = "<!-- END_MATRIX -->"

STANDARDS_ORDER = ["SPF", "DKIM", "DMARC", "DANE", "MTA-STS", "TLS-RPT", "BIMI", "STARTTLS"]
STANDARDS_DOCS = {
    "SPF": "docs/standards/spf.md",
    "DKIM": "docs/standards/dkim.md",
    "DMARC": "docs/standards/dmarc.md",
    "DANE": "docs/standards/dane.md",
    "MTA-STS": "docs/standards/mta-sts.md",
    "TLS-RPT": "docs/standards/tls-rpt.md",
    "BIMI": "docs/standards/bimi.md",
    "STARTTLS": "docs/standards/starttls.md",
}

STATUS_ICONS = {
    "mandatory": "✅ M",
    "recommended": "🔶 R",
    "informational": "ℹ️",
    "none": "➖",
    "unknown": "❓",
}

FLAG_EMOJI = {
    "NL": "🇳🇱", "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪",
    "AU": "🇦🇺", "FR": "🇫🇷", "CA": "🇨🇦", "EU": "🇪🇺",
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


def build_matrix_table(countries):
    # Header row
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

        req_map = {r["standard"]: r for r in data.get("requirements", [])}

        # Authority summary
        authority_set = set()
        for req in data.get("requirements", []):
            if req.get("authority"):
                authority_set.add(req["authority"])
        authority_str = "; ".join(sorted(authority_set)) if authority_set else "—"

        # Per-standard cells
        cells = []
        for std in STANDARDS_ORDER:
            req = req_map.get(std)
            if req:
                icon = STATUS_ICONS.get(req.get("status", "unknown"), "❓")
                level = req.get("level", "")
                if level and req.get("status") == "mandatory":
                    icon += f" ({level})"
            else:
                icon = "❓"
            cells.append(icon)

        # Applies-to summary
        applies_set = set()
        for req in data.get("requirements", []):
            for a in req.get("applies_to", []):
                applies_set.add(a.replace("_", " ").title())
        applies_str = ", ".join(sorted(applies_set)) if applies_set else "—"

        row = f"| {display_name} | {authority_str} | " + " | ".join(cells) + f" | {applies_str} |"
        rows.append(row)

    rows.append("")
    rows.append(
        "**Legend:** ✅ M = Mandatory &nbsp;·&nbsp; "
        "🔶 R = Recommended &nbsp;·&nbsp; "
        "ℹ️ = Informational &nbsp;·&nbsp; "
        "➖ = No requirement &nbsp;·&nbsp; "
        "❓ = No data / Unknown"
    )

    return "\n".join(rows)


def inject_table(readme_content, table_content):
    begin_idx = readme_content.find(BEGIN_SENTINEL)
    end_idx = readme_content.find(END_SENTINEL)

    if begin_idx == -1 or end_idx == -1:
        print(
            f"ERROR: Could not find sentinels '{BEGIN_SENTINEL}' and/or '{END_SENTINEL}' in README.md"
        )
        sys.exit(1)

    before = readme_content[: begin_idx + len(BEGIN_SENTINEL)]
    after = readme_content[end_idx:]

    return before + "\n\n" + table_content + "\n\n" + after


def main():
    countries = load_country_data()
    print(f"Loaded {len(countries)} country files.")

    table = build_matrix_table(countries)

    with open(README_PATH, encoding="utf-8") as f:
        readme = f.read()

    updated = inject_table(readme, table)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"Updated matrix table in {README_PATH}")


if __name__ == "__main__":
    main()
