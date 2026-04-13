# ASPA — Autonomous System Provider Authorization

## Purpose

ASPA (Autonomous System Provider Authorization) extends RPKI by allowing an Autonomous System (AS) to cryptographically register its authorized upstream transit providers. This enables **path validation** — detecting not only route origin hijacks (already addressed by RPKI ROA) but also **route leaks** and more sophisticated BGP path manipulation attacks.

A route leak occurs when a network announces routes to a peer or upstream that it should not be redistributing, causing traffic to be misrouted through unintended intermediaries. Route leaks have historically caused large-scale internet outages and can be used to intercept email and other traffic.

ASPA is newer than RPKI ROA and still in active IETF standardization and early deployment. It is the natural next step after RPKI ROA for organizations that want to address the full scope of BGP-level routing security.

## How It Works

1. An AS creates an **ASPA object** — a signed attestation listing its authorized upstream providers (i.e., the ASNs it has legitimate transit relationships with).
2. ASPA objects are published in the RPKI repository alongside ROAs.
3. Routers implementing **ASPA verification** check the AS path of incoming BGP announcements against the registered provider relationships.
4. Paths that violate the declared provider relationships are flagged as route leaks and can be rejected.

**Key terminology:**
- **ASPA object** — the signed RPKI object listing authorized upstream providers for an AS
- **Customer cone** — the set of networks reachable through a given AS as a transit customer
- **Route leak** — propagation of a BGP announcement beyond its intended scope (e.g., a customer re-advertising a provider's routes to another provider)
- **Path validation** — verifying that an AS path follows legitimate provider-customer or peer relationships

## RFCs and Specifications

ASPA is still being standardized. The primary documents are:

| Document | Description |
|---|---|
| [draft-ietf-sidrops-aspa-profile](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-profile/) | ASPA object format and profile |
| [draft-ietf-sidrops-aspa-verification](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-verification/) | BGP AS path verification using ASPA |
| [RFC 9582](https://datatracker.ietf.org/doc/html/rfc9582) | Updated ROA profile (related RPKI infrastructure) |

> These documents were in active IETF working group process as of 2026. Check IETF Datatracker for current status.

## Deployment Considerations

- ASPA deployment requires that **both** the publishing AS (creating ASPA objects) **and** the validating routers (implementing ASPA verification) are ASPA-capable.
- As of 2026, ASPA deployment is at an early stage globally. Some major networks and IXPs have begun testing.
- Creating an ASPA object requires access to your RIR portal (same as for ROAs).
- ASPA complements RPKI ROA — deploying ROAs first is the recommended starting point.
- Route leak protection only becomes effective when enough networks in the routing ecosystem deploy ASPA validation.

## Relationship to RPKI ROA

| Feature | RPKI ROA | ASPA |
|---|---|---|
| What it protects against | Route origin hijacks | Route leaks + path manipulation |
| Maturity | Deployed, widely used | Early deployment (drafts in IETF) |
| What you publish | Prefix → ASN binding | AS → authorized upstream ASNs |
| Enforcement requires | ROV-capable routers | ASPA-capable routers |
| Prerequisite | RIR account | RIR account + RPKI ROA experience |

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| RIPE NCC RPKI Dashboard | https://rpki-validator.ripe.net | RPKI/ASPA dashboard and validator |
| Cloudflare RPKI Validator | https://rpki.cloudflare.com | RPKI ROA validation; ASPA support evolving |
| IETF Datatracker | https://datatracker.ietf.org/wg/sidrops/documents/ | Track ASPA standards progress |

## Countries with ASPA Requirements

ASPA is a new and emerging standard. As of 2026, no country has formally mandated or officially recommended ASPA in government policy. Most countries with routing security awareness have it classified as informational.

> **Note:** Given ASPA's early deployment stage, the most actionable step for most organizations is to ensure RPKI ROA coverage first, then monitor ASPA standardization progress for future deployment.
