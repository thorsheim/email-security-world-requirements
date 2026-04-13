# CLAUDE.md — AI Assistant Instructions

This file provides context for Claude Code or other AI assistants working in this repository.

## Project Purpose

This repository documents government-level email security requirements and recommendations by country. The goal is to provide an authoritative, community-maintained reference for which email security standards (SPF, DKIM, DMARC, DANE, MTA-STS, TLS-RPT, BIMI, STARTTLS) are required or recommended in each country.

## Repository Structure

```
data/countries/XX.yaml   — Country data files (one per country, XX = ISO A2 code)
data/standards.yaml      — Master standards registry with RFC links and tools
data/schema/             — JSON Schema for validation
docs/standards/*.md      — Human-written documentation per standard
docs/map.svg             — GENERATED: do not edit directly
docs/index.html          — GENERATED: do not edit directly
webversion/              — GENERATED: do not edit directly
scripts/                 — Python generation and validation scripts
```

**Never edit generated files directly.** Always edit data/ and re-run scripts.

## Adding Country Data

1. Copy `data/countries/_template.yaml` to `data/countries/XX.yaml`
2. Fill all required fields (see the template and schema)
3. Every `mandatory`/`recommended` entry needs at least one `references` URL
4. Validate: `python scripts/validate_data.py`

## Regenerating Outputs

```bash
pip install -r scripts/requirements.txt

# One-time basemap download (run once, then reuse)
python scripts/fetch_basemap.py

# Regenerate everything
python scripts/generate_map.py              # docs/map.svg + docs/index.html
python scripts/generate_readme_table.py     # README.md matrix table
python scripts/generate_webversion.py       # webversion/ (for passwordscon.org)
```

## Key Conventions

- Country codes: ISO 3166-1 alpha-2 (uppercase, e.g., `NL`, `US`, `GB`)
- Dates: ISO 8601 (`YYYY-MM-DD`)
- All mandatory/recommended sources must be official government/agency documents
- Valid status values: `mandatory`, `recommended`, `informational`, `none`, `unknown`
- Valid standard IDs: `SPF`, `DKIM`, `DMARC`, `DANE`, `MTA-STS`, `TLS-RPT`, `BIMI`, `STARTTLS`

## Schema Location

`data/schema/country.schema.json` — JSON Schema v7, defines all valid fields and values.

## CI Behavior

- On every PR touching `data/**`: validates YAML against schema
- On push to main: regenerates map, README table, and webversion; auto-commits
- On push to main (docs/ changed): deploys to GitHub Pages

## Webversion Deployment

The `webversion/` directory contains files for manual upload to `passwordscon.org/mailrequirements/`.
After running `python scripts/generate_webversion.py`, upload `webversion/index.html` and
`webversion/map.svg` to the server via FTP/SFTP. WordPress serves static files from subfolders
without any additional configuration.
