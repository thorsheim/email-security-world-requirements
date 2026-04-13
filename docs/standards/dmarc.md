# DMARC — Domain-based Message Authentication, Reporting and Conformance

## Purpose

DMARC builds on SPF and DKIM by giving domain owners control over what happens to emails that fail authentication. It allows you to publish a policy (none, quarantine, or reject) that instructs receiving servers how to handle messages that don't pass SPF or DKIM checks *and* aren't aligned with your `From:` domain.

DMARC also provides a reporting mechanism: receiving servers send aggregate (RUA) and forensic (RUF) reports back to the domain owner, giving visibility into who is sending email using your domain name — including unauthorized senders.

DMARC at `p=reject` is the gold standard. It blocks all unauthorized email using your domain, making phishing and spoofing attacks significantly harder.

## How It Works

1. You publish a DMARC policy record at `_dmarc.your-domain.com`.
2. When a receiving server gets a message claiming to be from `@your-domain.com`, it checks:
   - Does SPF pass, **and** is the SPF-verified domain aligned with the `From:` header domain?
   - Does DKIM pass, **and** is the DKIM signing domain aligned with the `From:` header domain?
3. If neither SPF nor DKIM alignment passes, DMARC instructs the server to apply your policy.
4. Aggregate reports are sent daily to your RUA address; forensic reports on individual failures to RUF.

**Key concept:** DMARC *alignment* requires the domain in `From:` to match (strictly or relaxedly) the domain verified by SPF or DKIM. This prevents subdomain bypass attacks.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 7489](https://datatracker.ietf.org/doc/html/rfc7489) | DMARC (2015) — current standard |
| [RFC 9091](https://datatracker.ietf.org/doc/html/rfc9091) | Experimental: DMARC with PSDs |
| [RFC 8601](https://datatracker.ietf.org/doc/html/rfc8601) | Message header field for auth results |

## DNS Record Format

```dns
_dmarc.your-domain.com.  IN TXT  "v=DMARC1; p=reject; rua=mailto:dmarc-agg@your-domain.com; ruf=mailto:dmarc-forensic@your-domain.com; adkim=s; aspf=s; pct=100"
```

### Key Tags

| Tag | Values | Description |
|---|---|---|
| `p=` | `none`, `quarantine`, `reject` | **Required.** Policy for failing messages |
| `rua=` | `mailto:` URI | Aggregate report destination |
| `ruf=` | `mailto:` URI | Forensic report destination |
| `sp=` | `none`, `quarantine`, `reject` | Subdomain policy (defaults to `p=`) |
| `adkim=` | `s` (strict), `r` (relaxed) | DKIM alignment mode |
| `aspf=` | `s` (strict), `r` (relaxed) | SPF alignment mode |
| `pct=` | 1–100 | Percentage of messages to apply policy to |
| `fo=` | `0`, `1`, `d`, `s` | Forensic report options |

### Policy Levels

| Policy | Effect | Countries requiring this level |
|---|---|---|
| `p=none` | Monitor only — no messages blocked | — (starting point only) |
| `p=quarantine` | Send failing messages to spam/junk | — |
| `p=reject` | Block and discard failing messages | NL, US (federal), GB, AU (recommended) |

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite, Dutch government operated |
| MXToolbox DMARC | https://mxtoolbox.com/dmarc.aspx | Quick lookup |
| dmarcian | https://dmarcian.com | Full DMARC platform + analyzer |
| Postmark DMARC | https://dmarc.postmarkapp.com | Free weekly digest |
| DMARC Advisor | https://dmarcadvisor.com | Enterprise management |
| Mailcheck | https://passwordscon.org/mailcheck/ | Combined tester |

## Recommended Rollout Path

1. Start at `p=none` with `rua=` set — gather reports for 2–4 weeks
2. Review reports; identify all legitimate sending sources
3. Ensure all legitimate sources have SPF and DKIM configured
4. Move to `p=quarantine; pct=10` — gradually increase pct to 100
5. Move to `p=reject; pct=100` — complete enforcement

## Implementation Guides

- [Google: Set up DMARC](https://support.google.com/a/answer/2466580)
- [Microsoft 365: DMARC configuration](https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/email-authentication-dmarc-configure)
- [CISA: Email Authentication Guide](https://www.cisa.gov/sites/default/files/publications/email_authentication_how-to_guide_508c.pdf)
- [NCSC UK: Anti-spoofing using DMARC](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing/anti-spoofing-using-dmarc)

## Countries with DMARC Requirements

| Country | Status | Required Level | Applies To | Authority |
|---|---|---|---|---|
| Netherlands | **Mandatory** | p=reject | Government agencies | Forum Standaardisatie / BIO |
| United States | **Mandatory** | p=reject | Federal agencies | CISA BOD 18-01 |
| United Kingdom | **Mandatory** | p=reject | Government agencies | NCSC |
| Germany | Recommended | — | Gov / Critical infra | BSI TR-03108 |
| Australia | Recommended | p=reject | Government agencies | ASD / ACSC ISM |
| France | Recommended | — | Gov / Critical infra | ANSSI |
| Canada | Recommended | — | Government agencies | CCCS |
| EU | Informational | — | Critical infrastructure | ENISA / NIS2 |
