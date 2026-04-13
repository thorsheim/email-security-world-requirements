# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Initial release of the email-security-world-requirements repository
- Seed data for 8 countries/regions: Netherlands, United States, United Kingdom,
  Germany, Australia, France, Canada, and European Union
- Documentation pages for all 8 email security standards:
  SPF, DKIM, DMARC, DANE, MTA-STS, TLS-RPT, BIMI, STARTTLS
- World map visualization (dark theme for GitHub Pages, light theme for website)
- Interactive requirements matrix with filtering and sorting
- JSON Schema validation for all country data files
- GitHub Actions workflows for CI validation and map generation
- Contribution guide (CONTRIBUTING.md)
- Web version for deployment to passwordscon.org/mailrequirements/

---

## How to Contribute Changes

When contributing a notable change, add an entry under `[Unreleased]` with:
- `Added` — new countries, new standards documentation
- `Changed` — updates to existing country requirements
- `Fixed` — corrections to incorrect data
- `Removed` — data that has been removed (e.g., a requirement that was withdrawn)

Include the date, country code, and a brief description. Example:

```
- [2026-04-13] Added NO (Norway) — SPF/DKIM/DMARC recommended by NSM
- [2026-04-13] Updated US — corrected DKIM status from recommended to mandatory
```
