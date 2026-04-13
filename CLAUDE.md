# CLAUDE.md — AI Assistant Instructions

This file provides context for Claude Code or other AI assistants working in this repository.

## Project Purpose

This repository documents government-level email security requirements and recommendations by country. The goal is an authoritative, community-maintained reference for which of the 13 tracked standards are **mandatory**, **recommended**, **informational**, or absent in each country — with source citations, a generated world map, and documentation for each standard.

## Standards Tracked (13 total)

| ID | Full Name | RFC |
|---|---|---|
| `SPF` | Sender Policy Framework | RFC 7208 |
| `DKIM` | DomainKeys Identified Mail | RFC 6376 |
| `DMARC` | Domain-based Message Authentication, Reporting and Conformance | RFC 7489 |
| `STARTTLS` | SMTP STARTTLS (Opportunistic TLS) | RFC 3207 |
| `DANE` | DNS-based Authentication of Named Entities | RFC 6698, 7671 |
| `DNSSEC` | DNS Security Extensions | RFC 4033–4035, 9364 |
| `MTA-STS` | Mail Transfer Agent Strict Transport Security | RFC 8461 |
| `TLS-RPT` | SMTP TLS Reporting | RFC 8460 |
| `CAA` | Certification Authority Authorization | RFC 8659 |
| `IPv6` | IPv6 Support for Email | RFC 8200, RFC 3596 |
| `RPKI` | Resource Public Key Infrastructure | RFC 6480, 9582 |
| `ASPA` | Autonomous System Provider Authorization | IETF SIDROPS draft |
| `BIMI` | Brand Indicators for Message Identification | BIMI Group draft |

## Repository Structure

```
data/countries/XX.yaml        Country data files (one per country, XX = ISO 3166-1 alpha-2)
data/countries/_template.yaml Starter file for contributors
data/standards.yaml           Master registry: names, RFCs, testing tools
data/schema/country.schema.json  JSON Schema v7 — the validation contract

docs/standards/*.md           Human-written documentation per standard (13 files)
docs/map.svg                  GENERATED — do not edit directly
docs/index.html               GENERATED — do not edit directly

webversion/index.html         GENERATED — do not edit directly (passwordscon.org deploy)
webversion/map.svg            GENERATED — do not edit directly

scripts/fetch_basemap.py      One-time: download Natural Earth GeoJSON → assets/world-110m.svg
scripts/validate_data.py      Validate all YAML against schema
scripts/generate_map.py       Write docs/map.svg + docs/index.html
scripts/generate_readme_table.py  Inject matrix table into README.md (between sentinels)
scripts/generate_webversion.py    Write webversion/ (light theme, self-contained HTML)
scripts/requirements.txt      pip dependencies: pyyaml, jsonschema, lxml, requests

assets/world-110m.svg         Basemap SVG (Natural Earth, CC0) — generated once by fetch_basemap.py
```

**Never edit generated files directly.** Always edit `data/` and re-run scripts.

## Adding or Updating Country Data

1. Copy `data/countries/_template.yaml` → `data/countries/XX.yaml`
2. Fill all required fields (`country_code`, `country_name`, `last_reviewed`, `requirements`)
3. Every `mandatory` or `recommended` entry must have at least one URL in `references` pointing to an official government or agency document
4. Validate: `python scripts/validate_data.py`
5. Open a Pull Request

## Regenerating Outputs

```bash
pip install -r scripts/requirements.txt

# One-time basemap setup (only needed when assets/world-110m.svg is missing)
python scripts/fetch_basemap.py

# Regenerate everything
python scripts/generate_map.py              # → docs/map.svg + docs/index.html
python scripts/generate_readme_table.py     # → injects matrix into README.md
python scripts/generate_webversion.py       # → webversion/index.html + webversion/map.svg
```

The README matrix is bounded by `<!-- BEGIN_MATRIX -->` and `<!-- END_MATRIX -->` sentinels. Only `generate_readme_table.py` should modify that section.

## Key Conventions

- **Country codes**: ISO 3166-1 alpha-2, uppercase (`NL`, `US`, `GB`). Use `EU` for the European Union.
- **Dates**: ISO 8601, `YYYY-MM-DD`
- **Status values**: `mandatory` | `recommended` | `informational` | `none` | `unknown`
- **Valid standard IDs**: `SPF`, `DKIM`, `DMARC`, `STARTTLS`, `DANE`, `DNSSEC`, `MTA-STS`, `TLS-RPT`, `CAA`, `BIMI`
- **Sources**: Only official government/agency documents count as valid references for `mandatory` or `recommended` status

## Schema

`data/schema/country.schema.json` — JSON Schema v7. All country YAML files are validated against this. The `standard` field uses a closed enum matching the 10 IDs above.

## CI / GitHub Actions

| Workflow | Trigger | Action |
|---|---|---|
| `validate.yml` | PR touching `data/**` | Runs `validate_data.py`; fails on schema errors |
| `generate-map.yml` | Push to `main` touching `data/**` or `scripts/generate_*.py` | Regenerates map, README table, webversion; auto-commits |
| `pages.yml` | Push to `main` touching `docs/**` | Deploys `docs/` to GitHub Pages |

## Webversion Deployment

After `python scripts/generate_webversion.py`, upload **two files** to the WordPress server:

```
webversion/index.html  →  passwordscon.org/mailrequirements/index.html
webversion/map.svg     →  passwordscon.org/mailrequirements/map.svg
```

No WordPress plugin or shortcode needed — WordPress serves static files from subfolders automatically.
