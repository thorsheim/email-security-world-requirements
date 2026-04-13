# CAA — Certification Authority Authorization

## Purpose

CAA DNS records allow domain owners to specify which Certificate Authorities (CAs) are authorized to issue TLS certificates for their domain. Before issuing a certificate, every CA is required by the CA/Browser Forum Baseline Requirements to check CAA records and refuse issuance if they are not listed.

For email security, CAA protects the TLS certificates used by:
- **STARTTLS** — the certificate used by your mail server for SMTP TLS
- **MTA-STS** — the HTTPS certificate for the `mta-sts.` policy endpoint
- **BIMI** — the HTTPS endpoint hosting your SVG logo

Without CAA, any CA in the hundreds of globally-trusted root certificates could issue a certificate for your domain — even without your knowledge or consent. CAA is a simple, effective defense against certificate mis-issuance.

## How It Works

1. You publish one or more CAA DNS records at `your-domain.com` (and optionally subdomains).
2. When a CA receives a certificate signing request for `your-domain.com`, it checks the CAA records.
3. If the CA is listed, it may proceed. If another CA is listed (or if the `issue` tag is blank — `""`), the CA must refuse issuance.
4. Certificate Transparency (CT) logs allow monitoring for any unauthorized certificates that were issued despite CAA.

CAA is enforced by CAs, not by browsers or mail clients. It is a preventive control, not a detection control. Pair with [cert-spotter](https://sslmate.com/certspotter/) or similar CT monitoring for detection.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 8659](https://datatracker.ietf.org/doc/html/rfc8659) | CAA Resource Record (2019) — current standard |
| [RFC 6844](https://datatracker.ietf.org/doc/html/rfc6844) | Original CAA RFC (2013) — obsoleted by RFC 8659 |
| [CA/Browser Forum BRs](https://cabforum.org/baseline-requirements/) | Baseline Requirements mandating CA checking |

## DNS Record Format

```dns
your-domain.com.  IN CAA  0 issue "letsencrypt.org"
your-domain.com.  IN CAA  0 issue "digicert.com"
your-domain.com.  IN CAA  0 issuewild "letsencrypt.org"
your-domain.com.  IN CAA  0 iodef "mailto:ssl-abuse@your-domain.com"
```

### CAA Tags

| Tag | Meaning |
|---|---|
| `issue` | Authorizes a CA to issue regular (non-wildcard) certificates |
| `issuewild` | Authorizes a CA to issue wildcard certificates |
| `iodef` | URL/email for CA to report policy violations |
| `contactemail` | Contact for certificate issues (informational) |
| `contactphone` | Contact for certificate issues (informational) |

### Block All Issuance

```dns
your-domain.com.  IN CAA  0 issue ";"
```

Use `";"` (semicolon) to block all certificate issuance for a domain (e.g., non-sending domains that should never have certificates).

### Common CA Values

| CA | CAA value |
|---|---|
| Let's Encrypt | `letsencrypt.org` |
| DigiCert | `digicert.com` |
| Sectigo | `sectigo.com` |
| GlobalSign | `globalsign.com` |
| Entrust | `entrust.net` |
| Google Trust Services | `pki.goog` |

## Implementation Notes

- CAA is **not inherited** by subdomains — each subdomain should have its own CAA record (or rely on the parent domain's record via the lookup algorithm).
- CAA lookup algorithm: check the exact domain; if none found, walk up the tree (e.g., `mail.example.com` → `example.com` → `com`).
- The flag value `0` is standard; `128` is "critical" (CA must refuse if it doesn't understand the tag).
- Certificate Transparency monitoring complements CAA: use CT logs to detect mis-issuance.

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite including CAA |
| MXToolbox CAA Lookup | https://mxtoolbox.com/caa.aspx | Quick DNS lookup |
| SSLMate CAA Generator | https://sslmate.com/caa/ | Generate CAA records |
| Hardenize | https://www.hardenize.com | Comprehensive check including CAA |
| crt.sh | https://crt.sh | Certificate Transparency log search |

## Countries with CAA Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United Kingdom | Recommended | Government agencies | NCSC |
| United States | Recommended | Federal agencies | CISA |
| Germany | Recommended | Gov / Critical infra | BSI |
| Australia | Recommended | Government agencies | ASD / ACSC ISM |
| France | Informational | Gov / Critical infra | — |
| Canada | Informational | Government agencies | — |
