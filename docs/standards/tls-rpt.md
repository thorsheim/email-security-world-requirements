# TLS-RPT — SMTP TLS Reporting

## Purpose

TLS-RPT (TLSRPT) provides a mechanism for receiving mail servers to send daily aggregate reports to domain owners about failures in TLS negotiation. This allows operators to monitor the health of their TLS configuration, detect connectivity problems, certificate issues, and potential downgrade attacks against their MTA-STS or DANE policies.

TLS-RPT is the companion reporting standard to MTA-STS and DANE — just as DMARC provides reporting for SPF/DKIM, TLS-RPT provides reporting for transport-layer security failures. Without TLS-RPT, you have no visibility into whether your TLS policies are functioning correctly or being bypassed.

## How It Works

1. You publish a DNS TXT record at `_smtp._tls.your-domain.com` specifying a reporting address.
2. Sending mail servers that support TLS-RPT send JSON-formatted aggregate reports daily.
3. Reports include statistics on successful and failed TLS connections, policy failures, and MX resolution issues.
4. You process the reports to identify problems with your configuration or signs of active attack.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 8460](https://datatracker.ietf.org/doc/html/rfc8460) | SMTP TLS Reporting (2018) — current standard |
| [RFC 8461](https://datatracker.ietf.org/doc/html/rfc8461) | MTA-STS (companion standard) |

## DNS Record Format

```dns
_smtp._tls.your-domain.com.  IN TXT  "v=TLSRPTv1; rua=mailto:tls-reports@your-domain.com"
```

You can also send to an HTTPS endpoint:

```dns
_smtp._tls.your-domain.com.  IN TXT  "v=TLSRPTv1; rua=https://tlsrpt.your-domain.com/upload"
```

## Report Format

Reports are JSON files compressed with gzip, attached to daily summary emails. Key fields:

```json
{
  "organization-name": "Example Corp",
  "date-range": { "start-datetime": "...", "end-datetime": "..." },
  "policies": [{
    "policy": { "policy-type": "sts", "policy-domain": "your-domain.com" },
    "summary": { "total-successful-session-count": 1234, "total-failure-session-count": 0 },
    "failure-details": []
  }]
}
```

## Failure Types

| Failure Type | Possible Cause |
|---|---|
| `starttls-not-supported` | Receiving server does not offer STARTTLS |
| `certificate-host-mismatch` | TLS certificate does not match MX hostname |
| `certificate-expired` | Certificate is past its validity period |
| `certificate-not-trusted` | Cert not trusted by sending server's CA store |
| `validation-failure` | DANE TLSA record mismatch |
| `sts-policy-fetch-error` | Cannot retrieve MTA-STS policy |
| `mx-mismatch` | Actual MX does not match MTA-STS policy |

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Checks TLS-RPT presence |
| MXToolbox TLS-RPT | https://mxtoolbox.com/TLSRpt.aspx | DNS record check |
| Mailhardener | https://www.mailhardener.com | Report ingestion + analysis |

## Countries with TLS-RPT Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United Kingdom | Recommended | Government agencies | NCSC |
| United States | Recommended | Federal agencies | CISA |
