# SPF — Sender Policy Framework

## Purpose

SPF allows a domain owner to specify which mail servers are authorized to send email on behalf of their domain. This is done by publishing a DNS TXT record that lists authorized sending IP addresses or hostnames. When a receiving mail server accepts a message, it checks whether the sending server's IP address is on the authorized list for the sender's domain.

SPF is the most widely deployed email authentication standard and is often the first step in an organization's email security posture. It prevents simple email address forgery at the envelope level, reducing the effectiveness of phishing and spam campaigns that use your domain name without authorization.

## How It Works

1. You publish a DNS TXT record at `your-domain.com` listing your authorized mail servers.
2. A sending server delivers an email claiming to be from `user@your-domain.com`.
3. The receiving server queries DNS for `your-domain.com TXT` and checks whether the sending IP is listed.
4. The result is `pass`, `fail`, `softfail`, `neutral`, `none`, `temperror`, or `permerror`.
5. The result alone does not cause rejection — DMARC policy determines what action to take.

**Important limitation:** SPF checks the *envelope sender* (MAIL FROM), not the visible `From:` header. This means SPF alone does not prevent display name spoofing. DMARC addresses this by requiring SPF alignment with the `From:` header domain.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 7208](https://datatracker.ietf.org/doc/html/rfc7208) | Sender Policy Framework (2014) — current standard |
| [RFC 4408](https://datatracker.ietf.org/doc/html/rfc4408) | SPF v1 (2006) — obsoleted by RFC 7208 |
| [RFC 6652](https://datatracker.ietf.org/doc/html/rfc6652) | SPF Auth-Results extension |

## DNS Record Format

```dns
your-domain.com.  IN TXT  "v=spf1 include:_spf.google.com ip4:203.0.113.0/24 -all"
```

| Mechanism | Meaning |
|---|---|
| `ip4:`, `ip6:` | Authorize a specific IP address or range |
| `include:` | Include another domain's SPF record |
| `a:`, `mx:` | Authorize the domain's A or MX records |
| `all` | Match anything (use as last term with qualifier) |

| Qualifier | Meaning |
|---|---|
| `+` (default) | Pass — authorized |
| `-` | Fail — not authorized (hard fail) |
| `~` | Softfail — not authorized but still accept |
| `?` | Neutral — no policy |

**Best practice:** End with `-all` (hard fail). `~all` is acceptable during transition.

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite test; government-operated |
| MXToolbox SPF Lookup | https://mxtoolbox.com/spf.aspx | Quick DNS lookup |
| dmarcian SPF Surveyor | https://dmarcian.com/spf-survey/ | Visualize all authorized IPs |
| Mailcheck | https://passwordscon.org/mailcheck/ | Combined email security tester |

## Implementation Guides

- [Google Workspace: Set up SPF](https://support.google.com/a/answer/33786)
- [Microsoft 365: Set up SPF](https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/email-authentication-spf-configure)
- [NCSC UK: Anti-spoofing using SPF](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing/anti-spoofing-using-spf)

## Countries with SPF Requirements

See the [requirements matrix](../../README.md#requirements-matrix) for a full overview.

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United States | **Mandatory** | Federal agencies | CISA BOD 18-01 |
| United Kingdom | **Mandatory** | Government agencies | NCSC |
| Germany | Recommended | Gov / Critical infra | BSI TR-03108 |
| Australia | Recommended | Government agencies | ASD / ACSC ISM |
| France | Recommended | Gov / Critical infra | ANSSI |
| Canada | Recommended | Government agencies | CCCS |
