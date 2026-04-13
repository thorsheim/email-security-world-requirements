# IPv6 — IPv6 Support for Email

## Purpose

IPv6 is the successor to IPv4, providing a vastly larger address space and improved routing efficiency. For email, IPv6 support means that mail servers publish AAAA DNS records for their MX hosts and accept inbound SMTP connections over IPv6.

As IPv6 adoption grows — and as some networks and regions move toward IPv6-only connectivity — mail servers that lack IPv6 support become unreachable from those networks. Several governments have mandated IPv6 for public sector digital infrastructure as part of broader modernisation programmes.

From an email security perspective, IPv6 also interacts with SPF (which requires separate SPF records covering IPv6 sending addresses) and with DANE (TLSA records must cover both IPv4 and IPv6 endpoints).

## How It Works

1. The domain's MX records point to mail server hostnames.
2. Those hostnames have both **A** (IPv4) and **AAAA** (IPv6) DNS records — this is called dual-stack.
3. The mail server software is configured to bind to and listen on IPv6 addresses.
4. Sending servers that prefer IPv6 can connect over IPv6; IPv4-only senders fall back to the A record.

**Key requirements for full IPv6 email support:**
- AAAA record(s) for all MX host names
- Mail server daemon (Postfix, Exim, Exchange, etc.) configured to accept on IPv6
- SPF record updated to include IPv6 sending addresses (either `ip6:` mechanism or `include:` for the provider)
- DANE/TLSA records covering the IPv6 endpoint if DANE is deployed
- Outbound mail sending over IPv6 (separate consideration from inbound)

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 8200](https://datatracker.ietf.org/doc/html/rfc8200) | Internet Protocol, Version 6 (IPv6) Specification |
| [RFC 3596](https://datatracker.ietf.org/doc/html/rfc3596) | DNS Extensions to Support IPv6 (AAAA records) |
| [RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321) | Simple Mail Transfer Protocol — §3.9 covers IPv6 addresses in SMTP |
| [RFC 7942](https://datatracker.ietf.org/doc/html/rfc7942) | Implementation Status Section — used in IPv6 BCP documents |

## Deployment Considerations

- **SPF and IPv6**: IPv6 sending addresses must be included in the SPF record. Many organisations add IPv6 after the fact and forget to update SPF, causing failures.
- **DANE and dual-stack**: If DANE is deployed, TLSA records should cover both the IPv4 and IPv6 listening addresses.
- **Outbound vs inbound**: Most organisations configure inbound IPv6 (receiving) before outbound (sending). Outbound IPv6 can trigger spam filter issues on some receivers; test carefully.
- **Managed hosting**: Cloud email providers (Google Workspace, Microsoft 365) handle IPv6 automatically. On-premises deployments require explicit configuration.
- **Blacklisting**: IPv6 addresses can be blacklisted just like IPv4. Monitor deliverability from new IPv6 ranges.

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Tests IPv6 reachability for MX hosts as part of the full email standards suite |
| MXToolbox Email Health | https://mxtoolbox.com/emailhealth.aspx | Checks MX records including IPv6 |
| test-ipv6.com | https://test-ipv6.com | General IPv6 connectivity tester |
| DNSViz | https://dnsviz.net | Visual DNS analysis including AAAA records |

## Countries with IPv6 Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie |
| United States | **Mandatory** | Federal agencies | OMB (M-21-07) |
| United Kingdom | Recommended | Government agencies | NCSC / GDS |
| Germany | Recommended | Gov / Critical infra | BSI |
| Australia | Recommended | Government agencies | ASD / ACSC (ISM) |
| Canada | Recommended | Government agencies | TBS / CCCS |

> **Note:** IPv6 for email interacts with SPF configuration — ensure your SPF record covers your IPv6 sending addresses or mail sent from IPv6 will fail authentication.
