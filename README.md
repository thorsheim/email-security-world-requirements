# Email Security World Requirements

> A community-maintained reference documenting which countries require or recommend
> SPF, DKIM, DMARC, STARTTLS, DANE, DNSSEC, MTA-STS, TLS-RPT, CAA, and BIMI
> at government or national policy level.

[![Validate Data](https://github.com/thorsheim/email-security-world-requirements/actions/workflows/validate.yml/badge.svg)](https://github.com/thorsheim/email-security-world-requirements/actions/workflows/validate.yml)
[![Countries](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fthorsheim%2Femail-security-world-requirements%2Fmain%2Fdata%2Fcountries%2FNL.yaml&label=countries&query=%24.country_code&color=blue)](data/countries/)

**Live interactive map:** [thorsheim.github.io/email-security-world-requirements](https://thorsheim.github.io/email-security-world-requirements/)  
**Web version:** [passwordscon.org/mailrequirements/](https://passwordscon.org/mailrequirements/)

---

## Why this exists

Phishing, spam, and email impersonation remain among the most effective attack vectors globally.
A growing number of governments have responded by mandating or formally recommending technical
email security standards for public sector organisations and critical infrastructure.

This project answers a simple question: **who requires what, and under which policy?**

The data is stored as machine-readable YAML, validated against a JSON Schema, and rendered as
an interactive world map and sortable requirements matrix. All sources are cited; contributions
via Pull Request are welcome.

---

## World Map

[![Email Security Requirements Map](docs/map.svg)](https://thorsheim.github.io/email-security-world-requirements/)

*Green = more mandatory standards · Red = no requirements · Grey = no data yet*  
*[Open interactive version →](https://thorsheim.github.io/email-security-world-requirements/)*

---

## Requirements Matrix

<!-- BEGIN_MATRIX -->

| Country | Authority | [SPF](docs/standards/spf.md) | [DKIM](docs/standards/dkim.md) | [DMARC](docs/standards/dmarc.md) | [STARTTLS](docs/standards/starttls.md) | [DANE](docs/standards/dane.md) | [DNSSEC](docs/standards/dnssec.md) | [MTA-STS](docs/standards/mta-sts.md) | [TLS-RPT](docs/standards/tls-rpt.md) | [CAA](docs/standards/caa.md) | [RPKI](docs/standards/rpki.md) | [ASPA](docs/standards/aspa.md) | [BIMI](docs/standards/bimi.md) | Applies To |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 🇦🇺 Australia | ASD / ACSC | 🔶 R | 🔶 R | 🔶 R | 🔶 R | ℹ️ | 🔶 R | ℹ️ | ℹ️ | 🔶 R | ℹ️ | ❓ | ℹ️ | Government Agencies |
| 🇨🇦 Canada | CCCS; CCCS / Treasury Board | 🔶 R | 🔶 R | 🔶 R | 🔶 R | ℹ️ | 🔶 R | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ❓ | ℹ️ | Government Agencies |
| 🇩🇪 Germany | BSI | 🔶 R | 🔶 R | 🔶 R | 🔶 R | ℹ️ | 🔶 R | ℹ️ | ℹ️ | 🔶 R | ℹ️ | ❓ | ℹ️ | Critical Infrastructure, Government Agencies |
| 🇪🇺 European Union | ENISA / NIS2 | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ❓ | ℹ️ | Critical Infrastructure |
| 🇫🇷 France | ANSSI | 🔶 R | 🔶 R | 🔶 R | 🔶 R | ℹ️ | 🔶 R | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ❓ | ℹ️ | Critical Infrastructure, Government Agencies |
| 🇬🇧 United Kingdom | NCSC | ✅ M | ✅ M | ✅ M (reject) | ✅ M | ℹ️ | 🔶 R | 🔶 R | 🔶 R | 🔶 R | ℹ️ | ❓ | ℹ️ | Government Agencies |
| 🇳🇱 Netherlands | Forum Standaardisatie / NCSA; NCSC | ✅ M | ✅ M | ✅ M (reject) | ✅ M | ✅ M | ✅ M | 🔶 R | ✅ M | ✅ M | 🔶 R | ℹ️ | ℹ️ | Government Agencies |
| 🇺🇸 United States | CISA | ✅ M | 🔶 R | ✅ M (reject) | ✅ M | ℹ️ | ✅ M | 🔶 R | 🔶 R | 🔶 R | ℹ️ | ❓ | ℹ️ | Federal Agencies |

### Legend

**Status icons**

| Icon | Status | Meaning |
| :---: | :--- | :--- |
| ✅ M | **Mandatory** | Legally or policy-required; non-compliance has consequences |
| 🔶 R | **Recommended** | Official guidance or best-practice document published by a government body |
| ℹ️ | **Informational** | Mentioned in an official document but no clear directive |
| ➖ | **None** | Explicitly confirmed as not required |
| ❓ | **Unknown** | No official data found |

**Standards grouping**

| Group | Standards | Purpose |
| :--- | :--- | :--- |
| Sender authentication | SPF · DKIM · DMARC | Verify who sent the message |
| Transport security | STARTTLS · DANE · DNSSEC · MTA-STS · TLS-RPT | Encrypt and secure delivery |
| Infrastructure | CAA | Restrict certificate issuance |
| Routing security | RPKI · ASPA | Protect against BGP hijacking and route leaks |
| Emerging | BIMI | Visual brand verification |

> DANE requires DNSSEC — if a country mandates DANE, DNSSEC is implicitly required too. ASPA extends RPKI ROA and is still in IETF standardization as of 2026.

<!-- END_MATRIX -->

---

## Standards Covered (12)

| Standard | Full Name | RFC / Spec | Purpose |
|---|---|---|---|
| [SPF](docs/standards/spf.md) | Sender Policy Framework | [RFC 7208](https://datatracker.ietf.org/doc/html/rfc7208) | Authorize which servers may send mail for a domain |
| [DKIM](docs/standards/dkim.md) | DomainKeys Identified Mail | [RFC 6376](https://datatracker.ietf.org/doc/html/rfc6376) | Cryptographic signature on outgoing mail |
| [DMARC](docs/standards/dmarc.md) | Domain-based Message Authentication, Reporting and Conformance | [RFC 7489](https://datatracker.ietf.org/doc/html/rfc7489) | Policy enforcement and reporting for SPF/DKIM |
| [STARTTLS](docs/standards/starttls.md) | SMTP STARTTLS | [RFC 3207](https://datatracker.ietf.org/doc/html/rfc3207) | Encrypted mail transport baseline |
| [DANE](docs/standards/dane.md) | DNS-based Authentication of Named Entities | [RFC 6698](https://datatracker.ietf.org/doc/html/rfc6698) | Bind TLS certificates to DNS via DNSSEC |
| [DNSSEC](docs/standards/dnssec.md) | DNS Security Extensions | [RFC 4033–4035](https://datatracker.ietf.org/doc/html/rfc4033) | Cryptographically sign DNS responses; required for DANE |
| [MTA-STS](docs/standards/mta-sts.md) | Mail Transfer Agent Strict Transport Security | [RFC 8461](https://datatracker.ietf.org/doc/html/rfc8461) | Enforce TLS on delivery without requiring DNSSEC |
| [TLS-RPT](docs/standards/tls-rpt.md) | SMTP TLS Reporting | [RFC 8460](https://datatracker.ietf.org/doc/html/rfc8460) | Aggregate reports on TLS connection failures |
| [CAA](docs/standards/caa.md) | Certification Authority Authorization | [RFC 8659](https://datatracker.ietf.org/doc/html/rfc8659) | Restrict which CAs may issue certificates for a domain |
| [RPKI](docs/standards/rpki.md) | Resource Public Key Infrastructure | [RFC 6480](https://datatracker.ietf.org/doc/html/rfc6480) / [RFC 9582](https://datatracker.ietf.org/doc/html/rfc9582) | Prevent BGP hijacking via cryptographic route origin validation |
| [ASPA](docs/standards/aspa.md) | Autonomous System Provider Authorization | [IETF SIDROPS draft](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-profile/) | Extend RPKI to detect route leaks via provider relationship validation |
| [BIMI](docs/standards/bimi.md) | Brand Indicators for Message Identification | [BIMI Group](https://bimigroup.org) | Display a verified brand logo in supporting mail clients |

---

## Testing Tools

Test your own domain against these standards:

| Tool | URL | What it tests |
|---|---|---|
| **internet.nl** | https://internet.nl | SPF, DKIM, DMARC, DANE, DNSSEC, STARTTLS, TLS-RPT, MTA-STS — full suite; operated by the Dutch government |
| **Mailcheck** | https://passwordscon.org/mailcheck/ | SPF, DKIM, DMARC, STARTTLS, headers — quick combined tester |
| **MXToolbox** | https://mxtoolbox.com | Individual lookups for all standards |
| **dmarcian** | https://dmarcian.com | DMARC management, reporting, and SPF/DKIM analysis |
| **Hardenize** | https://www.hardenize.com | Comprehensive posture including MTA-STS and CAA |
| **DNSViz** | https://dnsviz.net | Visual DNSSEC chain analysis |
| **Verisign DNSSEC Analyzer** | https://dnssec-analyzer.verisignlabs.com | DNSSEC validation |
| **SSLMate CAA Generator** | https://sslmate.com/caa/ | Generate and validate CAA records |

---

## Contributing

Found a country that's missing? Have newer policy information? **Contributions are very welcome.**

See [CONTRIBUTING.md](CONTRIBUTING.md) for full instructions. Quick start:

1. Copy [`data/countries/_template.yaml`](data/countries/_template.yaml) to `data/countries/XX.yaml`  
   (where `XX` is the ISO 3166-1 alpha-2 country code)
2. Fill in the fields — refer to an existing file like [NL.yaml](data/countries/NL.yaml) for examples
3. Every `mandatory` or `recommended` entry needs at least one source URL in `references`  
   pointing to an official government or agency document
4. Run `python scripts/validate_data.py` — all files must pass before opening a PR
5. Open a Pull Request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

**Unknown data is also valuable.** If you researched a country and found nothing, create the file
with `status: unknown` for all standards and note what you searched. This tells others not to
duplicate the effort.

---

## Data Format

Country data lives in [`data/countries/`](data/countries/) — one YAML file per country, validated
against [`data/schema/country.schema.json`](data/schema/country.schema.json).

Each file records, per standard:

| Field | Example values |
|---|---|
| `status` | `mandatory` · `recommended` · `informational` · `none` · `unknown` |
| `applies_to` | `government_agencies` · `federal_agencies` · `critical_infrastructure` · `all_organizations` · … |
| `authority` | `"CISA"`, `"NCSC"`, `"Forum Standaardisatie / NCSA"` |
| `policy_document` | `"BOD 18-01"`, `"BIO"`, `"BSI TR-03108"` |
| `effective_date` | `"2018-10-16"` |
| `references` | List of `{title, url}` pointing to official documents |

See [`data/countries/_template.yaml`](data/countries/_template.yaml) for the full annotated template.

---

## Repository Structure

```
data/
  countries/          One YAML file per country (XX.yaml, ISO alpha-2)
  standards.yaml      Master standards registry with RFC links and testing tools
  schema/             JSON Schema for validation

docs/
  standards/          Documentation page per standard (spf.md, dkim.md, …)
  map.svg             Generated world map (dark theme, for GitHub display)
  index.html          Generated interactive GitHub Pages page

webversion/
  index.html          Generated self-contained page for passwordscon.org/mailrequirements/
  map.svg             Generated world map (light theme)

scripts/
  validate_data.py        Validate all country YAML files
  fetch_basemap.py        One-time: download basemap from Natural Earth
  generate_map.py         Generate docs/map.svg + docs/index.html
  generate_readme_table.py  Inject requirements matrix into README.md
  generate_webversion.py    Generate webversion/

assets/
  world-110m.svg      Natural Earth 110m basemap (CC0)
```

---

## License

- **Data** (`data/`): [CC-BY-4.0](LICENSE-DATA) — free to use with attribution
- **Code** (`scripts/`, `docs/`): [MIT](LICENSE-CODE)

---

## About

Created by [Per Thorsheim](https://passwordscon.org) as part of an ongoing effort to document
the global email security policy landscape.

If you operate email infrastructure for a government agency, hospital, bank, or other organisation —
test your domain today at [internet.nl](https://internet.nl) and [Mailcheck](https://passwordscon.org/mailcheck/).

Issues and discussion welcome via [GitHub Issues](https://github.com/thorsheim/email-security-world-requirements/issues).
