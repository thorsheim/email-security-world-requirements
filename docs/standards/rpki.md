# RPKI — Resource Public Key Infrastructure

## Purpose

RPKI provides cryptographic attestations — called Route Origin Authorizations (ROAs) — that bind IP address prefixes to Autonomous System Numbers (ASNs). When networks implement Route Origin Validation (ROV), they can reject BGP routes that lack a valid ROA, preventing BGP hijacking and route leaks.

For email security, RPKI matters because the routing layer is the foundation everything else runs on:

- A BGP hijack can silently redirect SMTP connections to a malicious mail server.
- Hijacked routes can intercept SPF DNS lookups, DMARC aggregate reports, or certificate validation traffic.
- Without routing security, even a perfectly configured mail server can have its traffic intercepted before any application-layer authentication takes effect.

RPKI ROA is the currently deployed and operationally mature component of routing security. Its companion standard, ASPA, addresses route leak detection and is still in active deployment.

## How It Works

1. An organization holding an IP address block creates a **ROA** — a signed object declaring which ASN is authorized to originate routes for that prefix.
2. ROAs are published to the **RPKI repository** (maintained by Regional Internet Registries: ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC).
3. Networks implementing **Route Origin Validation (ROV)** download the ROA data and check BGP route announcements against it.
4. Routes that are **ROV-invalid** (wrong ASN for the prefix) can be rejected or de-preferred, preventing the hijacked route from propagating.

**Key terminology:**
- **ROA (Route Origin Authorization)** — the signed attestation binding a prefix to an ASN
- **ROV (Route Origin Validation)** — the router-side process that checks incoming BGP routes against RPKI data
- **RIR (Regional Internet Registry)** — ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC; each manages RPKI for their address space
- **RPKI repository** — distributed set of publication points where ROAs and related objects are stored

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 6480](https://datatracker.ietf.org/doc/html/rfc6480) | RPKI infrastructure overview |
| [RFC 6481](https://datatracker.ietf.org/doc/html/rfc6481) | RPKI repository structure |
| [RFC 6482](https://datatracker.ietf.org/doc/html/rfc6482) | ROA format |
| [RFC 6483](https://datatracker.ietf.org/doc/html/rfc6483) | ROA validation for BGP routing |
| [RFC 6811](https://datatracker.ietf.org/doc/html/rfc6811) | BGP prefix origin validation |
| [RFC 9582](https://datatracker.ietf.org/doc/html/rfc9582) | A profile for Route Origin Authorizations (ROAs) — 2024 update |

## Deployment Considerations

- Creating ROAs requires access to your organization's RIR portal (e.g., RIPE NCC's RPKI dashboard, ARIN's ROA manager).
- ROV (the enforcement side) must be implemented by the **network operator** (ISP, hosting provider, enterprise network team), not just the domain owner.
- ROAs should cover all prefixes you originate in BGP — including any /24s used for mail infrastructure.
- Max-length should be set carefully: overly permissive max-length (e.g., ROA for /16 with max-length /24) reduces hijack protection.
- Most major CDN/cloud providers and many ISPs now validate RPKI — adoption is growing rapidly.

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| Cloudflare RPKI Validator | https://rpki.cloudflare.com | Check ROA coverage and validity for a prefix/ASN |
| RIPE NCC RPKI Validator | https://rpki-validator.ripe.net | Full RPKI validation dashboard |
| internet.nl | https://internet.nl | Includes routing security checks |
| IRRexplorer | https://irrexplorer.nlnog.net | Compare IRR and RPKI data for a prefix |
| RIPE Stat | https://stat.ripe.net | Comprehensive BGP/RPKI data per prefix or ASN |

## Countries with RPKI Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | Recommended | Government agencies | NCSC / Forum Standaardisatie |
| United States | Informational | Federal agencies | CISA |
| United Kingdom | Informational | Government agencies | NCSC |
| Germany | Informational | Gov / Critical infra | BSI |
| European Union | Informational | Critical infrastructure | ENISA / NIS2 |

> **Note:** RPKI ROA covers origin validation only — it does not prevent all BGP path manipulation. ASPA extends RPKI to address route leak detection (upstream provider validation). Deploying ROAs is the immediate actionable step; ROV enforcement depends on your transit providers and peers.
