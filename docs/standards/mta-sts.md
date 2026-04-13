# MTA-STS — Mail Transfer Agent Strict Transport Security

## Purpose

MTA-STS allows mail server operators to publish a policy declaring that their server supports TLS and that sending servers should refuse to deliver email if a trusted TLS connection cannot be established. It prevents downgrade attacks and eliminates opportunistic TLS's weakness of being silently bypassed.

Unlike DANE, MTA-STS **does not require DNSSEC**. Instead, it publishes the policy via HTTPS, relying on the Web PKI (public CA certificates) for authenticity. This makes it significantly easier to deploy than DANE, at the cost of trusting the Web CA infrastructure rather than DNSSEC.

MTA-STS and DANE are complementary: organizations that can deploy DNSSEC should use DANE; those that cannot should use MTA-STS. The Netherlands mandates DANE but recommends MTA-STS; the UK recommends MTA-STS.

## How It Works

1. You publish a DNS TXT record at `_mta-sts.your-domain.com` with a policy version and ID.
2. You publish a policy file at `https://mta-sts.your-domain.com/.well-known/mta-sts.txt` via HTTPS.
3. The policy file lists your MX hostnames and specifies the mode (`enforce`, `testing`, or `none`).
4. A sending server fetches the policy, verifies the HTTPS connection (Web PKI), and caches it.
5. On delivery, the sending server ensures TLS is established with a certificate matching the policy's MX hostnames. If not, delivery is refused in `enforce` mode.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 8461](https://datatracker.ietf.org/doc/html/rfc8461) | MTA-STS (2018) — current standard |
| [RFC 8460](https://datatracker.ietf.org/doc/html/rfc8460) | TLS-RPT — companion reporting standard |

## DNS Record Format

```dns
_mta-sts.your-domain.com.  IN TXT  "v=STSv1; id=20240101000000Z"
```

The `id` value must be updated whenever the policy file changes (triggers cache refresh).

## Policy File Format

Published at `https://mta-sts.your-domain.com/.well-known/mta-sts.txt`:

```
version: STSv1
mode: enforce
mx: mail.your-domain.com
mx: mail2.your-domain.com
max_age: 86400
```

### Policy Modes

| Mode | Behavior |
|---|---|
| `enforce` | Reject delivery if TLS fails — full protection |
| `testing` | Report failures via TLS-RPT but do not reject |
| `none` | Policy withdrawn — no enforcement |

**Start with `testing` mode** while monitoring TLS-RPT reports, then move to `enforce` once confident.

## Infrastructure Requirements

- A subdomain `mta-sts.your-domain.com` with a valid HTTPS certificate
- A web server serving the policy file at the well-known path
- A DNS TXT record at `_mta-sts.your-domain.com`
- TLS-RPT configured to receive failure reports (strongly recommended)

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite test |
| Hardenize | https://www.hardenize.com | Detailed MTA-STS analysis |
| Mailhardener MTA-STS | https://www.mailhardener.com/tools/mta-sts-validator | Validator |
| MXToolbox MTA-STS | https://mxtoolbox.com/mta-sts.aspx | Quick check |

## Countries with MTA-STS Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | Recommended | Government agencies | NCSC |
| United Kingdom | Recommended | Government agencies | NCSC |
| United States | Recommended | Federal agencies | CISA |
| Canada | Informational | Government agencies | — |
