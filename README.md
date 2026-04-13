# Email Security World Requirements

> Which countries require or recommend SPF, DKIM, DMARC, DANE, MTA-STS, TLS-RPT, BIMI, and STARTTLS at government or national policy level?

[![Validate Data](https://github.com/thorsheim/email-security-world-requirements/actions/workflows/validate.yml/badge.svg)](https://github.com/thorsheim/email-security-world-requirements/actions/workflows/validate.yml)

This repository documents government-level email security requirements and recommendations by country. Data is stored in machine-readable YAML files, contributions are welcome via Pull Request, and a generated world map provides a visual overview.

**Live site:** [thorsheim.github.io/email-security-world-requirements](https://thorsheim.github.io/email-security-world-requirements/)  
**Web version:** [passwordscon.org/mailrequirements/](https://passwordscon.org/mailrequirements/)

---

## World Map

[![Email Security Requirements Map](docs/map.svg)](https://thorsheim.github.io/email-security-world-requirements/)

*Click the map for the interactive version. Green = more standards mandatory, red = no requirements, gray = no data.*

---

## Requirements Matrix

<!-- BEGIN_MATRIX -->

| Country | Authority | [SPF](docs/standards/spf.md) | [DKIM](docs/standards/dkim.md) | [DMARC](docs/standards/dmarc.md) | [DANE](docs/standards/dane.md) | [MTA-STS](docs/standards/mta-sts.md) | [TLS-RPT](docs/standards/tls-rpt.md) | [BIMI](docs/standards/bimi.md) | [STARTTLS](docs/standards/starttls.md) | Applies To |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 🇦🇺 Australia | ASD / ACSC | 🔶 R | 🔶 R | 🔶 R | ℹ️ | ℹ️ | ℹ️ | ℹ️ | 🔶 R | Government Agencies |
| 🇨🇦 Canada | CCCS; CCCS / Treasury Board | 🔶 R | 🔶 R | 🔶 R | ℹ️ | ℹ️ | ℹ️ | ℹ️ | 🔶 R | Government Agencies |
| 🇩🇪 Germany | BSI | 🔶 R | 🔶 R | 🔶 R | ℹ️ | ℹ️ | ℹ️ | ℹ️ | 🔶 R | Critical Infrastructure, Government Agencies |
| 🇪🇺 European Union | ENISA / NIS2 | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | ℹ️ | Critical Infrastructure |
| 🇫🇷 France | ANSSI | 🔶 R | 🔶 R | 🔶 R | ℹ️ | ℹ️ | ℹ️ | ℹ️ | 🔶 R | Critical Infrastructure, Government Agencies |
| 🇬🇧 United Kingdom | NCSC | ✅ M | ✅ M | ✅ M (reject) | ℹ️ | 🔶 R | 🔶 R | ℹ️ | ✅ M | Government Agencies |
| 🇳🇱 Netherlands | Forum Standaardisatie / NCSA; NCSC | ✅ M | ✅ M | ✅ M (reject) | ✅ M | 🔶 R | ✅ M | ℹ️ | ✅ M | Government Agencies |
| 🇺🇸 United States | CISA | ✅ M | 🔶 R | ✅ M (reject) | ℹ️ | 🔶 R | 🔶 R | ℹ️ | ✅ M | Federal Agencies |

**Legend:** ✅ M = Mandatory &nbsp;·&nbsp; 🔶 R = Recommended &nbsp;·&nbsp; ℹ️ = Informational &nbsp;·&nbsp; ➖ = No requirement &nbsp;·&nbsp; ❓ = No data / Unknown

<!-- END_MATRIX -->

---

## Standards Covered

| Standard | Full Name | RFC | Purpose |
|---|---|---|---|
| [SPF](docs/standards/spf.md) | Sender Policy Framework | [RFC 7208](https://datatracker.ietf.org/doc/html/rfc7208) | Authorize mail servers per domain |
| [DKIM](docs/standards/dkim.md) | DomainKeys Identified Mail | [RFC 6376](https://datatracker.ietf.org/doc/html/rfc6376) | Cryptographic signature on outgoing mail |
| [DMARC](docs/standards/dmarc.md) | Domain-based Message Authentication, Reporting and Conformance | [RFC 7489](https://datatracker.ietf.org/doc/html/rfc7489) | Policy + reporting for SPF/DKIM |
| [DANE](docs/standards/dane.md) | DNS-based Authentication of Named Entities | [RFC 6698](https://datatracker.ietf.org/doc/html/rfc6698) | TLS cert binding via DNSSEC |
| [MTA-STS](docs/standards/mta-sts.md) | Mail Transfer Agent Strict Transport Security | [RFC 8461](https://datatracker.ietf.org/doc/html/rfc8461) | Enforce TLS without DNSSEC |
| [TLS-RPT](docs/standards/tls-rpt.md) | SMTP TLS Reporting | [RFC 8460](https://datatracker.ietf.org/doc/html/rfc8460) | Report TLS failures |
| [BIMI](docs/standards/bimi.md) | Brand Indicators for Message Identification | [BIMI Group](https://bimigroup.org) | Verified logo in email clients |
| [STARTTLS](docs/standards/starttls.md) | SMTP STARTTLS | [RFC 3207](https://datatracker.ietf.org/doc/html/rfc3207) | Encrypted mail transport baseline |

---

## Testing Tools

Test your own domain's email security configuration:

| Tool | URL | Notes |
|---|---|---|
| **internet.nl** | https://internet.nl | Full test suite; operated by Dutch government |
| **Mailcheck** | https://passwordscon.org/mailcheck/ | Combined email security tester |
| **MXToolbox** | https://mxtoolbox.com | Individual lookups for all standards |
| **dmarcian** | https://dmarcian.com | DMARC management and analysis |
| **Hardenize** | https://www.hardenize.com | Comprehensive security posture |
| **DMARC Advisor** | https://dmarcadvisor.com | Enterprise DMARC |

---

## Contributing

Found a missing country? Have an update to an existing entry? **Contributions are very welcome!**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions. The short version:

1. Copy [`data/countries/_template.yaml`](data/countries/_template.yaml) to `data/countries/XX.yaml`
2. Fill in the fields with references to official government documents
3. Run `python scripts/validate_data.py` to check your work
4. Open a Pull Request

Every `mandatory` or `recommended` entry requires at least one source URL pointing to an official government or agency document.

---

## Data Format

Country data lives in [`data/countries/`](data/countries/) as individual YAML files. The schema is defined in [`data/schema/country.schema.json`](data/schema/country.schema.json).

Each file covers:
- Which standards have requirements (SPF, DKIM, DMARC, etc.)
- Whether each is **mandatory**, **recommended**, **informational**, or has **no requirement**
- Who it applies to (government agencies, federal agencies, critical infrastructure, etc.)
- The issuing authority and policy document name
- Source URLs for verification
- Last-reviewed date

---

## License

- **Data** (`data/`): [CC-BY-4.0](LICENSE-DATA) — free to use with attribution
- **Code** (`scripts/`, `docs/`): [MIT](LICENSE-CODE)

---

## About

Created by [Per Thorsheim](https://passwordscon.org) as part of an ongoing effort to document the global email security landscape. If you maintain email infrastructure for a government, bank, hospital, or other organization — test yourself at [internet.nl](https://internet.nl) and [Mailcheck](https://passwordscon.org/mailcheck/).

Issues and discussions welcome via [GitHub Issues](https://github.com/thorsheim/email-security-world-requirements/issues).
