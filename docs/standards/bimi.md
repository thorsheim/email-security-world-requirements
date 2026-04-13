# BIMI — Brand Indicators for Message Identification

## Purpose

BIMI is an emerging standard that allows domain owners to display a verified brand logo next to their authenticated emails in supporting mail clients. It provides a visual trust signal for recipients, making it easier to identify legitimate email at a glance and harder for attackers to impersonate brands.

BIMI requires a strong DMARC policy (`p=quarantine` or `p=reject`) as a prerequisite, meaning it can only be implemented once an organization has solid SPF, DKIM, and DMARC infrastructure in place. Some implementations also require a Verified Mark Certificate (VMC) — a certificate issued by an authorized CA that confirms legal ownership of the logo.

BIMI is not currently mandated by any government. It is an industry-driven standard with growing support among major email providers.

## How It Works

1. The domain owner publishes a BIMI DNS record pointing to an SVG logo file.
2. Some implementations require a Verified Mark Certificate (VMC) from an approved authority (DigiCert, Entrust).
3. When a recipient's email client receives a message that passes DMARC, it fetches the BIMI record.
4. The logo is displayed in the email client's sender avatar/icon area.
5. If a VMC is present, clients may show a verified checkmark alongside the logo.

## Support Status (as of 2026)

| Client / Provider | BIMI Support | VMC Required |
|---|---|---|
| Gmail | Yes | Yes (for checkmark) |
| Apple Mail (iOS/macOS) | Yes | Yes |
| Yahoo Mail | Yes | No |
| Fastmail | Yes | No |
| Outlook / Microsoft 365 | Limited / in progress | — |

## RFCs and Specifications

BIMI is an industry draft, not yet an IETF RFC:

| Document | Description |
|---|---|
| [BIMI Group Specification](https://bimigroup.org/bimi-guide/) | Official specification and guide |
| [BIMI Working Group](https://bimigroup.org) | Governing body |
| [VMC Certificate Profile](https://bimigroup.org/verified-mark-certificates-vmc/) | VMC requirements |

## DNS Record Format

```dns
default._bimi.your-domain.com.  IN TXT  "v=BIMI1; l=https://your-domain.com/bimi-logo.svg; a=https://your-domain.com/bimi.pem"
```

| Tag | Description |
|---|---|
| `v=BIMI1` | Version (required) |
| `l=` | URL to SVG logo (must be hosted via HTTPS, SVG Tiny PS format) |
| `a=` | URL to VMC certificate (required by Gmail, Apple Mail) |

## Logo Requirements

- Format: SVG Tiny Portable/Secure (SVG Tiny PS) — a restricted subset of SVG
- Aspect ratio: 1:1 (square)
- Must be served over HTTPS
- Maximum file size: typically 32KB

## Prerequisites

1. **DMARC at `p=quarantine` or `p=reject`** — mandatory before BIMI
2. SPF and DKIM properly configured and aligned
3. Logo in SVG Tiny PS format
4. (For VMC-requiring clients) A Verified Mark Certificate

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| BIMI Group Inspector | https://bimigroup.org/bimi-generator/ | Generate and test BIMI records |
| MXToolbox BIMI | https://mxtoolbox.com/bimi.aspx | DNS record check |
| BIMI Group Checker | https://bimigroup.org/bimi-guide/check-your-bimi/ | End-to-end validation |

## Countries with BIMI Requirements

No country currently mandates BIMI. It is informational in all tracked jurisdictions.

| Country | Status | Notes |
|---|---|---|
| Netherlands | Informational | NCSC awareness materials only |
| All others | No data / Informational | No government guidance found |
