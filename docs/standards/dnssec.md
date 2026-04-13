# DNSSEC — DNS Security Extensions

## Purpose

DNSSEC adds cryptographic signatures to DNS responses, allowing resolvers to verify that DNS data has not been tampered with in transit. Without DNSSEC, DNS responses can be forged or poisoned by attackers (DNS cache poisoning / Kaminsky attack), potentially redirecting email to malicious servers or undermining SPF and DKIM lookups.

For email security, DNSSEC serves two critical functions:

1. **Prerequisite for DANE** — DANE/TLSA records only provide meaningful protection when the DNS chain is cryptographically signed. Without DNSSEC, an attacker can forge or remove TLSA records, defeating DANE entirely.
2. **Protects all email-related DNS lookups** — MX records, SPF TXT records, DKIM public key records, and DMARC records are all DNS lookups. DNSSEC protects the authenticity of all of them.

## How It Works

1. The domain owner signs their DNS zone with a private key; the corresponding public key is published in DNS.
2. The trust chain runs from the DNS root (signed by IANA) through TLDs to the domain.
3. A validating resolver checks signatures at each level of the chain.
4. If any signature is missing or invalid, the resolver returns `SERVFAIL` rather than an unverified answer.
5. Clients receive either a cryptographically verified answer or an explicit failure — not a silently forged one.

**Key terminology:**
- **DNSKEY** — the public signing key published in DNS
- **DS (Delegation Signer)** — a hash of the DNSKEY published in the parent zone to chain trust
- **RRSIG** — the actual signature record attached to each DNS record set
- **NSEC/NSEC3** — authenticated denial of existence

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 4033](https://datatracker.ietf.org/doc/html/rfc4033) | DNSSEC introduction and requirements |
| [RFC 4034](https://datatracker.ietf.org/doc/html/rfc4034) | Resource records for DNSSEC |
| [RFC 4035](https://datatracker.ietf.org/doc/html/rfc4035) | Protocol modifications for DNSSEC |
| [RFC 5155](https://datatracker.ietf.org/doc/html/rfc5155) | NSEC3 — hashed authenticated denial of existence |
| [RFC 6781](https://datatracker.ietf.org/doc/html/rfc6781) | DNSSEC operational practices |
| [RFC 9364](https://datatracker.ietf.org/doc/html/rfc9364) | DNSSEC tutorial and deployment guide (2023) |

## Deployment Considerations

- DNSSEC must be enabled at the **registrar level** (DS record delegation) as well as at the **authoritative nameserver level** (DNSKEY + RRSIGs).
- Key rollover must be performed carefully to avoid breakage (follow RFC 6781 guidance).
- NSEC3 with opt-out is typically used for large zones; NSEC is fine for small domain zones.
- Signed zones must be re-signed periodically (before signature expiry — typically 30-day signatures refreshed weekly).
- Many DNS hosting providers (Cloudflare, Route53, Azure DNS, Hetzner DNS) handle signing automatically.

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite including DNSSEC |
| DNSSEC Analyzer (Verisign) | https://dnssec-analyzer.verisignlabs.com | Visual trust chain analysis |
| SIDN DNSSEC Check | https://check.sidnlabs.nl | Dutch NIC DNSSEC checker |
| MXToolbox DNSSEC | https://mxtoolbox.com/dnssec.aspx | Quick lookup |
| DNSViz | https://dnsviz.net | Detailed visual DNSSEC path analysis |
| Zonemaster | https://zonemaster.net | Comprehensive zone quality tests |

## Countries with DNSSEC Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United States | **Mandatory** | Federal agencies (.gov) | CISA BOD 18-01 |
| United Kingdom | Recommended | Government agencies | NCSC |
| Germany | Recommended | Gov / Critical infra | BSI |
| Australia | Recommended | Government agencies | ASD / ACSC ISM |
| France | Recommended | Gov / Critical infra | ANSSI |
| Canada | Recommended | Government agencies | CCCS |

> **Note:** Without DNSSEC, DANE cannot be deployed. If your country mandates DANE, DNSSEC is implicitly mandatory as well.
