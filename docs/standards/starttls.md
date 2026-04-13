# STARTTLS — SMTP Opportunistic TLS

## Purpose

STARTTLS upgrades a plaintext SMTP connection to an encrypted TLS connection via an in-band negotiation command. It is the baseline standard for encrypted email transport between mail servers (SMTP on port 25) and between email clients and their submission servers (port 587).

Without STARTTLS, email is transmitted in cleartext, making it trivially readable to anyone with access to the network path. STARTTLS is supported by virtually all modern mail servers and is the minimum expected level of email transport security. Most security frameworks and government mandates include STARTTLS as a baseline requirement.

**Important limitation:** STARTTLS is *opportunistic* — it can be silently downgraded to plaintext by a network attacker (a "STRIPTLS" attack). DANE and MTA-STS address this limitation by making TLS mandatory with certificate verification.

## How It Works

1. The sending server connects to the receiving server on port 25 (SMTP).
2. The receiving server advertises `STARTTLS` in its EHLO response.
3. The sending server issues the `STARTTLS` command.
4. Both servers perform a TLS handshake, upgrading the connection to encrypted transport.
5. The SMTP session continues over the encrypted channel.

For client submission (port 587), the same mechanism applies. Implicit TLS on port 465 (SMTPS) wraps the entire connection in TLS from the start without needing STARTTLS negotiation.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 3207](https://datatracker.ietf.org/doc/html/rfc3207) | SMTP Service Extension for Secure SMTP over TLS (2002) |
| [RFC 8314](https://datatracker.ietf.org/doc/html/rfc8314) | Cleartext Considered Obsolete — recommends TLS for MUAs (2018) |
| [RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321) | SMTP base protocol |
| [RFC 7525](https://datatracker.ietf.org/doc/html/rfc7525) | TLS/DTLS recommendations |

## Configuration Recommendations

- Enable STARTTLS on port 25 (inbound and outbound MTA)
- Enable implicit TLS on port 465 for client submission (preferred over STARTTLS on 587)
- Use TLS 1.2 minimum; TLS 1.3 preferred
- Disable TLS 1.0 and TLS 1.1
- Use strong cipher suites (disable RC4, 3DES, export ciphers, NULL ciphers)
- Use a valid, trusted TLS certificate (not self-signed for MTA-to-MTA)
- Pair with DANE or MTA-STS to prevent downgrade attacks

## Ports Reference

| Port | Protocol | Use |
|---|---|---|
| 25 | SMTP + STARTTLS | Server-to-server (MTA) |
| 465 | SMTPS (implicit TLS) | Client-to-server submission (preferred) |
| 587 | Submission + STARTTLS | Client-to-server submission |
| 993 | IMAPS (implicit TLS) | IMAP over TLS |
| 995 | POP3S (implicit TLS) | POP3 over TLS |

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Tests STARTTLS, TLS version, cipher suites |
| MXToolbox SMTP Diagnostics | https://mxtoolbox.com/diagnostic.aspx | Full SMTP test including TLS |
| Mailcheck | https://passwordscon.org/mailcheck/ | Combined email security tester |
| Hardenize | https://www.hardenize.com | Detailed TLS configuration analysis |
| SSL Labs (for port 443) | https://www.ssllabs.com/ssltest/ | Note: tests HTTPS, not SMTP |
| testssl.sh | https://testssl.sh | CLI tool for any TLS service |

## Implementation Guides

- [NCSC UK: Securing email in transit](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing/securing-email-in-transit)
- [BSI TR-03108: Sicherer E-Mail-Transport](https://www.bsi.bund.de/)
- [Forum Standaardisatie: STARTTLS+DANE](https://www.forumstandaardisatie.nl/open-standaarden/starttls-dane)

## Countries with STARTTLS Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United States | **Mandatory** | Federal agencies | CISA BOD 18-01 |
| United Kingdom | **Mandatory** | Government agencies | NCSC |
| Germany | Recommended | Gov / Critical infra | BSI TR-03108 |
| Australia | Recommended | Government agencies | ASD / ACSC ISM |
| France | Recommended | Gov / Critical infra | ANSSI |
| Canada | Recommended | Government agencies | CCCS |
