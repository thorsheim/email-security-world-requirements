# DANE — DNS-based Authentication of Named Entities

## Purpose

DANE uses DNSSEC-secured TLSA records to bind a TLS certificate or public key to a specific domain name in DNS. For email (SMTP), DANE/TLSA prevents downgrade attacks (where an attacker forces cleartext delivery by pretending TLS is unavailable) and certificate substitution attacks (where a rogue CA issues a fraudulent certificate for your domain).

Unlike traditional TLS certificate validation, which relies on a large number of trusted Certificate Authorities (CAs), DANE anchors trust in DNSSEC, allowing domain owners to directly specify which certificates are valid for their mail server. DANE for SMTP is described in RFC 7672.

The Netherlands mandates DANE for all government mail servers — the most comprehensive government requirement for DANE globally.

## How It Works

1. The mail server operator publishes a TLSA record in DNSSEC-signed DNS.
2. A sending mail server (via SMTP) does an SMTP lookup for the recipient's MX record.
3. It also fetches the TLSA record for the MX hostname.
4. DNSSEC validation confirms the TLSA record is authentic.
5. The sending server connects via TLS and verifies the server's certificate matches the TLSA record.
6. If the certificate does not match or TLS cannot be established, delivery is refused (no downgrade to plaintext).

**Prerequisite:** DNSSEC must be enabled on the domain hosting the MX record(s). Without DNSSEC, DANE cannot be used.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 6698](https://datatracker.ietf.org/doc/html/rfc6698) | DANE: TLS Protocol TLSA records (2012) |
| [RFC 7671](https://datatracker.ietf.org/doc/html/rfc7671) | DANE TLS protocol updates (2015) |
| [RFC 7672](https://datatracker.ietf.org/doc/html/rfc7672) | SMTP Security via Opportunistic DANE TLS |
| [RFC 8461](https://datatracker.ietf.org/doc/html/rfc8461) | MTA-STS (complementary standard) |

## DNS Record Format

TLSA records are published at: `_port._protocol.hostname`

For SMTP (port 25):

```dns
_25._tcp.mail.your-domain.com.  IN TLSA  3 1 1 <hex-sha256-of-public-key>
```

### TLSA Record Fields

| Field | Value | Meaning |
|---|---|---|
| Certificate Usage | `3` | DANE-EE (domain-issued certificate) |
| Selector | `1` | SubjectPublicKeyInfo (public key only) |
| Matching Type | `1` | SHA-256 hash |

**Recommended:** `3 1 1` (DANE-EE, SPKI, SHA-256) — most widely supported and interoperable.

## Implementation Requirements

- DNSSEC must be signed and validated for the zone containing MX records
- TLSA records must be created for each MX hostname
- TLS must be supported by the mail server on port 25
- Certificate must match the TLSA record (keep records in sync when renewing certificates)

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite, including DANE for SMTP |
| DANE SMTP Validator | https://danetools.com/smtp | DANE-specific test |
| MXToolbox DANE Lookup | https://mxtoolbox.com/dane.aspx | Quick DNS check |
| SIDN DANE Checker | https://check.sidnlabs.nl/dane/ | Dutch NIC DANE tool |

## Countries with DANE Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United States | Informational | Federal agencies | — |
| United Kingdom | Informational | Government agencies | — |
| Germany | Informational | Government agencies | BSI |

> **Note:** DANE requires DNSSEC, which has lower global adoption than other email security standards. This makes DANE one of the more challenging standards to deploy at scale.
